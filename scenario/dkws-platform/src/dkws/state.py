"""任务 / 知识资产 / 发布 状态机（DKWS-SPEC-001 §11）。"""

from dataclasses import dataclass, field

from .errors import TransitionError


@dataclass
class SM:
    """通用状态机：state -> 允许的 next states 集合。"""

    name: str
    transitions: dict[str, list[str]] = field(default_factory=dict)
    _terminal: set[str] = field(default_factory=set, init=False)

    def __post_init__(self):
        self._terminal = {self.name, *[s for to in self.transitions.values() for s in to]}

    def can(self, cur: str, nxt: str) -> bool:
        if cur not in self.transitions:
            return nxt in self.transitions.get(cur, [])
        return nxt in self.transitions[cur]

    def transition(self, cur: str, nxt: str) -> str:
        allowed = self.transitions.get(cur, [])
        if nxt not in allowed:
            raise TransitionError(
                f"{self.name}: 非法状态跳转 {cur} -> {nxt}（允许: {allowed or '无'}）"
            )
        return nxt


# 11.1 任务状态机
JOB_SM = SM("job", {
    "PENDING": ["RUNNING", "BLOCKED", "FAILED"],
    "RUNNING": ["VALIDATING", "FAILED", "CANCEL_REQUESTED", "COMPLETED"],
    "VALIDATING": ["COMPLETED", "FAILED"],
    "CANCEL_REQUESTED": ["CANCELLED", "FAILED"],
    "FAILED": ["RETRYING"],
    "RETRYING": ["RUNNING"],
    "PENDING_BLOCKED": [],  # 占位（BLOCKED 为终态）
})
JOB_TERMINAL = {"COMPLETED", "FAILED", "CANCELLED", "BLOCKED"}

# 11.2 知识资产状态机
ASSET_SM = SM("knowledge_asset", {
    "CANDIDATE": ["IN_REVIEW"],
    "IN_REVIEW": ["APPROVED", "REJECTED", "CANDIDATE"],
    "APPROVED": ["PUBLISHED", "INACTIVE"],
    "PUBLISHED": ["INACTIVE", "SUPERSEDED"],
    "REJECTED": [],
})
# validation_status 与 status 分离：
# validation_status: CANDIDATE/IN_REVIEW/APPROVED/REJECTED
# status:            ACTIVE/INACTIVE/SUPERSEDED/PUBLISHED

# 11.3 发布状态机
RELEASE_SM = SM("release", {
    "DRAFT_RELEASE": ["VALIDATING", "VALIDATION_FAILED"],
    "VALIDATING": ["READY_TO_PUBLISH", "VALIDATION_FAILED"],
    "READY_TO_PUBLISH": ["PUBLISHING", "VALIDATION_FAILED"],
    "PUBLISHING": ["PUBLISHED", "PUBLISH_FAILED"],
    "VALIDATION_FAILED": [],  # 终态
    "PUBLISH_FAILED": [],     # 终态
    "PUBLISHED": [],
})


def check_terminal(sm: SM, jtype: str, state: str) -> None:
    if state in JOB_TERMINAL and jtype == "job" and sm is JOB_SM:
        return
    # 通用终态判定由调用方负责