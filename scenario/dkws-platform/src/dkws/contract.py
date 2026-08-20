"""契约化 Markdown 框架（DKWS-SPEC-001 §8/§9）：frontmatter 解析、字段规则、schema 校验、DSL 校验、正文固定标题。

- 每个 Markdown 文件 = YAML frontmatter（结构化字段） + 正文（固定标题分节）。
- 生成物只读；不承载宿主绝对路径；用工作区相对路径。
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

import yaml

from .errors import ContractError

_YAML_TRUTHY = {"true", "yes", "on", "y"}
_YAML_FALSY = {"false", "no", "off", "n"}


def _str_to_type(value: str, kind: str):
    """frontmatter 值是字符串，按字段声明类型转换。"""
    try:
        if kind in ("string", "enum", "schema", "expression"):
            return value
        if kind == "integer":
            return int(value)
        if kind == "number":
            return float(value)
        if kind == "boolean":
            low = value.strip().lower()
            if low in _YAML_TRUTHY:
                return True
            if low in _YAML_FALSY:
                return False
            raise ValueError(f"不是布尔: {value}")
        if kind in ("list", "list[string]", "list[str]"):
            parsed = yaml.safe_load(value)
            return parsed if isinstance(parsed, list) else [v.strip() for v in value.split(",") if v.strip()]
        if kind == "list[object]":
            parsed = yaml.safe_load(value)
            return parsed if isinstance(parsed, list) else []
        if kind == "map":
            parsed = yaml.safe_load(value)
            return parsed if isinstance(parsed, dict) else {}
        if kind == "date":
            return value  # ISO 字符串
        if kind == "timestamp":
            return value
        return value
    except Exception as exc:  # noqa: BLE001
        raise ContractError(
            f"字段类型转换失败: kind={kind} value={value!r}: {exc}",
            code="FIELD_TYPE",
        ) from exc


@dataclass
class FieldRule:
    """单个字段声明。name 支持点路径（list 内嵌 map 用 .field）。"""

    name: str
    kind: str = "string"          # string/integer/number/boolean/enum/list/map/date/timestamp/expression/object
    required: bool = False
    enum: list[str] | None = None
    condition: str | None = None  # "field==VALUE" 条件必填
    default: Any = None
    description: str = ""
    kind_in_list: str | None = None  # 元素类型


@dataclass
class Schema:
    """一种合同 schema（对应 9.x 各文件类型）。"""

    name: str                        # MANIFEST / DOCUMENT / NORMALIZED / ...
    contract: str                    # frontmatter schema 值，如 "manifest/v1"
    fields: list[FieldRule] = field(default_factory=list)
    required_headings: list[str] = field(default_factory=list)
    path_regex: str | None = None
    check: Any = None                # 附加语义校验函数 (values)->list[str] 错误

    def validate_contract(self, value: str) -> None:
        if value != self.contract:
            raise ContractError(f"schema 字段应为 '{self.contract}'，实际 '{value}'", code="SCHEMA_MISMATCH")

    def apply_fields(self, raw: dict[str, Any]) -> dict[str, Any]:
        """类型化 + 默认值 + 必填/枚举/条件校验，返回规范化的字段值。"""
        values: dict[str, Any] = {}
        for rule in self.fields:
            present = rule.name in raw
            if not present and rule.default is not _MISSING:
                values[rule.name] = rule.default
                continue
            if not present:
                # 条件必填
                if rule.condition:
                    cond_field, cond_val = rule.condition.split("==", 1)
                    if values.get(cond_field) == cond_val and rule.required:
                        raise ContractError(f"缺失必填字段(条件): {rule.name}", field=rule.name)
                if rule.required:
                    raise ContractError(f"缺失必填字段: {rule.name}", field=rule.name)
                continue
            raw_val = raw[rule.name]
            if isinstance(raw_val, str) and rule.kind not in ("list", "list[object]", "map", "object") \
                    and rule.kind not in ("list[string]",):
                # YAML 已解析的多行列表，跳过字符串强制转换
                if rule.kind.startswith("list"):
                    values[rule.name] = _str_to_type(raw_val, rule.kind) if isinstance(raw_val, str) else raw_val
                else:
                    values[rule.name] = _coerce_scalar(raw_val, rule.kind)
            else:
                values[rule.name] = _coerce(raw_val, rule)
            # enum
            if rule.enum is not None:
                val = values[rule.name]
                if isinstance(val, list):
                    if any(v not in rule.enum for v in val):
                        raise ContractError(
                            f"字段 {rule.name} 含非法枚举值（允许: {rule.enum}）", field=rule.name, code="ENUM")
                elif val not in rule.enum:
                    raise ContractError(f"字段 {rule.name} 值 {val} 不在枚举 {rule.enum}", field=rule.name, code="ENUM")
        return values


_MISSING = object()


def _coerce_scalar(val, kind):
    if kind in ("string", "enum", "expression", "schema", "object"):
        return val
    if kind == "integer":
        return int(val)
    if kind == "number":
        return float(val)
    if kind == "boolean":
        if isinstance(val, bool):
            return val
        low = str(val).strip().lower()
        if low in _YAML_TRUTHY:
            return True
        if low in _YAML_FALSY:
            return False
        raise ContractError(f"不是布尔: {val}", code="FIELD_TYPE", field=None)
    if kind in ("date", "timestamp"):
        return val
    return val


def _coerce(val, rule: FieldRule):
    if rule.kind == "list[string]":
        if isinstance(val, list):
            return [str(v) for v in val]
        return _str_to_type(str(val), "list[string]")
    if rule.kind == "list[object]":
        return val if isinstance(val, list) else []
    if rule.kind.startswith("list"):
        return val if isinstance(val, list) else _str_to_type(str(val), "list")
    return _coerce_scalar(val, rule.kind)


# ---------------------------------------------------------------- 解析器

def parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    """解析 Markdown frontmatter（--- 分隔）。返回 (字段 dict, 正文)。正文未分割为标题，调用方处理。

    支持说明：frontmatter 由 YAML 解析；若 YAML 非 dict，抛错。
    """
    norm = text if not isinstance(text, bytes) else text.decode("utf-8")
    if norm.startswith("\ufeff"):
        norm = norm[1:]
    lines = norm.split("\n")
    if not lines or lines[0].strip() != "---":
        raise ContractError("缺少 frontmatter 定界符（首行为 ---）", code="FRONTMATTER")
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        raise ContractError("frontmatter 缺少闭合 ---", code="FRONTMATTER")
    fm = "\n".join(lines[1:end])
    body = "\n".join(lines[end + 1:])
    if not fm.strip():
        raise ContractError("frontmatter 为空", code="FRONTMATTER")
    try:
        data = yaml.safe_load(fm)
    except yaml.YAMLError as exc:
        raise ContractError(f"frontmatter YAML 解析失败: {exc}", code="FRONTMATTER_YAML") from exc
    if not isinstance(data, dict):
        raise ContractError("frontmatter 必须是 key-value 映射", code="FRONTMATTER")
    return data, body


# ---------------------------------------------------------------- 正文标题校验

_H1_TITLE = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)
_H2 = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)


def validate_headings(body: str, required: list[str]) -> list[str]:
    """校验正文是否包含要求的标题。返回缺失项列表。

    兼容声明形式：required 项可按 `# 清单`（H1）或 `## 摘要`（H2）书写。
    实际匹配时 H1/H2 前缀均被剥离后按文本名比较。
    """
    h1s = [m.group(1).strip() for m in _H1_TITLE.finditer(body)]
    h2s = [m.group(1).strip() for m in _H2.finditer(body)]
    present = {("H1", t) for t in h1s} | {("H2", t) for t in h2s}
    missing = []
    for h in required:
        stripped = h.lstrip("#").strip()
        level = "H1" if h.startswith("# ") else "H2"
        if (level, stripped) not in present:
            missing.append(h)
    return missing


def heading_map(body: str) -> dict[str, str]:
    """提取 H2 标题 -> 该节正文（直到下一 H2 或 H1）。参数式标题（## x(foo)）按前缀匹配归并。"""
    sections: list[tuple[str, list[str]]] = []
    current: tuple[str, list[str]] | None = None
    for line in body.split("\n"):
        m = _H2.match(line)
        if m:
            if current:
                sections.append(current)
            current = (m.group(1).strip(), [])
            continue
        if _H1_TITLE.match(line) and current:
            sections.append(current)
            current = None
            continue
        if current:
            current[1].append(line)
    if current:
        sections.append(current)
    result: dict[str, str] = {}
    for title, lines in sections:
        result[title] = "\n".join(lines).strip()
    return result


# ---------------------------------------------------------------- DSL 校验（§9.8 受限 DSL）

_DSL_KEYWORDS = {"all", "any", "not", "eq", "ne", "gt", "gte", "lt", "lte", "in", "not_in",
                 "contains", "starts_with", "exists", "is_null"}
_DANGEROUS = re.compile(r"(\$\(|;|\||`|import|exec|eval|subprocess|open\(|os\.|sys\.|__)", re.IGNORECASE)


def _validate_dsl_expr(expr: Any, path: str, errors: list[str]) -> None:
    if isinstance(expr, bool) or expr is None:
        return
    if isinstance(expr, (int, float)):
        return
    if isinstance(expr, str):
        if _DANGEROUS.search(expr):
            errors.append(f"{path}: DSL 含禁止字符（shell/import/exec/open/fileIO）")
        return
    if isinstance(expr, list):
        if expr and isinstance(expr[0], str) and expr[0] in _DSL_KEYWORDS:
            for child in expr[1:]:
                _validate_dsl_expr(child, f"{path}.{expr[0]}", errors)
        else:
            if expr and isinstance(expr[0], str) and expr[0] not in _DSL_KEYWORDS:
                errors.append(f"{path}.{expr[0]}: 未知 DSL 关键字（仅允许 {sorted(_DSL_KEYWORDS)}）")
            for i, child in enumerate(expr):
                _validate_dsl_expr(child, f"{path}[{i}]", errors)
        return
    if isinstance(expr, dict):
        for key, child in expr.items():
            if str(key) not in _DSL_KEYWORDS:
                errors.append(f"{path}.{key}: 未知 DSL 关键字（仅允许 {sorted(_DSL_KEYWORDS)}）")
            _validate_dsl_expr(child, f"{path}.{key}", errors)
        return
    errors.append(f"{path}: 不支持的 DSL 类型 {type(expr).__name__}")


def validate_dsl(value: Any) -> list[str]:
    """校验 when/then/else 的受限 DSL。返回错误列表。"""
    errors: list[str] = []
    _validate_dsl_expr(value, "dsl", errors)
    # then 不允许任意代码：只允许设置结果字段、提示、列出要求
    return errors


# ---------------------------------------------------------------- schema 注册表

SCHEMAS: dict[str, Schema] = {}


def register(schema: Schema) -> Schema:
    SCHEMAS[schema.name] = schema
    return schema


def get_schema(name: str) -> Schema:
    if name not in SCHEMAS:
        raise ContractError(f"registry 未注册 schema 合同类型: {name}", code="UNSUPPORTED_CONTRACT")
    return SCHEMAS[name]


def resolve_by_contract(contract: str) -> Schema:
    for s in SCHEMAS.values():
        if s.contract == contract:
            return s
    raise ContractError(f"未注册的合同 schema 值: {contract}", code="UNSUPPORTED_SCHEMA")


def validate_text(text: str, schema: Schema) -> dict[str, Any]:
    """对一个 MD 全文做完整合同校验，返回规范化字段 dict。"""
    data, body = parse_frontmatter(text)
    schema.validate_contract(str(data.get("schema", "")))
    values = schema.apply_fields(data)
    if schema.check:
        extra = schema.check(values, body) or []
        if extra:
            raise ContractError("；".join(extra), code="SEMANTIC")
    if schema.required_headings:
        missing = validate_headings(body, schema.required_headings)
        if missing:
            raise ContractError(f"正文缺少必需标题: {missing}", code="HEADINGS")
    # H1 文档主标题必填（`# <title>`）
    if not _H1_TITLE.search(body):
        raise ContractError("正文缺少一级标题（# <标题>）", code="HEADINGS")
    return values