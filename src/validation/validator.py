"""Coordinate validation checks for workbook data."""

from src.models.validation_models import (
    Recommendation,
    ReviewItem,
    ValidationResults,
)
from src.models.workbook_models import WorkbookData
from src.validation.project_parser import parse_projects


def validate_workbook(workbook: WorkbookData) -> ValidationResults:
    """Run all workbook validation checks."""
    print("Starting validation...")
    results = ValidationResults()

    print("Running required worksheet checks...")
    validate_required_worksheets(workbook, results)

    if not workbook.is_structurally_valid:
        print(
            "Workbook contains structural errors. "
            "Remaining validation skipped."
        )
        return results

    print("Running required column checks...")
    validate_required_columns(workbook, results)

    print("Running missing value checks...")
    validate_missing_values(workbook, results)

    print("Running date checks...")
    validate_dates(workbook, results)

    print("Running controlled vocabulary checks...")
    validate_controlled_vocabularies(workbook, results)

    print("Running relationship checks...")
    validate_relationships(workbook, results)

    print("Running duplicate checks...")
    validate_duplicates(workbook, results)

    print("Calculating completeness metrics...")
    calculate_completeness_metrics(workbook, results)

    print("Generating recommendations...")
    generate_recommendations(workbook, results)

    print(f"Interaction review items: {len(results.interactions)}")

    print("Validation complete.")
    return results


# ==================================================
# REQUIRED WORKSHEETS
# ==================================================


def validate_required_worksheets(
    workbook: WorkbookData,
    results: ValidationResults,
) -> None:
    """Create review items for required worksheets that are unavailable."""
    for sheet_name in workbook.missing_sheets:
        display_name = sheet_name.replace("_", " ").title()
        results.structural.append(
            ReviewItem(
                title=f"Missing required worksheet: {display_name}",
                category="missing_worksheet",
                priority="error",
                table_name=sheet_name,
                record_id=None,
                excel_row=1,
                message=(
                    f"The required '{display_name}' worksheet is missing."
                ),
                suggested_action=(
                    f"Add a worksheet named '{sheet_name}' to the workbook."
                ),
            )
        )

    print(
        "Required worksheet validation complete. "
        f"Missing worksheets found: {len(workbook.missing_sheets)}"
    )


# ==================================================
# REQUIRED COLUMNS
# ==================================================


def validate_required_columns(
    workbook: WorkbookData,
    results: ValidationResults,
) -> None:
    """Check that every workbook table contains its required columns."""
    # Define the columns required by each workbook table.
    researchers_required_columns = [
        "researcher_id",
        "email",
        "project",
        "role",
        "organization",
        "date_added",
        "researcher_status",
    ]
    engagements_required_columns = [
        "engagement_id",
        "engagement_status",
        "title",
    ]
    interactions_required_columns = [
        "interaction_id",
        "engagement_id",
        "researcher_id",
        "project",
        "interaction_date",
        "interaction_channel",
        "engagement_direction",
        "interaction_purpose",
        "interaction_summary",
        "next_action",
    ]
    contributions_required_columns = [
        "contribution_id",
        "researcher_id",
        "source_interaction_id",
        "date_received",
        "content_type",
    ]

    missing_column_count = 0

    # Check the researchers table for every required column.
    print("Checking required columns for researchers...")
    for column_name in researchers_required_columns:
        if column_name not in workbook.researchers_df.columns:
            results.researchers.append(
                ReviewItem(
                    title=(
                        "Researchers sheet missing "
                        f"{column_name.replace('_', ' ').title()} column"
                    ),
                    category="missing_column",
                    priority="error",
                    table_name="researchers",
                    record_id=None,
                    excel_row=1,
                    field_name=column_name,
                    current_value=None,
                    message=f"Required column '{column_name}' is missing",
                    suggested_action=f"Add column '{column_name}'",
                )
            )
            missing_column_count += 1

    # Check the engagements table for every required column.
    print("Checking required columns for engagements...")
    for column_name in engagements_required_columns:
        if column_name not in workbook.engagements_df.columns:
            results.engagements.append(
                ReviewItem(
                    title=(
                        "Engagements sheet missing "
                        f"{column_name.replace('_', ' ').title()} column"
                    ),
                    category="missing_column",
                    priority="error",
                    table_name="engagements",
                    record_id=None,
                    excel_row=1,
                    field_name=column_name,
                    current_value=None,
                    message=f"Required column '{column_name}' is missing",
                    suggested_action=f"Add column '{column_name}'",
                )
            )
            missing_column_count += 1

    # Check the interactions table for every required column.
    print("Checking required columns for interactions...")
    for column_name in interactions_required_columns:
        if column_name not in workbook.interactions_df.columns:
            results.interactions.append(
                ReviewItem(
                    title=(
                        "Interactions sheet missing "
                        f"{column_name.replace('_', ' ').title()} column"
                    ),
                    category="missing_column",
                    priority="error",
                    table_name="interactions",
                    record_id=None,
                    excel_row=1,
                    field_name=column_name,
                    current_value=None,
                    message=f"Required column '{column_name}' is missing",
                    suggested_action=f"Add column '{column_name}'",
                )
            )
            missing_column_count += 1

    # Check the contributions table for every required column.
    print("Checking required columns for contributions...")
    for column_name in contributions_required_columns:
        if column_name not in workbook.contributions_df.columns:
            results.contributions.append(
                ReviewItem(
                    title=(
                        "Contributions sheet missing "
                        f"{column_name.replace('_', ' ').title()} column"
                    ),
                    category="missing_column",
                    priority="error",
                    table_name="contributions",
                    record_id=None,
                    excel_row=1,
                    field_name=column_name,
                    current_value=None,
                    message=f"Required column '{column_name}' is missing",
                    suggested_action=f"Add column '{column_name}'",
                )
            )
            missing_column_count += 1

    # Report the total number of missing columns across all tables.
    print("Required column validation complete.")
    print(f"Missing columns found: {missing_column_count}")


# ==================================================
# MISSING VALUES
# ==================================================


def validate_missing_values(
    workbook: WorkbookData,
    results: ValidationResults,
) -> None:
    """Create review items for missing values in required fields."""
    import pandas as pd

    researchers_required_fields = [
        "researcher_id",
        "email",
        "researcher_status",
        "project",
    ]
    engagements_required_fields = [
        "engagement_id",
        "engagement_status",
        "title",
    ]
    interactions_required_fields = [
        "interaction_id",
        "engagement_id",
        "researcher_id",
        "interaction_date",
        "interaction_channel",
        "engagement_direction",
        "interaction_purpose",
    ]
    contributions_required_fields = [
        "contribution_id",
        "researcher_id",
        "source_interaction_id",
        "content_type",
        "date_received",
    ]

    missing_value_count = 0

    def is_missing(value: object) -> bool:
        """Return whether a workbook value is empty."""
        return pd.isna(value) or value == ""

    # Validate required researcher fields row by row.
    print("Checking missing values for researchers...")
    for excel_row, (row_index, row) in enumerate(
        workbook.researchers_df.iterrows(),
        start=2,
    ):
        record_id = row_index
        if "researcher_id" in workbook.researchers_df.columns:
            researcher_id = row["researcher_id"]
            if not is_missing(researcher_id):
                record_id = researcher_id

        for field_name in researchers_required_fields:
            if field_name not in workbook.researchers_df.columns:
                continue

            if is_missing(row[field_name]):
                field_label = field_name.replace("_", " ").title()
                results.researchers.append(
                    ReviewItem(
                        title=(
                            f"Researcher {record_id} missing {field_label}"
                        ),
                        category="missing_value",
                        priority="error",
                        table_name="researchers",
                        record_id=record_id,
                        excel_row=excel_row,
                        field_name=field_name,
                        current_value=None,
                        message=f"{field_name} is missing",
                        suggested_action=f"Populate {field_name} field",
                    )
                )
                missing_value_count += 1

    # Validate required engagement fields row by row.
    print("Checking missing values for engagements...")
    for excel_row, (row_index, row) in enumerate(
        workbook.engagements_df.iterrows(),
        start=2,
    ):
        record_id = row_index
        if "engagement_id" in workbook.engagements_df.columns:
            engagement_id = row["engagement_id"]
            if not is_missing(engagement_id):
                record_id = engagement_id

        for field_name in engagements_required_fields:
            if field_name not in workbook.engagements_df.columns:
                continue

            if is_missing(row[field_name]):
                field_label = field_name.replace("_", " ").title()
                results.engagements.append(
                    ReviewItem(
                        title=(
                            f"Engagement {record_id} missing {field_label}"
                        ),
                        category="missing_value",
                        priority="error",
                        table_name="engagements",
                        record_id=record_id,
                        excel_row=excel_row,
                        field_name=field_name,
                        current_value=None,
                        message=f"{field_name} is missing",
                        suggested_action=f"Populate {field_name} field",
                    )
                )
                missing_value_count += 1

    # Validate required interaction fields row by row.
    print("Checking missing values for interactions...")

    # Build researcher -> project lookup
    researcher_project_lookup = (
        workbook.researchers_df
        .set_index("researcher_id")["project"]
        .to_dict()
        )

    for excel_row, (row_index, row) in enumerate(
        workbook.interactions_df.iterrows(),
        start=2,
    ):
        record_id = row_index
        if "interaction_id" in workbook.interactions_df.columns:
            interaction_id = row["interaction_id"]
            if not is_missing(interaction_id):
                record_id = interaction_id

        for field_name in interactions_required_fields:
            if field_name not in workbook.interactions_df.columns:
                continue

            if is_missing(row[field_name]):
                field_label = field_name.replace("_", " ").title()
                results.interactions.append(
                    ReviewItem(
                        title=(
                            f"Interaction {record_id} missing {field_label}"
                        ),
                        category="missing_value",
                        priority="error",
                        table_name="interactions",
                        record_id=record_id,
                        excel_row=excel_row,
                        field_name=field_name,
                        current_value=None,
                        message=f"{field_name} is missing",
                        suggested_action=f"Populate {field_name} field",
                    )
                )
                missing_value_count += 1

        # Validate project field
        researcher_id = row.get("researcher_id")
        interaction_project = row.get("project")

        if not is_missing(researcher_id):
            researcher_projects = researcher_project_lookup.get(
                researcher_id,
                "",
            )

            project_list = parse_projects(researcher_projects)

            if (
                len(project_list) > 1
                and is_missing(interaction_project)
            ):
                print(
                    f"MISSING PROJECT ERROR: interaction={record_id}"
                )
                results.interactions.append(
                    ReviewItem(
                        title=(
                            f"Interaction {record_id} missing Project"
                        ),
                        category="missing_value",
                        priority="error",
                        table_name="interactions",
                        record_id=record_id,
                        excel_row=excel_row,
                        field_name="project",
                        current_value=None,
                        message=(
                            "Project must be specified for "
                            "multi-project researchers"
                        ),
                        suggested_action=(
                            "Select one of the researcher's "
                            f"associated projects: {', '.join(project_list)}"
                        ),
                    )
                )
                missing_value_count += 1

    # Validate required contribution fields row by row.
    print("Checking missing values for contributions...")
    for excel_row, (row_index, row) in enumerate(
        workbook.contributions_df.iterrows(),
        start=2,
    ):
        record_id = row_index
        if "contribution_id" in workbook.contributions_df.columns:
            contribution_id = row["contribution_id"]
            if not is_missing(contribution_id):
                record_id = contribution_id

        for field_name in contributions_required_fields:
            if field_name not in workbook.contributions_df.columns:
                continue

            if is_missing(row[field_name]):
                field_label = field_name.replace("_", " ").title()
                results.contributions.append(
                    ReviewItem(
                        title=(
                            f"Contribution {record_id} missing {field_label}"
                        ),
                        category="missing_value",
                        priority="error",
                        table_name="contributions",
                        record_id=record_id,
                        excel_row=excel_row,
                        field_name=field_name,
                        current_value=None,
                        message=f"{field_name} is missing",
                        suggested_action=f"Populate {field_name} field",
                    )
                )
                missing_value_count += 1

    print("Missing value validation complete.")
    print(f"Missing values found: {missing_value_count}")


# ==================================================
# DATE VALIDATION
# ==================================================


def validate_dates(
    workbook: WorkbookData,
    results: ValidationResults,
) -> None:
    """Create review items for dates that may be data entry errors."""
    import pandas as pd

    # Date validation identifies values that could distort reports and metrics.
    date_checks = [
        (
            "researchers",
            workbook.researchers_df,
            results.researchers,
            "researcher_id",
            "date_added",
        ),
        (
            "interactions",
            workbook.interactions_df,
            results.interactions,
            "interaction_id",
            "interaction_date",
        ),
        (
            "contributions",
            workbook.contributions_df,
            results.contributions,
            "contribution_id",
            "date_received",
        ),
    ]
    today = pd.Timestamp.today().date()
    future_date_count = 0

    print("Checking dates...")

    for (
        table_name,
        dataframe,
        review_items,
        identifier_column,
        field_name,
    ) in date_checks:
        if field_name not in dataframe.columns:
            continue

        for excel_row, (row_index, row) in enumerate(
            dataframe.iterrows(),
            start=2,
        ):
            current_value = row[field_name]
            if pd.isna(current_value) or current_value == "":
                continue

            # Invalid dates are skipped so a separate rule can handle them.
            try:
                parsed_date = pd.to_datetime(current_value, errors="coerce")
            except (TypeError, ValueError, OverflowError):
                continue

            if pd.isna(parsed_date):
                continue

            # A date is considered future-dated only when it is after today.
            if parsed_date.date() <= today:
                continue

            record_id = row_index
            if identifier_column in dataframe.columns:
                identifier_value = row[identifier_column]
                if not pd.isna(identifier_value) and identifier_value != "":
                    record_id = identifier_value

            # Generate a warning ReviewItem instead of changing workbook data.
            review_items.append(
                ReviewItem(
                    title=(
                        f"{table_name.removesuffix('s').title()} "
                        f"{record_id} has a future date"
                    ),
                    category="future_date",
                    priority="warning",
                    table_name=table_name,
                    record_id=record_id,
                    excel_row=excel_row,
                    field_name=field_name,
                    current_value=current_value,
                    message=f"{field_name} is in the future",
                    suggested_action=(
                        "Verify and correct the date if it was entered "
                        "incorrectly"
                    ),
                )
            )
            future_date_count += 1

    print(f"Future dates found: {future_date_count}")


# ==================================================
# CONTROLLED VOCABULARY
# ==================================================


def validate_controlled_vocabularies(
    workbook: WorkbookData,
    results: ValidationResults,
) -> None:
    """Validate workbook values against lists matched by column name."""
    import pandas as pd

    max_display_list_values = workbook.config["max_display_list_values"]
    invalid_list_count = 0
    invalid_value_count = 0

    # Store table details so every workbook list can be matched dynamically.
    tables = [
        (
            "researchers",
            workbook.researchers_df,
            results.researchers,
            "researcher_id",
        ),
        (
            "engagements",
            workbook.engagements_df,
            results.engagements,
            "engagement_id",
        ),
        (
            "interactions",
            workbook.interactions_df,
            results.interactions,
            "interaction_id",
        ),
        (
            "contributions",
            workbook.contributions_df,
            results.contributions,
            "contribution_id",
        ),
    ]

    def is_empty(value: object) -> bool:
        """Return whether a workbook value should be skipped."""
        return pd.isna(value) or value == ""

    print("Checking controlled vocabularies...")

    # Match each list to exactly one workbook column, then validate its values.
    for list_name, valid_values in workbook.lists.items():
        print(f"Validating list: {list_name}")
        matching_tables = []

        for table in tables:
            dataframe = table[1]
            if list_name in dataframe.columns:
                matching_tables.append(table)

        if not matching_tables:
            message = (
            f"List '{list_name}' does not match any workbook column"
            )

            results.researchers.append(
                ReviewItem(
                    title=(
                        f"List {list_name} does not match exactly one "
                        "workbook column"
                    ),
                    category="invalid_list_definition",
                    priority="error",
                    table_name="lists",
                    record_id=list_name,
                    excel_row=1,
                    field_name=list_name,
                    current_value=None,
                    message=message,
                    suggested_action=(
                        "Check the list name and corresponding column names"
                    ),
                )
            )
            invalid_list_count += 1
            continue

        for (
            table_name,
            dataframe,
            review_items,
            identifier_column,
        ) in matching_tables:

            # Build the guidance shown for invalid values.
            invalid_value_message = "Value not found in controlled vocabulary."
            if len(valid_values) <= max_display_list_values:
                valid_values_text = ", ".join(
                    str(valid_value) for valid_value in valid_values
                )
                invalid_value_message += (
                    f"\n\nValid values:\n{valid_values_text}"
                )
            else:
                invalid_value_message += (
                    "\n\nSee Lists worksheet for valid values."
                )

            for excel_row, (row_index, row) in enumerate(
                dataframe.iterrows(),
                start=2,
            ):
                current_value = row[list_name]

                if is_empty(current_value):
                    continue

                # Project fields may contain one or more memberships.
                values_to_validate = (
                    parse_projects(current_value)
                    if list_name == "project"
                    else [current_value]
                )
                invalid_values = [
                    value
                    for value in values_to_validate
                    if value not in valid_values
                ]

                if not invalid_values:
                    continue

                record_id = row_index
                if identifier_column in dataframe.columns:
                    identifier_value = row[identifier_column]
                    if not is_empty(identifier_value):
                        record_id = identifier_value

                # Report each invalid value separately. For projects, this
                # identifies the exact membership that needs correction.
                for invalid_value in invalid_values:
                    review_items.append(
                        ReviewItem(
                            title=(
                                f"{table_name.removesuffix('s').title()} "
                                f"{record_id} {list_name.replace('_', ' ')} "
                                f"\"{invalid_value}\" not in "
                                f"{list_name.replace('_', ' ').title()} list"
                            ),
                            category="invalid_value",
                            priority="error",
                            table_name=table_name,
                            record_id=record_id,
                            excel_row=excel_row,
                            field_name=list_name,
                            current_value=invalid_value,
                            message=invalid_value_message,
                            suggested_action=(
                                f"Select a valid {list_name} value"
                            ),
                        )
                    )
                    invalid_value_count += 1

    print("Controlled vocabulary validation complete.")
    print(f"Invalid lists found: {invalid_list_count}")
    print(f"Invalid values found: {invalid_value_count}")


# ==================================================
# RELATIONSHIPS
# ==================================================


def validate_relationships(
    workbook: WorkbookData,
    results: ValidationResults,
) -> None:
    """Create review items for references to records that do not exist."""
    import pandas as pd

    # Relationship definitions are maintained in this single list.
    relationships = [
        {
            "source_table": "interactions",
            "source_column": "engagement_id",
            "target_table": "engagements",
            "target_column": "engagement_id",
        },
        {
            "source_table": "interactions",
            "source_column": "researcher_id",
            "target_table": "researchers",
            "target_column": "researcher_id",
        },
        {
            "source_table": "contributions",
            "source_column": "researcher_id",
            "target_table": "researchers",
            "target_column": "researcher_id",
        },
        {
            "source_table": "contributions",
            "source_column": "source_interaction_id",
            "target_table": "interactions",
            "target_column": "interaction_id",
        },
    ]

    table_details = {
        "researchers": {
            "dataframe": workbook.researchers_df,
            "review_items": results.researchers,
            "identifier_column": "researcher_id",
        },
        "interactions": {
            "dataframe": workbook.interactions_df,
            "review_items": results.interactions,
            "identifier_column": "interaction_id",
        },
        "engagements": {
            "dataframe": workbook.engagements_df,
            "review_items": results.engagements,
            "identifier_column": "engagement_id",
        },
        "contributions": {
            "dataframe": workbook.contributions_df,
            "review_items": results.contributions,
            "identifier_column": "contribution_id",
        },
    }

    relationship_errors_found = 0

    def is_missing(value: object) -> bool:
        """Return whether a relationship value should be ignored."""
        return pd.isna(value) or value == ""

    print("Checking relationships...")

    for relationship in relationships:
        source_table_name = relationship["source_table"]
        source_column = relationship["source_column"]
        target_table_name = relationship["target_table"]
        target_column = relationship["target_column"]

        print("Validating:")
        print(f"{source_table_name}.{source_column}")
        print("    ->")
        print(f"{target_table_name}.{target_column}")

        # Look up the source table and its review collection.
        source_details = table_details[source_table_name]
        source_dataframe = source_details["dataframe"]
        source_review_items = source_details["review_items"]
        identifier_column = source_details["identifier_column"]

        # Look up the target table that contains the referenced records.
        target_details = table_details[target_table_name]
        target_dataframe = target_details["dataframe"]

        if (
            source_column not in source_dataframe.columns
            or target_column not in target_dataframe.columns
        ):
            continue

        target_values = target_dataframe[target_column].tolist()
        target_record_name = target_table_name.removesuffix("s")

        # Validate every non-empty source value against the target table.
        for excel_row, (row_index, row) in enumerate(
            source_dataframe.iterrows(),
            start=2,
        ):
            source_value = row[source_column]
            if is_missing(source_value):
                continue

            if source_value in target_values:
                continue

            record_id = row_index
            if identifier_column in source_dataframe.columns:
                identifier_value = row[identifier_column]
                if not is_missing(identifier_value):
                    record_id = identifier_value

            source_review_items.append(
                ReviewItem(
                    title=(
                        f"{source_table_name.removesuffix('s').title()} "
                        f"{record_id} references missing "
                        f"{target_record_name.title()} {source_value}"
                    ),
                    category="missing_relationship",
                    priority="error",
                    table_name=source_table_name,
                    record_id=record_id,
                    excel_row=excel_row,
                    field_name=source_column,
                    current_value=source_value,
                    message=(
                        f"Referenced {target_record_name} record "
                        "does not exist"
                    ),
                    suggested_action=(
                        f"Update {source_column} or create the missing "
                        f"{target_record_name} record"
                    ),
                )
            )
            relationship_errors_found += 1

    # Engagements may be created before their interactions are recorded.
    # Report these unused records as warnings rather than errors.
    if (
        "engagement_id" in workbook.engagements_df.columns
        and "engagement_id" in workbook.interactions_df.columns
    ):
        referenced_engagement_ids = {
            engagement_id
            for engagement_id in workbook.interactions_df["engagement_id"]
            if not is_missing(engagement_id)
        }

        for excel_row, (row_index, row) in enumerate(
            workbook.engagements_df.iterrows(),
            start=2,
        ):
            engagement_id = row["engagement_id"]
            if (
                is_missing(engagement_id)
                or engagement_id in referenced_engagement_ids
            ):
                continue

            results.engagements.append(
                ReviewItem(
                    title=(
                        f"Engagement {engagement_id} has no interactions"
                    ),
                    category="missing_relationship",
                    priority="warning",
                    table_name="engagements",
                    record_id=engagement_id,
                    excel_row=excel_row,
                    field_name="engagement_id",
                    current_value=engagement_id,
                    message=(
                        "No interactions reference this engagement."
                    ),
                    suggested_action=(
                        "Verify the engagement is still needed or record "
                        "interactions associated with it."
                    ),
                )
            )

    # Validate that interaction projects belong to the
    # associated researcher's project memberships.
    print("Validating interaction project memberships...")

    researcher_project_lookup = (
        workbook.researchers_df
        .set_index("researcher_id")["project"]
        .to_dict()
    )

    for excel_row, (row_index, row) in enumerate(
        workbook.interactions_df.iterrows(),
        start=2,
    ):
        researcher_id = row["researcher_id"]
        interaction_project = row.get("project")

        if (
            is_missing(researcher_id)
            or is_missing(interaction_project)
        ):
            continue

        researcher_projects = researcher_project_lookup.get(
            researcher_id,
            "",
        )
        # Existing relationship validation will already
        # report missing researchers.
        if researcher_id not in researcher_project_lookup:
            continue

        researcher_project_list = parse_projects(researcher_projects)
        interaction_projects = parse_projects(interaction_project)
        invalid_projects = [
            project
            for project in interaction_projects
            if project not in researcher_project_list
        ]

        if not invalid_projects:
            continue

        interaction_id = row_index
        if "interaction_id" in workbook.interactions_df.columns:
            interaction_value = row["interaction_id"]
            if not is_missing(interaction_value):
                interaction_id = interaction_value

        for invalid_project in invalid_projects:
            results.interactions.append(
                ReviewItem(
                    title=(
                        f"Interaction {interaction_id} project "
                        f"'{invalid_project}' is not assigned "
                        f"to researcher {researcher_id}"
                    ),
                    category="invalid_relationship",
                    priority="error",
                    table_name="interactions",
                    record_id=interaction_id,
                    excel_row=excel_row,
                    field_name="project",
                    current_value=invalid_project,
                    message=(
                        "Interaction project is not one of the "
                        "researcher's project memberships"
                    ),
                    suggested_action=(
                        "Select from the researcher's projects: "
                        f"{', '.join(researcher_project_list)}"
                    ),
                )
            )
            relationship_errors_found += 1

    print("Relationship validation complete.")
    print(
        f"Invalid relationships found: {relationship_errors_found}"
    )


# ==================================================
# DUPLICATES
# ==================================================


def validate_duplicates(
    workbook: WorkbookData,
    results: ValidationResults,
) -> None:
    """Create review items for values that should be unique."""
    import pandas as pd

    # Duplicate rule definitions are maintained in this single list.
    duplicate_checks = [
        {
            "table": "researchers",
            "column": "researcher_id",
        },
        {
            "table": "researchers",
            "column": "email",
        },
        {
            "table": "engagements",
            "column": "engagement_id",
        },
        {
            "table": "interactions",
            "column": "interaction_id",
        },
        {
            "table": "contributions",
            "column": "contribution_id",
        },
    ]

    table_details = {
        "researchers": {
            "dataframe": workbook.researchers_df,
            "review_items": results.researchers,
            "identifier_column": "researcher_id",
        },
        "engagements": {
            "dataframe": workbook.engagements_df,
            "review_items": results.engagements,
            "identifier_column": "engagement_id",
        },
        "interactions": {
            "dataframe": workbook.interactions_df,
            "review_items": results.interactions,
            "identifier_column": "interaction_id",
        },
        "contributions": {
            "dataframe": workbook.contributions_df,
            "review_items": results.contributions,
            "identifier_column": "contribution_id",
        },
    }

    duplicate_count = 0

    def is_missing(value: object) -> bool:
        """Return whether a value should be excluded from duplicate checks."""
        return pd.isna(value) or value == ""

    print("Checking duplicates...")

    for duplicate_check in duplicate_checks:
        table_name = duplicate_check["table"]
        column_name = duplicate_check["column"]

        print("Validating:")
        print(f"{table_name}.{column_name}")

        table = table_details[table_name]
        dataframe = table["dataframe"]
        review_items = table["review_items"]
        identifier_column = table["identifier_column"]

        if column_name not in dataframe.columns:
            continue

        # Detect duplicate non-empty values in the configured column.
        value_counts = {}
        for value in dataframe[column_name]:
            if is_missing(value):
                continue

            if value not in value_counts:
                value_counts[value] = 0
            value_counts[value] += 1

        for excel_row, (row_index, row) in enumerate(
            dataframe.iterrows(),
            start=2,
        ):
            current_value = row[column_name]
            if is_missing(current_value):
                continue

            if value_counts[current_value] <= 1:
                continue

            record_id = row_index
            if identifier_column in dataframe.columns:
                identifier_value = row[identifier_column]
                if not is_missing(identifier_value):
                    record_id = identifier_value

            # Create one ReviewItem for every row containing a duplicate.
            review_items.append(
                ReviewItem(
                    title=(
                        f"{table_name.removesuffix('s').title()} "
                        f"{record_id} has duplicate "
                        f"{column_name.replace('_', ' ').title()} "
                        f"\"{current_value}\""
                    ),
                    category="duplicate_record",
                    priority="error",
                    table_name=table_name,
                    record_id=record_id,
                    excel_row=excel_row,
                    field_name=column_name,
                    current_value=current_value,
                    message=f"Duplicate {column_name} found",
                    suggested_action=(
                        f"Ensure {column_name} is unique"
                    ),
                )
            )
            duplicate_count += 1

    print("Duplicate validation complete.")
    print(f"Duplicate records found: {duplicate_count}")


# ==================================================
# COMPLETENESS METRICS
# ==================================================


def calculate_completeness_metrics(
    workbook: WorkbookData,
    results: ValidationResults,
) -> None:
    """Calculate completeness percentages for every workbook column."""
    import pandas as pd

    tables = [
        ("researchers", workbook.researchers_df),
        ("engagements", workbook.engagements_df),
        ("interactions", workbook.interactions_df),
        ("contributions", workbook.contributions_df),
    ]

    results.completeness_metrics = {}

    def is_missing(value: object) -> bool:
        """Return whether a value is missing for completeness purposes."""
        return pd.isna(value) or value == ""

    print("Calculating completeness metrics...")

    # Iterate through every workbook table without hardcoding its columns.
    for table_name, dataframe in tables:
        table_metrics = {}
        total_rows = len(dataframe)

        # Calculate the completeness percentage for each column.
        for column_name in dataframe.columns:
            non_missing_count = 0

            for value in dataframe[column_name]:
                if not is_missing(value):
                    non_missing_count += 1

            if total_rows == 0:
                completeness_percentage = 0.0
            else:
                completeness_percentage = round(
                    non_missing_count / total_rows * 100,
                    1,
                )

            table_metrics[column_name] = completeness_percentage
            print(
                f"{table_name}.{column_name}: "
                f"{completeness_percentage:.1f}%"
            )

        # Store all column metrics under the table being measured.
        results.completeness_metrics[table_name] = table_metrics

    print("Completeness metric calculation complete.")


# ==================================================
# RECOMMENDATIONS
# ==================================================


def generate_recommendations(
    workbook: WorkbookData,
    results: ValidationResults,
) -> None:
    """Generate configurable researcher status recommendations."""
    import pandas as pd

    # Recommendation rules and their configurable thresholds.
    recommendation_rules = {
        "prospect_to_participant": {
            "label": "Prospect -> Participant",
            "suggested_status": "participant",
        },
        "participant_to_contributor": {
            "label": "Participant -> Contributor",
            "suggested_status": "contributor",
        },
        "contributor_to_champion": {
            "label": "Contributor -> Champion",
            "suggested_status": "champion",
            "threshold": workbook.config["champion_contributions"],
        },
    }

    researchers = workbook.researchers_df
    interactions = workbook.interactions_df
    contributions = workbook.contributions_df

    researchers_with_inbound_interactions = set()
    contribution_counts = {}
    most_recent_interactions = {}

    recommendation_counts = {}
    for rule_name in recommendation_rules:
        recommendation_counts[rule_name] = 0

    def is_missing(value: object) -> bool:
        """Return whether a value cannot be used by a recommendation rule."""
        return pd.isna(value) or value == ""

    # Track inbound interactions and most recent dates by researcher.
    interaction_researcher_column_available = (
        "researcher_id" in interactions.columns
    )
    interaction_direction_columns_available = all(
        column_name in interactions.columns
        for column_name in ["researcher_id", "engagement_direction"]
    )
    interaction_date_columns_available = all(
        column_name in interactions.columns
        for column_name in ["researcher_id", "interaction_date"]
    )
    if interaction_researcher_column_available:
        for _, interaction in interactions.iterrows():
            researcher_id = interaction["researcher_id"]
            if is_missing(researcher_id):
                continue

            if (
                interaction_direction_columns_available
                and interaction["engagement_direction"] == "inbound"
            ):
                researchers_with_inbound_interactions.add(researcher_id)

            if not interaction_date_columns_available:
                continue

            interaction_date = interaction["interaction_date"]
            if is_missing(interaction_date):
                continue

            interaction_date = pd.Timestamp(interaction_date)
            if (
                researcher_id not in most_recent_interactions
                or interaction_date
                > most_recent_interactions[researcher_id]
            ):
                most_recent_interactions[researcher_id] = interaction_date

    # Calculate contribution counts by researcher.
    contribution_columns_available = (
        "researcher_id" in contributions.columns
    )
    if contribution_columns_available:
        for _, contribution in contributions.iterrows():
            researcher_id = contribution["researcher_id"]
            if is_missing(researcher_id):
                continue

            if researcher_id not in contribution_counts:
                contribution_counts[researcher_id] = 0
            contribution_counts[researcher_id] += 1

    print("Generating recommendations...")

    researcher_columns_available = all(
        column_name in researchers.columns
        for column_name in ["researcher_id", "researcher_status"]
    )

    if researcher_columns_available:
        today = pd.Timestamp.today().normalize()

        # Generate recommendations for each researcher from all valid rules.
        for _, researcher in researchers.iterrows():
            researcher_id = researcher["researcher_id"]
            current_status = researcher["researcher_status"]

            if is_missing(researcher_id) or is_missing(current_status):
                continue

            contribution_count = contribution_counts.get(researcher_id, 0)
            most_recent_interaction = most_recent_interactions.get(
                researcher_id
            )

            prospect_rule = recommendation_rules["prospect_to_participant"]
            if (
                interaction_direction_columns_available
                and current_status == "prospect"
                and researcher_id in researchers_with_inbound_interactions
            ):
                results.recommendations.append(
                    Recommendation(
                        recommendation_type="status_change",
                        researcher_id=researcher_id,
                        current_status=current_status,
                        suggested_status=prospect_rule[
                            "suggested_status"
                        ],
                        reason=(
                            "Researcher has responded through an "
                            "inbound interaction"
                        ),
                    )
                )
                recommendation_counts["prospect_to_participant"] += 1

            contributor_rule = recommendation_rules[
                "participant_to_contributor"
            ]
            if (
                contribution_columns_available
                and contribution_count > 0
                and current_status not in ["contributor", "champion"]
            ):
                results.recommendations.append(
                    Recommendation(
                        recommendation_type="status_change",
                        researcher_id=researcher_id,
                        current_status=current_status,
                        suggested_status=contributor_rule[
                            "suggested_status"
                        ],
                        reason=(
                            f"{contribution_count} contributions recorded"
                        ),
                    )
                )
                recommendation_counts["participant_to_contributor"] += 1

            champion_rule = recommendation_rules[
                "contributor_to_champion"
            ]
            if (
                contribution_columns_available
                and contribution_count >= champion_rule["threshold"]
                and current_status != "champion"
            ):
                results.recommendations.append(
                    Recommendation(
                        recommendation_type="status_change",
                        researcher_id=researcher_id,
                        current_status=current_status,
                        suggested_status=champion_rule[
                            "suggested_status"
                        ],
                        reason=(
                            f"{contribution_count} contributions meet the "
                            f"configured threshold of "
                            f"{champion_rule['threshold']}"
                        ),
                    )
                )
                recommendation_counts[
                    "contributor_to_champion"
                ] += 1

    for rule_name, rule in recommendation_rules.items():
        print(
            f"{rule['label']} recommendations: "
            f"{recommendation_counts[rule_name]}"
        )

    print("Recommendation generation complete.")
    total_recommendations = sum(recommendation_counts.values())
    print(f"Total recommendations: {total_recommendations}")
