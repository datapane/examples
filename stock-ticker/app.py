# A simple stock market data visualization
# See demo video - https://watch.screencastify.com/v/Fp4usuStyWr2wC0QFnIs


import datapane as dp
import pandas as pd
import yfinance as yf
from datetime import date, timedelta
import plotly.express as px


def f(params):
    
    Start = date.today() - timedelta(365)
    Start.strftime('%Y-%m-%d')

    End = date.today() + timedelta(2)
    End.strftime('%Y-%m-%d')
    
    df = pd.DataFrame(yf.download(params['ticker'], start=Start, end=End)['Adj Close']).reset_index()    
    df.columns = ['date', 'adjusted_close']
    
    fig = px.line(df, x = "date", y = "adjusted_close")
    
    return dp.View(dp.Group(dp.BigNumber("Ticker", params['ticker']),
                            dp.BigNumber("52-week High", df['adjusted_close'].max().round(2)),                            
                            dp.BigNumber("52-week Low", df['adjusted_close'].min().round(2)),
                            dp.BigNumber("Closing Price", df['adjusted_close'].iloc[-1].round(2)),
                            columns = 4),
                   dp.Plot(fig),
                   name = "xyz")


controls = dp.Controls(dp.TextBox("ticker", "Stock Ticker (e.g. AMZN, WMT, AAPL, ^DJI)", default="^DJI"))


v = dp.View(
    dp.Interactive(f, target = "xyz", controls = controls),
    dp.Empty(name = "xyz")
)


dp.serve(v)

