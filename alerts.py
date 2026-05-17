# alerts.py — notifications Telegram
import requests
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID


def send_telegram(message: str) -> bool:
    """Envoie un message Telegram"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram non configuré.")
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id":    TELEGRAM_CHAT_ID,
        "text":       message,
        "parse_mode": "Markdown"
    }

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"Erreur Telegram : {e}")
        return False


def format_pe_alert(price: float, htf_bias: dict, pe: dict) -> str:
    """Formate le Plan d'Exécution pour Telegram"""

    bias    = pe.get("biais_global", "N/A")
    resume  = pe.get("resume_marche", "")
    sp      = pe.get("scenario_principal", {})
    sa      = pe.get("scenario_alternatif", {})
    inv     = pe.get("invalidation", "")
    niveaux = pe.get("niveaux_cles", [])
    risque  = pe.get("risque", "N/A")

    emoji = "📈" if "HAUSSIER" in bias else "📉" if "BAISSIER" in bias else "➡️"

    niveaux_text = "\n".join([f"  • {n}" for n in niveaux]) if niveaux else "N/A"

    message = f"""🥇 *XAUUSD — Plan d'Exécution*
💰 Prix actuel : *{price}*
{emoji} Biais global : *{bias}*

📋 *Résumé marché :*
{resume}

🎯 *Scénario Principal :*
  Direction : *{sp.get('direction', 'N/A')}*
  Zone d'entrée : `{sp.get('entree_zone', 'N/A')}`
  Type : _{sp.get('entree_type', 'N/A')}_
  SL : `{sp.get('sl', 'N/A')}`
  TP1 : `{sp.get('tp1', 'N/A')}`
  TP2 : `{sp.get('tp2', 'N/A')}`
  R/R : *{sp.get('rr', 'N/A')}*
  ⏰ Timing : _{sp.get('timing', 'N/A')}_

🔄 *Scénario Alternatif :*
  _{sa.get('condition', 'N/A')}_
  Zone : `{sa.get('zone', 'N/A')}`

🚫 *Invalidation :* `{inv}`

📊 *Niveaux clés :*
{niveaux_text}

⚠️ *Risque :* {risque}
💬 _{pe.get('patience', '')}_"""

    return message