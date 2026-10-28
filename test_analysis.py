import numpy as np
import pandas as pd
import pytest

import analysis


def frame(closes):
    idx = pd.bdate_range("2026-01-01", periods=len(closes))
    close = pd.Series(closes, index=idx, dtype=float)
    return pd.DataFrame({"Open": close, "High": close, "Low": close, "Close": close, "Volume": 1000}, index=idx)


def test_price_change():
    assert analysis.price_change(frame([100, 110, 120])) == pytest.approx(20.0)


def test_price_change_with_one_row_is_zero():
    assert analysis.price_change(frame([100])) == 0.0


def test_max_drawdown():
    # peak 200, falls to 100 -> -50%
    assert analysis.max_drawdown(frame([100, 200, 100, 150])) == pytest.approx(-50.0)


def test_max_drawdown_when_always_rising():
    assert analysis.max_drawdown(frame([100, 101, 102])) == 0.0


def test_volatility_flat_price_is_zero():
    assert analysis.volatility(frame([100] * 10)) == pytest.approx(0.0)


def test_volatility_uses_252_and_square_root():
    df = frame([100, 101, 100, 101, 100, 101])
    daily = df["Close"].pct_change().dropna()
    assert analysis.volatility(df) == pytest.approx(daily.std() * np.sqrt(252) * 100)


def test_rebase_starts_at_100():
    out = analysis.rebase_to_100(frame([50, 75, 100])["Close"])
    assert list(out) == [100.0, 150.0, 200.0]


def test_averages_need_enough_days():
    df = analysis.add_averages(frame(range(1, 61)))
    assert df["20-day average"].isna().sum() == 19
    assert df["50-day average"].isna().sum() == 49


def test_clean_prices_rejects_empty():
    with pytest.raises(ValueError):
        analysis.clean_prices(pd.DataFrame())


def test_sample_is_repeatable():
    a = analysis.make_sample("TCS.NS", 3200, "3mo")
    b = analysis.make_sample("TCS.NS", 3200, "3mo")
    assert a["Close"].equals(b["Close"])


def test_summary_mentions_direction_and_name():
    text = analysis.plain_english_summary("TCS", "6 months", 12.0, 10.0, -5.0)
    assert "TCS" in text
    assert "went up" in text
    assert "6 months" in text.lower()


def test_summary_handles_a_flat_price():
    text = analysis.plain_english_summary("TCS", "1 year", 0.2, 5.0, -1.0)
    assert "stayed about the same" in text
