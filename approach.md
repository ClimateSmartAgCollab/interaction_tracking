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

---



# Workbook Structure



## Data Tables



### Researchers

Fields:

```text
researcher_ID
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


| setting                | value |
| ---------------------- | ----- |
| inactive_days          | 120   |
| champion_contributions | 3     |
| prospect_interactions  | 5     |


The Python code should read configuration values at runtime.

Examples:

```text
inactive_days
champion_contributions
prospect_interactions
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



# Run Management

Outputs should never overwrite previous runs.

Every execution creates a timestamped folder.

Example:

```text
runs/
│
├── 2026-09-24_1430/
│   ├── quality_report.html
│   ├── dashboard.html
│   ├── metrics.json
│   ├── run_info.json
│   └── workbook_snapshot.xlsx
│
├── 2026-10-01_0945/
│   └── ...
```

Benefits:

- Historical snapshots
- Audit trail
- Report reproducibility
- Trend analysis over time

---



# Validation Workflow



## Goal

Determine:

```text
Can the data be trusted?
```

---



## Validation Categories



### Errors

Must be corrected.

Examples:

```text
Invalid controlled vocabulary value
Duplicate primary key
Missing referenced researcher
Missing referenced interaction
```

---



### Warnings

May require review.

Examples:

```text
Missing role
Missing organization
Missing interaction outcome
Contribution without source interaction
```

---



### Data Completeness

Examples:

```text
Researchers with status
Researchers with ICT
Researchers with role
Interactions with outcome
```

Output as percentages.

---



# Researcher Recommendations

The code must generate recommendations.

The code must never apply changes.

Users decide whether to update Excel.

---



## Suggested Inactive

Rule:

```text
Last interaction older than inactive_days
AND
Current status is not inactive
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
Status is prospect or active
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
Interaction count exceeds threshold
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
Researchers suggested for inactive status
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
```

Reasons:

- Works directly with Excel
- Generates interactive charts
- Produces standalone HTML
- Easy future migration to Streamlit if desired

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