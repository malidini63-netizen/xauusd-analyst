# storage.py — historique des Plans d'Exécution
import json
import os
from datetime import datetime, timezone

HISTORY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pe_history.json")


def load_history() -> list:
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_pe(price: float, htf_bias: dict, pe: dict) -> bool:
    history = load_history()
    sp = pe.get("scenario_principal", {})

    entry = {
        "timestamp":   datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "price":       price,
        "bias":        htf_bias.get("bias", "N/A"),
        "score":       htf_bias.get("score", 0),
        "direction":   sp.get("direction", "N/A"),
        "entree":      sp.get("entree_zone", "N/A"),
        "sl":          sp.get("sl", "N/A"),
        "tp1":         sp.get("tp1", "N/A"),
        "tp2":         sp.get("tp2", "N/A"),
        "rr":          sp.get("rr", "N/A"),
        "timing":      sp.get("timing", "N/A"),
        "invalidation": pe.get("invalidation", "N/A"),
        "risque":      pe.get("risque", "N/A"),
        "resume":      pe.get("resume_marche", ""),
        "niveaux":     pe.get("niveaux_cles", [])
    }

    history.append(entry)

    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Erreur sauvegarde PE : {e}")
        return False


def get_last_pe(n: int = 10) -> list:
    return load_history()[-n:]


def clear_history() -> bool:
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)
        return True
    except Exception:
        return False