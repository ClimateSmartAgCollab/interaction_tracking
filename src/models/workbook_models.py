"""Data models representing the contents of an engagement workbook."""

from dataclasses import dataclass
from typing import Any

import pandas as pd


@dataclass
class WorkbookData:
    """All workbook data loaded from Excel."""

    researchers_df: pd.DataFrame
    engagements_df: pd.DataFrame
    interactions_df: pd.DataFrame
    contributions_df: pd.DataFrame
    lists: dict[str, list[Any]]
    config: dict[str, Any]
