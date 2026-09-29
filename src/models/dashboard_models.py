"""Structured results for engagement dashboard reporting."""

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class EngagementMetrics:
    """Engagement totals shared by summary and ICT reporting."""

    total_researchers: int
    new_researchers_this_month: int
    total_engagements: int
    interactions_this_month: int
    contributions_this_month: int
    total_contributions: int


@dataclass(frozen=True)
class ICTMetrics(EngagementMetrics):
    """Engagement metrics for one ICT."""

    ict_name: str


@dataclass(frozen=True)
class ActionItem:
    """A future dashboard action for a researcher or ICT."""

    title: str
    description: str
    researcher_id: Any | None = None
    ict_name: str | None = None


@dataclass
class ActionQueue:
    """A named collection of related dashboard actions."""

    name: str
    title: str
    items: list[ActionItem] = field(default_factory=list)


@dataclass
class DashboardMetrics:
    """All calculated data required by the engagement dashboard."""

    executive_summary: EngagementMetrics
    ict_performance: list[ICTMetrics]
    action_queues: list[ActionQueue] = field(default_factory=list)
