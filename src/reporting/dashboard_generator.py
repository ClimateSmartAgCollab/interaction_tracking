"""Generate a self-contained HTML engagement dashboard."""

from datetime import datetime
from html import escape
from pathlib import Path
from typing import Any
from urllib.parse import quote

from src.models.dashboard_models import (
    ActionQueue,
    ContributionTypeMetrics,
    DashboardMetrics,
    EngagementReview,
    ProjectMetrics,
    InteractionHistoryItem,
    OutstandingAction,
)

_BACK_TO_TOP_LINK = (
    '<p class="back-to-top"><a href="#top">↑ Back to Top</a></p>'
)


def _display_value(value: Any) -> str:
    """Convert a dashboard value to safe display text."""
    return escape(str(value))


def _render_project_performance(project_metrics: list[ProjectMetrics]) -> str:
    """Render PROJECT metrics as a comparison table."""
    if not project_metrics:
        return '<p class="empty-message">No PROJECT metrics found.</p>'

    rows = []
    for metrics in sorted(
        project_metrics,
        key=lambda item: item.total_researchers,
        reverse=True,
    ):
        rows.append(
            "        <tr>\n"
            f"          <td>{_display_value(metrics.project_name)}</td>\n"
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
            <th>Project</th>
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


def _render_contribution_breakdown(
    contribution_metrics: list[ContributionTypeMetrics],
) -> str:
    """Render contribution totals by content type and project."""
    if not contribution_metrics:
        return '<p class="empty-message">No contribution data found.</p>'

    project_names = list(
        dict.fromkeys(
            project_name
            for metrics in contribution_metrics
            for project_name in metrics.project_counts
        )
    )
    project_headers = "\n".join(
        f"            <th>{_display_value(project_name)}</th>"
        for project_name in project_names
    )

    rows = []
    for metrics in contribution_metrics:
        project_cells = "\n".join(
            "          <td>"
            f"{metrics.project_counts.get(project_name, 0) or '-'}"
            "</td>"
            for project_name in project_names
        )
        rows.append(
            "        <tr>\n"
            f"          <td>{_display_value(metrics.content_type)}</td>\n"
            f"          <td>{metrics.total_contributions}</td>\n"
            f"{project_cells}\n"
            "        </tr>"
        )

    return f"""<div class="table-container">
      <table class="contribution-breakdown-table">
        <thead>
          <tr>
            <th>Content Type</th>
            <th>Total</th>
{project_headers}
          </tr>
        </thead>
        <tbody>
{chr(10).join(rows)}
        </tbody>
      </table>
    </div>"""


def _render_outstanding_actions(
    outstanding_actions: list[OutstandingAction],
) -> str:
    """Render outstanding next actions as an oldest-first work queue."""
    if not outstanding_actions:
        return '<p class="empty-message">No outstanding actions found.</p>'

    rows = []
    for action in outstanding_actions:
        engagement_fragment = quote(str(action.engagement_id), safe="")
        rows.append(
            "        <tr>\n"
            f"          <td>{action.days_since_last_interaction}</td>\n"
            f"          <td>{_display_value(action.project_name)}</td>\n"
            f"          <td>{_display_value(action.researcher_email)}</td>\n"
            f"          <td>{_display_value(action.next_action)}</td>\n"
            "          <td>"
            f'<a href="#{engagement_fragment}">'
            f"{_display_value(action.engagement_id)}</a></td>\n"
            "        </tr>"
        )

    return f"""<div class="table-container">
      <table class="outstanding-actions-table">
        <thead>
          <tr>
            <th>Days Since Last Interaction</th>
            <th>Project</th>
            <th>Researcher Email</th>
            <th>Next Action</th>
            <th>Engagement</th>
          </tr>
        </thead>
        <tbody>
{chr(10).join(rows)}
        </tbody>
      </table>
    </div>"""


def _render_interaction_history_item(
    item: InteractionHistoryItem,
) -> str:
    """Render one interaction history table row."""
    return (
        "              <tr>\n"
        f"                <td>{_display_value(item.interaction_date)}</td>\n"
        f"                <td>{_display_value(item.engagement_direction)}</td>\n"
        f"                <td>{_display_value(item.interaction_channel)}</td>\n"
        f"                <td>{_display_value(item.interaction_purpose)}</td>\n"
        f"                <td>{_display_value(item.next_action)}</td>\n"
        "              </tr>"
    )


def _render_engagement_review(review: EngagementReview) -> str:
    """Render one expandable engagement review card."""
    history_rows = "\n".join(
        _render_interaction_history_item(item)
        for item in review.interaction_history
    )
    if not history_rows:
        history_rows = (
            '              <tr><td colspan="5" class="history-empty">'
            "No interaction history found.</td></tr>"
        )

    interaction_label = (
        "interaction" if review.interaction_count == 1 else "interactions"
    )
    day_label = "day" if review.engagement_duration_days == 1 else "days"
    interaction_activity = (
        f"{review.interaction_count} {interaction_label} over "
        f"{review.engagement_duration_days} {day_label}"
    )

    return f"""<details id="{_display_value(review.engagement_id)}" class="engagement-card">
        <summary class="engagement-summary">
          <span class="engagement-title">
            <span class="summary-label">Engagement ID</span>
            <strong>{_display_value(review.engagement_id)}</strong>
          </span>
          <span class="summary-item">
            <span class="summary-label">Project</span>
            <span class="summary-value">{_display_value(review.project_name)}</span>
          </span>
          <span class="summary-item researcher-summary">
            <span class="summary-label">Researcher Email</span>
            <span class="summary-value">{_display_value(review.researcher_email)}</span>
          </span>
          <span class="summary-item">
            <span class="summary-label">Latest Interaction Date</span>
            <span class="summary-value">{_display_value(review.latest_interaction_date)}</span>
          </span>
          <span class="summary-item latest-action-summary">
            <span class="summary-label">Latest Next Action</span>
            <span class="summary-value">{_display_value(review.latest_next_action)}</span>
          </span>
          <span class="summary-item">
            <span class="summary-label">Interaction Activity</span>
            <span class="summary-value">{interaction_activity}</span>
          </span>
          <span class="summary-item">
            <span class="summary-label">Contribution Count</span>
            <span class="summary-value">{review.contribution_count}</span>
          </span>
        </summary>
        <div class="engagement-expanded">
          <div class="researcher-details">
            <h4>Researcher Details</h4>
            <dl>
              <div><dt>Role</dt><dd>{_display_value(review.role)}</dd></div>
            </dl>
          </div>
        <h4>Interaction History</h4>
        <div class="history-table-container">
          <table class="history-table">
            <thead>
              <tr>
                <th>Date</th>
                <th>Direction</th>
                <th>Channel</th>
                <th>Purpose</th>
                <th>Next Action</th>
              </tr>
            </thead>
            <tbody>
{history_rows}
            </tbody>
          </table>
        </div>
        {_BACK_TO_TOP_LINK}
        </div>
      </details>"""


def _render_engagement_reviews(
    engagement_reviews: list[EngagementReview],
) -> str:
    """Render engagement reviews in the supplied metrics order."""
    if not engagement_reviews:
        return '<p class="empty-message">No engagement reviews found.</p>'
    return "\n".join(
        _render_engagement_review(review)
        for review in engagement_reviews
    )


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
            if item.project_name is not None:
                parts.append(
                    "      <p class=\"action-detail\"><strong>Project:</strong> "
                    f"{_display_value(item.project_name)}</p>"
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
        ("Total Unique Researchers", summary.total_researchers),
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
    .action-card,
    .engagement-card {{
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
      text-align: center;
    }}
    .kpi-card strong {{
      margin-top: auto;
      color: #102a43;
      font-size: 1.8rem;
      text-align: center;
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
    .contribution-breakdown-table {{
      min-width: 640px;
      table-layout: auto;
    }}
    .contribution-breakdown-table th:first-child,
    .contribution-breakdown-table td:first-child {{
      width: 30%;
      min-width: 200px;
    }}
    .contribution-breakdown-table th:not(:first-child),
    .contribution-breakdown-table td:not(:first-child) {{
      min-width: 90px;
      text-align: center;
    }}
    .outstanding-actions-table th:nth-child(1) {{
      width: 14%;
    }}
    .outstanding-actions-table th:nth-child(2) {{
      width: 16%;
    }}
    .outstanding-actions-table th:nth-child(3) {{
      width: 22%;
    }}
    .outstanding-actions-table th:nth-child(4) {{
      width: 34%;
    }}
    .outstanding-actions-table th:nth-child(5) {{
      width: 14%;
    }}
    .outstanding-actions-table td {{
      text-align: left;
      white-space: normal;
      overflow-wrap: anywhere;
    }}
    .outstanding-actions-table td:first-child,
    .outstanding-actions-table td:last-child {{
      text-align: center;
    }}
    .engagement-card {{
      margin-top: 16px;
      scroll-margin-top: 16px;
      overflow: hidden;
    }}
    .engagement-card[open] {{
      box-shadow: 0 3px 10px rgba(16, 42, 67, 0.12);
    }}
    .engagement-summary {{
      display: grid;
      grid-template-columns: minmax(130px, 0.75fr) repeat(3, minmax(150px, 1fr));
      gap: 14px 18px;
      padding: 16px 44px 16px 18px;
      position: relative;
      cursor: pointer;
      list-style: none;
    }}
    .engagement-summary::-webkit-details-marker {{
      display: none;
    }}
    .engagement-summary::after {{
      content: "›";
      position: absolute;
      top: 50%;
      right: 20px;
      color: #486581;
      font-size: 1.7rem;
      line-height: 1;
      transform: translateY(-50%) rotate(90deg);
      transition: transform 0.15s ease;
    }}
    .engagement-card[open] > .engagement-summary {{
      border-bottom: 1px solid #d9e2ec;
      background: #f8fafc;
    }}
    .engagement-card[open] > .engagement-summary::after {{
      transform: translateY(-50%) rotate(-90deg);
    }}
    .engagement-summary:hover {{
      background: #f8fafc;
    }}
    .engagement-summary:focus-visible {{
      outline: 3px solid #9fb3c8;
      outline-offset: -3px;
    }}
    .engagement-title,
    .summary-item {{
      display: flex;
      flex-direction: column;
      min-width: 0;
    }}
    .engagement-title strong {{
      color: #102a43;
      font-size: 1.08rem;
      overflow-wrap: anywhere;
    }}
    .summary-label,
    .researcher-details dt {{
      color: #627d98;
      font-size: 0.82rem;
      font-weight: bold;
    }}
    .summary-value {{
      margin-top: 2px;
      overflow-wrap: anywhere;
      color: #102a43;
    }}
    .latest-action-summary {{
      grid-column: span 2;
    }}
    .engagement-expanded {{
      padding: 18px;
    }}
    .researcher-details {{
      margin-bottom: 18px;
    }}
    .researcher-details dl {{
      margin: 0;
    }}
    .researcher-details dd {{
      margin: 2px 0 0;
      color: #102a43;
      overflow-wrap: anywhere;
    }}
    .history-table-container {{
      overflow-x: auto;
      border: 1px solid #d9e2ec;
      border-radius: 6px;
    }}
    .history-table {{
      min-width: 680px;
      font-size: 0.9rem;
    }}
    .history-table th,
    .history-table td {{
      padding: 8px;
      text-align: left;
      white-space: normal;
      overflow-wrap: break-word;
    }}
    .history-table th:nth-child(1) {{
      width: 14%;
    }}
    .history-table th:nth-child(2),
    .history-table th:nth-child(3) {{
      width: 13%;
    }}
    .history-table th:nth-child(4) {{
      width: 24%;
    }}
    .history-table th:nth-child(5) {{
      width: 36%;
    }}
    .history-table .history-empty {{
      width: auto;
      text-align: center;
      color: #627d98;
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
    .back-to-top {{
      margin: 12px 0 0;
      font-size: 0.9rem;
      text-align: right;
    }}
    .back-to-top a {{
      color: #3e7cb1;
      text-decoration: none;
    }}
    .back-to-top a:hover {{
      text-decoration: underline;
    }}
    @media (max-width: 900px) {{
      .engagement-summary {{
        grid-template-columns: repeat(2, minmax(0, 1fr));
      }}
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
      .engagement-summary {{
        grid-template-columns: 1fr;
        gap: 10px;
      }}
      .engagement-title,
      .latest-action-summary {{
        grid-column: auto;
        grid-row: auto;
      }}
    }}
  </style>
</head>
<body>
  <a id="top"></a>
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
      <h2>Project Performance</h2>
      {_render_project_performance(dashboard_metrics.project_performance)}
      {_BACK_TO_TOP_LINK}
    </section>

    <section>
      <h2>Contribution Breakdown</h2>
      {_render_contribution_breakdown(dashboard_metrics.contribution_breakdown)}
      {_BACK_TO_TOP_LINK}
    </section>

    <section>
      <h2>Outstanding Actions</h2>
      {_render_outstanding_actions(dashboard_metrics.outstanding_actions)}
      {_BACK_TO_TOP_LINK}
    </section>

    <section>
      <h2>Engagement Review</h2>
      {_render_engagement_reviews(dashboard_metrics.engagement_reviews)}
    </section>

  </main>
</body>
</html>
"""

    Path(output_path).write_text(html_document, encoding="utf-8")

    print("Dashboard generated successfully.")
