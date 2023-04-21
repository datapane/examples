import pandas as pd
import altair as alt
import hranalytics as hr
import datapane as dp
import seaborn as sns

def dp_theme():
    font = "Helvetica"
    base_size = 16
    lg_font = base_size * 1.25
    sm_font = base_size * 0.8  # st.table size
    xl_font = base_size * 1.75
    font_color = "#1f2937"
    return {
        "config" : {
            "title": {
                "fontSize": base_size,
                "font": font,
                "anchor": "start", # equivalent of left-aligned.
                "fontColor": font_color,
                "fontWeight": 400,
                "offset": 14,
            },
             "axis": {
                "titleFont": font,
                "titleColor": font_color,
                "titleFontSize": sm_font,
                "labelFont": font,
                "labelColor": font_color,
                "labelFontSize": sm_font,
                "grid": True,
                "gridColor": "#fff",
                "gridOpacity": 1,
                "domain": False,
                # "domainColor": font_color,
                "tickColor": font_color,
                "titleFontSize": sm_font,
                "titlePadding": 10,
                "labelPadding": 4,
            },
              "legend": {
                "labelColor": font_color,
                "labelFontSize": 11,
                "padding": 1,
                "symbolSize": 30,
                "symbolType": 'square',
                "titleColor": font_color,
                "titleFontSize": 14,
                "titlePadding": 10,
              },
            "view":{
             "strokeWidth":0
            }
        }
    }

alt.themes.register('dp_theme', dp_theme)
alt.themes.enable('dp_theme')

cm = sns.light_palette("green", as_cmap=True)

df_raw = pd.read_csv('./HRDataset_v14.csv')
df = df_raw.apply(lambda x: x.str.strip() if x.dtype == "object" else x)

hr_data = df

plots = [
    hr.plot_salary_distribution(hr_data),
    hr.plot_employees_by_dept(hr_data),
    hr.plot_gender_distribution(hr_data),
    hr.plot_performance_by_department(hr_data),
    hr.plot_employee_satisfaction(hr_data)
]

kpis = [
    dp.BigNumber("Total Employees", hr.total_employees(hr_data)), 
    dp.BigNumber("Average Salary", f"${round(hr.average_salary(hr_data))}"),
    dp.BigNumber("Gender Diversity (% Male)", round(hr.gender_diversity(hr_data), 2)),
    dp.BigNumber("Turnover Rate (%)", round(hr.turnover_rate(hr_data), 2)),
    dp.BigNumber("Average Employee Satisfaction", f"{round(hr.average_employee_satisfaction(hr_data), 2)} / 5")
]

hr_data['IsTerminated'] = hr_data['Termd']
top_features = hr.key_drivers_of_attrition(hr_data)
styled_top_features = top_features[['Features', 'ScaledImportance']].style.background_gradient(cmap=cm)

most_at_risk = hr.predict_employee_attrition(hr_data)
styled_most_at_risk = most_at_risk.style.background_gradient(cmap=cm)

def benchmark_employee(employee_name):
    benchmark = hr.benchmark_employee(hr_data, employee_name)
    benchmark_styled = benchmark.style.bar(subset='Percentile', color='#a5b4fc')
    return dp.Table(benchmark_styled)

def breakdown(col1,col2):
    if col1 not in hr_data.columns or col2 not in hr_data.columns:
        raise ValueError("One or both of the specified columns are not found in the dataset.")

    if col1 == col2:
      return dp.Text("You cannot breakdown by the same two columns! Please choose two different columns.")
    # Group by the two columns and count the occurrences
    grouped_data = hr_data.groupby([col1, col2]).size().reset_index(name='Count')

    # Create the Altair chart
    chart = alt.Chart(grouped_data).mark_bar().encode(
        x=alt.X(f'{col1}:N', title=col1),
        y=alt.Y('Count:Q', title='Count'),
        color=alt.Color(f'{col2}:N', legend=alt.Legend(title=col2)),
        tooltip=[alt.Tooltip(f'{col1}:N', title=col1), alt.Tooltip(f'{col2}:N', title=col2), alt.Tooltip('Count:Q', title='Count')]
    ).properties(
        title=f'Breakdown of {col1} by {col2}',
        width=600,
        height=400
    )

    return chart

def find_categorical_columns(data, unique_value_threshold = 10):
    categorical_columns = []

    for column in data.columns:
        if data[column].nunique() <= unique_value_threshold:
            categorical_columns.append(column)

    return categorical_columns

cat_columns = find_categorical_columns(hr_data)

v = dp.View(
    dp.Page(
        dp.Group(*kpis, columns=3),
        dp.Group(*plots, columns=2),
        title='Key KPIs',
    ),
    dp.Page(
        dp.Select(
            dp.Table(styled_top_features, label='Top drivers'),
            dp.Table(styled_most_at_risk, label='Most at risk employees'),
        ),
        title='Attrition Prediction',
    ),
    dp.Page(
        dp.Form(
            controls=[
                dp.Choice(options=list(df['Employee_Name'].unique()), name='employee_name')
            ],
            on_submit=benchmark_employee,
        ),
        title='Employee Benchmark Tool'
    ),
    dp.Page(
        dp.Form(
            controls=[
                dp.Choice(options=cat_columns, name='col1', label='Breakdown...'),
                dp.Choice(options=cat_columns, name='col2', label='by...')
            ],
            on_submit=breakdown,
        ),
        title='Breakdown'
    ),

)
dp.serve_app(v)
