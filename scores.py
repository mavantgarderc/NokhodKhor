import json
import os
from typing import Dict

from config import DIFFICULTIES

SCORES_FILE = "scores.json"
DEFAULT_SCORES: Dict[str, int] = {name: 0 for name in DIFFICULTIES.keys()}


def load_high_scores() -> Dict[str, int]:

    if not os.path.exists(SCORES_FILE):
        return DEFAULT_SCORES.copy()
    try:
        with open(SCORES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        scores = DEFAULT_SCORES.copy()
        for key, value in data.items():
            if key in scores and isinstance(value, int):
                scores[key] = value
        return scores
    except Exception:

        return DEFAULT_SCORES.copy()


def save_high_scores(scores: Dict[str, int]) -> None:

    try:
        with open(SCORES_FILE, "w", encoding="utf-8") as f:
            json.dump(scores, f, indent=2)
    except Exception:
        pass


def get_high_score(scores: Dict[str, int], difficulty: str) -> int:

    return scores.get(difficulty, 0)


def maybe_update_high_score(
    scores: Dict[str, int], difficulty: str, score: int
) -> bool:

    prev = scores.get(difficulty, 0)
    if score > prev:
        scores[difficulty] = score
        return True
    return False
