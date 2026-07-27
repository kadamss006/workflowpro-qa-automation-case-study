from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4


@dataclass(frozen=True)
class ProjectData:
    name: str
    description: str
    team_members: list[str]


def unique_project_data(prefix: str = "QA-AUTO") -> ProjectData:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    suffix = uuid4().hex[:8]
    return ProjectData(
        name=f"{prefix}-{timestamp}-{suffix}",
        description="Created by automated API + UI integration validation",
        team_members=[],
    )
