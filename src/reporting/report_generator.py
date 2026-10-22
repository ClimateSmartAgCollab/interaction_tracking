"""Generate a self-contained HTML validation report."""

from datetime import datetime
from html import escape
from pathlib import Path
from typing import Any

from src.models.validation_models import (
    Recommendation,
    ReviewItem,
    ValidationResults,
)
from src.models.workbook_models import WorkbookData


def _display_value(value: Any) -> str:
    """Convert a report value to safe display text."""
    if value is None:
        return "—"
    return escape(str(value))


def _display_label(value: str) -> str:
    """Convert an internal name to a readable label."""
    return escape(value.replace("_", " ").title())


def _render_review_items(
    heading: str,
    review_items: list[ReviewItem],
) -> str:
    """Render one worksheet's review items."""
    html_parts = [f"<h3>{escape(heading)} Review Items</h3>"]

    if not review_items:
        html_parts.append("<p class=\"empty-message\">No review items found.</p>")
        return "\n".join(html_parts)

    for item in review_items:
        priority = item.priority.lower()
        if priority not in {"error", "warning"}:
            priority = "info"

        html_parts.extend(
            [
                "<article class=\"review-card\">",
                "  <div class=\"card-heading\">",
                "    <input type=\"checkbox\">",
                f"    <strong>{_display_value(item.title)}</strong>",
                (
                    f"    <span class=\"priority {priority}\">"
                    f"{_display_label(item.priority)}</span>"
                ),
                "  </div>",
                "  <div class=\"record-details\">",
                f"    <span><strong>Sheet:</strong> "
                f"{_display_label(item.table_name)}</span>",
                f"    <span><strong>Excel Row:</strong> "
                f"{item.excel_row}</span>",
                f"    <span class=\"field-detail\"><strong>Field:</strong> "
                f"{_display_label(item.field_name or '')}</span>",
                "  </div>",
                f"  <p>{_display_value(item.message)}</p>",
                "  <div class=\"suggested-action\">",
                "    <strong>Suggested Action:</strong>",
                f"    <div>{_display_value(item.suggested_action)}</div>",
                "  </div>",
                "</article>",
            ]
        )

    return "\n".join(html_parts)


def _render_recommendations(
    recommendations: list[Recommendation],
) -> str:
    """Render researcher lifecycle recommendations."""
    html_parts = ["<h2>RECOMMENDATIONS</h2>"]

    if not recommendations:
        html_parts.append(
            "<p class=\"empty-message\">No recommendations found.</p>"
        )
        return "\n".join(html_parts)

    for recommendation in recommendations:
        html_parts.extend(
            [
                "<article class=\"recommendation-card\">",
                "  <div class=\"card-heading\">",
                "    <input type=\"checkbox\">",
                "    <strong>Researcher "
                f"{_display_value(recommendation.researcher_id)}</strong>",
                "  </div>",
                "  <div class=\"status-change\">",
                f"    {_display_value(recommendation.current_status)}",
                "    <span aria-label=\"changes to\">→</span>",
                f"    {_display_value(recommendation.suggested_status)}",
                "  </div>",
                f"  <p>{_display_value(recommendation.reason)}</p>",
                "</article>",
            ]
        )

    return "\n".join(html_parts)


def _render_completeness_metrics(
    completeness_metrics: dict[str, dict[str, float]],
) -> str:
    """Render completeness percentages grouped by workbook table."""
    html_parts = ["<h2>COMPLETENESS METRICS</h2>"]

    for table_name in ["researchers", "interactions", "contributions"]:
        table_metrics = completeness_metrics.get(table_name, {})
        html_parts.append(f"<h3>{_display_label(table_name)}</h3>")

        if not table_metrics:
            html_parts.append(
                "<p class=\"empty-message\">"
                "No completeness metrics found."
                "</p>"
            )
            continue

        html_parts.extend(
            [
                "<table>",
                "  <thead>",
                "    <tr><th>Field</th><th>Completeness</th></tr>",
                "  </thead>",
                "  <tbody>",
            ]
        )

        for column_name, percentage in table_metrics.items():
            html_parts.append(
                "    <tr>"
                f"<td>{escape(str(column_name))}</td>"
                f"<td>{percentage:.1f}%</td>"
                "</tr>"
            )

        html_parts.extend(["  </tbody>", "</table>"])

    return "\n".join(html_parts)


def generate_html_validation_report(
    workbook: WorkbookData,
    validation: ValidationResults,
    output_path: str,
) -> None:
    """Write a self-contained HTML validation report."""
    print("Generating HTML report...")
    print("Writing report to:")
    print(output_path)

    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M")

    executive_summary = [
        ("Number of Structural Errors", len(validation.structural)),
        ("Number of Researchers", len(workbook.researchers_df)),
        ("Number of Interactions", len(workbook.interactions_df)),
        ("Number of Contributions", len(workbook.contributions_df)),
        ("Number of Researcher Review Items", len(validation.researchers)),
        ("Number of Interaction Review Items", len(validation.interactions)),
        (
            "Number of Contribution Review Items",
            len(validation.contributions),
        ),
        ("Number of Recommendations", len(validation.recommendations)),
    ]

    summary_cards = []
    for label, value in executive_summary:
        summary_cards.append(
            "<div class=\"summary-card\">"
            f"<span>{escape(label)}</span>"
            f"<strong>{value}</strong>"
            "</div>"
        )

    html_document = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Researcher Engagement Validation Report</title>
  <style>
    :root {{
      color: #1f2933;
      background: #f5f7fa;
      font-family: Arial, Helvetica, sans-serif;
      line-height: 1.5;
    }}
    body {{
      max-width: 1100px;
      margin: 0 auto;
      padding: 32px 20px 64px;
    }}
    h1 {{
      margin-bottom: 4px;
      color: #102a43;
    }}
    h2 {{
      margin-top: 48px;
      padding-bottom: 8px;
      border-bottom: 2px solid #486581;
      color: #243b53;
    }}
    h3 {{
      margin-top: 32px;
      color: #334e68;
    }}
    .generated-at {{
      margin-top: 0;
      color: #627d98;
    }}
    .summary-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
      gap: 12px;
    }}
    .summary-card,
    .review-card,
    .recommendation-card {{
      border: 1px solid #bcccdc;
      border-radius: 6px;
      background: #ffffff;
      box-shadow: 0 1px 2px rgba(16, 42, 67, 0.08);
    }}
    .summary-card {{
      display: flex;
      flex-direction: column;
      padding: 16px;
    }}
    .summary-card span {{
      color: #486581;
    }}
    .summary-card strong {{
      margin-top: 6px;
      font-size: 1.6rem;
      color: #102a43;
    }}
    .review-card,
    .recommendation-card {{
      margin: 14px 0;
      padding: 18px;
    }}
    .card-heading {{
      display: flex;
      align-items: center;
      gap: 10px;
    }}
    input[type="checkbox"] {{
      width: 18px;
      height: 18px;
      margin: 0;
    }}
    .priority {{
      margin-left: auto;
      padding: 3px 9px;
      border-radius: 999px;
      font-size: 0.8rem;
      font-weight: bold;
      text-transform: uppercase;
    }}
    .priority.error {{
      color: #8a1c1c;
      background: #ffe3e3;
    }}
    .priority.warning {{
      color: #8d5b00;
      background: #fff3bf;
    }}
    .priority.info {{
      color: #0b4f6c;
      background: #d9f0ff;
    }}
    .record-details {{
      display: flex;
      flex-wrap: wrap;
      gap: 24px;
      margin-top: 14px;
      color: #486581;
    }}
    .field-detail {{
      flex-basis: 100%;
    }}
    .suggested-action {{
      margin-top: 14px;
      padding: 12px;
      border-left: 4px solid #3e7cb1;
      background: #f0f7ff;
    }}
    .status-change {{
      margin-top: 14px;
      font-size: 1.15rem;
      font-weight: bold;
      color: #334e68;
      text-transform: capitalize;
    }}
    .status-change span {{
      margin: 0 8px;
      color: #3e7cb1;
    }}
    table {{
      width: 100%;
      margin-bottom: 24px;
      border-collapse: collapse;
      background: #ffffff;
    }}
    th,
    td {{
      padding: 10px 12px;
      border: 1px solid #bcccdc;
      text-align: left;
    }}
    th {{
      color: #243b53;
      background: #e8eef3;
    }}
    td:last-child {{
      width: 160px;
    }}
    .empty-message {{
      padding: 14px;
      border: 1px dashed #9fb3c8;
      border-radius: 6px;
      color: #627d98;
      background: #ffffff;
    }}
  </style>
</head>
<body>
  <header>
    <h1>Researcher Engagement Validation Report</h1>
    <p class="generated-at">Generated: {generated_at}</p>
  </header>

  <main>
    <section>
      <h2>EXECUTIVE SUMMARY</h2>
      <div class="summary-grid">
        {"".join(summary_cards)}
      </div>
    </section>

    <section>
      <h2>DATA CORRECTIONS</h2>
      {_render_review_items("Workbook Structure", validation.structural)}
      {_render_review_items("Researchers", validation.researchers)}
      {_render_review_items("Interactions", validation.interactions)}
      {_render_review_items("Contributions", validation.contributions)}
    </section>

    <section>
      {_render_recommendations(validation.recommendations)}
    </section>

    <section>
      {_render_completeness_metrics(validation.completeness_metrics)}
    </section>
  </main>
</body>
</html>
"""

    report_path = Path(output_path)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(html_document, encoding="utf-8")

    print("HTML report generated successfully.")
