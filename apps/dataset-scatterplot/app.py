import typing as t

import datapane as dp
import pandas as pd
import altair as alt

import datapane_components as dc
from datapane_components import datasets


def plot_dataset(params: t.Dict, session: t.Dict) -> dp.Plot:
    df: pd.DataFrame = session["df"]

    fig = (
        alt.Chart(df)
        .mark_point()
        .encode(
            x=alt.X(params["x_axis"], scale=alt.Scale(zero=False)),
            y=alt.X(params["y_axis"], scale=alt.Scale(zero=False)),
            color=params["color"],
            tooltip=list(df.columns),
        )
    )

    return dp.Plot(fig)


def upload_dataset(params: t.Dict, session: t.Dict) -> dp.View:
    df = datasets.load_dataset(params)
    columns = list(df.columns)
    session["df"] = df

    plot_controls = dp.Controls(
        x_axis=dp.Choice(options=columns, initial=columns[0]),
        y_axis=dp.Choice(options=columns, initial=columns[0]),
        color=dp.Choice(options=columns, initial=columns[0]),
    )

    return dp.View(
        dp.DataTable(df),
        dp.Group(
            dp.Form(
                on_submit=plot_dataset,
                target="plot",
                submit_label="Plot",
                controls=plot_controls,
            ),
            dp.Empty(name="plot"),
            columns=2,
        ),
    )


upload_and_display = dp.View(
    dp.Form(
        on_submit=upload_dataset,
        target="dataset",
        submit_label="Upload",
        controls=datasets.data_choice_with_file,
    ),
    dc.divider(),
    dp.Text("Please upload a dataset.", name="dataset"),
)

dp.serve_app(upload_and_display)
