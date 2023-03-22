import datapane as dp
import pandas as pd
import plotly.express as px
import yfinance as yf

from datetime import datetime
import threading
from time import sleep


TICKER = "MSFT"
REFRESH = 5 * 60
view = dp.View("No data yet")


dp.enable_logging()


def process(ticker: str) -> dp.View:
    # download the data and place into a df
    df = pd.DataFrame(yf.download(ticker, period="1d", interval="5m")["Adj Close"]).reset_index()
    df.columns = ["time", "adjusted_close"]
    # build the plot
    fig = px.line(df, x="time", y="adjusted_close")

    return dp.View(
        dp.Group(
            dp.BigNumber("Ticker", ticker),
            dp.BigNumber("Opening Price", df["adjusted_close"].iloc[0].round(2)),
            dp.BigNumber("Daily High", df["adjusted_close"].max().round(2)),
            dp.BigNumber("Daily Low", df["adjusted_close"].min().round(2)),
            columns=4,
        ),
        dp.Plot(fig),
    )


def update_data():
    global view

    while True:
        print(f"Updating data at {datetime.now().time()}")
        view = process(TICKER)
        sleep(REFRESH)


# run update_view in background
threading.Thread(target=update_data, daemon=True).start()


def return_view() -> dp.View:
    return dp.View(f"Refreshed at {datetime.now().time()}", view)


# run the dashboard
dp.serve_app(dp.View(dp.Dynamic(on_timer=return_view, seconds=30)))
