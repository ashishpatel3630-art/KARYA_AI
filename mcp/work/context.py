from dataclasses import dataclass


@dataclass(frozen=True)
class WorkContext:
    work_id: str
    task_id: str
    user_id: str
    role: str