"""Persist run history for auditing and reproducibility."""

from datetime import datetime
import json
from pathlib import Path

from src.models.validation_models import ValidationResults
from src.models.workbook_models import WorkbookData


def save_run_history(
    workbook: WorkbookData,
    validation: ValidationResults,
) -> Path:
    """Create a timestamped run folder and save run artifacts."""

    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")

    run_dir = Path("runs") / timestamp
    run_dir.mkdir(parents=True, exist_ok=True)

    print(f"Saving run history to: {run_dir}")

    # Save snapshots only when the source worksheets were loaded.
    if workbook.is_structurally_valid:
        workbook.researchers_df.to_parquet(
            run_dir / "researchers.parquet",
            index=False,
        )

        workbook.interactions_df.to_parquet(
            run_dir / "interactions.parquet",
            index=False,
        )

        workbook.contributions_df.to_parquet(
            run_dir / "contributions.parquet",
            index=False,
        )

    # Save run metadata
    metadata = {
        "run_timestamp": timestamp,
        "structurally_valid": workbook.is_structurally_valid,
        "missing_sheets": workbook.missing_sheets,
        "structural_review_items": len(validation.structural),
        "researcher_count": len(workbook.researchers_df),
        "interaction_count": len(workbook.interactions_df),
        "contribution_count": len(workbook.contributions_df),
        "researcher_review_items": len(validation.researchers),
        "interaction_review_items": len(validation.interactions),
        "contribution_review_items": len(validation.contributions),
        "recommendation_count": len(validation.recommendations),
    }

    metadata_path = run_dir / "run_metadata.json"

    with open(metadata_path, "w", encoding="utf-8") as file:
        json.dump(metadata, file, indent=4)

    config_path = run_dir / "config.json"

    with open(config_path, "w", encoding="utf-8") as file:
        json.dump(workbook.config, file, indent=4)

    lists_path = run_dir / "lists.json"

    with open(lists_path, "w", encoding="utf-8") as file:
        json.dump(
            workbook.lists,
            file,
            indent=4,
            default=str,
        )

    print("Run history saved successfully.")

    return run_dir