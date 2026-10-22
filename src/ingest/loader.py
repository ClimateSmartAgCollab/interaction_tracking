"""Load engagement data from an Excel workbook."""

from typing import Any

import pandas as pd

from src.models.workbook_models import WorkbookData


REQUIRED_SHEETS = [
    "researchers",
    "engagements",
    "interactions",
    "contributions",
    "lists",
    "configuration",
]


def _trim_string(value: Any) -> Any:
    """Remove surrounding whitespace from a string value."""
    if isinstance(value, str):
        return value.strip()
    return value


def load_table(
    excel_path: str,
    sheet_name: str,
    date_columns: list[str] | None = None,
) -> pd.DataFrame:

    """Load and clean a standard data table from the workbook."""
    print(f"Loading sheet: {sheet_name}")

    if date_columns is None:
        table = pd.read_excel(excel_path, sheet_name=sheet_name)
    else:
        table = pd.read_excel(
            excel_path,
            sheet_name=sheet_name,
            parse_dates=date_columns,
        )
    
    # Remove rows where every column is empty.
    table = table.dropna(how="all")

    cleaned_column_names = []
    for column_name in table.columns:
        cleaned_column_names.append(str(column_name).strip())
    table.columns = cleaned_column_names

    for column_name in table.columns:
        table[column_name] = table[column_name].map(_trim_string)

    print(f"Loaded {len(table)} rows from {sheet_name}")
    return table


def load_lists(excel_path: str) -> dict:
    """Load controlled vocabulary lists from the Lists sheet."""
    lists_table = load_table(excel_path, "lists")
    lists = {}

    for column_name in lists_table.columns:
        values = []

        for value in lists_table[column_name]:
            if pd.isna(value):
                continue
            if isinstance(value, str) and value == "":
                continue
            values.append(value)

        lists[column_name] = values
        print(f"Loaded {len(values)} values for list: {column_name}")

    return lists


def load_config(excel_path: str) -> dict:
    """Load setting and value pairs from the Configuration sheet."""
    config_table = load_table(excel_path, "configuration")
    config = {}

    for _, row in config_table.iterrows():
        setting = row["setting"]
        value = row["value"]

        if pd.isna(setting):
            continue
        if isinstance(setting, str) and setting == "":
            continue

        config[setting] = value

    return config


def load_workbook(excel_path: str) -> WorkbookData:
    """Load all required sheets into a WorkbookData object."""
    print(f"Starting workbook load: {excel_path}")

    workbook = pd.ExcelFile(excel_path)
    missing_sheets = [
        sheet_name
        for sheet_name in REQUIRED_SHEETS
        if sheet_name not in workbook.sheet_names
    ]

    if missing_sheets:
        missing_sheet_names = ", ".join(missing_sheets)
        print(
            "Workbook is missing required sheet(s): "
            f"{missing_sheet_names}"
        )
        print("Worksheet data loading skipped.")
        return WorkbookData(
            researchers_df=pd.DataFrame(),
            engagements_df=pd.DataFrame(),
            interactions_df=pd.DataFrame(),
            contributions_df=pd.DataFrame(),
            lists={},
            config={},
            missing_sheets=missing_sheets,
        )

    researchers_df = load_table(
        excel_path,
        "researchers",
        ["date_added"],
    )
    engagements_df = load_table(
        excel_path,
        "engagements",
    )
    interactions_df = load_table(
        excel_path,
        "interactions",
        ["interaction_date"],
    )
    contributions_df = load_table(
        excel_path,
        "contributions",
        ["date_received"],
    )

    lists = load_lists(excel_path)
    config = load_config(excel_path)

    workbook_data = WorkbookData(
        researchers_df=researchers_df,
        engagements_df=engagements_df,
        interactions_df=interactions_df,
        contributions_df=contributions_df,
        lists=lists,
        config=config,
    )

    print(
        "Workbook load complete: "
        f"{len(researchers_df)} researchers, "
        f"{len(engagements_df)} engagements, "
        f"{len(interactions_df)} interactions, "
        f"{len(contributions_df)} contributions, "
        f"{len(lists)} lists, "
        f"{len(config)} config values"
    )

    return workbook_data
