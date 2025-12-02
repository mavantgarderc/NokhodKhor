import os
import tempfile

import nokhodkhor.scores as scores
from nokhodkhor.config import DIFFICULTIES


def test_load_default_high_scores_without_file(tmp_path):
    orig_file = scores.SCORES_FILE
    tmp_file = tmp_path / "scores_test.json"
    scores.SCORES_FILE = str(tmp_file)

    try:
        if tmp_file.exists():
            tmp_file.unlink()
        hs = scores.load_high_scores()
        assert set(hs.keys()) == set(DIFFICULTIES.keys())
        assert all(v == 0 for v in hs.values())
    finally:
        scores.SCORES_FILE = orig_file


def test_save_and_load_high_scores(tmp_path):
    orig_file = scores.SCORES_FILE
    tmp_file = tmp_path / "scores_test.json"
    scores.SCORES_FILE = str(tmp_file)

    try:
        data = {name: (idx + 1) * 100 for idx, name in enumerate(DIFFICULTIES.keys())}
        scores.save_high_scores(data)
        loaded = scores.load_high_scores()
        assert loaded == data
    finally:
        scores.SCORES_FILE = orig_file


def test_maybe_update_high_score_logic():
    hs = {name: 1000 for name in DIFFICULTIES.keys()}
    diff = next(iter(DIFFICULTIES.keys()))

    changed = scores.maybe_update_high_score(hs, diff, 900)
    assert changed is False
    assert hs[diff] == 1000

    changed = scores.maybe_update_high_score(hs, diff, 1000)
    assert changed is False
    assert hs[diff] == 1000

    changed = scores.maybe_update_high_score(hs, diff, 1500)
    assert changed is True
    assert hs[diff] == 1500
