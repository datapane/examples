import typing as t
from pathlib import Path

import datapane as dp
import pandas as pd

from components import chatgpt


def ask_question(user_question: str, question_type: str, session: t.Dict) -> t.List:
    df = session["df"]

    if question_type == "Dataset":
        res = chatgpt.ask_data_question(df, user_question)
    else:  # Visualization
        res = chatgpt.ask_viz_question(df, user_question)

    return [
        dp.Divider(),
        f"<h4>🙋‍♂️ {user_question}</h4>",
        f"<h4 style='text-align:right'>🤖 Here's your {question_type}</h4>",
        res,
    ]


def load_file(file: Path, session: t.Dict) -> t.List:
    df = pd.read_csv(file)

    # Trim whitespace as it confuses chatgpt
    df.columns = df.columns.str.strip()

    # Replace spaces with _
    df.columns = df.columns.str.replace(" ", "_")

    session["df"] = df

    return [
        dp.DataTable(df),
        dp.Compute(
            ask_question,
            target="results",
            swap=dp.Swap.PREPEND,
            controls=dict(
                user_question=dp.TextBox(label="What do you want to know?"),
                question_type=dp.Choice(label="What type of result?", options=["Visualization", "Dataset"]),
            ),
        ),
        dp.Group("Your results will appear here!", name="results"),
    ]


upload_view = [
    dp.Text("## 🧙‍ Upload a CSV to analyze"),
    dp.Form(
        load_file,
        controls=dict(
            file=dp.File(label="Choose your file..."),
        ),
    ),
]

dp.serve_app(upload_view)
