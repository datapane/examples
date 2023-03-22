import altair as alt
from vega_datasets import data
import datapane as dp
import pandas as pd
import seaborn as sns
cm = sns.light_palette("green", as_cmap=True)

df = pd.DataFrame(data.iris())

def make_plot(params):
    return [alt.Chart(df).mark_point().encode(x=params['x'], y=params['y'], color='species'), df]
    
view = dp.Blocks(
    dp.Select(
        dp.Group(
            dp.Form(
                make_plot,
                controls=dp.Controls(
                  dp.Choice(options=list(df.columns), name='x'), 
                  dp.Choice(options=list(df.columns), name='y')
                 ),
                submit_label='Try me'                
            ),
            label="Interactive function",
        ),
        dp.Group(
            "# Dataset information",
            df.describe(),
            dp.Table(df.style.background_gradient(cmap=cm)),
            label='Dataset information'
        )
    )
)

dp.serve_app(view, embed_mode=True)
