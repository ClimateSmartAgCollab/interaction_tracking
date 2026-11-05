# Researcher Engagement Tracker

A lightweight researcher engagement tracking and reporting system built around a single Excel workbook. Day-to-day tools are self-contained HTML files that open locally. Python reporting code remains available but is not required to review the dashboard.

## Repository Contents

- `approach.md` – project architecture, design decisions, workflows, and development guidance
- `dashboard.html` – local engagement dashboard (double-click, load the workbook)
- `validation.html` – local workbook validation
- `data_entry.html` – local data entry and export of a versioned workbook copy
- `src/` – Python code for validation, reporting, and dashboard generation
- `data/` – location for the Excel workbook (not tracked in Git)
- `runs/` – generated reports and run outputs (not tracked in Git)

## Workflow

1. Maintain researcher data in the Excel workbook.
2. Open `validation.html` and load the workbook to review data quality issues.
3. Open `data_entry.html` to add records and export a new versioned copy.
4. Open `dashboard.html` and load the workbook for program review.

## Design Principles

- Excel is the source of truth.
- The HTML tools never upload the workbook; they read it on this computer.
- Python never modifies the workbook.
- Validation and reporting are separate workflows.
- All business rules and controlled vocabularies are maintained in Excel.

For full project details, see **`approach.md`**.