"""
# Calendar Heatmap

<!-- A single number or change can often be the most important thing in an app. The `BigNumber`component allows you to present KPIs, changes, and statistics in a friendly way to your viewers. You can optionally set intent, and pass in numbers or text.&#x20; -->

The Calendar Heatmap component works with timeseries data to visualize counts over a calendar year.
"""
import typing as t

import datapane as dp
import altair as alt
import pandas as pd


def plot_heatmap(
    metric: str,
    df_yt_analytics: pd.DataFrame,
    *,
    labels: bool = True,
    legend: bool = True,
    color_scheme: str = "viridis",
    height: int = 120,
) -> dp.Plot:
    """Given a dataframe with a Date field,
    plot a heatmap based on count of occurances specified by the `metrics` field

    # The wrangling and visualization functions expect a pandas `DataFrame` with two columns:
    # - `Date`: Unique dates corresponding to some measure.
    # - `Incidents`: containing the value counts, e.g. number of incidents on a particular day.

    """

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
                scale=alt.Scale(scheme=color_scheme),
            ),
            tooltip=["Date", f"{metric}"],
        )
        .configure_view(strokeWidth=0)
        .configure_axis(labelFontSize=12)
        .properties(width="container", height=height)
    )

    return dp.Plot(chart)


def wrangle_df(df: pd.DataFrame, year: t.Optional[int] = None) -> t.Tuple[pd.DataFrame, int, t.Any]:
    """Process the df, filtering for the given `year`, and ensuring that each day for the year has an entry
    The function expect a pandas `DataFrame` with a column containing a `Date` field, consiting of unique dates corresponding to some measure.
    """
    df = df.set_index("Date")
    df.index = pd.DatetimeIndex(df.index)

    # If specific year not specified, use year from last sample date
    last_sample_date = df.index.max()
    if not year:
        year = last_sample_date.year

    # Subsample to samples from the same year
    df = df[df.index.year == year]

    # Fill our DataFrame so there's a sample for every day of the year
    idx = pd.date_range(f"01-01-{year}", f"12-31-{year}")
    df = df.reindex(idx, fill_value=0)
    df["Date"] = df.index

    return df, year, last_sample_date


def example() -> dp.Plot:
    """Return an example heatmap based on sample data"""
    from vega_datasets import data

    # Load and wrangle data
    # The wrangling and visualization functions expect a pandas `DataFrame` with two columns:
    # - `Date`: Unique dates corresponding to some measure.
    # - `Incidents`: containing the value counts, e.g. number of incidents on a particular day.
    df_birdstrikes = data.birdstrikes()
    df_daily_incidents = pd.DataFrame(df_birdstrikes["Flight_Date"].value_counts()).reset_index()
    df_daily_incidents.columns = ["Date", "Incidents"]

    # The name of the value counts column, e.g. `Incidents`, can be anything. If you
    # change the column name, be sure to update the corresponding argument to
    # `plot_calendar_heatmap`.
    df, year, last_sample_date = wrangle_df(df_daily_incidents, year=2000)

    # Now we can pass this `DataFrame` to the provided function for wrangling.
    # Specify the year to be visualized below, or omit it to visualize the latest year available.
    return plot_heatmap("Incidents", df, legend=True, color_scheme="viridis")
