#!/usr/bin/env python
# coding: utf-8

# # Social media analytics dashboard

# In[1]:


import altair as alt
import datapane as dp
import json
import numpy as np
import pandas as pd

from datetime import datetime, timedelta


# ## Wrangling and visualisation functions

# In[2]:


def youtube_analytics_to_df(yt_analytics_rows, yt_analytics_columns, year=None):
    df_yt_analytics = pd.DataFrame(yt_analytics_rows, columns=yt_analytics_columns)
    df_yt_analytics = df_yt_analytics.set_index("Date")
    df_yt_analytics.index = pd.DatetimeIndex(df_yt_analytics.index)

    # If not after a specific year, use year from last sample date
    year = None
    last_sample_date = datetime.strptime(yt_analytics_rows[-1][0], "%Y-%m-%d")
    if not year:
        year = last_sample_date.year

    # Subsample to samples from the same year
    df_yt_analytics = df_yt_analytics[df_yt_analytics.index.year == year]

    # Fill our DataFrame so there's a sample for every day of the year
    idx = pd.date_range(f"01-01-{year}", f"12-31-{year}")
    df_yt_analytics = df_yt_analytics.reindex(idx, fill_value=0)
    df_yt_analytics["Date"] = df_yt_analytics.index

    return df_yt_analytics, year, last_sample_date


# In[3]:


def get_last_28_days(df_yt_analytics, last_28_days_end=None):
    last_28_days_start = last_28_days_end - timedelta(days=28)
    last_28_days_mask = (df_yt_analytics["Date"] > last_28_days_start) & (df_yt_analytics["Date"] <= last_28_days_end)
    df_yt_last_28_days = df_yt_analytics[last_28_days_mask]

    return df_yt_last_28_days


# ## Load and wrangle data

# Plot a calendar heatmap for a particular metric, similar to the GitHub contribution plot.

# In[4]:


def plot_calendar_heatmap(metric, df_yt_analytics, labels=True, legend=True, height=120):
    chart = (
        alt.Chart(df_yt_analytics)
        .mark_rect(stroke="white", strokeWidth=2)
        .encode(
            alt.X(
                "week(Date):T",
                title=None,
                axis=alt.Axis(
                    grid=False,
                    labels=labels,
                    ticks=False,
                    domain=False,
                    tickCount="month",
                    format="%b",
                ),
            ),
            alt.Y(
                "day(Date):T",
                sort="descending",
                title=None,
                axis=alt.Axis(
                    labelBaseline="top",
                    grid=False,
                    labels=labels,
                    ticks=False,
                    domain=False,
                    tickCount={"interval": "day", "step": 3},
                ),
            ),
            alt.Color(
                f"{metric}:Q",
                legend=alt.Legend() if legend else None,
                title=None,
                scale=alt.Scale(
                    range=[
                        "RGBA(140,107,254,0.15)",
                        "RGBA(140,107,254,1)",
                        "RGBA(154,232,255,1)",
                    ]
                ),
            ),
            tooltip=["Date", f"{metric}"],
        )
        .configure_view(strokeWidth=0)
        .configure_axis(labelFontSize=12)
        .properties(width="container", height=height)
    )

    return chart


# Generate an interesting calendar heatmap banner by mixing engagement data with noise .

# In[5]:


def plot_banner(df_yt_analytics):
    df_banner = df_yt_analytics.copy()
    df_banner["Views"] = df_banner["Views"] + np.random.randint(1, 10, df_banner.shape[0])

    return plot_calendar_heatmap("Views", df_banner, labels=False, legend=False, height=100)


# In[6]:


def plot_metric_time_series(metric, df_yt_analytics):
    base = (
        alt.Chart(df_yt_analytics)
        .encode(x=alt.X("Date:T", axis=alt.Axis(title=None)))
        .properties(width="container", height=200)
    )

    selection = alt.selection_single(fields=["Date"], nearest=True, on="mouseover", empty="none", clear="mouseout")

    area = base.mark_area(line=True, interpolate="monotone", fill="RGBA(140,107,254,1)", opacity=0.15).encode(
        y=alt.Y(f"{metric}:Q", axis=alt.Axis(orient="right", title=None)),
        color=alt.value("RGBA(140,107,254,1)"),
    )

    points = area.mark_point(fill="RGBA(140,107,254,1)", stroke="white", size=100, opacity=1).transform_filter(
        selection
    )

    rule = (
        base.mark_rule(stroke="RGBA(154,232,255,1)", strokeWidth=4)
        .encode(
            opacity=alt.condition(selection, alt.value(0.5), alt.value(0)),
            tooltip=[
                alt.Tooltip(shorthand="Date:T", title="Date"),
                alt.Tooltip(f"{metric}:Q", title="Value"),
            ],
        )
        .add_selection(selection)
    )

    chart = area + points + rule

    return chart


# In[7]:


def plot_metric_popular_day(metric, df_yt_analytics):
    max_value = df_yt_analytics.groupby(df_yt_analytics["Date"].dt.weekday).sum()[metric].max()

    bars = (
        alt.Chart(df_yt_analytics)
        .mark_bar(stroke="RGBA(140,107,254,1)", strokeWidth=2)
        .encode(
            x=alt.X("day(Date):O", title=None),
            y=alt.Y(f"sum({metric}):Q", title=None),
            color=alt.condition(
                f"datum['sum_{metric}'] >= {max_value}",
                alt.value("RGBA(154,232,255,1)"),
                alt.value("RGBA(140,107,254,0.15)"),
            ),
        )
        .properties(width="container", height=200)
    )

    text = bars.mark_text(
        baseline="bottom",
        fill="gray",
        dy=-2,
    ).encode(
        text=f"sum({metric}):Q",
    )

    chart = (bars + text).configure_scale(bandPaddingInner=0.2)

    return chart


# ## Load and wrangle data

# In[8]:


with open("./assets/youtube_analytics_data.json", "r") as f:
    yt_analytics_data = json.load(f)

yt_analytics_rows = yt_analytics_data["rows"]
yt_analytics_columns = yt_analytics_data["columns"]

df_yt_analytics, year, last_sample_date = youtube_analytics_to_df(yt_analytics_rows, yt_analytics_columns)

df_yt_last_28_days = get_last_28_days(df_yt_analytics, last_sample_date)


# ## Build metric pages

# In[9]:


yt_overview_pages = []
for metric in df_yt_last_28_days.columns[:-1]:
    metric_sum = round(df_yt_last_28_days[metric].sum(), 2)
    yt_overview_pages.append(
        dp.Group(
            dp.Group(
                dp.Plot(plot_metric_time_series(metric, df_yt_last_28_days)),
                dp.Plot(plot_metric_popular_day(metric, df_yt_last_28_days)),
                columns=2,
            ),
            dp.Plot(plot_calendar_heatmap(metric, df_yt_analytics)),
            label=f"{metric}: {metric_sum}",
        )
    )

# Placeholder pages for Twitter and Facebook channels.
blank_overview_pages = []
for metric in df_yt_last_28_days.columns[:-1]:
    blank_overview_pages.append(
        dp.Group(
            "Placeholder",
            label=f"{metric}",
        )
    )


# ## Build social media channel pages

# In[10]:


social_media_pages = [
    dp.Select(blocks=yt_overview_pages, type=dp.SelectType.TABS, label="YouTube"),
    dp.Select(blocks=blank_overview_pages, type=dp.SelectType.TABS, label="Twitter"),
    dp.Select(blocks=blank_overview_pages, type=dp.SelectType.TABS, label="Facebook"),
]


# ## Build header and overview blocks

# In[11]:


banner_block = dp.Plot(plot_banner(df_yt_analytics))

period_block = dp.BigNumber(
    heading=f"{last_sample_date.strftime('%d %b')} - {last_sample_date.strftime('%d %b')} {last_sample_date.strftime('%Y')}",
    value="Last 28 days",
)

introduction_block = dp.Text(
    """This report highlights user engagement with our social media channels in 2022. 
            
The report covers [YouTube](#), [Twitter](#), and [Facebook](#)."""
)


# ## Build report

# In[13]:


v = dp.Blocks(
    # header material
    banner_block,
    "# Social media dashboard",
    dp.Group(
        introduction_block,
        period_block,
        columns=2,
    ),
    # analytics page per social media channel (e.g. YouTube, Twitter, etc.)
    dp.Select(
        blocks=social_media_pages,
        type=dp.SelectType.TABS,
    ),
)

dp.save_report(v, path="template.html", open=True)
