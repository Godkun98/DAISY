import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf

import analysis

st.set_page_config(page_title="DAISY", layout="wide")

# name: (Yahoo Finance ticker, rough price used only for the offline sample)
INDICES = {
    "Nifty 50": ("^NSEI", 25000),
    "BSE Sensex": ("^BSESN", 82000),
}
STOCKS = {
    "Reliance Industries": ("RELIANCE.NS", 1450),
    "TCS": ("TCS.NS", 3200),
    "Infosys": ("INFY.NS", 1450),
    "HDFC Bank": ("HDFCBANK.NS", 1550),
    "ICICI Bank": ("ICICIBANK.NS", 1000),
    "Larsen & Toubro": ("LT.NS", 3200),
    "State Bank of India": ("SBIN.NS", 750),
    "ITC": ("ITC.NS", 450),
    "Bharti Airtel": ("BHARTIARTL.NS", 1600),
    "Hindustan Unilever": ("HINDUNILVR.NS", 2500),
    "Kotak Mahindra Bank": ("KOTAKBANK.NS", 1800),
    "Axis Bank": ("AXISBANK.NS", 1150),
    "Bajaj Finance": ("BAJFINANCE.NS", 7000),
    "Asian Paints": ("ASIANPAINT.NS", 2500),
    "Maruti Suzuki": ("MARUTI.NS", 11000),
    "Sun Pharma": ("SUNPHARMA.NS", 1800),
    "Titan Company": ("TITAN.NS", 3400),
    "Wipro": ("WIPRO.NS", 550),
    "HCL Technologies": ("HCLTECH.NS", 1800),
    "Tata Steel": ("TATASTEEL.NS", 150),
    "Adani Enterprises": ("ADANIENT.NS", 3000),
    "Power Grid Corporation": ("POWERGRID.NS", 320),
    "NTPC": ("NTPC.NS", 380),
    "UltraTech Cement": ("ULTRACEMCO.NS", 11000),
    "Nestle India": ("NESTLEIND.NS", 2300),
    "Mahindra & Mahindra": ("M&M.NS", 2900),
    "JSW Steel": ("JSWSTEEL.NS", 1000),
    "IndusInd Bank": ("INDUSINDBK.NS", 1000),
    "Dr Reddy's Laboratories": ("DRREDDY.NS", 1200),
    "Cipla": ("CIPLA.NS", 1500),
    "Divi's Laboratories": ("DIVISLAB.NS", 6000),
    "Britannia Industries": ("BRITANNIA.NS", 5000),
    "Dabur India": ("DABUR.NS", 500),
    "Godrej Consumer Products": ("GODREJCP.NS", 1200),
    "Hero MotoCorp": ("HEROMOTOCO.NS", 4500),
    "Bajaj Auto": ("BAJAJ-AUTO.NS", 9000),
    "Eicher Motors": ("EICHERMOT.NS", 5000),
    "Grasim Industries": ("GRASIM.NS", 2600),
    "Shree Cement": ("SHREECEM.NS", 27000),
    "Ambuja Cements": ("AMBUJACEM.NS", 550),
    "Coal India": ("COALINDIA.NS", 400),
    "Oil & Natural Gas Corporation": ("ONGC.NS", 250),
    "Indian Oil Corporation": ("IOC.NS", 140),
    "Bharat Petroleum": ("BPCL.NS", 300),
    "Adani Ports": ("ADANIPORTS.NS", 1300),
    "Adani Green Energy": ("ADANIGREEN.NS", 1000),
    "Vedanta": ("VEDL.NS", 450),
    "Hindalco Industries": ("HINDALCO.NS", 650),
    "Pidilite Industries": ("PIDILITIND.NS", 2900),
    "Tech Mahindra": ("TECHM.NS", 1600),
    "LTIMindtree": ("LTIM.NS", 5500),
    "Bajaj Finserv": ("BAJAJFINSV.NS", 1800),
    "SBI Life Insurance": ("SBILIFE.NS", 1500),
    "HDFC Life Insurance": ("HDFCLIFE.NS", 700),
    "Bank of Baroda": ("BANKBARODA.NS", 240),
    "Punjab National Bank": ("PNB.NS", 100),
    "DLF": ("DLF.NS", 800),
}
ASSETS = {**INDICES, **STOCKS}

PERIODS = {"3 months": "3mo", "6 months": "6mo", "1 year": "1y", "2 years": "2y", "5 years": "5y"}


@st.cache_data(ttl=900, show_spinner=False)  # grab fresh prices at most every 15 minutes
def fetch(symbol, period):
    raw = yf.Ticker(symbol).history(period=period, auto_adjust=False, actions=False)
    return analysis.clean_prices(raw)


def get_data(name, period):
    """Returns (prices, is_sample). Uses made-up practice prices if the real data can't be reached."""
    symbol, sample_start = ASSETS[name]
    try:
        return fetch(symbol, period), False
    except Exception:
        return analysis.make_sample(symbol, sample_start, period), True


def fmt_price(name, value):
    return f"{value:,.2f}" if name in INDICES else f"₹{value:,.2f}"


def style(fig, height):
    fig.update_layout(
        template="plotly_white", height=height, hovermode="x unified",
        margin=dict(l=10, r=10, t=50, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
    )
    fig.update_xaxes(rangeslider_visible=False)
    return fig


# ---------- sidebar ----------
st.sidebar.header("Pick something to look at")
name = st.sidebar.selectbox("A company or an index", list(ASSETS))
period_label = st.sidebar.selectbox("How far back?", list(PERIODS), index=2)
period = PERIODS[period_label]
chart_type = st.sidebar.radio("How should the chart look?", ["Line", "Candlestick"], horizontal=True)

others = [n for n in ASSETS if n != name]
default_compare = [n for n in ["Nifty 50", "BSE Sensex", "TCS"] if n in others]
compare = st.sidebar.multiselect("Compare it with (up to 4 others)", others, default=default_compare, max_selections=4)

st.sidebar.divider()
if st.sidebar.button("Refresh prices"):
    st.cache_data.clear()
    st.rerun()
st.sidebar.caption("Prices are about 15 minutes behind real time, and they refresh on their own every 15 minutes. Hit the button above for a fresh look right now.")

# ---------- header + the two index numbers ----------
st.title("DAISY")
st.write("A friendly little dashboard for the Nifty 50, the BSE Sensex, and a bunch of big Indian companies — no finance degree needed.")

used_sample = False
top = st.columns(len(INDICES))
for col, idx_name in zip(top, INDICES):
    idx_df, sample = get_data(idx_name, "5d")
    used_sample = used_sample or sample
    if len(idx_df) >= 2:
        last, previous = idx_df["Close"].iloc[-1], idx_df["Close"].iloc[-2]
        col.metric(idx_name, f"{last:,.2f}", f"{(last / previous - 1) * 100:+.2f}% vs previous day")
    else:
        col.metric(idx_name, f"{idx_df['Close'].iloc[-1]:,.2f}")

# ---------- selected stock ----------
df, sample = get_data(name, period)
used_sample = used_sample or sample
if used_sample:
    st.warning("Couldn't reach the real data right now, so a few of the numbers below are just made-up practice numbers. Don't treat them as real!")

df = analysis.add_averages(df)
st.subheader(name)
st.caption(f"Last seen at {fmt_price(name, df['Close'].iloc[-1])} on {df.index[-1]:%d %b %Y}")

change = analysis.price_change(df)
vol = analysis.volatility(df)
drawdown = analysis.max_drawdown(df)
volume = analysis.last_volume(df)

# ---------- plain-English summary ----------
st.info(analysis.plain_english_summary(name, period_label, change, vol, drawdown))

c1, c2, c3, c4 = st.columns(4)
c1.metric(f"How much it moved ({period_label})", f"{change:+.2f}%",
          help="This just compares the very first price in this time window to the very last one. A plus sign means it grew, a minus sign means it shrank.")
c2.metric("How bumpy the ride was", f"{vol:.1f}%",
          help="A bigger number means the price jumped around more from day to day — more ups and downs. A smaller number means it moved more smoothly. This doesn't tell you which way it's headed next.")
c3.metric("Its biggest dip", f"{drawdown:.1f}%",
          help="The largest drop from a high point to a lower point sometime after, inside this time window.")
c4.metric("How many shares changed hands", f"{volume:,.0f}" if volume > 0 else "n/a",
          help="How many shares were bought and sold on the most recent day. (Indices don't really have a 'volume', so this shows n/a for them.)")

# ---------- price chart ----------
fig = go.Figure()
if chart_type == "Candlestick":
    fig.add_trace(go.Candlestick(x=df.index, open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"], name="Price"))
else:
    fig.add_trace(go.Scatter(x=df.index, y=df["Close"], name="Price", line=dict(width=2)))
fig.add_trace(go.Scatter(x=df.index, y=df["20-day average"], name="Last 20 days, on average", line=dict(width=1.5)))
fig.add_trace(go.Scatter(x=df.index, y=df["50-day average"], name="Last 50 days, on average", line=dict(width=1.5)))
fig.update_layout(title=f"{name}'s price over time", yaxis_title="Price")
st.plotly_chart(style(fig, 440))
st.caption("The two smoother lines are rolling averages — they iron out the daily jitters. Price above them? It's been drifting up lately. Price below them? Drifting down. The 50-day line needs 50 days of history, so it starts a bit later on short windows.")

# ---------- comparison ----------
st.subheader("How does it stack up?")
st.write("Every line below starts at the same spot (100), so you can tell which one grew faster — even if their actual prices are wildly different.")

rows = []
race = go.Figure()
for item in [name] + compare:
    item_df, sample = get_data(item, period)
    if sample:
        st.caption(f"{item}: using practice numbers for this one.")
    race.add_trace(go.Scatter(x=item_df.index, y=analysis.rebase_to_100(item_df["Close"]), name=item))
    rows.append({
        "Name": item,
        "Change": analysis.price_change(item_df),
        "Last price": fmt_price(item, item_df["Close"].iloc[-1]),
    })
race.add_hline(y=100, line_dash="dot", line_color="gray")
race.update_layout(title=f"If everyone started at 100, {period_label} later...", yaxis_title="Value")
st.plotly_chart(style(race, 380))

table = pd.DataFrame(rows).sort_values("Change", ascending=False)
table["Change"] = table["Change"].map(lambda v: f"{v:+.2f}%")
st.caption(f"Sorted from best to worst over the last {period_label.lower()}.")
st.dataframe(table, hide_index=True)

st.divider()
st.caption("DAISY only looks backward, never forward. Past prices don't predict future ones — this isn't investment advice, just a friendly look at what already happened.")
