"""Structured results for engagement dashboard reporting."""

from __future__ import annotations

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
class ProjectMetrics(EngagementMetrics):
    """Engagement metrics for one PROJECT."""

    project_name: str


@dataclass(frozen=True)
class ActionItem:
    """A future dashboard action for a researcher or PROJECT."""

    title: str
    description: str
    researcher_id: Any | None = None
    project_name: str | None = None


@dataclass
class ActionQueue:
    """A named collection of related dashboard actions."""

    name: str
    title: str
    items: list[ActionItem] = field(default_factory=list)


@dataclass(frozen=True)
class ContributionTypeMetrics:
    """Contribution totals and project counts for one content type."""

    content_type: str
    total_contributions: int
    project_counts: dict[str, int]


@dataclass
class DashboardMetrics:
    """All calculated data required by the engagement dashboard."""

    executive_summary: EngagementMetrics
    project_performance: list[ProjectMetrics]
    contribution_breakdown: list[ContributionTypeMetrics] = field(
        default_factory=list
    )
    action_queues: list[ActionQueue] = field(default_factory=list)
    engagement_reviews: list[EngagementReview] = field(default_factory=list)
    outstanding_actions: list[OutstandingAction] = field(default_factory=list)

@dataclass(frozen=True)
class InteractionHistoryItem:
    """One interaction displayed in an engagement review."""

    interaction_date: str
    engagement_direction: str
    interaction_channel: str
    interaction_purpose: str
    interaction_summary: str
    next_action: str


@dataclass(frozen=True)
class EngagementReview:
    """Summary of a single engagement."""

    engagement_id: str
    researcher_id: int | str
    researcher_email: str
    role: str
    project_name: str
    interaction_count: int
    contribution_count: int
    latest_interaction_date: str
    latest_next_action: str

    interaction_history: list[InteractionHistoryItem]


@dataclass(frozen=True)
class OutstandingAction:
    """Latest actionable next step for one engagement."""

    days_since_last_interaction: int
    project_name: str
    researcher_email: str
    next_action: str
    engagement_id: str
