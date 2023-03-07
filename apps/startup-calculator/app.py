import altair as alt
import pandas as pd
import datapane as dp


def calculate_runway(
    current_cash: float,
    initial_revenue: float,
    monthly_burn: float,
    weekly_growth_percent: float,
    forecast_length_years: int,
    cash_injection: float,
    cash_injection_offset: int,
) -> dp.Blocks:
    forecast_length_days = 365 * forecast_length_years
    monthly_growth_rate = pow((1 + weekly_growth_percent / 100), 4) - 1
    today = pd.to_datetime("today")
    end_forecast = today + pd.Timedelta(forecast_length_days, unit="d")

    # empty df
    df = pd.DataFrame(columns=[])
    idx = pd.date_range(today, end_forecast, freq="m")
    df = df.reindex(idx, fill_value=0)
    df.index.names = ["date"]
    df.reset_index(inplace=True)

    df["burn"] = monthly_burn  # Burn remains constant for now.
    df["revenue_0g"] = initial_revenue
    df["injection"] = 0

    # Set initial cash and revenue
    df.loc[0, "cash_0g"] = current_cash
    df.loc[0, "cash_dg"] = current_cash
    df.loc[0, "revenue_dg"] = initial_revenue

    # Cas injection (e.g. R&D tax or fundraise)
    df.loc[cash_injection_offset + 1, "injection"] = cash_injection  # 0dx adjustment

    for i in range(1, len(df)):
        prev = df.loc[i - 1]
        df.loc[i, "cash_0g"] = prev["cash_0g"] - prev["burn"] + prev["injection"] + prev["revenue_0g"]
        df.loc[i, "cash_dg"] = prev["cash_dg"] - prev["burn"] + prev["injection"] + prev["revenue_dg"]
        df.loc[i, "revenue_dg"] = prev["revenue_dg"] * (1 + monthly_growth_rate)

    start_revenue = initial_revenue if initial_revenue > 100 else 100
    scale = (-current_cash, current_cash * 2)

    monthly_growth_percent = weekly_growth_percent * 4

    slider = alt.binding_range(min=0, max=100, step=0.1, name="Monthly growth rate (%)")
    selector = alt.selection_single(
        fields=["month_growth"],
        bind=slider,
        init={"month_growth": monthly_growth_percent},
    )

    base = (
        alt.Chart(df[["date", "cash_0g"]])
        .transform_window(
            # Use count() to find out the current month we're on (i.e. the index),
            # as we use that as the power for our growth rate
            index="count()"
        )
        .transform_calculate(
            # Transform a % growth rate (i.e. 7) into sometime useful (i.e. 1.07).
            # Raise that to our current month (i.e. for month 2, 1.07 ** 2 = ~1.145), and
            # multiply that by our revenue amount (~1.145 * 500)
            forecast_revenue=((1 + (selector.month_growth / 100)) ** alt.datum.index)
            * start_revenue
        )
        .transform_window(
            # Take what is in practice the cumulative product of revenue (i.e. total revenue earned so far)
            forecast_total_revenue="sum(forecast_revenue)",
            frame=[None, 0],
        )
        .transform_calculate(
            # Add cumprod to current cash to find cash standing (i.e. if we have £100k cash,
            # and 10 months of £10k revenue, we have £200k now)
            adj_cash=alt.datum.cash_0g
            + alt.datum.forecast_total_revenue
        )
        .encode(x="yearmonth(date):T")
    )

    cash = base.encode(y=alt.Y("adj_cash:Q", scale=alt.Scale(domain=scale))).mark_area(opacity=0.75)
    revenue = base.encode(y="forecast_total_revenue:Q").mark_line(color="#f26522", size=5)
    revenue_growth = base.encode(y="forecast_revenue:Q").mark_line(color="purple", size=5)

    charts = cash + revenue + revenue_growth

    chart_final = charts.add_selection(selector).interactive().properties(width="container")

    return dp.Blocks(
        dp.Group(
            blocks=[
                dp.BigNumber(value=f"${round(monthly_burn)}", heading="Monthly outgoings"),
                dp.BigNumber(
                    value=f"${current_cash}",
                    heading="Cash in bank",
                    is_upward_change=True,
                    change=7,
                ),
            ],
            columns=2,
        ),
        dp.Select(
            blocks=[
                dp.Group(
                    blocks=[
                        """This plot models cash and revenue, dependent on various other growth scenarios and based on this month's burn. 
                    - Blue area is cash remaining
                    - Orange line is the cumulative sum of all revenue
                    - Purple line is monthly revenue
                    > Drag the slider to adjust growth rate. The growth rate at which the blue area never crosses 0 is the growth you need to achieve **[Default Alive](http://paulgraham.com/aord.html)**.
                    """,
                        chart_final,
                    ],
                    label="Interactive Plot",
                ),
                dp.Group(
                    blocks=[
                        "> In this dataset, `cash_0g`/`revenue_0g` presumes no further growth, whereas "
                        + "`cash_dg`/`revenue_dg` presumes growth at the current rate continues.",
                        dp.DataTable(df),
                    ],
                    label="Interactive Dataset",
                ),
            ]
        ),
    )


# main view and controls
controls = dict(
    current_cash=dp.NumberBox(initial=10000),
    forecast_length_years=dp.Range(min=1, max=10, initial=1),
    weekly_growth_percent=dp.NumberBox(),
    initial_revenue=dp.NumberBox(),
    monthly_burn=dp.NumberBox(),
    cash_injection=dp.NumberBox(),
    cash_injection_offset=dp.NumberBox(),
)

v = dp.View(
    "# Finance model",
    dp.Group(
        dp.Form(
            controls=controls,
            on_submit=calculate_runway,
            target="result",
        ),
        dp.Empty(name="result"),
        columns=2,
        widths=[1, 3],
    ),
)

dp.serve_app(v)
