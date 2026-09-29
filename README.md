# Researcher Engagement Tracker

A lightweight researcher engagement tracking and reporting system built around a single Excel workbook and Python-based reporting tools.

## Repository Contents

- `approach.md` – project architecture, design decisions, workflows, and development guidance
- `src/` – Python code for validation, reporting, and dashboard generation
- `data/` – location for the Excel workbook (not tracked in Git)
- `runs/` – generated reports and run outputs (not tracked in Git)

## Workflow

1. Maintain researcher data in the Excel workbook.
2. Run validation scripts to identify data quality issues and suggested status updates.
3. Manually update the workbook as needed.
4. Generate an HTML dashboard and reports for team review.

## Design Principles

- Excel is the source of truth.
- Python never modifies the workbook.
- Validation and reporting are separate workflows.
- All business rules and controlled vocabularies are maintained in Excel.
- Reports are generated as self-contained HTML files.

For full project details, see **`approach.md`**.