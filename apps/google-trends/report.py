"""
Datapane App - Google Trends Analysis
"""
from pytrends.request import TrendReq
import altair as alt
import datapane as dp

pytrends = TrendReq(tz=360)
# pytrends = TrendReq(hl='en-US', tz=360, timeout=(10, 25), retries=2,
#                    backoff_factor = 0.1, requests_args = {'verify': False})


def f(keyword: str = "python", timeframe: str = "3-m") -> dp.Select:
    # Choose your query!
    try:
        pytrends.build_payload([keyword], cat=0, timeframe=f"today {timeframe}", geo="", gprop="")
    except Exception as e:
        raise dp.DPClientError("Google trends error") from e
    top_queries = pytrends.related_queries()[keyword]["top"]
    related = top_queries.style.bar(subset=["value"], align="mid", color=["#d65f5f", "#5fba7d"])

    # Plotting our trends
    alt.themes.enable("quartz")
    fig = alt.Chart(top_queries).mark_bar().encode(x="query", y="value").interactive()

    # Interest over Time
    r_o_t = pytrends.interest_over_time().reset_index()
    r_o_t.rename(columns={keyword: "search_volume"}, inplace=True)
    r_o_t_plot = alt.Chart(r_o_t).encode(x="date", y="search_volume").mark_area(line=True).interactive()

    # Geographical Interest
    regions = pytrends.interest_by_region(resolution="COUNTRY", inc_geo_code=True)
    regions.rename(columns={keyword: "search_volume"}, inplace=True)
    regions.reset_index()

    subset = regions.reset_index().sort_values(by="search_volume", ascending=False)[:20]
    bar = alt.Chart(subset).encode(x="geoName", y="search_volume").mark_bar()

    heading = f"""<div style="display:flex;justify-content:center;background: rgb(229, 231, 235);flex-direction: column;text-align: center;margin-bottom: ;">
      <h1 style="font-size: 2em;">SEO forecast analysis of <code style="color: rgb(129, 140, 248); font-size:1.2em;">{keyword}</code></h1>
    </div>"""

    return dp.Select(
        dp.Group(
            dp.HTML(heading),
            "This data was pulled from the Google Trends API for your search term. This report is refreshed _daily_, but please reach out if you need to change the cadence.",
            "## Search volume",
            dp.Plot(r_o_t_plot, caption="Observed data"),
            label="Interest over time",
        ),
        dp.Group(
            "These are queries which are related to your keyword",
            fig,
            label="Related queries",
        ),
        dp.Group(
            "This data was pulled from the Google Trends API",
            dp.DataTable(r_o_t, caption="Time series data"),
            label="Input Dataset",
        ),
    )


v = dp.View(
    dp.Form(
        on_submit=f,
        controls=dict(keyword=dp.TextBox(initial="python"), timeframe=dp.TextBox(initial="3-m")),
    )
)

dp.serve_app(v)
