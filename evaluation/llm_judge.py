import json
import os
import re

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

load_dotenv()

JUDGE_SYSTEM_PROMPT = """
You are an expert medical AI evaluation assistant for AfyaPlus.
Score the AI response from 1 to 5 on:
1. CORRECTNESS
2. GROUNDEDNESS
3. RELEVANCE
4. HELPFULNESS

Respond ONLY with valid JSON:
{
  "correctness": <1-5>,
  "groundedness": <1-5>,
  "relevance": <1-5>,
  "helpfulness": <1-5>,
  "overall": <average rounded to 1 decimal>,
  "reasoning": "<2-3 sentences>"
}
"""


def llm_judge(question: str, reference: str, hypothesis: str, judge_model: str = "gpt-4o") -> dict:
    if not os.getenv("OPENAI_API_KEY"):
        return _demo_judge(reference, hypothesis)

    judge_llm = ChatOpenAI(model=judge_model, temperature=0, max_tokens=400)
    user_prompt = f"""
USER QUERY: {question}
REFERENCE: {reference}
AI RESPONSE: {hypothesis}
"""
    response = judge_llm.invoke([
        SystemMessage(content=JUDGE_SYSTEM_PROMPT),
        HumanMessage(content=user_prompt),
    ])
    raw = response.content.strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            return json.loads(match.group())
    return {
        "correctness": 0, "groundedness": 0, "relevance": 0,
        "helpfulness": 0, "overall": 0, "reasoning": "JSON parse failure",
    }


def _demo_judge(reference: str, hypothesis: str) -> dict:
    """Offline fallback when no API key — rough heuristic from overlap."""
    from evaluator import compute_token_f1

    f1 = compute_token_f1(reference, hypothesis)
    score = max(1, min(5, round(f1 * 5, 1)))
    return {
        "correctness": score,
        "groundedness": score,
        "relevance": score,
        "helpfulness": score,
        "overall": score,
        "reasoning": "Demo judge score derived from token overlap (offline mode).",
    }
