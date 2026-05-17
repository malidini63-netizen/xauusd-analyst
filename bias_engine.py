# bias_engine.py — calcul du biais multi-timeframe ICT/SMC
from structure import detect_market_structure
from levels import get_all_levels


def analyze_timeframe(df, tf_name: str) -> dict:
    """Analyse complète d'un timeframe"""
    if df is None or df.empty:
        return {"tf": tf_name, "trend": "N/A", "error": True}

    structure = detect_market_structure(df)
    levels    = get_all_levels(df)
    price     = float(df["close"].iloc[-1])

    # Proximité OB
    nearest_bull_ob = None
    nearest_bear_ob = None

    for ob in levels.get("bullish_ob", []):
        if ob["bottom"] <= price <= ob["top"] * 1.002:
            nearest_bull_ob = ob

    for ob in levels.get("bearish_ob", []):
        if ob["bottom"] * 0.998 <= price <= ob["top"]:
            nearest_bear_ob = ob

    # Proximité FVG
    nearest_bull_fvg = None
    nearest_bear_fvg = None

    for fvg in levels.get("bullish_fvg", []):
        if fvg["bottom"] <= price <= fvg["top"]:
            nearest_bull_fvg = fvg

    for fvg in levels.get("bearish_fvg", []):
        if fvg["bottom"] <= price <= fvg["top"]:
            nearest_bear_fvg = fvg

    # Liquidité proche
    bsl_above = [b for b in levels.get("bsl", []) if b["level"] > price]
    ssl_below  = [s for s in levels.get("ssl", []) if s["level"] < price]

    nearest_bsl = min(bsl_above, key=lambda x: x["level"]) if bsl_above else None
    nearest_ssl = max(ssl_below, key=lambda x: x["level"]) if ssl_below else None

    return {
        "tf":             tf_name,
        "price":          round(price, 2),
        "trend":          structure["trend"],
        "bos":            structure["last_bos"],
        "choch":          structure["last_choch"],
        "hh_hl":          structure["hh_hl"],
        "lh_ll":          structure["lh_ll"],
        "bullish_ob":     levels["bullish_ob"][-1] if levels["bullish_ob"] else None,
        "bearish_ob":     levels["bearish_ob"][-1] if levels["bearish_ob"] else None,
        "bullish_fvg":    levels["bullish_fvg"][-1] if levels["bullish_fvg"] else None,
        "bearish_fvg":    levels["bearish_fvg"][-1] if levels["bearish_fvg"] else None,
        "nearest_bull_ob": nearest_bull_ob,
        "nearest_bear_ob": nearest_bear_ob,
        "nearest_bull_fvg": nearest_bull_fvg,
        "nearest_bear_fvg": nearest_bear_fvg,
        "nearest_bsl":    nearest_bsl,
        "nearest_ssl":    nearest_ssl,
        "swing_highs":    structure["swing_highs"],
        "swing_lows":     structure["swing_lows"],
    }


def compute_htf_bias(analyses: dict) -> dict:
    """Calcule le biais global HTF → LTF"""

    score = 0
    details = []

    # Poids par timeframe
    weights = {"H4": 3, "H1": 2, "M15": 1, "M5": 0.5}

    for tf, analysis in analyses.items():
        if analysis.get("error"):
            continue

        w = weights.get(tf, 1)
        trend = analysis.get("trend", "")

        if trend == "HAUSSIER":
            score += w
            details.append(f"✅ {tf} : structure HAUSSIÈRE (+{w})")
        elif trend == "BAISSIER":
            score -= w
            details.append(f"🔴 {tf} : structure BAISSIÈRE (-{w})")
        else:
            details.append(f"⚪ {tf} : {trend} (0)")

        # Bonus CHoCH
        if analysis.get("choch"):
            choch = analysis["choch"]
            if choch["type"] == "HAUSSIER":
                score += 0.5
                details.append(f"  ↗️ CHoCH haussier détecté sur {tf}")
            else:
                score -= 0.5
                details.append(f"  ↘️ CHoCH baissier détecté sur {tf}")

    # Biais final
    if score >= 4:
        bias = "HAUSSIER FORT"
        emoji = "📈📈"
    elif score >= 1.5:
        bias = "HAUSSIER"
        emoji = "📈"
    elif score <= -4:
        bias = "BAISSIER FORT"
        emoji = "📉📉"
    elif score <= -1.5:
        bias = "BAISSIER"
        emoji = "📉"
    else:
        bias = "NEUTRE"
        emoji = "➡️"

    return {
        "score":   round(score, 2),
        "bias":    bias,
        "emoji":   emoji,
        "details": details
    }