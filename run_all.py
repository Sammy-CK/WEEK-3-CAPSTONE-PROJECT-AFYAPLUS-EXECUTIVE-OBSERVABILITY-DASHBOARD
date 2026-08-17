"""Run all capstone phases in order. Usage: python run_all.py"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent

STEPS = [
    ("Phase 1 - Evaluation", ROOT / "evaluation" / "run_full_evaluation.py"),
    ("Phase 2a - Simulate drift data", ROOT / "drift" / "simulate_monthly_data.py"),
    ("Phase 2b - Drift reports", ROOT / "drift" / "run_drift_reports.py"),
    ("Phase 3 - Cost analysis", ROOT / "cost" / "run_cost_analysis.py"),
    ("Phase 5 - Executive summary PDF", ROOT / "generate_executive_summary.py"),
]


def main():
    print("AfyaPlus Capstone - running all phases\n")
    for label, script in STEPS:
        print(f"=== {label} ===")
        result = subprocess.run([sys.executable, str(script)], cwd=ROOT)
        if result.returncode != 0:
            print(f"\nFAILED: {script.name} (exit {result.returncode})")
            sys.exit(result.returncode)
        print()

    print("All phases complete.")
    print("Start dashboard: uvicorn dashboard.app:app --reload --port 8000")


if __name__ == "__main__":
    main()
