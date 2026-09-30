# -*- coding: utf-8 -*-
"""Haftalik monitoring dayjesti — operatorga bot orqali.

Vazifa: L1 modelining holatini (sifat + dreyf + FPR trendi) haftada bir marta
operatorga qisqa, raqamlarga asoslangan xabar sifatida yuborish.

Tamoyillar:
  • Raqamlar faqat registrdan/artefaktdan (model metadata, monitor hisobi) — matn shablon.
  • Haftalik kadans — holat fayli (`reports/digest_state.json`) bilan; takroriy yuborish yo'q.
  • Telegram 4096 belgi chegarasi — xabar avtomatik qisqartiriladi (mazmun saqlanadi).
  • Yuborish muvaffaqiyatsiz bo'lsa — holat yozilmaydi, keyingi sikl qayta urinadi.
"""
from __future__ import annotations

import json
import os
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE)

from src import features as F          # noqa: E402
from src import monitor as MN          # noqa: E402
from src.evaluate import metrics_at    # noqa: E402
from src.models import score_if        # noqa: E402

TELEGRAM_LIMIT = 4000                  # 4096 dan xavfsiz zaxira bilan
PERIOD_DAYS = 7


def collect(base: str = BASE) -> dict:
    """Artefaktlardan ko'rsatkichlarni yig'adi (hisobotni qayta hisoblaydi — parse emas)."""
    import joblib

    data_path = os.path.join(base, "data", "features_v1.csv.gz")
    model_dir = os.path.join(base, "models")
    df = pd.read_csv(data_path)
    X, meta = F.feature_matrix(df)
    y = meta["label"].to_numpy()
    tr = (meta["q_index"] <= 17).to_numpy()
    te = ~tr

    meta_json = json.load(open(os.path.join(model_dir, "metadata.json"), encoding="utf-8"))
    model = joblib.load(os.path.join(model_dir, "if_v1.joblib"))
    s_te = score_if(model, X[te])
    met = metrics_at(y[te], s_te, meta_json["threshold_if"])

    mon = MN.run(data_path, model_dir, os.path.join(base, "reports"),
                 os.path.join(base, "reports", "figures"))
    return {"metrics": met, "model": meta_json, "monitor": mon}


def build_message(data: dict, now: datetime | None = None) -> str:
    now = now or datetime.now()
    m = data["metrics"]
    mon = data["monitor"]
    vd = mon["verdict"]
    trend = mon["trend"]
    params = data["model"]["params"]

    # ⚠️ belgilangan davrlar (chegaradan oshgan)
    bad = [t for t in trend if (t["fpr"] or 0) > 0.10]
    bad_txt = ", ".join(f"{t['quarter']} ({t['fpr']:.3f})" for t in bad) if bad else "yo'q ✅"

    n_dr = len(vd["drifted"])
    n_wa = len(vd["watch"])
    lines = [
        "📊 <b>HAFTALIK MONITORING — E-GAZ-AUDIT</b>",
        f"<i>{now.strftime('%Y-%m-%d')} · model: IsolationForest "
        f"(n={params['n_estimators']}, max_samples={params['max_samples']}) · rule {data['model']['rule_version']}</i>",
        "",
        "<b>Model sifati</b> (test 2025Q3–2026Q2):",
        f"• F1 {m['f1']} · Precision {m['precision']} · Recall {m['recall']}",
        f"• FPR {m['fpr']} {'✅ (AC-2: ≤0,10)' if m['fpr'] <= 0.10 else '❌ chegaradan oshgan'} · ROC-AUC {m['roc_auc']}",
        f"• Alertlar: {m['tp'] + m['fp']} (tekshiruvga tavsiya)",
        "",
        "<b>Dreyf (PSI/KS)</b>:\n"
        f"• 🔴 dreyf: {n_dr} · 🟡 kuzatuv: {n_wa} · 🟢 stabil: {len(F.FEATURES) - n_dr - n_wa - 1} · ⚪ vaqt: 1",
        f"<b>FPR trendi</b>: chegaradan oshgan davrlar — {bad_txt}",
        "",
        f"<b>Qaror:</b> {vd['action']}",
    ]
    for r in vd["reason"][:2]:
        lines.append(f"• {r}")
    lines += ["", f"<i>Keyingi hisobot: {(now + timedelta(days=PERIOD_DAYS)).strftime('%Y-%m-%d')} · "
                  f"to'liq: reports/monitor_report.md</i>"]

    text = "\n".join(lines)
    if len(text) > TELEGRAM_LIMIT:
        text = text[:TELEGRAM_LIMIT - 40].rstrip() + "\n<i>… (qisqartirildi)</i>"
    return text


def load_state(path: str) -> dict:
    try:
        return json.load(open(path, encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def should_send(state: dict, now: datetime, period_days: int = PERIOD_DAYS) -> bool:
    last = state.get("last_sent")
    if not last:
        return True
    try:
        last_dt = datetime.fromisoformat(last)
    except ValueError:
        return True
    return (now - last_dt) >= timedelta(days=period_days)


def send_telegram(text: str, token: str, chat_ids: list[int]) -> list[dict]:
    """Yuboradi; har chat uchun natija qaytaradi. Tarmoq xatosi — False (job yiqilmaydi)."""
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    out = []
    for chat in chat_ids:
        data = urllib.parse.urlencode({"chat_id": chat, "text": text, "parse_mode": "HTML"}).encode()
        try:
            with urllib.request.urlopen(url, data=data, timeout=20) as r:
                body = json.loads(r.read().decode())
                out.append({"chat_id": chat, "ok": bool(body.get("ok")),
                            "error": None if body.get("ok") else body.get("description")})
        except Exception as e:                       # noqa: BLE001
            out.append({"chat_id": chat, "ok": False, "error": f"{type(e).__name__}: {str(e)[:100]}"})
    return out


def run(base: str = BASE, token: str = "", chat_ids: list[int] | None = None,
        force: bool = False, dry_run: bool = False, now: datetime | None = None) -> dict:
    now = now or datetime.now()
    chat_ids = chat_ids or []
    state_path = os.path.join(base, "reports", "digest_state.json")
    state = load_state(state_path)

    # dry-run hech narsa yubormaydi — kadans tekshiruvi unga taalluqli emas (har doim ko'rsatiladi)
    if not force and not dry_run and not should_send(state, now):
        return {"sent": False, "reason": f"oxirgi yuborish: {state.get('last_sent')} (hafta to'lmagan)"}

    data = collect(base)
    text = build_message(data, now)

    if dry_run or not token or not chat_ids:
        return {"sent": False, "reason": "dry-run yoki token/chat yo'q", "preview": text, "data": data}

    results = send_telegram(text, token, chat_ids)
    ok = [r for r in results if r["ok"]]
    if ok:
        state.update({"last_sent": now.isoformat(timespec="seconds"),
                      "chats": [r["chat_id"] for r in ok],
                      "f1": data["metrics"]["f1"], "fpr": data["metrics"]["fpr"],
                      "decision": data["monitor"]["verdict"]["action"]})
        os.makedirs(os.path.dirname(state_path), exist_ok=True)
        json.dump(state, open(state_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    return {"sent": bool(ok), "results": results, "chars": len(text),
            "decision": data["monitor"]["verdict"]["action"]}


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Haftalik monitoring dayjesti")
    ap.add_argument("--force", action="store_true", help="kadansni chetlab o'tish (qo'lda yuborish)")
    ap.add_argument("--dry-run", action="store_true", help="yubormasdan matnni ko'rsatish")
    ap.add_argument("--preview", action="store_true", help="faqat matnni chop etish va chiqish")
    args = ap.parse_args()

    token = os.environ.get("ECO_BOT_TOKEN", "")
    chats = [int(x) for x in os.environ.get("ECO_ADMIN_CHAT_ID", "").replace(" ", "").split(",")
             if x.lstrip("-").isdigit()]

    if args.preview:
        d = collect(BASE)
        print(build_message(d))
        raise SystemExit(0)

    res = run(BASE, token=token, chat_ids=chats, force=args.force, dry_run=args.dry_run)
    if res.get("sent"):
        print(f"✅ Dayjest yuborildi ({res['chars']} belgi) · qaror: {res['decision']}")
        for r in res["results"]:
            print(f"   chat {r['chat_id']}: {'✅' if r['ok'] else '❌ ' + str(r['error'])}")
    else:
        print(f"ℹ️  Yuborilmadi: {res.get('reason')}")
        for r in res.get("results", []):
            print(f"   chat {r['chat_id']}: ❌ {r['error']}")
