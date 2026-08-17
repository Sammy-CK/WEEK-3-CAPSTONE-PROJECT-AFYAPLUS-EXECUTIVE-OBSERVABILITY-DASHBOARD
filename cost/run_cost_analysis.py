import json
import random
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

from cost_model import USD_TO_KSH, calculate_cost

random.seed(42)
np.random.seed(42)

OUTPUT_DIR = Path(__file__).parent

# Production-scale daily request volumes (75/25 mini/gpt-4o split applied in script)
FEATURES = {
    "triage_advisor": {"daily_requests": 8000, "avg_prompt_toks": 300, "avg_completion_toks": 180},
    "epidemic_alerts": {"daily_requests": 25000, "avg_prompt_toks": 250, "avg_completion_toks": 80},
    "clinical_summaries": {"daily_requests": 15000, "avg_prompt_toks": 200, "avg_completion_toks": 120},
}

MODEL_SPLIT = {"gpt-4o-mini": 0.75, "gpt-4o": 0.25}
DAILY_BUDGET_USD = 50.0
MONTHLY_BUDGET_USD = 1500.0


def simulate_30_days():
    records = []
    base = datetime(2026, 6, 1)

    for day in range(30):
        for feature, cfg in FEATURES.items():
            for model, share in MODEL_SPLIT.items():
                daily_n = int(cfg["daily_requests"] * share)
                p = max(50, int(np.random.normal(cfg["avg_prompt_toks"], 30)))
                c = max(20, int(np.random.normal(cfg["avg_completion_toks"], 20)))
                unit_cost = calculate_cost(model, p, c)
                records.append({
                    "day": day + 1,
                    "date": (base + timedelta(days=day)).date().isoformat(),
                    "feature": feature,
                    "model": model,
                    "requests": daily_n,
                    "prompt_tokens": p,
                    "completion_tokens": c,
                    "total_tokens": p + c,
                    "cost_usd": round(unit_cost * daily_n, 4),
                    "cost_ksh": round(unit_cost * daily_n * USD_TO_KSH, 4),
                    "latency_ms": round(np.random.normal(700 if "mini" in model else 1800, 120), 1),
                })
    return pd.DataFrame(records)


def main():
    df = simulate_30_days()
    log_path = OUTPUT_DIR / "inference_costs.jsonl"
    if log_path.exists():
        log_path.unlink()
    with open(log_path, "w") as f:
        for row in df.to_dict("records"):
            f.write(json.dumps(row) + "\n")

    # 30-day projection by model and feature
    projection = df.groupby(["model", "feature"]).agg(
        total_requests=("requests", "sum"),
        total_cost_usd=("cost_usd", "sum"),
    ).round(4)
    projection["avg_cost_per_request_usd"] = (
        projection["total_cost_usd"] / projection["total_requests"]
    ).round(8)
    projection.to_csv(OUTPUT_DIR / "30_day_cost_projection.csv")
    print("Saved: 30_day_cost_projection.csv")

    # Cost per request comparison
    totals = df.groupby("model").agg(
        requests=("requests", "sum"),
        total_cost_usd=("cost_usd", "sum"),
        avg_latency_ms=("latency_ms", "mean"),
        avg_tokens=("total_tokens", "mean"),
    )
    totals["avg_cost_usd"] = (totals["total_cost_usd"] / totals["requests"]).round(8)
    totals.drop(columns=["total_cost_usd"]).round(6).to_csv(OUTPUT_DIR / "cost_per_request_comparison.csv")
    print("Saved: cost_per_request_comparison.csv")

    # Savings analysis — route all eligible traffic to mini if quality gate passes
    all_gpt4o = df[df["model"] == "gpt-4o"]["cost_usd"].sum()
    all_mini = df[df["model"] == "gpt-4o-mini"]["cost_usd"].sum()
    current_total = df["cost_usd"].sum()
    optimized_total = all_mini + (all_gpt4o * 0.10)  # keep 10% gpt-4o for high-risk only

    savings = pd.DataFrame([
        {
            "scenario": "current_75_25_split",
            "monthly_cost_usd": round(current_total, 2),
        },
        {
            "scenario": "optimized_routing_to_mini",
            "monthly_cost_usd": round(optimized_total, 2),
        },
        {
            "scenario": "estimated_savings_usd",
            "monthly_cost_usd": round(current_total - optimized_total, 2),
        },
        {
            "scenario": "estimated_savings_pct",
            "monthly_cost_usd": round((current_total - optimized_total) / current_total * 100, 2),
        },
    ])
    savings.to_csv(OUTPUT_DIR / "savings_analysis.csv", index=False)
    print("Saved: savings_analysis.csv")

    # Budget summary for dashboard
    daily_spend = df.groupby("day")["cost_usd"].sum().mean()
    budget_summary = {
        "daily_spend_usd": round(daily_spend, 2),
        "daily_cap_usd": DAILY_BUDGET_USD,
        "monthly_spend_usd": round(df["cost_usd"].sum(), 2),
        "monthly_cap_usd": MONTHLY_BUDGET_USD,
        "daily_utilisation_pct": round(daily_spend / DAILY_BUDGET_USD * 100, 1),
        "monthly_utilisation_pct": round(df["cost_usd"].sum() / MONTHLY_BUDGET_USD * 100, 1),
    }
    with open(OUTPUT_DIR / "budget_summary.json", "w") as f:
        json.dump(budget_summary, f, indent=2)
    print("Saved: budget_summary.json")


if __name__ == "__main__":
    main()
