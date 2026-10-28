"""The maths behind DAISY. No Streamlit in here, so it is easy to test."""
import hashlib

import numpy as np
import pandas as pd

TRADING_DAYS = 252  # roughly how many days the market is open in a year

SAMPLE_DAYS = {"5d": 5, "3mo": 66, "6mo": 130, "1y": 252, "2y": 504, "5y": 1260}


def clean_prices(frame):
    """Turn whatever Yahoo returns into Open/High/Low/Close/Volume with a plain date index."""
    if frame is None or frame.empty:
        raise ValueError("no data came back for this symbol")
    frame = frame.copy()
    if isinstance(frame.columns, pd.MultiIndex):
        frame.columns = frame.columns.get_level_values(0)
    columns = ["Open", "High", "Low", "Close", "Volume"]
    missing = [c for c in columns if c not in frame.columns]
    if missing:
        raise ValueError("missing columns: " + ", ".join(missing))
    frame = frame[columns].dropna(subset=["Close"])
    frame.index = pd.to_datetime(frame.index)
    if frame.index.tz is not None:
        frame.index = frame.index.tz_localize(None)
    frame.index.name = "Date"
    return frame.sort_index()


def add_averages(df):
    """Add the 20-day and 50-day moving averages of the closing price."""
    df = df.copy()
    df["20-day average"] = df["Close"].rolling(20).mean()
    df["50-day average"] = df["Close"].rolling(50).mean()
    return df


def price_change(df):
    """Metric 1: % change from the first close to the last close."""
    if len(df) < 2:
        return 0.0
    first, last = df["Close"].iloc[0], df["Close"].iloc[-1]
    if first == 0:
        return 0.0
    return float((last / first - 1) * 100)


def volatility(df):
    """Metric 2: how bumpy the daily moves were, scaled up to a year.

    Standard deviation of daily returns, times sqrt(252). Daily wiggles add up
    like a random walk, so they grow with the square root of time, not time.
    """
    daily = df["Close"].pct_change().dropna()
    if len(daily) < 2:
        return 0.0
    return float(daily.std() * np.sqrt(TRADING_DAYS) * 100)


def max_drawdown(df):
    """Metric 3: the worst fall from a previous high, as a negative %."""
    highest_so_far = df["Close"].cummax()
    fall = (df["Close"] / highest_so_far - 1) * 100
    return float(fall.min())


def last_volume(df):
    """Metric 4: shares traded on the most recent day."""
    return float(df["Volume"].iloc[-1])


def rebase_to_100(close):
    """Make a price series start at 100 so different stocks can share one chart."""
    return close / close.iloc[0] * 100


def plain_english_summary(name, period_label, change, vol, drawdown):
    """Metric 5: turn the four numbers into one friendly sentence a beginner can read."""
    if change > 1:
        move = f"went up {change:.0f}%"
    elif change < -1:
        move = f"went down {abs(change):.0f}%"
    else:
        move = "stayed about the same"

    if vol < 15:
        ride = "a calm, steady ride"
    elif vol < 30:
        ride = "a bit of an up-and-down ride"
    else:
        ride = "a wild, rollercoaster ride"

    return (
        f"Over the last {period_label.lower()}, {name} {move}. "
        f"It's been {ride} along the way, and its biggest dip from a high point was {abs(drawdown):.0f}%."
    )


def make_sample(symbol, start_price, period):
    """Made-up prices, only used when Yahoo can't be reached. Same symbol, same numbers."""
    days = SAMPLE_DAYS[period]
    seed = int(hashlib.sha256(symbol.encode()).hexdigest()[:8], 16)
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range(end=pd.Timestamp.today().normalize(), periods=days)
    close = start_price * np.exp(np.cumsum(rng.normal(0.0004, 0.012, size=days)))
    open_ = close * (1 + rng.normal(0, 0.004, size=days))
    high = np.maximum(open_, close) * (1 + rng.uniform(0.001, 0.01, size=days))
    low = np.minimum(open_, close) * (1 - rng.uniform(0.001, 0.01, size=days))
    volume = rng.integers(300_000, 5_000_000, size=days)
    return pd.DataFrame(
        {"Open": open_, "High": high, "Low": low, "Close": close, "Volume": volume},
        index=pd.DatetimeIndex(dates, name="Date"),
    )
