"""Generate a self-contained HTML engagement dashboard."""

from datetime import datetime
from html import escape
from pathlib import Path
from typing import Any

from src.models.dashboard_models import (
    ActionQueue,
    DashboardMetrics,
    ICTMetrics,
)


def _display_value(value: Any) -> str:
    """Convert a dashboard value to safe display text."""
    return escape(str(value))


def _render_ict_performance(ict_metrics: list[ICTMetrics]) -> str:
    """Render ICT metrics as a comparison table."""
    if not ict_metrics:
        return '<p class="empty-message">No ICT metrics found.</p>'

    rows = []
    for metrics in sorted(
        ict_metrics,
        key=lambda item: item.total_researchers,
        reverse=True,
    ):
        rows.append(
            "        <tr>\n"
            f"          <td>{_display_value(metrics.ict_name)}</td>\n"
            f"          <td>{metrics.total_researchers}</td>\n"
            f"          <td>{metrics.new_researchers_this_month}</td>\n"
            f"          <td>{metrics.total_engagements}</td>\n"
            f"          <td>{metrics.interactions_this_month}</td>\n"
            f"          <td>{metrics.contributions_this_month}</td>\n"
            f"          <td>{metrics.total_contributions}</td>\n"
            "        </tr>"
        )

    return f"""<div class="table-container">
      <table>
        <thead>
          <tr>
            <th>ICT</th>
            <th title="Total Researchers">Researchers</th>
            <th title="New Researchers This Month">New</th>
            <th title="Total Engagements">Engagements</th>
            <th title="Interactions This Month">Interactions</th>
            <th title="Contributions This Month">New Contributions</th>
            <th title="Total Contributions">Total Contributions</th>
          </tr>
        </thead>
        <tbody>
{chr(10).join(rows)}
        </tbody>
      </table>
    </div>"""


def _render_action_queue(queue: ActionQueue) -> str:
    """Render one action queue and its items."""
    parts = [
        '<div class="action-queue">',
        f"  <h3>{_display_value(queue.title)}</h3>",
    ]

    if not queue.items:
        parts.append(
            '  <p class="empty-message">No action items found.</p>'
        )
    else:
        parts.append('  <div class="action-grid">')
        for item in queue.items:
            parts.extend(
                [
                    '    <article class="action-card">',
                    f"      <h4>{_display_value(item.title)}</h4>",
                    f"      <p>{_display_value(item.description)}</p>",
                ]
            )
            if item.researcher_id is not None:
                parts.append(
                    "      <p class=\"action-detail\"><strong>"
                    "Researcher ID:</strong> "
                    f"{_display_value(item.researcher_id)}</p>"
                )
            if item.ict_name is not None:
                parts.append(
                    "      <p class=\"action-detail\"><strong>ICT:</strong> "
                    f"{_display_value(item.ict_name)}</p>"
                )
            parts.append("    </article>")
        parts.append("  </div>")

    parts.append("</div>")
    return "\n".join(parts)


def _render_action_queues(action_queues: list[ActionQueue]) -> str:
    """Render all action queues."""
    if not action_queues:
        return '<p class="empty-message">No action items found.</p>'
    return "\n".join(_render_action_queue(queue) for queue in action_queues)


def generate_html_dashboard(
    dashboard_metrics: DashboardMetrics,
    output_path: str,
) -> None:
    """Write a self-contained researcher engagement dashboard."""
    print("Generating dashboard...")
    print("Writing dashboard to:")
    print(output_path)

    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M")
    summary = dashboard_metrics.executive_summary
    summary_metrics = [
        ("Total Researchers", summary.total_researchers),
        (
            "New Researchers This Month",
            summary.new_researchers_this_month,
        ),
        ("Total Engagements", summary.total_engagements),
        ("Interactions This Month", summary.interactions_this_month),
        ("Contributions This Month", summary.contributions_this_month),
        ("Total Contributions", summary.total_contributions),
    ]
    summary_cards = "\n".join(
        "        <div class=\"kpi-card\">\n"
        f"          <span>{escape(label)}</span>\n"
        f"          <strong>{value}</strong>\n"
        "        </div>"
        for label, value in summary_metrics
    )

    html_document = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Researcher Engagement Dashboard</title>
  <style>
    :root {{
      color: #1f2933;
      background: #f5f7fa;
      font-family: Arial, Helvetica, sans-serif;
      line-height: 1.5;
    }}
    * {{
      box-sizing: border-box;
    }}
    body {{
      max-width: 1200px;
      margin: 0 auto;
      padding: 32px 20px 64px;
    }}
    h1 {{
      margin: 0 0 4px;
      color: #102a43;
    }}
    h2 {{
      margin: 0 0 20px;
      padding-bottom: 8px;
      border-bottom: 2px solid #486581;
      color: #243b53;
    }}
    h3 {{
      margin: 0 0 14px;
      color: #334e68;
    }}
    h4 {{
      margin: 0 0 8px;
      color: #243b53;
    }}
    section {{
      margin-top: 48px;
    }}
    .generated-at {{
      margin: 0;
      color: #627d98;
    }}
    .kpi-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 14px;
    }}
    .kpi-card,
    .action-card {{
      border: 1px solid #bcccdc;
      border-radius: 8px;
      background: #ffffff;
      box-shadow: 0 1px 3px rgba(16, 42, 67, 0.08);
    }}
    .kpi-card {{
      display: flex;
      flex-direction: column;
      padding: 18px;
    }}
    .kpi-card span {{
      color: #486581;
    }}
    .kpi-card strong {{
      margin-top: 8px;
      color: #102a43;
      font-size: 1.8rem;
    }}
    .table-container {{
      overflow-x: auto;
      border: 1px solid #bcccdc;
      border-radius: 8px;
      background: #ffffff;
    }}
    table {{
      width: 100%;
      table-layout: fixed;
      border-collapse: collapse;
    }}
    th,
    td {{
      padding: 10px 8px;
      border-bottom: 1px solid #d9e2ec;
      text-align: left;
    }}
    th {{
      color: #243b53;
      background: #e8eef3;
      font-size: 0.9rem;
      line-height: 1.25;
      white-space: normal;
      overflow-wrap: break-word;
    }}
    th:first-child,
    td:first-child {{
      width: 22%;
    }}
    td:first-child {{
      overflow-wrap: anywhere;
      white-space: normal;
    }}
    td:not(:first-child) {{
      white-space: nowrap;
    }}
    tbody tr:last-child td {{
      border-bottom: 0;
    }}
    tbody tr:nth-child(even) {{
      background: #f8fafc;
    }}
    td:not(:first-child),
    th:not(:first-child) {{
      text-align: center;
    }}
    .action-queue + .action-queue {{
      margin-top: 32px;
    }}
    .action-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
      gap: 14px;
    }}
    .action-card {{
      padding: 18px;
    }}
    .action-card p {{
      margin: 8px 0 0;
    }}
    .action-detail {{
      color: #486581;
    }}
    .empty-message {{
      padding: 14px;
      border: 1px dashed #9fb3c8;
      border-radius: 8px;
      color: #627d98;
      background: #ffffff;
    }}
    @media (max-width: 600px) {{
      body {{
        padding: 24px 14px 48px;
      }}
      section {{
        margin-top: 36px;
      }}
      .kpi-grid {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>
</head>
<body>
  <header>
    <h1>Researcher Engagement Dashboard</h1>
    <p class="generated-at">Generated: {generated_at}</p>
  </header>

  <main>
    <section>
      <h2>Executive Summary</h2>
      <div class="kpi-grid">
{summary_cards}
      </div>
    </section>

    <section>
      <h2>ICT Performance</h2>
      {_render_ict_performance(dashboard_metrics.ict_performance)}
    </section>

  </main>
</body>
</html>
"""

    Path(output_path).write_text(html_document, encoding="utf-8")

    print("Dashboard generated successfully.")
