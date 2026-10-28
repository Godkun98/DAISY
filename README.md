# DAISY

**Live app:** [add your streamlit.app link here]

A small stock dashboard for the Nifty 50, the BSE Sensex and a few large Indian companies. It boils each one down to four numbers and explains them in plain words.

## The four numbers

| Number | What it tells you | How it's worked out |
|---|---|---|
| Change | How far the price moved over the window | (last close / first close - 1) x 100 |
| Volatility | How bumpy the ride was | standard deviation of daily returns x sqrt(252) |
| Max drawdown | The worst fall from a high point | lowest value of (close / highest close so far - 1) |
| Volume | Shares traded on the last day | taken straight from the data |

All four are in `analysis.py`.

## Data

Prices come from Yahoo Finance through `yfinance`, cached for 15 minutes (there is a Refresh button). Yahoo's free data can be about 15 minutes late, so this is not a tick-by-tick live feed. If Yahoo can't be reached, the app shows a warning and falls back to made-up sample prices.

## Run it

```
python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Tests: `pytest`

## Why I built this

[the main reason to build DAISY was to simplify the complex jargon of finance market in simple terms so that it becomes it a bit accessible for people to read and understand , it helps to have a basic idea of how the finance markets are  functioning and to understand about the current on going trends about the fucnitoning of the markets in easier terms]

## Ideas for later
[future scope includes to add more updating market referenes and also to make it more usable and accesible across paltforms, also to include more parameters to understand the stocks etc]


## Notes


DAISY shows past prices only. It is not investment advice.
