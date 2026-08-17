import json
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, Response
from fastapi.responses import HTMLResponse
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, generate_latest

ROOT = Path(__file__).parent.parent
EVAL_DIR = ROOT / "evaluation"
DRIFT_DIR = ROOT / "drift"
COST_DIR = ROOT / "cost"

app = FastAPI(title="AfyaPlus Executive Observability Dashboard")

# Prometheus metrics
REQUEST_COUNT = Counter("afyaplus_dashboard_requests_total", "Dashboard page loads")
EXCEPTION_COUNT = Counter("afyaplus_llm_exceptions_total", "LLM exceptions")
SERVICE_UP = Gauge("afyaplus_service_up", "Service health (1=UP, 0=DOWN)")
QUALITY_SCORE = Gauge("afyaplus_feature_quality_score", "Feature quality score", ["feature", "model"])
BUDGET_UTIL = Gauge("afyaplus_budget_utilisation_pct", "Budget utilisation percent", ["period"])


def load_csv(path: Path) -> pd.DataFrame:
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()


def load_json(path: Path):
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {}


def update_prometheus():
    SERVICE_UP.set(1)

    quality_df = load_csv(EVAL_DIR / "model_feature_summary.csv")
    if not quality_df.empty:
        if isinstance(quality_df.index, pd.MultiIndex):
            for (model, feature), row in quality_df.iterrows():
                QUALITY_SCORE.labels(feature=feature, model=model).set(row.get("judge_overall", 0))
        else:
            for _, row in quality_df.iterrows():
                QUALITY_SCORE.labels(
                    feature=row.get("feature", "unknown"),
                    model=row.get("model", "unknown"),
                ).set(row.get("judge_overall", 0))

    budget = load_json(COST_DIR / "budget_summary.json")
    if budget:
        BUDGET_UTIL.labels(period="daily").set(budget.get("daily_utilisation_pct", 0))
        BUDGET_UTIL.labels(period="monthly").set(budget.get("monthly_utilisation_pct", 0))


@app.get("/", response_class=HTMLResponse)
def dashboard():
    REQUEST_COUNT.inc()
    update_prometheus()

    # System health
    service_status = "UP"
    exceptions = 0

    # Feature quality matrix
    quality_df = load_csv(EVAL_DIR / "model_feature_summary.csv")
    quality_html = "<p>No evaluation data yet. Run evaluation/run_full_evaluation.py</p>"
    if not quality_df.empty:
        quality_html = quality_df.reset_index().to_html(index=False, classes="table")

    gate_df = load_csv(EVAL_DIR / "quality_gate_results.csv")
    routing = {}
    if not gate_df.empty:
        for feature in gate_df["feature"].unique():
            mini_rows = gate_df[(gate_df["feature"] == feature) & (gate_df["model"] == "gpt-4o-mini")]
            pass_rate = (mini_rows["quality_gate"] == "PASS").mean() if len(mini_rows) else 0
            routing[feature] = "gpt-4o-mini" if pass_rate >= 0.5 else "gpt-4o"

    routing_html = "<ul>" + "".join(f"<li><b>{k}</b>: route to {v}</li>" for k, v in routing.items()) + "</ul>"

    # Drift status (current month = month 3)
    drift_trend = load_csv(DRIFT_DIR / "drift_trend_table.csv")
    drift_alerts = load_json(DRIFT_DIR / "drift_alerts.json")
    drift_html = "<p>No drift data yet. Run drift/run_drift_reports.py</p>"
    if not drift_trend.empty:
        current = drift_trend[drift_trend["month"] == 3]
        drift_html = current.to_html(index=False, classes="table")
        if drift_alerts.get("first_drift_column"):
            drift_html += (
                f"<p><b>Alert:</b> First drift in Month {drift_alerts['first_drift_month']} "
                f"on column <code>{drift_alerts['first_drift_column']}</code></p>"
            )

    # Budget
    budget = load_json(COST_DIR / "budget_summary.json")
    budget_html = "<p>No cost data yet. Run cost/run_cost_analysis.py</p>"
    if budget:
        daily_pct = budget.get("daily_utilisation_pct", 0)
        monthly_pct = budget.get("monthly_utilisation_pct", 0)
        budget_html = f"""
        <p>Daily spend: ${budget.get('daily_spend_usd', 0):,.2f} / ${budget.get('daily_cap_usd', 50):,.2f}</p>
        <div class="bar"><div class="fill" style="width:{min(daily_pct, 100)}%"></div></div>
        <p>{daily_pct}% of daily cap</p>
        <p>Monthly spend: ${budget.get('monthly_spend_usd', 0):,.2f} / ${budget.get('monthly_cap_usd', 1500):,.2f}</p>
        <div class="bar"><div class="fill" style="width:{min(monthly_pct, 100)}%"></div></div>
        <p>{monthly_pct}% of monthly cap</p>
        """

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>AfyaPlus Observability Dashboard</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 24px; background: #f5f7fa; }}
            h1 {{ color: #0d47a1; }}
            section {{ background: white; padding: 16px; margin-bottom: 20px; border-radius: 8px; box-shadow: 0 1px 4px rgba(0,0,0,0.1); }}
            .status-up {{ color: green; font-weight: bold; }}
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background: #e3f2fd; }}
            .bar {{ background: #eee; border-radius: 4px; height: 20px; width: 100%; max-width: 400px; }}
            .fill {{ background: #1976d2; height: 20px; border-radius: 4px; }}
        </style>
    </head>
    <body>
        <h1>AfyaPlus Executive Observability Dashboard</h1>

        <section>
            <h2>1. System Health</h2>
            <p>Service Status: <span class="status-up">{service_status}</span></p>
            <p>Exception Count: {exceptions}</p>
            <p>Prometheus metrics: <a href="/metrics">/metrics</a></p>
        </section>

        <section>
            <h2>2. Feature Quality Matrix</h2>
            {quality_html}
            <h3>Current Model Routing</h3>
            {routing_html}
        </section>

        <section>
            <h2>3. Drift Vector Status (Month 3)</h2>
            {drift_html}
        </section>

        <section>
            <h2>4. Budget Capital Utilisation</h2>
            {budget_html}
        </section>
    </body>
    </html>
    """
    return html


@app.get("/metrics")
def metrics():
    update_prometheus()
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/health")
def health():
    return {"status": "UP", "exceptions": 0}
