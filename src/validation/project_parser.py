"""Helpers for parsing project memberships."""

import pandas as pd


def parse_projects(value: object) -> list[str]:
    """Return the non-empty projects in a semicolon-separated value."""
    if value is None or pd.isna(value) or value == "":
        return []

    return [
        project.strip()
        for project in str(value).split(";")
        if project.strip()
    ]
