# structure.py — détection de la structure de marché ICT/SMC
import pandas as pd
import numpy as np


def find_swing_points(df: pd.DataFrame, window: int = 5) -> pd.DataFrame:
    """Détecte les swing highs et swing lows"""
    df = df.copy()
    df["swing_high"] = False
    df["swing_low"] = False

    for i in range(window, len(df) - window):
        # Swing High : bougie la plus haute sur la fenêtre
        if df["high"].iloc[i] == df["high"].iloc[i-window:i+window+1].max():
            df.at[i, "swing_high"] = True
        # Swing Low : bougie la plus basse sur la fenêtre
        if df["low"].iloc[i] == df["low"].iloc[i-window:i+window+1].min():
            df.at[i, "swing_low"] = True

    return df


def detect_market_structure(df: pd.DataFrame, window: int = 5) -> dict:
    """Analyse la structure de marché : HH, HL, LH, LL, CHoCH, BOS"""

    df = find_swing_points(df, window)

    swing_highs = df[df["swing_high"]].copy()
    swing_lows  = df[df["swing_low"]].copy()

    structure = {
        "swing_highs": swing_highs[["datetime", "high"]].tail(5).to_dict("records"),
        "swing_lows":  swing_lows[["datetime", "low"]].tail(5).to_dict("records"),
        "trend":       "indéterminé",
        "last_bos":    None,
        "last_choch":  None,
        "hh_hl":       False,
        "lh_ll":       False,
    }

    # Analyse HH/HL ou LH/LL
    if len(swing_highs) >= 2 and len(swing_lows) >= 2:
        last_hh  = swing_highs["high"].iloc[-1]
        prev_hh  = swing_highs["high"].iloc[-2]
        last_hl  = swing_lows["low"].iloc[-1]
        prev_hl  = swing_lows["low"].iloc[-2]

        hh = last_hh > prev_hh   # Higher High
        hl = last_hl > prev_hl   # Higher Low
        lh = last_hh < prev_hh   # Lower High
        ll = last_hl < prev_hl   # Lower Low

        if hh and hl:
            structure["trend"] = "HAUSSIER"
            structure["hh_hl"] = True
        elif lh and ll:
            structure["trend"] = "BAISSIER"
            structure["lh_ll"] = True
        elif hh and ll:
            structure["trend"] = "INDÉCIS"
        elif lh and hl:
            structure["trend"] = "CONSOLIDATION"

    # Détection BOS (Break of Structure)
    if len(swing_highs) >= 2:
        last_high = swing_highs["high"].iloc[-2]
        current_close = df["close"].iloc[-1]

        if current_close > last_high:
            structure["last_bos"] = {
                "type":  "HAUSSIER",
                "level": round(last_high, 2),
                "time":  str(swing_highs["datetime"].iloc[-2])
            }
        elif current_close < swing_lows["low"].iloc[-2] if len(swing_lows) >= 2 else False:
            structure["last_bos"] = {
                "type":  "BAISSIER",
                "level": round(swing_lows["low"].iloc[-2], 2),
                "time":  str(swing_lows["datetime"].iloc[-2])
            }

    # Détection CHoCH (Change of Character)
    if structure["trend"] == "HAUSSIER" and len(swing_lows) >= 2:
        last_hl = swing_lows["low"].iloc[-1]
        if df["close"].iloc[-1] < last_hl:
            structure["last_choch"] = {
                "type":  "BAISSIER",
                "level": round(last_hl, 2),
                "msg":   "CHoCH baissier — possible retournement"
            }
    elif structure["trend"] == "BAISSIER" and len(swing_highs) >= 2:
        last_lh = swing_highs["high"].iloc[-1]
        if df["close"].iloc[-1] > last_lh:
            structure["last_choch"] = {
                "type":  "HAUSSIER",
                "level": round(last_lh, 2),
                "msg":   "CHoCH haussier — possible retournement"
            }

    return structure