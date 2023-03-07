import datapane as dp
import pandas as pd
import altair as alt

DATA_SRC = "http://streamlit-demo-data.s3-us-west-2.amazonaws.com/agri.csv.gz"
df = pd.read_csv(DATA_SRC)
df = df.set_index("Region")


def process(countries: str) -> dp.Group:
    data = df.loc[countries]
    data /= 1000000.0
    table_data = data.sort_index()

    data = data.T.reset_index()
    data = pd.melt(data, id_vars=["index"]).rename(
        columns={"index": "year", "value": "Gross Agricultural Product ($B)"}
    )

    chart = (
        alt.Chart(data)
        .mark_area(opacity=0.3)
        .encode(x="year:T", y=alt.Y("Gross Agricultural Product ($B):Q", stack=None), color="Region:N")
    )

    return dp.Group("### Gross Agricultural Production ($B)", dp.Table(table_data), chart)


dp.serve_app(
    dp.Form(
        on_submit=process,
        controls=dict(countries=dp.MultiChoice(initial=["China", "United States of America"], options=list(df.index))),
    )
)
