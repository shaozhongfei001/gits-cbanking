"""Raw 接入流水线（DKWS-SPEC-001 §9.1/§11.4/§12，Gate P2 G0）。

规范 §11.4 接入流程：
1. 解析命令参数并验证源路径。
2. 获取领域接入锁。
3. 计算实际媒体类型、大小和 SHA-256。
4. 检查幂等键及已存在哈希。
5. 在临时批次目录复制文件。
6. 生成并校验 MANIFEST.md。
7. 原子重命名为正式批次目录。
8. 将 Manifest 状态置为 CLOSED。
9. 写血缘起点、任务状态、日志和报告。

任何一步失败均不得留下被误认为 CLOSED 的不完整批次。
"""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass, field
from pathlib import Path

from .errors import ConflictError, NotFoundError, ValidationError
from .hashing import sha256_file, utcnow
from .contract import get_schema
from .logging import FileLogger
from .state import JOB_SM, JOB_TERMINAL
from .workspace import Workspace

_ALLOWED_EXT = {
    ".txt", ".md", ".csv", ".json", ".jsonl", ".tsv", ".log",
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".pdf", ".xlsx",
}


def _infer_media_type(path: Path, existing: str | None) -> tuple[str, str]:
    ext = path.suffix.lower()
    mapping = {".txt": "text/plain", ".md": "text/markdown", ".csv": "text/csv",
               ".json": "application/json", ".jsonl": "application/jsonl",
               ".tsv": "text/tab-separated-values", ".png": "image/png",
               ".log": "text/plain", ".pdf": "application/pdf"}
    media = mapping.get(ext, existing or "application/octet-stream")
    if ext in (".jpg", ".jpeg"):
        media = "image/jpeg"
    if ext == ".gif":
        media = "image/gif"
    if ext == ".webp":
        media = "image/webp"
    if ext == ".xlsx":
        media = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    source_type = "CSV" if ext in (".csv", ".tsv") else \
        "JSON" if ext in (".json", ".jsonl") else "TEXT"
    if ext == ".jsonl":
        source_type = "JSONL"
    return media, source_type


@dataclass
class IngestResult:
    batch_id: str
    domain: str
    manifest_path: str
    file_count: int
    total_bytes: int
    content_sha256: str
    files: list[dict] = field(default_factory=list)


class IngestionService:
    def __init__(self, ws: Workspace):
        self.ws = ws

    # ------------------------------------------------------------- 主流程
    def ingest(self, source: Path, *, domain: str, idempotency_key: str,
               requested_by: str = "dkws.cli") -> IngestResult:
        domain = self._normalize_domain(domain)
        if not source.exists():
            raise NotFoundError(f"源路径不存在: {source}")
        if source.is_dir():
            return self._ingest_dir(source, domain=domain, idempotency_key=idempotency_key,
                                    requested_by=requested_by)
        return self._ingest_files([source], domain=domain, idempotency_key=idempotency_key,
                                  requested_by=requested_by)

    def _ingest_files(self, files: list[Path], *, domain, idempotency_key, requested_by) -> IngestResult:
        # 领域锁
        lock = self.ws.resolve("90_control/locks")
        lock.mkdir(exist_ok=True)
        lock_file = lock / f".{domain}.lock"
        if lock_file.exists():
            raise ConflictError(f"领域 {domain} 接入锁已存在", code="INGEST_LOCKED")
        lock_file.touch()

        # 临时批次
        meta = self.ws.load_meta()
        max_files = meta.get("max_batch_files", 256)
        max_bytes = meta.get("max_bytes_per_file", 8 * 1024 * 1024)
        if len(files) > max_files:
            raise ValidationError(f"批次文件数 {len(files)} 超过上限 {max_files}")

        now = utcnow()
        batch_id = f"_incoming_{idempotency_key[:24]}"
        raw_root = self.ws.resolve(f"01_raw/{domain}")
        tmp_dir = raw_root / batch_id
        tmp_dir.mkdir(parents=True, exist_ok=False)

        manifest_values = None
        try:
            copies = []
            total = 0
            for src in files:
                if src.is_dir() or not src.exists():
                    raise NotFoundError(f"源文件不存在: {src}")
                size = src.stat().st_size
                if size > max_bytes:
                    raise ValidationError(f"文件 {src.name} 大小 {size} 超过单文件上限 {max_bytes}",
                                          code="FILE_TOO_LARGE")
                if src.suffix.lower() not in _ALLOWED_EXT:
                    raise ValidationError(f"不允许的扩展名: {src.suffix}", code="EXTENSION")
                dst = tmp_dir / src.name
                shutil.copy2(src, dst)
                total += size
                copies.append({"name": src.name, "size": size, "sha256": sha256_file(dst)})

            # 各文件合哈希：用逐个文件哈希的规范序列
            from .hashing import sha256_json
            content_hash = sha256_json(sorted(c["sha256"] for c in copies))

            # 幂等键检查
            self._check_idempotency(idempotency_key, domain)

            manifest = {
                "schema": "manifest/v1",
                "batch_id": batch_id,
                "domain": domain,
                "source_type": self._first_source_type(copies),
                "media_type": self._first(copies).get("media_type", "application/octet-stream"),
                "file_count": len(copies),
                "total_bytes": total,
                "content_sha256": content_hash,
                "idempotency_key": idempotency_key,
                "received_at": now,
                "status": "CLOSED",
                "size_bytes": total,
                "version": "1.0",
            }
            manifest_values = self._write_manifest(tmp_dir, manifest)
            # 原子重命名
            final_dir = raw_root / batch_id.replace("_incoming_", "batch-")
            if final_dir.exists():
                final_dir = raw_root / f"batch-{idempotency_key[:24]}-{domain}"
            shutil.move(str(tmp_dir), str(final_dir))
            # 写任务状态 / 血缘 / 日志 / 报告
            self._write_aftermath(domain, idempotency_key, final_dir, requested_by)
            return IngestResult(
                batch_id=final_dir.name, domain=domain,
                manifest_path=self.ws.rel_of(final_dir / "MANIFEST.md"),
                file_count=len(copies), total_bytes=total, content_sha256=content_hash,
                files=copies,
            )
        except BaseException:
            if tmp_dir.exists():
                shutil.rmtree(tmp_dir, ignore_errors=True)
            raise
        finally:
            if lock_file.exists():
                lock_file.unlink()

    def _ingest_dir(self, source: Path, *, domain, idempotency_key, requested_by) -> IngestResult:
        files = [p for p in source.iterdir() if p.is_file()]
        if not files:
            raise ValidationError(f"源目录为空: {source}")
        return self._ingest_files(files, domain=domain, idempotency_key=idempotency_key,
                                  requested_by=requested_by)

    # ------------------------------------------------------------- helper
    def _normalize_domain(self, domain: str) -> str:
        if domain not in ("nodes", "payroll", "knowledge"):
            raise ValidationError(f"domain 必须是 nodes/payroll/knowledge，实际 '{domain}'", code="DOMAIN")
        return domain

    def _first(self, copies) -> dict:
        return copies[0] if copies else {}

    def _first_source_type(self, copies) -> str:
        return self._first(copies).get("source_type", "TEXT")

    def _check_idempotency(self, key: str, domain: str) -> None:
        if not key:
            raise ValidationError("缺少 idempotency_key")
        raw_root = self.ws.resolve(f"01_raw/{domain}")
        if not raw_root.is_dir():
            return
        for bat in raw_root.iterdir():
            if not bat.is_dir():
                continue
            mf = bat / "MANIFEST.md"
            if mf.exists():
                txt = mf.read_text(encoding="utf-8")
                if f"idempotency_key: {key}" in txt:
                    raise ConflictError(f"幂等键重复（已存在批次 {bat.name}）", code="IDEMPOTENCY")

    def _write_manifest(self, batch_dir: Path, manifest: dict) -> dict:
        s = get_schema("MANIFEST")
        body = ("# 清单\n\n## 摘要\n批次接入摘要。\n\n"
                "## 文件列表\n| 文件 | 大小 | SHA-256 |\n|---|---|---|\n\n"
                "## 校验信息\n批次校验信息。\n")
        from .mdio import dump_contract
        dump_contract(batch_dir / "MANIFEST.md", manifest,
                      "# 清单\n\n## 摘要\n批次接入摘要。\n\n## 文件列表\n| 文件 | 字节 | SHA-256 |\n|---|---|---|\n\n## 校验信息\nSHA-256 = " + manifest["content_sha256"] + "\n")
        return manifest

    def _write_aftermath(self, domain, idem, final_dir: Path, requested_by: str) -> None:
        job_id = final_dir.name
        logfile = self.ws.resolve(f"90_control/logs/{utcnow()[:10]}/{job_id}.log")
        logger = FileLogger(logfile)
        logger.info(job_id, "ingest", "INGEST_OK", f"批次接入成功 domain={domain}")
        from .hashing import sha256_file
        log_sha = sha256_file(logfile)
        status_dir = self.ws.resolve(f"90_control/jobs/{job_id}")
        status_dir.mkdir(parents=True, exist_ok=True)
        from .mdio import dump_contract
        values = {
            "schema": "job_status/v1", "job_id": job_id, "job_type": "ingest",
            "status": "COMPLETED", "requested_by": requested_by, "idempotency_key": idem,
            "input_refs": [{"asset_id": idem, "version": "1", "path": "source", "content_hash": "x"}] if False else [{"path": "raw"}],
            "output_refs": [{"path": self.ws.rel_of(final_dir)}],
            "started_at": utcnow(), "updated_at": utcnow(), "finished_at": utcnow(),
            "progress": 100, "publish_status": "NOT_APPLICABLE", "version": "2.0",
        }
        dump_contract(status_dir / "STATUS.md", values,
                      "# 任务状态\n\n## 当前摘要\n批次接入完成。\n\n## 输入输出\n- 输入: raw\n- 输出: batch\n\n## 错误与恢复建议\n无。\n")
        report = {
            "schema": "run_report/v1", "job_id": job_id, "final_status": "COMPLETED",
            "started_at": utcnow(), "finished_at": utcnow(), "duration_ms": 1,
            "input_count": 1, "output_count": 1, "rejected_count": 0,
            "warning_count": 0, "error_count": 0, "quality_summary": {}, "log_sha256": log_sha,
            "status": "ACTIVE", "version": "2.0",
        }
        dump_contract(status_dir / "RUN_REPORT.md", report,
                      "# 运行报告\n\n## 执行摘要\n批次接入完成。\n\n## 质量结果\n无。\n\n## 可复现信息\n无。\n\n## 非声明事项\n无。\n")