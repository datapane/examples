import datapane as dp
import pandas as pd
import altair as alt

dataset = None
columns = None


def plot_dataset(params):
    global dataset

    fig = (
        alt.Chart(dataset)
        .mark_point()
        .encode(
            x=alt.X(params["x_axis"], scale=alt.Scale(zero=False)),
            y=alt.X(params["y_axis"], scale=alt.Scale(zero=False)),
            color=params["color"],
            tooltip=columns,
        )
    )

    return dp.Plot(fig, name="plot")


def upload_dataset(params):
    global dataset, columns
    dataset = pd.read_csv(params["dataset"])
    columns = list(dataset.columns)

    plot_controls = dp.Controls(
        dp.Choice("x_axis", options=columns, initial=columns[0]),
        dp.Choice("y_axis", options=columns, initial=columns[0]),
        dp.Choice("color", options=columns, initial=columns[0]),
    )

    return dp.Group(
        dp.DataTable(dataset),
        dp.Group(
            dp.Function(
                plot_dataset,
                target="plot",
                submit_label="Plot",
                controls=plot_controls,
            ),
            dp.Empty(name="plot"),
            columns=2,
        ),
    )


controls = dp.Controls(
    dp.File("dataset", label="Upload test data"),
)

upload_and_display = dp.View(
    dp.Select(
        blocks=[
            dp.Group(
                dp.Text(
                    "Please upload a dataset.",
                ),
                label="Explore",
                name="dataset",
            ),
            dp.Group(
                dp.Function(
                    upload_dataset,
                    target="dataset",
                    submit_label="Upload",
                    swap=dp.Swap.INNER,
                    controls=controls,
                ),
                label="Upload dataset",
            ),
        ]
    )
)
dp.serve(upload_and_display)
