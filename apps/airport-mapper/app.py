import typing as t

import datapane as dp
import altair as alt
from vega_datasets import data

# globals
alt.data_transformers.disable_max_rows()
states = alt.topo_feature(data.us_10m.url, feature="states")
background = (
    alt.Chart(states)
    .mark_geoshape(
        fill="#f1f5f9",
        stroke="#818cf8",
    )
    .project("albersUsa")
    .properties(height=600, width="container")
)

# data
df = data.airports()

def get_sample(params: t.Dict) -> t.List:
    state = params["state"]
    sample = df[df['state'] == state]
    
    points = (
        alt.Chart(sample)
        .mark_circle(color="#4f46e5")
        .encode(longitude="longitude:Q", latitude="latitude:Q", size=alt.value(20), tooltip="name")
        .project(
            "albersUsa",
        )
    )
    return [background + points, dp.DataTable(sample)]


v = dp.View(
    dp.Page(
        dp.Text("# Airport searcher"),
        dp.Form(
            cache=True,
            on_submit=get_sample,
            controls=dp.Controls(state=dp.Choice(options=list(df["state"].dropna().unique()))),
        ),
        title="Filtered Dataset",
    ),
    dp.Page(dp.DataTable(df), title="Full Dataset"),
)
dp.serve_app(v)
