import typing as t

import pandas as pd
import seaborn as sns
import altair as alt
from vega_datasets import data
import datapane as dp

cm = sns.light_palette("green", as_cmap=True)

df = pd.DataFrame(data.iris())


def make_plot(x: str, y: str) -> t.List[dp.Block]:
    return [alt.Chart(df).mark_point().encode(x=x, y=y, color="species"), df]


view = dp.View(
    dp.Page(
        dp.Form(
            on_submit=make_plot,
            controls=dp.Controls(
                dp.Choice(options=list(df.columns), name="x"), dp.Choice(options=list(df.columns), name="y")
            ),
            submit_label="Try me",
        ),
        title="Interactive function",
    ),
    dp.Page(
        "# Dataset information",
        df.describe(),
        dp.Table(df.style.background_gradient(cmap=cm)),
        title="Dataset information",
    ),
)

dp.serve_app(view, embed_mode=True)
