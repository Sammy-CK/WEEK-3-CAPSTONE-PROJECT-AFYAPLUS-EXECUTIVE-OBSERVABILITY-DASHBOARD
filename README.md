# AfyaPlus Executive Observability Dashboard

Week 3 capstone — clinical evaluation, drift detection, cost tracking, and a FastAPI monitoring dashboard for AfyaPlus generative AI.

## What this project does

| Phase | Folder | Output |
|-------|--------|--------|
| 1 — Evaluation | `evaluation/` | BLEU, ROUGE, F1, LLM judge, quality gates |
| 2 — Drift | `drift/` | 3 monthly HTML reports, trend CSV, alert log |
| 3 — Cost | `cost/` | 30-day projections, savings analysis |
| 4 — Dashboard | `dashboard/` | FastAPI web console + Prometheus `/metrics` |
| 5 — Summary | root | `executive_summary.pdf` |

## Setup

Use your existing **`venv-ai`** from the AI workspace folder:

```powershell
cd "Desktop\WORK\AI"
venv-ai\Scripts\activate

cd Projects\WEEK-3-CAPSTONE-PROJECT-AFYAPLUS-EXECUTIVE-OBSERVABILITY-DASHBOARD
pip install -r requirements.txt
```

Optional — add your OpenAI key for live model evaluation:

```powershell
copy .env.example .env
# Edit .env and set OPENAI_API_KEY=sk-...
```

> **NLTK note:** `evaluator.py` auto-downloads `punkt` / `punkt_tab` tokenizers on first run. No manual step needed unless your network blocks downloads.

## Run everything (one command)

From the project root with `venv-ai` activated:

```powershell
python run_all.py
```

Then start the dashboard:

```powershell
uvicorn dashboard.app:app --reload --port 8000
```

- Dashboard: http://127.0.0.1:8000  
- Prometheus metrics: http://127.0.0.1:8000/metrics  
- Health check: http://127.0.0.1:8000/health  

## Run phases individually

```powershell
python evaluation/run_full_evaluation.py
python drift/simulate_monthly_data.py
python drift/run_drift_reports.py
python cost/run_cost_analysis.py
python generate_executive_summary.py
uvicorn dashboard.app:app --reload --port 8000
```

## Project structure

```
evaluation/
  evaluation_data.py          15 clinical questions
  evaluator.py                BLEU, ROUGE, Token F1
  llm_judge.py                LLM-as-a-Judge
  model_querier.py            gpt-4o-mini + gpt-4o
  run_full_evaluation.py
  full_evaluation_results.csv
  model_feature_summary.csv
  quality_gate_results.csv

drift/
  simulate_monthly_data.py
  run_drift_reports.py
  month1_drift_report.html
  month2_drift_report.html
  month3_drift_report.html
  drift_trend_table.csv
  drift_alerts.json

cost/
  cost_model.py
  cost_tracker.py
  run_cost_analysis.py
  30_day_cost_projection.csv
  cost_per_request_comparison.csv
  savings_analysis.csv
  budget_summary.json

dashboard/
  app.py

executive_summary.pdf
run_all.py
```

## Quality gates

| Metric | Minimum |
|--------|---------|
| BLEU-4 | 0.10 |
| ROUGE-L | 0.25 |
| Token F1 | 0.30 |
| LLM Judge (all dims) | 3.0 |

## Notes

- **No API key?** Evaluation runs in offline demo mode and still produces all CSV outputs.
- **Evidently:** Drift reports use Evidently AI (same as Week 3 lab).
- **Dependencies:** `numpy<2.0` and `pydantic>=2.7` are pinned so FastAPI and Evidently work together.
