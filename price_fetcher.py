# price_fetcher.py — récupération OHLCV via yFinance (gratuit)
import yfinance as yf
import pandas as pd

SYMBOL_YF = "GC=F"

TIMEFRAMES_YF = {
    "H4":  ("4h",  "60d"),
    "H1":  ("1h",  "30d"),
    "M15": ("15m", "8d"),
    "M5":  ("5m",  "5d")
}

def get_candles(timeframe: str, bars: int = 100) -> pd.DataFrame:
    try:
        interval, period = TIMEFRAMES_YF.get(timeframe, ("1h", "30d"))
        ticker = yf.Ticker(SYMBOL_YF)
        df = ticker.history(interval=interval, period=period)
        if df.empty:
            return pd.DataFrame()
        df = df.reset_index()
        df = df.rename(columns={"Datetime": "datetime", "Date": "datetime", "Open": "open", "High": "high", "Low": "low", "Close": "close", "Volume": "volume"})
        df["datetime"] = pd.to_datetime(df["datetime"], utc=True)
        df = df[["datetime", "open", "high", "low", "close"]].tail(bars)
        return df.reset_index(drop=True)
    except Exception as e:
        print(f"Erreur yFinance [{timeframe}] : {e}")
        return pd.DataFrame()

def get_all_timeframes(bars: int = 100) -> dict:
    return {tf: get_candles(tf, bars) for tf in TIMEFRAMES_YF.keys()}

def get_current_price() -> float:
    try:
        ticker = yf.Ticker(SYMBOL_YF)
        data = ticker.history(period="1d", interval="1m")
        if not data.empty:
            return round(float(data["Close"].iloc[-1]), 2)
        return 0.0
    except Exception as e:
        print(f"Erreur prix actuel : {e}")
        return 0.0
