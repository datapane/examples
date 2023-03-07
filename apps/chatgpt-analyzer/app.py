import duckdb
import json
import openai
import altair as alt
import datapane as dp
import pandas as pd

openai.api_key = "" # Enter your openAI key

def ask_chatgpt(question):
    
    completion = openai.ChatCompletion.create(
      model="gpt-3.5-turbo", 
      messages=[{"role": "user", "content": question}]
    )
    
    return completion['choices'][0]['message']['content']

def ask_viz_question(df, user_question):
        
    question = f"""
    Given a dataset with the following dtypes:
    
    {df.dtypes}, 
    
    Write me a vega_lite v5 specification for a plot with the following instructions: {user_question}. Do not
    do any transformations on the data (such as averages or aggregations) yourself. The data must not change. All transformations must happen in vega_lite, but only include the first 10 rows of the dataset. No not return any commentary, and only return JSON."""
        
    vega_spec = ask_chatgpt(question)

    result_dict = json.loads(vega_spec)

    # Load our dataset into the spec
    result_dict['data']['values'] = json.loads(df.to_json(orient="records"))
        
    plot = alt.Chart.from_json(json.dumps(result_dict))

    return [
        plot,
        dp.Toggle(dp.Code(vega_spec), label='Show vega-lite spec'),
    ]

def ask_data_question(df, user_question):

    con = duckdb.connect()

    con.execute("CREATE TABLE my_table AS SELECT * FROM df")
    con.execute("INSERT INTO my_table SELECT * FROM df")    
    
    table_description = con.execute('DESCRIBE').fetchall()[0]
    schema = [{'column':x, 'type':table_description[2][i]} for i,x in enumerate(table_description[1])] 
    
    question = f"""
    Given a duckdb database with a table named 'my_table' with the following schema:
    
    {schema}, 
    
    Write me a duckdb compatible sql query for the following instructions: {user_question}. Remember the table name is always 'my_table'. Return only the SQL statement, with no commentary.
    """
    
    generated_query = ask_chatgpt(question)
    sample = con.execute(generated_query).df()

    return [
        dp.DataTable(sample), 
        dp.Toggle(dp.Code(generated_query), label='Show SQL Query')
    ]

def ask_question(params, user_question, question_type, session):
    df = session['df']
    
    question_f = ask_data_question if question_type == "Dataset" else ask_viz_question
    
    return [
        dp.Divider(),
        f"<h4>🙋‍♂️ {user_question}</h4>",
        f"<h4 style='text-align:right'>🤖 Here's your {question_type}</h4>",
        dp.Group(blocks=question_f(df, user_question)),
    ]

def load_file(params, file, session):
    df = pd.read_csv(file)
    
    # Trim whitespace as it confuses chatgpt
    df.columns = df.columns.str.strip()
    
    # Replace spaces with _
    df.columns = df.columns.str.replace(' ', '_')

    session['df'] = df
    
    return [
        dp.DataTable(df),
        dp.Compute(
                ask_question, 
                target='results',
                swap=dp.Swap.PREPEND,
                controls=dict(
                    user_question=dp.TextBox(label='What do you want to know?'), 
                    question_type=dp.Choice(label='What type of result?', 
                    options=['Visualization', 'Dataset']
                )
            )
        ),
        dp.Group("Your results will appear here!", name='results')
    ]

upload_view = [
    dp.Text("## 🧙‍ Upload a CSV to analyze"),
    dp.Form(load_file, controls=dict(
        file=dp.File(label='Choose your file...'),
    )),
]

dp.serve_app(upload_view)