"""DKWS 统一错误层次：任何校验失败以异常形式抛出不吞没；消息不携带宿主绝对路径。"""


class DkwError(Exception):
    """平台级错误基类。"""


class ValidationError(DkwError):
    """结构/语义校验失败。字段可为空。"""

    def __init__(self, message: str, *, field: str | None = None, code: str = "VALIDATION_ERROR"):
        super().__init__(message)
        self.message = message
        self.field = field
        self.code = code


class ContractError(DkwError):
    """契约化 Markdown 合同不合法（frontmatter/schema/DSL）。"""

    def __init__(self, message: str, *, file: str | None = None, code: str = "CONTRACT_ERROR",
                 field: str | None = None):
        super().__init__(message)
        self.message = message
        self.file = file
        self.code = code
        self.field = field


class UnsupportedSchemaError(ContractError):
    def __init__(self, schema: str, *, file: str | None = None):
        super().__init__(f"不支持的 schema 合同类型: {schema}", file=file, code="UNSUPPORTED_SCHEMA")


class TransitionError(DkwError):
    """状态机非法跳转。"""

    def __init__(self, message: str, *, code: str = "ILLEGAL_TRANSITION"):
        super().__init__(message)
        self.code = code


class ConflictError(DkwError):
    """业务冲突（幂等冲突/哈希重复/并发写）。"""

    def __init__(self, message: str, *, code: str = "CONFLICT"):
        super().__init__(message)
        self.code = code


class NotFoundError(DkwError):
    def __init__(self, message: str, *, code: str = "NOT_FOUND"):
        super().__init__(message)
        self.code = code


class SecurityError(DkwError):
    def __init__(self, message: str, *, code: str = "SECURITY"):
        super().__init__(message)
        self.code = code