"""DKWS 文件目录型数据知识服务模拟平台 (DKWS-SPEC-001)."""

__version__ = "0.1.0"
SCHEMA = "dkws/0.1"

# 触发 schema 合同注册，保证 get_schema/get_service 立即可用（幂等）。
from . import schemas as _schemas  # noqa: E402,F401