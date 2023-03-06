# -*- coding: utf-8 -*-
"""Datapane - Financial Model

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1YCQB8HxS4jOsGAKjiBTDZD_bF6fzK-tP

## Datapane Tutorial - Financial Model

This is part of a series of tutorials to help you learn how to use Datapane.

Before getting started, you will need your API token, which you can find on your [settings page](https://datapane.com/settings). 

Once you have you token, add it to the form field in the cell below to login to Datapane.

Tip: if you are using Datapane Community, keep the `datapane_server_url` as `https://datapane.com`. Alternatively, if you are using a Teams instance, enter the URL of your instance.
"""
import datapane as dp

"""# Import libraries and set parameters

Although we can generate our Datapane report by manually running this notebook on Colab or our local machine, in the future we may want to deploy it to Datapane Cloud as an app which stakeholders can run with parameters.

To enable this, we are using `dp.Params`, which allows us to access parameters when this notebook is run as a Datapane App (where Datapane will use our parameters to generate a form for end-users).

Params is a Python dictionary which is injected at runtime and will be empty if we are running it elsewhere, so we are choosing some defaults.

"""

import pandas as pd
import requests
import datetime
import numpy as np
import altair as alt

# inputs
input_params = dp.Params

CURRENT_CASH_GBP = input_params.get('current_cash', 100000)
FORECAST_LENGTH_DAYS = 365 * input_params.get('forecast_years', 2)
WEEKLY_GROWTH_PERCENT = input_params.get('weekly_growth_rate', 2)
INITIAL_REVENUE = input_params.get('initial_revenue', 100)
MONTHLY_BURN = input_params.get('monthly_burn', CURRENT_CASH_GBP / 12)

# Misc cash injection

INJECTION_AMOUNT = input_params.get('cash_injection', 100000) # TODO: calculate as derived value
INJECTION_OFFSET = input_params.get('cash_injection_offset', 5) # Number of mos until R&D grant

"""# Finance Model
This is the core finance model and visualization which we will build using the Python library Altair.
"""

# derived values

monthly_growth_rate = pow((1+WEEKLY_GROWTH_PERCENT/100), 4) - 1
today = pd.to_datetime('today')
end_forecast = today + pd.Timedelta(FORECAST_LENGTH_DAYS, unit='d')

burn = MONTHLY_BURN

# This forecast is worst-case scenario / most conservative - predicated on if you do not grow at all.

df = pd.DataFrame(columns=[])

idx = pd.date_range(today, end_forecast, freq='m')
df = df.reindex(idx, fill_value=0)
df.index.names = ['date']
df.reset_index(inplace=True)

df['burn'] = burn # Burn remains constant for now.
df['revenue_0g'] = INITIAL_REVENUE
df['injection'] = 0

# Set initial cash and revenue
df.loc[0, 'cash_0g'] = CURRENT_CASH_GBP
df.loc[0, 'cash_dg'] = CURRENT_CASH_GBP
df.loc[0, 'revenue_dg'] = INITIAL_REVENUE

# Cas injection (e.g. R&D tax or fundraise)
df.loc[INJECTION_OFFSET + 1, 'injection'] = INJECTION_AMOUNT # 0dx adjustment

for i in range(1, len(df)):
    prev = df.loc[i-1]
    df.loc[i, 'cash_0g'] = prev['cash_0g'] - prev['burn'] + prev['injection'] + prev['revenue_0g']
    df.loc[i, 'cash_dg'] = prev['cash_dg'] - prev['burn'] + prev['injection'] + prev['revenue_dg']
    df.loc[i, 'revenue_dg'] = prev['revenue_dg'] * (1 + monthly_growth_rate)
df.dtypes
# This is a variable forecast for modelling different growth-rates.
# Initial growth rate is set to be the current growth rate

# This cannot be 0, as growth rate wouldn't work
start_revenue = INITIAL_REVENUE if INITIAL_REVENUE > 100 else 100
scale = (-CURRENT_CASH_GBP, CURRENT_CASH_GBP * 2)

monthly_growth_percent = WEEKLY_GROWTH_PERCENT * 4
slider = alt.binding_range(min=0, max=100, step=0.1, name='Monthly growth rate (%)')
selector = alt.selection_single(fields=['month_growth'], bind=slider, init={'month_growth': monthly_growth_percent})

base = alt.Chart(df[['date', 'cash_0g']]).transform_window(
    # Use count() to find out the current month we're on (i.e. the index), as we use that as the power for our growth rate
    index='count()'
).transform_calculate(
    # Transform a % growth rate (i.e. 7) into sometime useful (i.e. 1.07).
    # Raise that to our current month (i.e. for month 2, 1.07 ** 2 = ~1.145), and multiply that by our revenue amount (~1.145 * 500)
    forecast_revenue = ((1+(selector.month_growth / 100)) ** alt.datum.index) * start_revenue
).transform_window(
    # Take what is in practice the cumulative product of revenue (i.e. total revenue earned so far)
    forecast_total_revenue = 'sum(forecast_revenue)', frame=[None, 0]
).transform_calculate(
    # Add cumprod to current cash to find cash standing (i.e. if we have £100k cash, and 10 months of £10k revenue, we have £200k now)
    adj_cash = alt.datum.cash_0g + alt.datum.forecast_total_revenue
).encode(x='yearmonth(date):T')

cash = base.encode(y=alt.Y('adj_cash:Q', scale=alt.Scale(domain=scale))).mark_area(opacity=0.75)
revenue = base.encode(y='forecast_total_revenue:Q').mark_line(color='#f26522', size=5) 
revenue_growth = base.encode(y='forecast_revenue:Q').mark_line(color='purple', size=5)

charts = cash + revenue + revenue_growth

chart_final = charts.add_selection(selector).interactive().properties(width='container')

"""# Building a Datapane report

Now that we have a series of plots, we can create a report using Datapane. 

In addition to the visualizations, this report includes Datapane's `BigNumber` component to display top level KPIs, and our `DataTable` component to allow our viewers to filter, explore, and download the data themselves.

Although we could create a linear list of all blocks (similar to how they are displayed in this notebook), we can build a more powerful and accessible report by using Datapane's [layout components](https://docs.datapane.com/reports/blocks/layout-pages-and-selects). 

From these components, we are using `Group` to place the `BigNumber` blocks in two columns, have used the `Page` block to add multiple pages to our report, and are using the `Select` block to create tabs where users can choose their dataset. This results in a beautiful, interactive document which we can publish and share.

"""

dp.Report(
    "# Finance Model",
    dp.Group(blocks=[
        dp.BigNumber(value=f"${round(burn)}", heading="Monthly outgoings"),
        dp.BigNumber(value=f"${CURRENT_CASH_GBP}", heading="Cash in bank", is_upward_change=True, change=7)
    ], columns=2),
    dp.Select(blocks=[
      dp.Group(
          blocks=[
"""This plot models cash and revenue, dependent on various other growth scenarios and based on this month's burn. 

- Blue area is cash remaining
- Orange line is the cumulative sum of all revenue
- Purple line is monthly revenue

> Drag the slider to adjust growth rate. The growth rate at which the blue area never crosses 0 is the growth you need to achieve **[Default Alive](http://paulgraham.com/aord.html)**.
""", chart_final
          ], 
          label='Interactive Plot'
      ), 
      dp.Group(
          blocks=[
              "> In this dataset, `cash_0g`/`revenue_0g` presumes no further growth, whereas `cash_dg`/`revenue_dg` presumes growth at the current rate continues.",
              dp.DataTable(df)
          ], label='Interactive Dataset'
      )
  ])
).publish(name='Finance Model', open=True)

"""# Deploying as an app

Because we defined the input variables using `dp.Params` above, we can also easily use Datapane to turn our script into an app which non-technical people can run themselves.

Note that deploying an app requires a private **Datapane Cloud** server, [so create one here](https://datapane.com/pricing/#contact-form) before continuing. Pricing starts at $99 per month with a 30-day free trial.

If we want user
To build an app, we need to include a YAML file which defines which parameters we want in our auto
"""

