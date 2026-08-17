import os

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

load_dotenv()

SYSTEM_PROMPT = (
    "You are a clinical triage assistant for AfyaPlus Health in Kenya. "
    "Answer clearly in 2-4 sentences with specific clinical guidance."
)


def query_model(model_name: str, question: str, reference: str = "") -> str:
    if not os.getenv("OPENAI_API_KEY"):
        return _demo_response(model_name, reference or question)

    llm = ChatOpenAI(model=model_name, temperature=0, max_tokens=300)
    response = llm.invoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=question),
    ])
    return response.content


def _demo_response(model_name: str, reference: str) -> str:
    """Offline fallback when no API key — returns reference text so pipeline completes."""
    return reference
