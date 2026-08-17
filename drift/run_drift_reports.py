import json
from pathlib import Path

import pandas as pd
from evidently.metrics import ColumnDriftMetric, DatasetDriftMetric
from evidently.report import Report

OUTPUT_DIR = Path(__file__).parent
TRACK_COLS = ["input_length", "rouge_l", "latency_ms", "token_count"]


def run_month_report(reference_df: pd.DataFrame, current_df: pd.DataFrame, month: int) -> list:
    metrics = [DatasetDriftMetric()] + [ColumnDriftMetric(column_name=c) for c in TRACK_COLS]
    report = Report(metrics=metrics)
    report.run(reference_data=reference_df, current_data=current_df)
    report.save_html(str(OUTPUT_DIR / f"month{month}_drift_report.html"))

    alerts = []
    for m in report.as_dict()["metrics"]:
        result = m.get("result", {})
        if "drift_detected" in result and result["drift_detected"]:
            alerts.append({
                "month": month,
                "column": result.get("column_name", "dataset"),
                "p_value": result.get("p_value"),
            })
    return alerts


def main():
    if not (OUTPUT_DIR / "reference_data.csv").exists():
        import subprocess
        import sys
        subprocess.run([sys.executable, str(OUTPUT_DIR / "simulate_monthly_data.py")], check=True)

    reference_df = pd.read_csv(OUTPUT_DIR / "reference_data.csv")
    trend_rows = []
    all_alerts = []
    first_drift = None

    for month in (1, 2, 3):
        current_df = pd.read_csv(OUTPUT_DIR / f"month{month}_production.csv")
        alerts = run_month_report(reference_df, current_df, month)

        trend_rows.append({
            "month": month,
            "rouge_l_mean": round(current_df["rouge_l"].mean(), 4),
            "latency_ms_mean": round(current_df["latency_ms"].mean(), 1),
            "input_length_mean": round(current_df["input_length"].mean(), 2),
            "drift_alert_count": len(alerts),
        })

        for alert in alerts:
            all_alerts.append(alert)
            if first_drift is None:
                first_drift = alert

    pd.DataFrame(trend_rows).to_csv(OUTPUT_DIR / "drift_trend_table.csv", index=False)
    print("Saved drift_trend_table.csv")

    alert_log = {
        "first_drift_month": first_drift["month"] if first_drift else None,
        "first_drift_column": first_drift["column"] if first_drift else None,
        "alerts": all_alerts,
    }
    with open(OUTPUT_DIR / "drift_alerts.json", "w") as f:
        json.dump(alert_log, f, indent=2)
    print("Saved drift_alerts.json")

    for month in (1, 2, 3):
        print(f"Saved: month{month}_drift_report.html")


if __name__ == "__main__":
    main()
