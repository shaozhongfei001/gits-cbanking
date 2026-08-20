"""真实 LLM 适配器（OpenAI 兼容 chat/completions，默认 DeepSeek 官方 API）。

凭据只从环境加载，绝不硬编码 / 落盘 / 打印：
  - API key：DSEEK_2026_SZF_KEY（DeepSeek），回退 LLM_API_KEY（通用）
  - base_url / model：DKWS_LLM_BASE_URL / DKWS_LLM_MODEL（默认 api.deepseek.com / deepseek-chat）

用法（与 Java 端 engagement.llm.mode 语义对齐）：
  LLM_MODE=real 时 PrevisitAssembler 使用本适配器；否则用 MockLlm。
真实调用结果无法复现（外部模型非确定性），因此本适配器只用于演示/验证链路的 LLM 环节，
数据组装逻辑本身保持确定性。
"""

from __future__ import annotations

import json
import os
import ssl
import time
import urllib.request
from dataclasses import dataclass


class LlmConfigError(RuntimeError):
    pass


def _dedupe(items: list) -> list:
    """保序去重（str 化去重，保留首次出现）。"""
    seen: set[str] = set()
    out = []
    for x in items:
        key = str(x).strip()
        if x is None or key in seen:
            continue
        seen.add(key)
        out.append(x)
    return out


@dataclass
class LlmCall:
    input_tokens: int = 0
    output_tokens: int = 0
    latency_ms: int = 0
    model: str = ""


class RealLlm:
    """OpenAI 兼容 chat/completions 客户端。converse() 返回模型生成的文本。"""

    def __init__(self, *, base_url: str | None = None, api_key: str | None = None,
                 model: str | None = None, timeout_s: int = 90):
        self.base_url = (base_url or os.environ.get("DKWS_LLM_BASE_URL")
                         or "https://api.deepseek.com").rstrip("/")
        self.api_key = api_key or os.environ.get("DSEEK_2026_SZF_KEY") or os.environ.get("LLM_API_KEY")
        self.model = model or os.environ.get("DKWS_LLM_MODEL") or "deepseek-chat"
        self.timeout_s = timeout_s
        if not self.api_key:
            raise LlmConfigError(
                "缺少 LLM 凭据：请先 eval \"$(grep '^export DSEEK_2026_SZF_KEY=' ~/.bashrc)\" "
                "或设置 LLM_API_KEY。凭据不得硬编码。")
        if not self.base_url.startswith(("https://", "http://")):
            raise LlmConfigError(f"非法 base_url: {self.base_url}")
        self._calls: list[LlmCall] = []

    def converse(self, system_prompt: str, user_prompt: str,
                 temperature: float = 0.2, max_tokens: int = 2048) -> str:
        body = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        payload = json.dumps(body).encode("utf-8")
        req = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
                "Accept": "application/json",
            },
            method="POST",
        )
        # 关闭 ssl 校验绕过（仅限受信任端点 proxy 场景）；默认保留校验
        ctx = ssl.create_default_context()
        t0 = time.perf_counter()
        try:
            with urllib.request.urlopen(req, timeout=self.timeout_s, context=ctx) as resp:
                raw = resp.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8")[:500]
            raise LlmConfigError(f"LLM HTTP {exc.code}: {detail}") from exc
        except urllib.error.URLError as exc:
            raise LlmConfigError(f"LLM 网络错误: {exc.reason}") from exc
        elapsed_ms = int((time.perf_counter() - t0) * 1000)

        parsed = json.loads(raw)
        try:
            content = parsed["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise LlmConfigError(f"LLM 响应缺少 choices[0].message.content: {raw[:300]}") from exc
        usage = parsed.get("usage", {})
        call = LlmCall(input_tokens=int(usage.get("prompt_tokens", 0)),
                       output_tokens=int(usage.get("completion_tokens", 0)),
                       latency_ms=elapsed_ms, model=parsed.get("model", self.model))
        self._calls.append(call)
        return content

    def compose_json(self, system_prompt: str, user_prompt: str,
                     *, temperature: float = 0.2, max_tokens: int = 2048) -> dict:
        """调用真实 LLM 并解析为 JSON dict（模型可能夹杂 markdown 围栏）。"""
        text = self.converse(system_prompt, user_prompt, temperature=temperature,
                             max_tokens=max_tokens)
        text = text.strip()
        for fence in ("```json", "```JSON", "```"):
            if text.startswith(fence):
                text = text[len(fence):]
                if text.endswith("```"):
                    text = text[:-3]
                text = text.strip()
                break
        return json.loads(text)

    def last_calls(self) -> list[LlmCall]:
        return list(self._calls)

    # ------------------------------------------------------------- 访前报告组装（与 MockLlm.compose 同签名）
    def compose(self, activation: dict, retrieved: dict) -> list[dict]:
        """真实 LLM 读激活合同 + 已检索的 DKWS 资产，生成结构化访前要点序列。

        返回与 MockLlm.compose 相同的 section 列表（assetId/purpose/required/sequence/items）。
        其中 items 由模型基于 retrieved 各资产数据归纳（synthetic 输入，模型带不确定性）。
        """
        system = (
            "你是客户经理持续经营的访前准备助手。请根据『激活合同』和『已检索的数据资产』，"
            "按 sequence 顺序生成访前数据组装清单。只输出 JSON 数组，不要 markdown 围栏。"
        )
        # 构造检索上下文（脱敏：仅业务字段，不含凭据/路径）
        retrieved_brief = {}
        for asset_id, hits in retrieved.items():
            retrieved_brief[asset_id] = [
                {k: v for k, v in h.items() if k in ("entity_id", "name", "entity_type", "status")}
                for h in hits
            ]
        user = json.dumps({
            "activation_contract": {
                "contractId": activation.get("contractId"),
                "routeMode": activation.get("routeMode"),
                "activations": [{ "assetId": a["assetId"], "purpose": a["purpose"],
                                  "required": a["required"], "sequence": a["sequence"] }
                                for a in activation.get("activations", [])],
            },
            "retrieved_assets": retrieved_brief,
        }, ensure_ascii=False)
        parsed = self.compose_json(system, user, max_tokens=2048)
        if not isinstance(parsed, list):
            parsed = parsed.get("sections", [])

        # 规整为与合同对齐的 section；模型结果与合同 assetId 对齐后合并
        by_id = {a["assetId"]: a for a in activation.get("activations", [])}
        out = []
        for item in parsed:
            if not isinstance(item, dict):
                continue
            asset_id = item.get("assetId") or item.get("asset_id")
            act = by_id.get(asset_id)
            if act is None:
                continue
            model_items = item.get("items")
            if not isinstance(model_items, list):
                model_items = [model_items] if model_items else []
            # 数据回填：LLM 确定结构，实际数据由 DKWS 已检索资产提供
            source_names = [h.get("name") for h in retrieved.get(asset_id, []) if h.get("name")]
            # 合并去重：保序去重（模型要点在前，DKWS 数据补全），不产生重复
            items = _dedupe(model_items + source_names) if model_items or source_names else []
            out.append({
                "assetId": asset_id,
                "purpose": act["purpose"],
                "required": act["required"],
                "sequence": item.get("sequence", act["sequence"]),
                "items": items,
                "_llm_generated": True,
            })
        out.sort(key=lambda s: s.get("sequence", 0))
        return out