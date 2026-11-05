# Core Principles

## Source of Truth

The Excel workbook is the authoritative data source.

The workbook contains:

- Researchers table
- Engagements table
- Interactions table
- Contributions table
- Controlled vocabulary sheets
- Configuration sheet

The Python application only:

- Reads workbook data
- Validates workbook data
- Generates recommendations
- Produces reports and dashboards

The Python application never modifies workbook contents.

All workbook corrections are performed manually by users after reviewing generated reports.

Day-to-day review uses self-contained HTML files that run in the browser with no server and no Python runtime:

- `index.html` – toolkit homepage
- `data_entry.html`
- `validation.html`
- `dashboard.html`

Open the hosted toolkit at `https://climatesmartagcollab.github.io/interaction_tracking/` after GitHub Pages is enabled from `main` / root, or open the same HTML files from this folder. The user selects or drops the `.xlsx` workbook. Nothing is uploaded. GitHub hosts the HTML only.

Usual sequence:

1. Create or update records in Data Entry
2. Check workbook quality in Validation
3. Review results in the Dashboard

Switching pages unloads the workbook; load the file again on the next tool. Each page shows a **Last updated** date from its `release-date` meta tag.

`dashboard.html` is the engagement dashboard; Python dashboard generation in `src/reporting/` remains in the repository but is not the default workflow.

---

# Workbook Structure

## Data Tables

### Researchers

Fields:

```text
researcher_id
email
researcher_name
project
role
organization
date_added
researcher_status
```

Researchers represent people or contacts involved in engagement activities.

A researcher may belong to one or more projects.

Multiple project memberships are represented as semicolon-separated values.

Example:

```text
ACTIVATE
```

```text
ACTIVATE;CAT-G
```

Researchers may participate in multiple engagements.

---

### Engagements

Fields:

```text
engagement_id
engagement_status
title
```

The Engagements table is the authoritative source of engagement metadata.

Each engagement represents a unit of work, relationship, initiative, conversation stream, or support activity.

Examples:

```text
ENG-0001
```

```text
DMP Outreach for Animal Genomics
```

Status values are maintained through controlled vocabularies.

Examples:

```text
Open
Closed
Reopened
```

The application must not hardcode engagement statuses.

An engagement may involve:

- Multiple researchers
- Multiple projects
- Multiple interactions
- Multiple contributions

---

### Interactions

Fields:

```text
interaction_id
engagement_id
researcher_id
project
interaction_date
interaction_channel
engagement_direction
interaction_purpose
interaction_summary
next_action
```

Interactions represent individual communication or activity records.

Examples:

```text
Meeting
Email
Documentation review
Dataset discussion
Training session
```

Interactions connect researchers to engagements.

Interactions may belong to one or more projects using semicolon-separated values.

Example:

```text
ACTIVATE
```

```text
ACTIVATE;CAT-G
```

All interaction records must reference a valid engagement.

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

Contributions represent outputs received as a result of engagement activity.

Examples:

```text
Dataset
Documentation
Metadata
Publication
Training Material
```

Contributions are linked back to interactions and researchers.

---

# Validation Workflow

## Goal

Determine whether workbook data is complete, consistent, and reliable for reporting.

Validation focuses on:

### Required Columns

Ensure all required worksheets and fields exist.

---

### Missing Values

Identify required values that are blank.

---

### Controlled Vocabulary Validation

Validate values against workbook-controlled lists.

The application should never hardcode vocabulary values.

---

### Relationship Validation

Confirm relationships are valid.

Examples:

```text
interaction.researcher_id
    →
researcher.researcher_id
```

```text
interaction.engagement_id
    →
engagement.engagement_id
```

```text
contribution.source_interaction_id
    →
interaction.interaction_id
```

---

### Engagement Validation

Validate engagement-specific structure and usage.

Examples:

```text
Engagement exists
```

```text
Engagement status is valid
```

```text
Interaction references a valid engagement
```

```text
Engagement has no interactions
```

(Warning only)

---

### Duplicate Detection

Identify values that should be unique.

Examples:

```text
researcher_id
```

```text
interaction_id
```

```text
contribution_id
```

```text
engagement_id
```

```text
email
```

---

### Completeness Metrics

Measure population percentages across workbook fields.

These metrics provide a high-level view of data quality and stewardship effort.

### Structural Validation

Required worksheets and required columns define the workbook structure.

If required worksheets or required columns are missing:

- Validation continues
- Validation reports are generated
- Run history is saved
- Dashboard generation is skipped
- The application exits cleanly

Structural validation failures prevent reporting because the workbook shape is incomplete.

---

# Dashboard Philosophy

## Purpose

The dashboard is an engagement management and review tool.

The dashboard should help answer:

```text
What work is active?

Which engagements require attention?

Which projects are receiving engagement effort?

Which activities are generating contributions?

Where should future engagement effort be focused?
```

The dashboard is not intended to be a simple historical report.

---

# Dashboard Sections

The live dashboard is `dashboard.html`. Its first metrics section is titled Program Snapshot. The Python-generated dashboard used the heading Executive Summary for the same role.

### Program Snapshot / Executive Summary

High-level portfolio metrics.

Examples:

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

Project-level engagement metrics.

The table should distinguish:

```text
Lifetime totals
```

from

```text
Current-period activity
```

Examples:

```text
Researchers

Researchers Added (Month Year)

Engagements

Total Interactions

Interactions (Month Year)

Total Contributions

Contributions (Month Year)
```

The purpose is to understand:

```text
Which projects are growing?

Which projects are active?

Which projects are generating outcomes?
```

---

### Engagement Review Summaries

Primary engagement navigation.

Engagements are grouped dynamically by:

```text
engagement_status
```

Examples:

```text
Open

Closed

Reopened
```

Status values should never be hardcoded.

Each status group provides a summary table linking to detailed engagement review cards.

---

### Engagement Reviews

Detailed engagement-level review cards.

An engagement review includes:

```text
Title

Status

Engagement ID

Projects

Participant Count

Interaction Activity

Latest Activity

Latest Next Action

Contribution Count
```

Expanded views include:

```text
Participant List

Interaction History
```

The engagement is the primary reporting object.

Researchers, interactions, projects, and contributions provide supporting context.

---

# Engagement Review Data Model

```text
EngagementReview
│
├── engagement_id
├── engagement_title
├── engagement_status
├── projects
├── participant_count
├── participants
├── interaction_count
├── contribution_count
├── latest_interaction_date
├── days_since_activity
├── latest_next_action
├── engagement_duration_days
└── interaction_history
```

```text
EngagementParticipant
│
├── researcher_id
├── researcher_name
├── researcher_email
└── role
```

This structure reflects the current business model where:

```text
One engagement may involve many researchers.

One engagement may involve many projects.
```

and engagements are the primary unit of reporting and review.