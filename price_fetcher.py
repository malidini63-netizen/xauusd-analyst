# price_fetcher.py — récupération des données OHLCV via Twelve Data
import requests
import pandas as pd
from config import TWELVEDATA_API_KEY, SYMBOL, TIMEFRAMES

BASE_URL = "https://api.twelvedata.com/time_series"

def get_candles(timeframe: str, bars: int = 100) -> pd.DataFrame:
    """Récupère les bougies OHLCV pour un timeframe donné"""

    params = {
        "symbol":     SYMBOL,
        "interval":   TIMEFRAMES.get(timeframe, timeframe),
        "outputsize": bars,
        "apikey":     TWELVEDATA_API_KEY,
        "format":     "JSON"
    }

    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()

        if "values" not in data:
            print(f"Erreur Twelve Data [{timeframe}] : {data.get('message', 'inconnue')}")
            return pd.DataFrame()

        df = pd.DataFrame(data["values"])
        df["datetime"] = pd.to_datetime(df["datetime"])
        df = df.sort_values("datetime").reset_index(drop=True)

        for col in ["open", "high", "low", "close"]:
            df[col] = pd.to_numeric(df[col])

        return df

    except Exception as e:
        print(f"Erreur price_fetcher [{timeframe}] : {e}")
        return pd.DataFrame()


def get_all_timeframes(bars: int = 100) -> dict:
    """Récupère les données pour tous les timeframes"""
    return {
        tf: get_candles(tf, bars)
        for tf in TIMEFRAMES.keys()
    }


def get_current_price() -> float:
    """Récupère le prix actuel de XAUUSD"""
    try:
        url = "https://api.twelvedata.com/price"
        params = {"symbol": SYMBOL, "apikey": TWELVEDATA_API_KEY}
        response = requests.get(url, params=params)
        data = response.json()
        return float(data.get("price", 0))
    except Exception as e:
        print(f"Erreur prix actuel : {e}")
        return 0.0