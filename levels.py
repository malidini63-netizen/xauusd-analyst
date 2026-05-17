# levels.py — détection Order Blocks, FVG, SSL/BSL
import pandas as pd


def detect_order_blocks(df: pd.DataFrame, lookback: int = 50) -> dict:
    """Détecte les Order Blocks bullish et bearish"""

    df = df.tail(lookback).copy().reset_index(drop=True)
    bullish_obs = []
    bearish_obs = []

    for i in range(1, len(df) - 1):
        # Bullish OB : bougie baissière suivie d'un fort mouvement haussier
        if (df["close"].iloc[i] < df["open"].iloc[i] and
                df["close"].iloc[i+1] > df["high"].iloc[i]):
            bullish_obs.append({
                "top":    round(df["high"].iloc[i], 2),
                "bottom": round(df["low"].iloc[i], 2),
                "mid":    round((df["high"].iloc[i] + df["low"].iloc[i]) / 2, 2),
                "time":   str(df["datetime"].iloc[i])
            })

        # Bearish OB : bougie haussière suivie d'un fort mouvement baissier
        if (df["close"].iloc[i] > df["open"].iloc[i] and
                df["close"].iloc[i+1] < df["low"].iloc[i]):
            bearish_obs.append({
                "top":    round(df["high"].iloc[i], 2),
                "bottom": round(df["low"].iloc[i], 2),
                "mid":    round((df["high"].iloc[i] + df["low"].iloc[i]) / 2, 2),
                "time":   str(df["datetime"].iloc[i])
            })

    return {
        "bullish_ob": bullish_obs[-3:] if bullish_obs else [],
        "bearish_ob": bearish_obs[-3:] if bearish_obs else []
    }


def detect_fvg(df: pd.DataFrame, lookback: int = 50) -> dict:
    """Détecte les Fair Value Gaps (FVG)"""

    df = df.tail(lookback).copy().reset_index(drop=True)
    bullish_fvg = []
    bearish_fvg = []

    for i in range(1, len(df) - 1):
        # Bullish FVG : gap entre low[i+1] et high[i-1]
        if df["low"].iloc[i+1] > df["high"].iloc[i-1]:
            bullish_fvg.append({
                "top":    round(df["low"].iloc[i+1], 2),
                "bottom": round(df["high"].iloc[i-1], 2),
                "mid":    round((df["low"].iloc[i+1] + df["high"].iloc[i-1]) / 2, 2),
                "time":   str(df["datetime"].iloc[i])
            })

        # Bearish FVG : gap entre high[i+1] et low[i-1]
        if df["high"].iloc[i+1] < df["low"].iloc[i-1]:
            bearish_fvg.append({
                "top":    round(df["low"].iloc[i-1], 2),
                "bottom": round(df["high"].iloc[i+1], 2),
                "mid":    round((df["low"].iloc[i-1] + df["high"].iloc[i+1]) / 2, 2),
                "time":   str(df["datetime"].iloc[i])
            })

    return {
        "bullish_fvg": bullish_fvg[-3:] if bullish_fvg else [],
        "bearish_fvg": bearish_fvg[-3:] if bearish_fvg else []
    }


def detect_liquidity(df: pd.DataFrame, lookback: int = 50) -> dict:
    """Détecte les niveaux de liquidité SSL/BSL"""

    df = df.tail(lookback).copy().reset_index(drop=True)

    # BSL : Buy Side Liquidity = swing highs (liquidité au-dessus)
    bsl_levels = []
    for i in range(2, len(df) - 2):
        if (df["high"].iloc[i] > df["high"].iloc[i-1] and
                df["high"].iloc[i] > df["high"].iloc[i+1] and
                df["high"].iloc[i] > df["high"].iloc[i-2] and
                df["high"].iloc[i] > df["high"].iloc[i+2]):
            bsl_levels.append({
                "level": round(df["high"].iloc[i], 2),
                "time":  str(df["datetime"].iloc[i])
            })

    # SSL : Sell Side Liquidity = swing lows (liquidité en-dessous)
    ssl_levels = []
    for i in range(2, len(df) - 2):
        if (df["low"].iloc[i] < df["low"].iloc[i-1] and
                df["low"].iloc[i] < df["low"].iloc[i+1] and
                df["low"].iloc[i] < df["low"].iloc[i-2] and
                df["low"].iloc[i] < df["low"].iloc[i+2]):
            ssl_levels.append({
                "level": round(df["low"].iloc[i], 2),
                "time":  str(df["datetime"].iloc[i])
            })

    return {
        "bsl": bsl_levels[-5:] if bsl_levels else [],
        "ssl": ssl_levels[-5:] if ssl_levels else []
    }


def get_all_levels(df: pd.DataFrame) -> dict:
    """Retourne tous les niveaux clés"""
    obs  = detect_order_blocks(df)
    fvgs = detect_fvg(df)
    liq  = detect_liquidity(df)

    return {**obs, **fvgs, **liq}