# Researcher Engagement Tracker

A lightweight researcher engagement tracking and reporting system built around a single Excel workbook. Day-to-day tools are self-contained HTML files. Python reporting code remains available but is not required to review the dashboard.

## Open the tools

Usual path (after GitHub Pages is enabled on `main` / root):

https://climatesmartagcollab.github.io/interaction_tracking/

You can also open `index.html`, `data_entry.html`, `validation.html`, or `dashboard.html` from this folder. The workbook is never uploaded either way.

Each page shows **Last updated: YYYY-MM-DD**. To mark a release, change the `release-date` meta tag in that HTML file.

## Repository Contents

- `approach.md` – project architecture, design decisions, workflows, and development guidance
- `index.html` – toolkit homepage and launcher
- `dashboard.html` – engagement dashboard
- `validation.html` – workbook validation
- `data_entry.html` – data entry and export of a versioned workbook copy
- `src/` – Python code for validation, reporting, and dashboard generation
- `data/` – location for the Excel workbook (not tracked in Git)
- `runs/` – generated reports and run outputs (not tracked in Git)

## Workflow

1. Maintain researcher data in the Excel workbook.
2. Create or update records in Data Entry and export a new versioned copy.
3. Check workbook quality in Validation.
4. Review results in the Dashboard.

## Design Principles

- Excel is the source of truth.
- The HTML tools never upload the workbook; they read it on this computer.
- GitHub Pages hosts the HTML tools only. Switching tools unloads the workbook, so load the file again on the next page.
- Python never modifies the workbook.
- Validation and reporting are separate workflows.
- All business rules and controlled vocabularies are maintained in Excel.

For full project details, see **`approach.md`**.
