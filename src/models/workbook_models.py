"""Data models representing the contents of an engagement workbook."""

from dataclasses import dataclass, field
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
    missing_sheets: list[str] = field(default_factory=list)

    @property
    def is_structurally_valid(self) -> bool:
        """Return whether all required worksheets were available."""
        return not self.missing_sheets
