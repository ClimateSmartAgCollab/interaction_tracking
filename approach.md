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

1. Provide a high-level view of engagement performance across Projects.
2. Provide an action-oriented work queue that helps identify researchers who require outreach, follow-up, or recognition.

## The dashboard should not simply report historical activity. It should help determine where engagement efforts are succeeding and where future attention should be focused.



# Workbook Structure



## Data Tables



### Researchers

Fields:

```text
researcher_id
email
Project
role
organization
date_added
researcher_status
```

The Project field represents the researcher's primary Project.
 
Researchers associated with multiple Projects may list
multiple Project values separated by semicolons.
 
Future versions may attribute Project at the engagement level
if cross-Project participation becomes common.

---



### Interactions

Fields:

```text
interaction_id
engagement_id
researcher_id
interaction_date
interaction_channel
engagement_direction
interaction_purpose
interaction_summary
next_action
```

engagement_id

Groups related interactions into a single engagement.

Example:
ENG-0001
ENG-0002

interaction_purpose

The purpose of the interaction.

Examples:
initial_outreach
schema_discussion
dataset_discussion
documentation_request
content_submission
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
project
role
researcher_status
interaction_channel
engagement_direction
interaction_purpose
organization
content_type
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
│ ├── total_researchers
│ ├── new_researchers_this_month
│ ├── total_engagements
│ ├── interactions_this_month
│ ├── contributions_this_month
│ └── total_contributions
│
├── project_performance : list[PROJECTMetrics]
│   │
│   └── PROJECTMetrics
│       ├── project_name
│       ├── total_researchers
│       ├── new_researchers_this_month
│       ├── total_engagements
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
                └── project_name
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

### Engagement Validation
 
Verify engagement_id values are populated and consistently used.

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
Multiple Project engagements
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

## Executive Summary

```text
Total Researchers
New Researchers This Month

Total Engagements

Interactions This Month

Contributions This Month
Total Contributions
```

These metrics answer:

```text
Is the network growing?

How active have we been?

Are contributions being generated?
```

---

# Dashboard Design

Generate a self-contained HTML dashboard.

No web server required.

Open directly in a browser.

---

## Dashboard Sections

### Executive Summary

```text
Total Researchers
New Researchers This Month

Total Engagements

Interactions This Month

Contributions This Month
Total Contributions
```

---

### Project Performance
Table.
```text
Total Researchers

New Researchers This Month

Total Engagements

Interactions This Month

Contributions This Month

Total Contributions
```

The goal is to understand:

```text
Which Projects are growing?

Which Projects are receiving engagement effort?

Which Projects are generating contributions?
```

---

### Researcher Analytics
Future development
```text
Researchers by Project

Researchers by Role

Researchers by Status

Researchers by Organization
```

---

### Engagement Analytics
Future development
```text
Total Engagements

Total Interactions

Interactions by Channel

Interactions by Purpose

Interactions per Engagement

Engagements by Project
```

---

### Contribution Analytics
Future development
```text
Contributions by Content Type

Contributions by Project

Contributions by Month

Contributions by Researcher Status
```

---

### Action Queues

Future workflow-focused section.

Examples:

```text
Open Actions

Researchers Requiring Follow-Up

Researchers Suggested for Dormant Status

Researchers Suggested for Contributor Status

Researchers Suggested for Champion Status
```

---

### Future Metrics

### Future Metrics

```text
Average Interactions per Engagement

Average Interactions Before First Response

Average Interactions Before First Contribution

Inbound Response Rate

Response Rate by Project

Response Rate by Role

Contribution Rate by Project

Contribution Rate by Role

Average Engagement Duration

Open Engagements

Longest Running Open Engagements
```

These metrics are intended to answer questions such as:

```text
How much effort is typically required to get a response?

How much effort is typically required to obtain a contribution?

Which Projects are easiest to engage?

Which roles are most responsive?

Which Projects generate the strongest contribution outcomes?

How many interactions are required to support a typical engagement?

Which engagements require follow-up or may be stalled?
```

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