import os
from pathlib import Path

import pandas as pd
from tabulate import tabulate

from evaluation_data import EVAL_DATASET, QUALITY_GATES
from evaluator import evaluate_response
from llm_judge import llm_judge
from model_querier import query_model

MODELS = ["gpt-4o-mini", "gpt-4o"]
OUTPUT_DIR = Path(__file__).parent


def check_quality_gate(row: dict) -> str:
    checks = [
        row["bleu_4"] >= QUALITY_GATES["bleu_4_min"],
        row["rouge_l"] >= QUALITY_GATES["rouge_l_min"],
        row["token_f1"] >= QUALITY_GATES["token_f1_min"],
        row["correctness"] >= QUALITY_GATES["correctness_min"],
        row["groundedness"] >= QUALITY_GATES["groundedness_min"],
        row["relevance"] >= QUALITY_GATES["relevance_min"],
        row["helpfulness"] >= QUALITY_GATES["helpfulness_min"],
        row["judge_overall"] >= QUALITY_GATES["judge_overall_min"],
    ]
    return "PASS" if all(checks) else "FAIL"


def run_full_evaluation():
    results = []
    for example in EVAL_DATASET:
        for model in MODELS:
            hypothesis = query_model(model, example["question"], example["reference"])
            auto_scores = evaluate_response(example["reference"], hypothesis)
            judge_scores = llm_judge(example["question"], example["reference"], hypothesis)

            row = {
                "id": example["id"],
                "channel": example["channel"],
                "feature": example["feature"],
                "model": model,
                "question": example["question"],
                "reference": example["reference"],
                "hypothesis": hypothesis,
                **auto_scores,
                "correctness": judge_scores.get("correctness", 0),
                "groundedness": judge_scores.get("groundedness", 0),
                "relevance": judge_scores.get("relevance", 0),
                "helpfulness": judge_scores.get("helpfulness", 0),
                "judge_overall": judge_scores.get("overall", 0),
                "reasoning": judge_scores.get("reasoning", ""),
            }
            row["quality_gate"] = check_quality_gate(row)
            results.append(row)
    return pd.DataFrame(results)


if __name__ == "__main__":
    df = run_full_evaluation()

    # Raw metrics log
    csv_path = OUTPUT_DIR / "full_evaluation_results.csv"
    df.to_csv(csv_path, index=False)
    print(f"Saved: {csv_path}")

    # Model comparison by feature
    feature_summary = df.groupby(["model", "feature"])[
        ["bleu_4", "rouge_l", "token_f1", "correctness", "groundedness", "relevance", "helpfulness", "judge_overall"]
    ].mean().round(3)
    feature_path = OUTPUT_DIR / "model_feature_summary.csv"
    feature_summary.to_csv(feature_path)
    print(f"Saved: {feature_path}")

    # Quality gate log
    gate_path = OUTPUT_DIR / "quality_gate_results.csv"
    df[["id", "model", "feature", "quality_gate", "rouge_l", "judge_overall", "groundedness"]].to_csv(gate_path, index=False)
    print(f"Saved: {gate_path}")

    # Console summary
    model_summary = df.groupby("model")[
        ["bleu_4", "rouge_l", "token_f1", "judge_overall"]
    ].mean().round(3)
    print("\n=== Model Comparison ===")
    print(tabulate(model_summary, headers="keys", tablefmt="grid"))

    pass_rate = df.groupby("model")["quality_gate"].apply(lambda x: (x == "PASS").mean()).round(3)
    print("\n=== Quality Gate Pass Rate ===")
    print(pass_rate.to_string())

    if not os.getenv("OPENAI_API_KEY"):
        print("\nNote: Running in offline demo mode (no OPENAI_API_KEY). Add key for live evaluation.")
