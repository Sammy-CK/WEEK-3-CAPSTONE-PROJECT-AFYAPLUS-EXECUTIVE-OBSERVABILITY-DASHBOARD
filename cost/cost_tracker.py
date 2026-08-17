import json
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class InferenceCost:
    request_id: str
    timestamp: str
    model: str
    feature: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cost_usd: float
    cost_ksh: float
    latency_ms: float
    success: bool


class CostTracker:
    def __init__(self, log_file: str):
        self.log_file = Path(log_file)
        self._session = []

    def record(self, record: InferenceCost):
        self._session.append(record)
        with open(self.log_file, "a") as f:
            f.write(json.dumps(asdict(record)) + "\n")

    def session_summary(self) -> dict:
        if not self._session:
            return {"requests": 0, "total_usd": 0.0}
        return {
            "requests": len(self._session),
            "total_usd": round(sum(r.cost_usd for r in self._session), 4),
        }
