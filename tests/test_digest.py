# -*- coding: utf-8 -*-
"""Haftalik dayjest testlari — matn, kadans, yuborish xatolari, qisqartirish."""
import json
import os
import sys
from datetime import datetime, timedelta

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE)

from src import digest as DG  # noqa: E402


def fake_data(f1=0.5384, fpr=0.0861, decision="THRESHOLDNI QAYTA KALIBRLASH tavsiya etiladi",
              drifted=(), watch=("drift_slope",), trend=None):
    trend = trend or [{"quarter": "2025Q3", "fpr": 0.059, "n": 2300, "positives": 519, "alerts": 279},
                      {"quarter": "2026Q1", "fpr": 0.1258, "n": 2300, "positives": 440, "alerts": 526}]
    return {
        "metrics": {"f1": f1, "precision": 0.5896, "recall": 0.4954, "fpr": fpr, "roc_auc": 0.7888,
                    "tp": 257, "fp": 411},
        "model": {"params": {"n_estimators": 600, "max_samples": 0.5, "contamination": 0.12,
                             "random_state": 42}, "rule_version": "1.0"},
        "monitor": {"verdict": {"action": decision, "drifted": list(drifted), "watch": list(watch),
                                "reason": ["FPR chegaradan (0,10) oshgan davrlar: 2026Q1",
                                           "Model qayta o'qitilmaydi — threshold yangi train davridan"]},
                    "trend": trend},
    }


# ---------- 1. matn ----------
def test_message_contains_key_numbers():
    t = DG.build_message(fake_data(), datetime(2026, 9, 30))
    assert "0.5384" in t and "0.0861" in t and "0.7888" in t
    assert "2026-09-30" in t and "IsolationForest" in t and "n=600" in t


def test_message_marks_fpr_violation_quarter():
    t = DG.build_message(fake_data(), datetime(2026, 9, 30))
    assert "2026Q1 (0.126)" in t


def test_message_no_violation_message():
    trend = [{"quarter": "2025Q3", "fpr": 0.05, "n": 10, "positives": 2, "alerts": 3}]
    t = DG.build_message(fake_data(fpr=0.05, decision="STABIL — joriy model bilan davom", trend=trend),
                         datetime(2026, 9, 30))
    assert "yo'q ✅" in t and "STABIL" in t


def test_message_contains_next_report_date():
    t = DG.build_message(fake_data(), datetime(2026, 9, 30))
    assert "2026-10-07" in t


def test_message_has_no_forbidden_words():
    """Anti-da'vo: dayjest ayblamaydi va tavsiya bermaydi (faqat texnik qaror)."""
    t = DG.build_message(fake_data(), datetime(2026, 9, 30)).lower()
    for bad in ["ayblanadi", "aybdor", "jarima", "zavodni yopish", "fosh"]:
        assert bad not in t


def test_message_truncated_to_telegram_limit():
    long_reason = ["x" * 5000]
    d = fake_data()
    d["monitor"]["verdict"]["reason"] = long_reason
    t = DG.build_message(d, datetime(2026, 9, 30))
    assert len(t) <= DG.TELEGRAM_LIMIT
    assert "qisqartirildi" in t


# ---------- 2. kadans ----------
def test_should_send_first_time():
    assert DG.should_send({}, datetime(2026, 9, 30)) is True


def test_should_send_respects_period():
    now = datetime(2026, 9, 30, 9, 0)
    assert DG.should_send({"last_sent": (now - timedelta(days=3)).isoformat()}, now) is False
    assert DG.should_send({"last_sent": (now - timedelta(days=6, hours=23)).isoformat()}, now) is False
    assert DG.should_send({"last_sent": (now - timedelta(days=7)).isoformat()}, now) is True
    assert DG.should_send({"last_sent": (now - timedelta(days=30)).isoformat()}, now) is True


def test_should_send_handles_corrupt_state():
    assert DG.should_send({"last_sent": "buzilgan-sana"}, datetime(2026, 9, 30)) is True


def test_load_state_missing_file(tmp_path):
    assert DG.load_state(str(tmp_path / "yoq.json")) == {}


# ---------- 3. yuborish ----------
def test_send_telegram_reports_error(monkeypatch):
    class Boom:
        def __init__(self, *a, **k):
            raise OSError("tarmoq yo'q")

    monkeypatch.setattr(DG.urllib.request, "urlopen", Boom)
    res = DG.send_telegram("salom", "TOKEN", [111, 222])
    assert len(res) == 2 and all(not r["ok"] for r in res)
    assert "tarmoq" in res[0]["error"]


def test_run_dry_run_makes_no_state(tmp_path):
    """dry-run: kadansdan mustaqil matn qaytadi, state fayli o'zgarmaydi."""
    p = os.path.join(BASE, "reports", "digest_state.json")
    before = open(p, encoding="utf-8").read() if os.path.exists(p) else None
    res = DG.run(BASE, token="", chat_ids=[], dry_run=True)
    after = open(p, encoding="utf-8").read() if os.path.exists(p) else None
    assert res["sent"] is False and "preview" in res and "HAFTALIK" in res["preview"]
    assert before == after, "dry-run state faylini o'zgartirdi"


def test_run_skips_within_period(tmp_path):
    state = {"last_sent": datetime.now().isoformat(timespec="seconds")}
    p = os.path.join(BASE, "reports", "digest_state.json")
    old = open(p, encoding="utf-8").read() if os.path.exists(p) else None
    try:
        with open(p, "w", encoding="utf-8") as f:
            json.dump(state, f)
        res = DG.run(BASE, force=False)
        assert res["sent"] is False and "hafta to'lmagan" in res["reason"]
    finally:
        if old is not None:
            open(p, "w", encoding="utf-8").write(old)
        elif os.path.exists(p):
            os.remove(p)
