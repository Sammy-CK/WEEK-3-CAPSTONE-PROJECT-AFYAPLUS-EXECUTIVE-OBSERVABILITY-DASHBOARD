"""Generate executive_summary.pdf from Phase 1-4 outputs."""
import json
from pathlib import Path

import pandas as pd
from fpdf import FPDF, XPos, YPos

ROOT = Path(__file__).parent


def safe_mean(df, col):
    if df.empty or col not in df.columns:
        return 0.0
    return round(df[col].mean(), 3)


def main():
    eval_df = pd.read_csv(ROOT / "evaluation" / "full_evaluation_results.csv")
    gate_df = pd.read_csv(ROOT / "evaluation" / "quality_gate_results.csv")
    drift_df = pd.read_csv(ROOT / "drift" / "drift_trend_table.csv")
    drift_alerts = json.loads((ROOT / "drift" / "drift_alerts.json").read_text())
    savings_df = pd.read_csv(ROOT / "cost" / "savings_analysis.csv")
    budget = json.loads((ROOT / "cost" / "budget_summary.json").read_text())

    mini = eval_df[eval_df["model"] == "gpt-4o-mini"]
    gpt4o = eval_df[eval_df["model"] == "gpt-4o"]
    mini_pass = (gate_df[gate_df["model"] == "gpt-4o-mini"]["quality_gate"] == "PASS").mean()
    gpt4o_pass = (gate_df[gate_df["model"] == "gpt-4o"]["quality_gate"] == "PASS").mean()
    mini_judge_pass = (mini["judge_overall"] >= 3.0).mean()
    gpt4o_judge_pass = (gpt4o["judge_overall"] >= 3.0).mean()

    m1_rouge = drift_df[drift_df["month"] == 1]["rouge_l_mean"].iloc[0]
    m3_rouge = drift_df[drift_df["month"] == 3]["rouge_l_mean"].iloc[0]
    savings_usd = savings_df[savings_df["scenario"] == "estimated_savings_usd"]["monthly_cost_usd"].iloc[0]

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=12)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 8, "AfyaPlus Generative AI Observability - Executive Summary", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(0, 6, "To: CTO and Medical Director | From: Applied AI Engineering Team", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(4)

    sections = [
        (
            "Executive Summary",
            f"AfyaPlus clinical AI ran six weeks without automated evaluation. This week we deployed "
            f"evaluation, drift monitoring, and cost tracking. gpt-4o-mini averaged ROUGE-L {safe_mean(mini, 'rouge_l')} "
            f"vs gpt-4o {safe_mean(gpt4o, 'rouge_l')}. Monthly spend reached ${budget['monthly_spend_usd']:.0f} "
            f"({budget['monthly_utilisation_pct']:.0f}% of cap).",
        ),
        (
            "Quality Performance Breakdown",
            f"Across 15 clinical questions, automated gate pass rate is {mini_pass*100:.0f}% (mini) and "
            f"{gpt4o_pass*100:.0f}% (gpt-4o) due to BLEU/ROUGE formatting gaps. LLM judge safety scores "
            f"are stronger: mini {safe_mean(mini, 'judge_overall')} ({mini_judge_pass*100:.0f}% above 3.0 threshold), "
            f"gpt-4o {safe_mean(gpt4o, 'judge_overall')} ({gpt4o_judge_pass*100:.0f}% above 3.0). "
            f"Triage judge groundedness averaged {safe_mean(mini, 'groundedness')} (mini).",
        ),
        (
            "Cost and Efficiency Analysis",
            f"30-day projected spend: ${budget['monthly_spend_usd']:.0f} at 75/25 mini/gpt-4o split. "
            f"Routing low-acuity traffic to mini where judge scores clear the 3.0 safety bar saves "
            f"${savings_usd:.0f}/month. Human-in-the-loop review costs ~$12 per case vs ~$0.002 per automated inference.",
        ),
        (
            "Systemic Operational Risks",
            f"ROUGE-L drifted from {m1_rouge} (Month 1) to {m3_rouge} (Month 3). "
            f"First alert: Month {drift_alerts.get('first_drift_month')} column "
            f"{drift_alerts.get('first_drift_column')}. Latency rose to "
            f"{drift_df[drift_df['month']==3]['latency_ms_mean'].iloc[0]:.0f}ms avg - hallucination risk "
            f"increases when quality scores drop below gate thresholds.",
        ),
        (
            "Actionable Engineering Roadmap",
            "1) Route USSD and Mobile App triage to gpt-4o-mini (saves ~${:.0f}/mo; judge scores avg {:.1f}). "
            "2) Deploy monthly Evidently drift alerts to Slack when ROUGE-L drops >10%. "
            "3) Reserve gpt-4o for Web Portal high-acuity cases only.".format(
                savings_usd, safe_mean(mini, "judge_overall")
            ),
        ),
    ]

    for title, body in sections:
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 6, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font("Helvetica", "", 9)
        pdf.multi_cell(0, 5, body)
        pdf.ln(2)

    out = ROOT / "executive_summary.pdf"
    pdf.output(str(out))
    print(f"Saved: {out}")


if __name__ == "__main__":
    main()
