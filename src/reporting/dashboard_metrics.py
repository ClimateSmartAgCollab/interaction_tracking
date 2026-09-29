"""Calculate structured metrics for the engagement dashboard."""

from datetime import date, datetime

import pandas as pd

from src.models.dashboard_models import (
    ActionQueue,
    DashboardMetrics,
    EngagementMetrics,
    ICTMetrics,
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


def _validate_columns(workbook: WorkbookData) -> None:
    """Raise a clear error when dashboard source columns are unavailable."""
    required_columns = {
        "researchers": (
            workbook.researchers_df,
            {"researcher_id", "ict", "date_added"},
        ),
        "interactions": (
            workbook.interactions_df,
            {"researcher_id", "interaction_date", "engagement_id"},
        ),
        "contributions": (
            workbook.contributions_df,
            {"researcher_id", "date_received"},
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
    interaction_icts = interactions["researcher_id"].map(ict_lookup)
    contribution_icts = contributions["researcher_id"].map(ict_lookup)

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
    )
