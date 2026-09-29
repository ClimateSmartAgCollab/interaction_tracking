from src.ingest.loader import load_workbook
from src.validation.validator import validate_workbook
from src.reporting.report_generator import generate_html_validation_report
from src.reporting.run_history import save_run_history
from src.reporting.dashboard_metrics import calculate_dashboard_metrics
from src.reporting.dashboard_generator import generate_html_dashboard

def main():
    workbook = load_workbook("data/ICT_interactions_test_data.xlsx")

    results = validate_workbook(workbook)

    run_dir = save_run_history(workbook, results)

    generate_html_validation_report(
        workbook=workbook,
        validation=results,
        output_path=run_dir / "validation_report.html",
        )

    summary_metrics = calculate_dashboard_metrics(workbook)

    generate_html_dashboard(
        dashboard_metrics=summary_metrics,
        output_path=run_dir / "engagement_dashboard.html",
    )


if __name__ == "__main__":
    main()