#!/usr/bin/env python
# coding: utf-8

# # Survey data report
#
# Looking through the [2021 Kaggle Machine Learning & Data Science Survey](https://www.kaggle.com/c/kaggle-survey-2021https://www.kaggle.com/c/kaggle-survey-2021), let's build a report that's focussed on individuals that use Python.

# For those who use Python (`Q7_Part_1`) in segmenting by:
#
# - Current role (`Q5`)
# - Industry (`Q20`)
# - Size of data science team at work (`Q22`)
# - Primary tool (`41`)
#
# For the following questions:
#
# - What Python IDEs (`Q9`),
# - What hosted Python notebook products (`Q10`)
# - What visualization libraries (`Q14`)
# - What BI tools do they use (`Q34-A`)
# - What BI tools do they want to look at (`Q34-B`)
# - Where do you share data analyses (`Q39`)
# - What part of the pipeline? (`Q24`)

# In[1]:


import altair as alt
import datapane as dp
import pandas as pd
import random

alt.data_transformers.disable_max_rows()
pd.options.mode.chained_assignment = None


# ## Block building functions

# In[2]:


def build_segment_distribution(segments, segment_name):
    counts = pd.DataFrame(segments.value_counts()).rename_axis().reset_index()
    counts.columns = [segment_name, "counts"]
    counts

    fig = (
        alt.Chart(counts)
        .mark_bar()
        .encode(
            x=alt.X(counts.columns[0], sort="-y", axis=alt.Axis(labelAngle=-45)),
            y="counts",
            color=alt.Color(segment_name, scale=alt.Scale(scheme="rainbow"), legend=None),
        )
    )

    return dp.Plot(fig)


# In[3]:


def build_question_by_segment(data, segments, segment_name):
    segment_data = data.copy()
    segment_data[segment_name] = segments

    df = segment_data.melt(segment_name).dropna().drop(labels=["variable"], axis=1)

    blocks = []

    df_order = df.value.value_counts().index.tolist()

    fig_all = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X("value:O", sort=df_order, axis=alt.Axis(labelAngle=-45), title=None),
            y=alt.Y(
                f"count({segment_name})",
                axis=alt.Axis(title="Count"),
            ),
            color=alt.Color(segment_name, scale=alt.Scale(scheme="rainbow"), legend=None),
            tooltip=["value:O", f"{segment_name}", f"count({segment_name})"],
        )
    )

    blocks.append(dp.Plot(fig_all, label=f"All {segment_name}"))

    for segment in df[segment_name].unique():
        fig = (
            alt.Chart(df[df[segment_name] == segment])
            .mark_bar()
            .encode(
                x=alt.X("value:O", sort=df_order, axis=alt.Axis(labelAngle=-45), title=None),
                y=alt.Y(
                    f"count({segment_name})",
                    axis=alt.Axis(title="Count"),
                ),
                color=alt.Color(
                    segment_name,
                    scale=alt.Scale(scheme="rainbow", domain=sorted(df[segment_name].unique())),
                    legend=None,
                ),
            )
        )

        blocks.append(dp.Plot(fig, label=segment))

    select_df = dp.Select(
        blocks=blocks,
        type=dp.SelectType.DROPDOWN,
    )
    return select_df


# In[4]:


def build_questions_by_segment(questions, segment, segment_name):
    questions_by_segment = []

    for question, question_data in questions.items():
        questions_by_segment.append(f"## {question}")
        questions_by_segment.append(build_question_by_segment(question_data, segment, segment_name))

    return questions_by_segment


# In[5]:


def shuffled_range(n):
    return random.sample(range(n), k=n)


def build_banner(banner_data):
    words_and_counts = banner_data.melt()["value"].dropna().value_counts()

    words_and_counts = pd.DataFrame(words_and_counts).rename_axis().reset_index()
    words_and_counts.columns = ["word", "count"]

    n = len(words_and_counts)
    x = shuffled_range(n)
    y = shuffled_range(n)

    word_cloud_data = words_and_counts.assign(x=x, y=y)

    base = (
        alt.Chart(word_cloud_data)
        .encode(x=alt.X("x:O", axis=None), y=alt.Y("y:O", axis=None))
        .configure(background="white")
        .configure(background="#eef2ff")
        .properties(width="container", height=100)
    )

    word_cloud = (
        base.mark_text(baseline="middle")
        .encode(
            text="word:N",
            color=alt.Color("count:Q", scale=alt.Scale(scheme="purpleblue")),
            size=alt.Size("count:Q", legend=None, scale=alt.Scale(range=[20, 50])),
        )
        .configure_view(strokeWidth=0)
    )

    return dp.Plot(word_cloud)


# ## Load and wrangle data

# Load dataset

# In[6]:


data = pd.read_csv("assets/kaggle_survey_2021_responses.csv", low_memory=False)
data.head(2)


# Trim whitespace on strings

# In[7]:


data = data.applymap(lambda x: x.strip() if isinstance(x, str) else x)


# Drop descriptive first row

# In[8]:


data = data.iloc[1:]


# Get programming languages for our banner

# In[9]:


banner_data = data.filter(like="Q7_Part")


# Filter to those who use Python (Q7_Part_1)

# In[10]:


data = data[data["Q7_Part_1"] == "Python"]
data


# Merge Jupyter Notebook and Lab, update names

# In[11]:


data["Q9_Part_1"].loc[~data["Q9_Part_1"].isnull()] = "Jupyter NB/Lab"
data["Q9_Part_1"].loc[~data["Q9_Part_11"].isnull()] = "Jupyter NB/Lab"
data["Q9_Part_4"].loc[~data["Q9_Part_4"].isnull()] = "VSCode"


# Drop non-Python and redundant IDE columns

# In[12]:


data = data.drop(labels=["Q9_Part_2", "Q9_Part_3", "Q9_Part_10", "Q9_Part_11", "Q9_Part_12"], axis=1)
data = data.drop(labels=["Q10_Part_15", "Q10_Part_16"], axis=1)


# Drop those that have not indicated employment

# In[13]:


data = data[data["Q5"] != "Student"]
data = data[data["Q5"] != "Currently not employed"]


# Finally, build segments and questions dicts

# In[14]:


data


# In[15]:


segments = {
    "Roles": data["Q5"],
    "Industry": data["Q20"],
    "DS Team Size": data["Q22"],
    "Primary Tool": data["Q41"],
}


questions = {
    "What IDEs are used?": data.filter(like="Q9_Part"),
    "What hosted IDEs are used?": data.filter(like="10_Part"),
    "What BI tools are used?": data.filter(like="Q34_A_Part"),
    "What BI tools are interesting?": data.filter(like="Q34_B_Part"),
    "What visualization libraries are used?": data.filter(like="Q14_Part"),
    "What part of the pipeline?": data.filter(like="Q24_Part"),
    "Where are analyses shared?": data.filter(like="Q39_Part"),
}


# ## Build header and overview blocks

# In[16]:


banner_block = build_banner(banner_data)

stats_group = dp.Group(
    dp.BigNumber(heading="Participants", value=len(data)),
    dp.BigNumber(heading="Segments", value=len(segments)),
    dp.BigNumber(heading="Questions", value=len(questions)),
    columns=3,
)


# ## Build report

# In[17]:


segment_pages = {}

for segment_name, segment in segments.items():
    segment_pages[segment_name] = dp.Group(
        f"## Spread of {segment_name}",
        build_segment_distribution(segment, segment_name),
        *build_questions_by_segment(questions, segment, segment_name),
        label=segment_name,
    )

v = dp.Blocks(
    banner_block,
    "# Kaggle 2021 Survey - Python Edition",
    stats_group,
    dp.Select(
        blocks=segment_pages.values(),
        type=dp.SelectType.TABS,
    ),
)

dp.save_report(v, "template.html", open=True)
