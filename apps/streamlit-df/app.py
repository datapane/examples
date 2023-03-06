# see https://github.com/streamlit/streamlit/blob/87bb89a3b3ac77a5fd7d95c7dbc76335f01e23c1/lib/streamlit/hello/pages/3_DataFrame_Demo.py

import datapane as dp
import pandas as pd
import altair as alt

AWS_BUCKET_URL = "http://streamlit-demo-data.s3-us-west-2.amazonaws.com"
df = pd.read_csv(AWS_BUCKET_URL + "/agri.csv.gz")
df = df.set_index("Region")


def f(params):
    countries = params["countries"]

    if not countries:
        return dp.Text("Please select at least one country.")
    else:
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
            .encode(
                x="year:T",
                y=alt.Y("Gross Agricultural Product ($B):Q", stack=None),
                color="Region:N",
            )
        )

        return dp.Group(
            "### Gross Agricultural Production ($B)",
            dp.Table(table_data),
            chart,
            name="xyz",
        )


controls = dp.MultiChoice("countries", initial=["China", "United States of America"], options=list(df.index))

v = dp.View(dp.Function(f, target="xyz", controls=dp.Controls(controls)), dp.Empty(name="xyz"))

dp.serve(v)
