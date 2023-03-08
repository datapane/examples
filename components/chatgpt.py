from os import getenv
import json

import altair as alt
import datapane as dp
import pandas as pd
import duckdb
import openai

# Enter your openAI key or set within the environment
openai.api_key = getenv("OPENAI_API_KEY", "")


def _ask_chatgpt(question: str) -> str:
    completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": question}])

    return completion["choices"][0]["message"]["content"]


def ask_viz_question(df: pd.DataFrame, user_question: str) -> dp.Select:
    question = f"""
    Given a dataset with the following dtypes:

    {df.dtypes}, 

    and where the sample of the first 10 rows is:

    {df.head(10)}

    Write me a valid vega_lite v4 specification based on the instructions for a visualization: {user_question}. 
    Do not do any transformations on the data (such as averages or aggregations) yourself. 
    This vega_lite spec must not have a url field, instead data will be specified in the values field.
    Only include a single row of data in the values field.
    JSON must not contain the characters //
    Automatically choose the best type of plot mark based on your understanding of the schema (for instance, scatter, line, points, area).
    All transformations must happen in vega_lite.
    Your response must not have any comments in, or contain the characters //. It must be valid JSON.
    Do not return any commentary, and only return JSON which is a valid vega_lite spec."""

    vega_spec = _ask_chatgpt(question)

    try:
        result_dict = json.loads(vega_spec)

        # Load our dataset into the spec
        result_dict["data"]["values"] = json.loads(df.to_json(orient="records"))

        plot = alt.Chart.from_json(json.dumps(result_dict))
    except Exception as e:
        msg = f"```Exception: {e}```\nVega-spec:```{vega_spec}```"
        print(msg)
        return dp.Text(msg)

    return dp.Select(dp.Plot(plot, label="Plot"), dp.Code(vega_spec, language="json", label="Show vega-lite spec"))


def ask_data_question(df: pd.DataFrame, user_question: str) -> dp.Select:
    # insert the df into duck so we can run sql on it
    con = duckdb.connect()
    con.execute("CREATE TABLE my_table AS SELECT * FROM df")
    con.execute("INSERT INTO my_table SELECT * FROM df")

    table_description = con.execute("DESCRIBE").fetchall()[0]
    schema = [{"column": x, "type": table_description[2][i]} for i, x in enumerate(table_description[1])]

    question = f"""
    Given a duckdb database with a table named 'my_table' with the following schema:

    {schema}, 

    Write me a duckdb compatible sql query for the following instructions: {user_question}. Remember the table name is always 'my_table'. Return only the SQL statement, with no commentary.
    """

    generated_query = _ask_chatgpt(question)
    sample = con.execute(generated_query).df()

    return dp.Select(
        dp.DataTable(sample, label="Dataset"), dp.Code(generated_query, language="sql", label="Show SQL Query")
    )
