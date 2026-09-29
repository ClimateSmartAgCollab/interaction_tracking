# Researcher Engagement Tracker - Architecture and Development Approach

## Project Goal

Build a lightweight researcher engagement tracking and reporting system using:

```text
Excel Workbook
    ↓
Validation and Data Quality Review
    ↓
Manual Data Corrections
    ↓
Analytics and Reporting
    ↓
Self-Contained HTML Dashboard
```

The Excel workbook is the single source of truth.

The Python code must never write changes back to the workbook.
All corrections are made manually by users after reviewing generated reports.
Controlled vocabulary validation is driven entirely by the Lists worksheet.
Lists are matched to workbook columns by name.

---



# Core Principles



## Source of Truth

The Excel workbook is the authoritative data source.

The workbook contains:

- Researchers table
- Interactions table
- Contributions table
- Controlled vocabulary sheets
- Configuration sheet

The Python application only:

- Reads workbook data
- Validates workbook data
- Generates recommendations
- Produces reports

The Python application never modifies workbook contents.

---



## Separation of Functions

The system is intentionally divided into two independent workflows.

### Workflow 1: Data Stewardship

Purpose:

Validate data quality and identify maintenance tasks.

```text
Workbook
    ↓
Validation Script
    ↓
Data Quality Report
    ↓
Manual Workbook Updates
```

Audience:

- Data steward
- Workbook maintainer

Output:

```text
quality_report.html
```

---



### Workflow 2: Team Reporting

Purpose:

Generate visual analytics and dashboards for stakeholders.

```text
Validated Workbook
    ↓
Reporting Script
    ↓
Dashboard HTML
```

Audience:

- Research team
- Project leadership
- Stakeholders

Output:

```text
engagement_dashboard.html
```

The dashboard has two objectives:

1. Provide a high-level view of engagement performance across ICTs.
2. Provide an action-oriented work queue that helps identify researchers who require outreach, follow-up, or recognition.

## The dashboard should not simply report historical activity. It should help determine where engagement efforts are succeeding and where future attention should be focused.



# Workbook Structure



## Data Tables



### Researchers

Fields:

```text
researcher_id
email
ICT
role
organization
date_added
researcher_status
```

---



### Interactions

Fields:

```text
interaction_id
researcher_id
date
interaction_type
engagement_direction
interaction_outcome
interaction_notes
```

---



### Contributions

Fields:

```text
contribution_id
researcher_id
source_interaction_id
date_received
content_type
```

---



# Controlled Vocabulary Sheets

The code should read these sheets dynamically every run.

Examples:

```text
ICT_List
Role_List
Status_List
Interaction_Type_List
Direction_List
Outcome_List
```

Rules:

- Never hardcode controlled vocabulary values.
- All validation should use workbook-controlled lists.
- New values can be added in Excel without code changes.

---



# Configuration Sheet

Business rules are stored in Excel.

Example:


| setting                 | value |
| ----------------------- | ----- |
| dormant_days            | 120   |
| champion_contributions  | 3     |
| max_display_list_values | 10    |


The Python code should read configuration values at runtime.

Examples:

```text
dormant_days
champion_contributions
```

Benefits:

- No code changes required
- Business rules are transparent
- Rules are versioned with data

---



# Project Structure

```text
researcher_tracker/
│
├── data/
│   └── engagement_tracker.xlsx
│
├── runs/
│
├── src/
│   ├── load_data.py
│   ├── validate.py
│   ├── recommendations.py
│   ├── metrics.py
│   ├── charts.py
│   ├── dashboard.py
│   └── utilities.py
│
└── approach.md
```

---



## Model Structure

Models are grouped by domain rather than creating one model file per module.

```text
WorkbookData
│
├── researchers_df
├── interactions_df
├── contributions_df
├── lists
└── config

ValidationResults
│
├── researchers
├── interactions
├── contributions
├── recommendations
└── completeness_metrics
    │
    ├── researchers
    ├── interactions
    └── contributions

ReviewItem
│
├── title
├── category
├── priority
├── table_name
├── record_id
├── excel_row
├── field_name
├── current_value
├── message
└── suggested_action

HTML Report
│
├── Executive Summary
├── Data Corrections
│   ├── Researchers
│   ├── Interactions
│   └── Contributions
├── Recommendations
└── Completeness Metrics

Data Correction Cards
│
├── Descriptive issue title
├── Priority indicator
├── Worksheet name
├── Excel row number
├── Field name
├── Validation message
├── Suggested action
└── Completion checkbox

DashboardMetrics
│
├── executive_summary : EngagementMetrics
│   ├── total_researchers
│   ├── new_researchers_this_month
│   ├── interactions_this_month
│   ├── contributions_this_month
│   └── total_contributions
│
├── ict_performance : list[ICTMetrics]
│   │
│   └── ICTMetrics
│       ├── ict_name
│       ├── total_researchers
│       ├── new_researchers_this_month
│       ├── interactions_this_month
│       ├── contributions_this_month
│       └── total_contributions
│
└── action_queues : list[ActionQueue]
    │
    └── ActionQueue
        ├── name
        ├── title
        └── items : list[ActionItem]
            │
            └── ActionItem
                ├── title
                ├── description
                ├── researcher_id
                └── ict_name
```

---



# Run Management

Outputs should never overwrite previous runs.

Every execution creates a timestamped folder.

Example:

```text
runs/
│
├── 2026-09-28_201530/
│   ├── validation_report.html
│   ├── researchers.parquet
│   ├── interactions.parquet
│   ├── contributions.parquet
│   ├── lists.json
│   ├── config.json
│   └── run_metadata.json
│
├── 2026-10-02_093015/
│   └── ...
```

Benefits:

- Historical snapshots
- Audit trail
- Report reproducibility
- Trend analysis over time



### Run Snapshots

Each run preserves the exact inputs used to generate the validation report. The goal is to provide a complete, reproducible record of the data, reference values, and business rules used during validation.

The run snapshot includes:

- researchers.parquet
- interactions.parquet
- contributions.parquet

These files contain the workbook data used during the run and allow future analysis to be performed without requiring access to the original Excel workbook. Using Parquet provides efficient storage, preserves data types, and supports rapid loading into pandas for troubleshooting or re-analysis.

The run snapshot also includes:

- lists.json
- config.json

These files preserve the controlled vocabularies and configuration settings that were in effect when the validation was executed. This ensures that historical reports can be understood and reproduced even if workbook lists or business rules change over time.

Together, the data snapshots, reference data, configuration, metadata, and generated reports create a complete audit package for each run.

---



# Validation Workflow



## Goal

Determine whether the workbook data is complete, consistent, and reliable for reporting.

Validation focuses on five areas:

### Required Columns

Ensure each workbook table contains the columns required for validation, reporting, and relationship checks.

### Missing Values

Identify records where required fields are blank and require data steward review.

### Controlled Vocabulary Validation

Verify that workbook values match the controlled vocabularies defined in the Lists worksheets.

### Relationship Validation

Confirm that references between researchers, interactions, and contributions point to valid records.

### Duplicate Detection

Identify values that should be unique, such as researcher IDs, interaction IDs, contribution IDs, and email addresses.

### Completeness Metrics

Measure the percentage of populated values for each field to provide a high-level view of data quality.

Validation results are presented as actionable review items in the HTML report. Each review item includes a descriptive issue title, worksheet name, Excel row number, affected field, and suggested action to support a checklist-style data correction workflow.

---



# Researcher Recommendations

The code must generate recommendations.

The code must never apply changes.

Users decide whether to update Excel.

---



## Suggested Dormant

Rule:

```text
Last interaction older than inactive_days
AND
Current status is not dormant
```

Output:

```text
Researcher ID
Current Status
Last Interaction Date
Suggested Status
Reason
```

---



## Suggested Contributor

Rule:

```text
Contribution count > 0
AND
Any status except Contributor or Champion
```

Output:

```text
Suggested Status = contributor
```

---



## Suggested Champion

Rule controlled by configuration.

Example:

```text
Contributions >= champion_contributions
```

Potential future rules:

```text
Referred colleagues
Multiple contributions
Multiple ICT engagements
```

---



## Suggested Active

Rule:

```text
Prospect
AND
At least one inbound interaction
```

Output:

```text
Suggested Status = active
```

---



# Analytics Workflow



## Goal

Determine:

```text
What does the data tell us?
```

---



# Metrics



## Researchers

Examples:

```text
Total Researchers
Researchers by ICT
Researchers by Role
Researchers by Status
```

---



## Interactions

Examples:

```text
Total Interactions
Interactions by Month
Interactions by Type
Interactions by Direction
Interactions by Outcome
```

---



## Contributions

Examples:

```text
Total Contributions
Contributions by Content Type
Contributions by ICT
Contributions by Month
```

---



## Engagement Funnel

Examples:

```text
Prospects
↓
Active
↓
Contributors
↓
Champions
```

---



## Content Pipeline

Compare:

```text
content_promised
```

against

```text
Contribution records
```

Questions:

```text
How much promised content was delivered?
Which ICTs generate content?
Which researchers contribute content?
```

---



# Dashboard Design

Generate a self-contained HTML file.

No web server required.

No cloud hosting required.

No GitHub Pages required.

Open directly in browser.

---



## Dashboard Sections



### Executive Summary

KPI Cards:

```text
Researchers
Interactions
Contributions
Active Researchers
Champions
```

---



### Researcher Analytics

Charts:

```text
Researchers by Status
Researchers by ICT
Researchers by Role
```

---



### Interaction Analytics

Charts:

```text
Interactions by Month
Interactions by Direction
Interactions by Outcome
```

---



### Contribution Analytics

Charts:

```text
Contributions by Type
Contributions by Month
Contributions by ICT
```

---



### Follow-Up Section

Useful action items:

```text
Researchers requiring follow-up
Researchers suggested for dormant status
Researchers suggested for contributor status
Researchers suggested for champion status
```

---



# Technology Choices

Preferred stack:

```text
Python
pandas
openpyxl
plotly
jinja2
pyarrow
```

Reasons:

- Works directly with Excel
- Generates interactive charts
- Produces standalone HTML
- Easy future migration to Streamlit if desired
- Provides efficient Parquet storage for run snapshots.

---



# Future Possibilities

Potential future enhancements:

```text
Streamlit dashboard
PDF exports
PowerPoint exports
Historical trend comparisons
Data quality scoring
Researcher activity scoring
```

The current goal is intentionally simple:

Excel Workbook → Validation Report → Manual Cleanup → Dashboard HTML