import random
from pathlib import Path

import numpy as np
import pandas as pd

random.seed(42)
np.random.seed(42)

OUTPUT_DIR = Path(__file__).parent

BASE_QUESTIONS = [
    "What documents do I need for a standard clinical lab screening?",
    "How long does it take to process outpatient laboratory results?",
    "Can I book an inpatient clinical appointment online?",
]

NEW_QUESTIONS = [
    "My infant has a sudden rash and high fever - what are my triage options?",
    "Has the new MoH policy changed our clinical referral rules?",
    "I need to restructure an emergency chronic care plan.",
]


def build_month(month: int, n: int = 200) -> pd.DataFrame:
    """Month 1 stable, Month 2 mild drift, Month 3 strong drift."""
    rows = []
    pool = BASE_QUESTIONS if month == 1 else BASE_QUESTIONS + NEW_QUESTIONS

    rouge_mean = {1: 0.42, 2: 0.36, 3: 0.30}[month]
    latency_mean = {1: 800, 2: 950, 3: 1100}[month]
    length_mean = {1: 8, 2: 10, 3: 12}[month]

    for _ in range(n):
        q = random.choice(pool)
        rows.append({
            "question": q,
            "input_length": max(3, int(np.random.normal(len(q.split()), length_mean / 4))),
            "rouge_l": round(max(0.05, np.random.normal(rouge_mean, 0.06)), 4),
            "latency_ms": round(max(200, np.random.normal(latency_mean, 120)), 0),
            "token_count": random.randint(150, 450),
        })
    return pd.DataFrame(rows)


def main():
    reference_df = build_month(1)
    reference_df.to_csv(OUTPUT_DIR / "reference_data.csv", index=False)

    for month in (1, 2, 3):
        df = build_month(month)
        df.to_csv(OUTPUT_DIR / f"month{month}_production.csv", index=False)

    print("Saved reference_data.csv and month1-3 production CSVs")


if __name__ == "__main__":
    main()
