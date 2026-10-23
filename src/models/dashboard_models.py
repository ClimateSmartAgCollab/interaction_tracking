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
    total_interactions: int


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
    reporting_period_label: str
    contribution_breakdown: list[ContributionTypeMetrics] = field(
        default_factory=list
    )
    action_queues: list[ActionQueue] = field(default_factory=list)
    engagement_reviews: list[EngagementReview] = field(default_factory=list)

@dataclass(frozen=True)
class InteractionHistoryItem:
    """One interaction displayed in an engagement review."""

    interaction_date: str
    participant: str
    project: str
    engagement_direction: str
    interaction_channel: str
    interaction_purpose: str
    interaction_summary: str
    next_action: str


@dataclass(frozen=True)
class EngagementParticipant:
    """One researcher participating in an engagement."""

    researcher_id: int | str
    researcher_name: str
    researcher_email: str
    role: str


@dataclass(frozen=True)
class EngagementReview:
    """Summary of a single engagement."""

    engagement_id: str
    engagement_title: str
    engagement_status: str
    projects: list[str]
    participant_count: int
    participants: list[EngagementParticipant]
    interaction_count: int
    contribution_count: int
    latest_interaction_date: str
    days_since_activity: int
    latest_next_action: str
    engagement_duration_days: int

    interaction_history: list[InteractionHistoryItem]
