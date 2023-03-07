from datetime import date, timedelta

import datapane as dp
import pandas as pd
import plotly.express as px
import yfinance as yf


def process(ticker: str) -> dp.View:
    start = date.today() - timedelta(365)
    end = date.today() + timedelta(2)
    # download the data and place into a df
    df = pd.DataFrame(yf.download(ticker, start=start, end=end)["Adj Close"]).reset_index()
    df.columns = ["date", "adjusted_close"]
    # build the plot
    fig = px.line(df, x="date", y="adjusted_close")

    return dp.View(
        dp.Group(
            dp.BigNumber("Ticker", ticker),
            dp.BigNumber("52-week High", df["adjusted_close"].max().round(2)),
            dp.BigNumber("52-week Low", df["adjusted_close"].min().round(2)),
            dp.BigNumber("Closing Price", df["adjusted_close"].iloc[-1].round(2)),
            columns=4,
        ),
        dp.Plot(fig),
    )


# build the form and run the app
controls = dp.Controls(ticker=dp.TextBox(label="Stock Ticker (e.g. AMZN, WMT, AAPL, ^DJI)", initial="AMZN"))
dp.serve_app(dp.View(dp.Form(on_submit=process, controls=controls)))
