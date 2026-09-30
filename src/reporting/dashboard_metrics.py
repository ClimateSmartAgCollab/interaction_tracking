"""Calculate structured metrics for the engagement dashboard."""

from datetime import date, datetime

import pandas as pd

from src.models.dashboard_models import (
    ActionQueue,
    DashboardMetrics,
    EngagementMetrics,
    EngagementReview,
    ICTMetrics,
    InteractionHistoryItem,
)
from src.models.workbook_models import WorkbookData


def _month_mask(
    table: pd.DataFrame,
    column_name: str,
    month: pd.Period,
) -> pd.Series:
    """Return a mask selecting rows whose date falls in the given month."""
    dates = pd.to_datetime(table[column_name], errors="coerce")
    return dates.dt.to_period("M").eq(month)


def _ict_names(workbook: WorkbookData) -> list[str]:
    """Return configured and observed ICT names in stable order."""
    names: list[str] = []

    for list_name, values in workbook.lists.items():
        if list_name.casefold() == "ict":
            names.extend(str(value) for value in values if not pd.isna(value))
            break

    for value in workbook.researchers_df["ict"]:
        if pd.isna(value) or (isinstance(value, str) and not value):
            continue
        name = str(value)
        if name not in names:
            names.append(name)

    return list(dict.fromkeys(names))


def _researcher_ict_lookup(researchers: pd.DataFrame) -> pd.Series:
    """Map each researcher ID to its ICT without duplicating activities."""
    identified = researchers.dropna(subset=["researcher_id"])
    unique_researchers = identified.drop_duplicates(
        subset=["researcher_id"],
        keep="first",
    )
    return unique_researchers.set_index("researcher_id")["ict"]


def _researcher_email_lookup(researchers: pd.DataFrame) -> pd.Series:
    """Map each researcher ID to its email without duplicating activities."""
    identified = researchers.dropna(subset=["researcher_id"])
    unique_researchers = identified.drop_duplicates(
        subset=["researcher_id"],
        keep="first",
    )
    return unique_researchers.set_index("researcher_id")["email"]


def _validate_columns(workbook: WorkbookData) -> None:
    """Raise a clear error when dashboard source columns are unavailable."""
    required_columns = {
        "researchers": (
            workbook.researchers_df,
            {"researcher_id", "email", "ict", "date_added"},
        ),
        "interactions": (
            workbook.interactions_df,
            {
                "interaction_id",
                "engagement_id",
                "researcher_id",
                "interaction_date",
                "engagement_direction",
                "interaction_channel",
                "interaction_purpose",
                "interaction_summary",
                "next_action",
            },
        ),
        "contributions": (
            workbook.contributions_df,
            {"researcher_id", "source_interaction_id", "date_received"},
        ),
    }

    missing = []
    for table_name, (table, required) in required_columns.items():
        for column_name in sorted(required - set(table.columns)):
            missing.append(f"{table_name}.{column_name}")

    if missing:
        raise ValueError(
            "Dashboard metrics require the following missing column(s): "
            + ", ".join(missing)
        )


def _display_text(value: object) -> str:
    """Return workbook content as text without displaying missing values."""
    return "" if pd.isna(value) else str(value)


def _date_text(value: object) -> str:
    """Return a workbook date in a consistent display and sorting format."""
    if pd.isna(value):
        return ""
    return pd.Timestamp(value).strftime("%Y-%m-%d")


def _build_engagement_reviews(
    workbook: WorkbookData,
    ict_lookup: pd.Series,
    email_lookup: pd.Series,
) -> list[EngagementReview]:
    """Build one review for each engagement in the interactions table."""
    interactions = workbook.interactions_df
    contributions = workbook.contributions_df
    reviews: list[EngagementReview] = []

    # Engagement grouping keeps every related interaction together and uses
    # engagement_id as the review's sole grouping key.
    for engagement_id, engagement in interactions.groupby(
        "engagement_id",
        sort=False,
    ):
        ordered_interactions = engagement.assign(
            _interaction_date_sort=pd.to_datetime(
                engagement["interaction_date"],
                errors="coerce",
            )
        ).sort_values(
            "_interaction_date_sort",
            ascending=True,
            na_position="first",
            kind="stable",
        )

        # Interaction history is built in chronological order so each review
        # tells the engagement story from the oldest activity to the newest.
        interaction_history = [
            InteractionHistoryItem(
                interaction_date=_date_text(interaction["interaction_date"]),
                engagement_direction=_display_text(
                    interaction["engagement_direction"]
                ),
                interaction_channel=_display_text(
                    interaction["interaction_channel"]
                ),
                interaction_purpose=_display_text(
                    interaction["interaction_purpose"]
                ),
                interaction_summary=_display_text(
                    interaction["interaction_summary"]
                ),
                next_action=_display_text(interaction["next_action"]),
            )
            for _, interaction in ordered_interactions.iterrows()
        ]

        latest_interaction = ordered_interactions.iloc[-1]
        researcher_id = latest_interaction["researcher_id"]
        interaction_ids = set(engagement["interaction_id"].dropna())

        # Contributions are counted when their source interaction belongs to
        # this engagement, rather than by researcher alone.
        contribution_count = int(
            contributions["source_interaction_id"].isin(interaction_ids).sum()
        )

        ict_name = ict_lookup.get(researcher_id, "")
        researcher_email = email_lookup.get(researcher_id, "")
        # The review combines engagement identity, outcomes, latest action,
        # and complete interaction history in one dashboard-ready object.
        reviews.append(
            EngagementReview(
                engagement_id=_display_text(engagement_id),
                researcher_id=researcher_id,
                researcher_email=_display_text(researcher_email),
                ict_name=_display_text(ict_name),
                interaction_count=len(engagement),
                contribution_count=contribution_count,
                latest_interaction_date=_date_text(
                    latest_interaction["interaction_date"]
                ),
                latest_next_action=_display_text(
                    latest_interaction["next_action"]
                ),
                interaction_history=interaction_history,
            )
        )

    return sorted(
        reviews,
        key=lambda review: review.latest_interaction_date,
        reverse=True,
    )


def calculate_dashboard_metrics(
    workbook: WorkbookData,
    reference_date: date | datetime | pd.Timestamp | None = None,
) -> DashboardMetrics:
    """Calculate all dashboard metrics without changing workbook data."""
    _validate_columns(workbook)

    current_month = pd.Timestamp(
        reference_date if reference_date is not None else datetime.now()
    ).to_period("M")

    researchers = workbook.researchers_df
    interactions = workbook.interactions_df
    contributions = workbook.contributions_df

    new_researchers = _month_mask(researchers, "date_added", current_month)
    current_interactions = _month_mask(interactions, "interaction_date", current_month)
    current_contributions = _month_mask(
        contributions,
        "date_received",
        current_month,
    )

    executive_summary = EngagementMetrics(
        total_researchers=len(researchers),
        new_researchers_this_month=int(new_researchers.sum()),
        total_engagements=int(interactions["engagement_id"].nunique()),
        interactions_this_month=int(current_interactions.sum()),
        contributions_this_month=int(current_contributions.sum()),
        total_contributions=len(contributions),
    )

    researcher_icts = researchers["ict"]
    ict_lookup = _researcher_ict_lookup(researchers)
    email_lookup = _researcher_email_lookup(researchers)
    interaction_icts = interactions["researcher_id"].map(ict_lookup)
    contribution_icts = contributions["researcher_id"].map(ict_lookup)
    engagement_reviews = _build_engagement_reviews(
        workbook,
        ict_lookup,
        email_lookup,
    )

    ict_performance = []
    for ict_name in _ict_names(workbook):
        ict_researchers = researcher_icts.eq(ict_name).fillna(False)
        ict_interactions = interaction_icts.eq(ict_name).fillna(False)
        ict_contributions = contribution_icts.eq(ict_name).fillna(False)

        ict_performance.append(
            ICTMetrics(
                ict_name=ict_name,
                total_researchers=int(ict_researchers.sum()),
                new_researchers_this_month=int(
                    (ict_researchers & new_researchers).sum()
                ),
                total_engagements=int(
                    interactions.loc[ict_interactions, "engagement_id"].nunique()
                ),
                interactions_this_month=int(
                    (ict_interactions & current_interactions).sum()
                ),
                contributions_this_month=int(
                    (ict_contributions & current_contributions).sum()
                ),
                total_contributions=int(ict_contributions.sum()),
            )
        )

    return DashboardMetrics(
        executive_summary=executive_summary,
        ict_performance=ict_performance,
        action_queues=[
            ActionQueue(
                name="follow_up",
                title="Follow-Up",
                items=[],
            )
        ],
        engagement_reviews=engagement_reviews,
    )
