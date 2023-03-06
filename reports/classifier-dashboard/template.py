#!/usr/bin/env python
# coding: utf-8

# # Classifier performance dashboard

# In[1]:


import altair as alt
import datapane as dp
import json
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix, precision_score, recall_score, f1_score

plt.ioff()


# ## Wrangling and visualisation functions

# In[2]:


def predictions_to_df(id_test, y_test, predictions):
    df_predictions = pd.DataFrame(
        {
            "sample": id_test,
            "true class": y_test,
            "predicted class": predictions,
        },
        index=id_test,
    )

    df_predictions["true positive"] = df_predictions["true class"] == df_predictions["predicted class"]
    return df_predictions


# In[3]:


def plot_banner(X_test, y_test):
    cm_sequential = [
        "Purples",
        "Blues",
        "Greens",
        "YlOrBr",
        "OrRd",
        "PuRd",
        "RdPu",
        "BuPu",
        "GnBu",
        "PuBu",
        "YlGnBu",
        "PuBuGn",
        "BuGn",
        "YlGn",
    ]

    plt_banner, axes = plt.subplots(ncols=26, nrows=2, figsize=(26, 2))
    for ax, image, truth in zip(axes.flatten(), np.array(X_test), y_test):
        ax.set_axis_off()
        image = image.reshape(8, 8)
        ax.imshow(image, cmap=plt.cm.get_cmap(cm_sequential[truth]), interpolation="nearest")
    plt_banner.tight_layout()
    plt.close()
    return plt_banner


# In[4]:


def plot_confusion_matrix(y_test, predictions, class_labels):
    cm_x, cm_y = np.meshgrid(class_labels, class_labels)
    cm = confusion_matrix(y_test, predictions)
    df_cm = pd.DataFrame(
        {
            "Predicted": cm_x.ravel(),
            "True": cm_y.ravel(),
            "z": cm.ravel(),
        }
    )

    heatmap = (
        alt.Chart(df_cm)
        .mark_rect()
        .encode(x="Predicted:O", y="True:O", color="z:Q")
        .properties(width="container", height=416)
    )

    text = heatmap.mark_text(baseline="middle").encode(
        text="z:Q",
        color=alt.condition(alt.datum.z < 50, alt.value("gray"), alt.value("white")),
    )

    fig = heatmap + text
    return fig, cm


# In[5]:


def plot_preview(X_test, predictions, y_test):
    fig, axes = plt.subplots(ncols=16, nrows=14, figsize=(11, 10))
    for ax, image, prediction, truth in zip(axes.flatten(), np.array(X_test), predictions, y_test):
        ax.set_axis_off()
        image = image.reshape(8, 8)
        if prediction == truth:
            col = plt.cm.gray_r
        else:
            col = plt.cm.Reds
        ax.imshow(image, cmap=col, interpolation="nearest")
        ax.set_title(f"pred: {prediction}")
    fig.tight_layout()
    plt.close()
    return fig


# In[6]:


def plot_tp_trade_offs(df_tp_trade_offs, class_labels):
    df_tp_trade_offs["clf_name"] = df_tp_trade_offs.index
    fig = (
        alt.Chart(df_tp_trade_offs)
        .transform_window(index="count()")
        .transform_fold(class_labels)
        .mark_line()
        .encode(
            x=alt.X(
                "key:N",
                scale=alt.Scale(
                    zero=False,
                    padding=0,
                ),
                axis=alt.Axis(grid=True),
                title="Digit",
            ),
            y=alt.Y("value:Q", scale=alt.Scale(zero=False), title="True Positives"),
            color=alt.Color("clf_name:N", scale=alt.Scale(scheme="viridis")),
            detail="clf_name:N",
            strokeWidth=alt.value(3),
            opacity=alt.value(0.7),
            tooltip=["clf_name:N", "key:N", "value:Q"],
        )
        .configure_legend(orient="top", title=None)
        .properties(width="container", height=200)
    )
    return fig


# ## Report blocks functions

# In[7]:


def build_metrics_group(y_test, predictions):
    metrics_block = dp.Group(
        dp.BigNumber(
            "Precision",
            value="{:.2f}".format(precision_score(y_test, predictions, average="weighted")),
        ),
        dp.BigNumber(
            "Recall",
            value="{:.2f}".format(recall_score(y_test, predictions, average="weighted")),
        ),
        dp.BigNumber(
            "F1-score",
            value="{:.2f}".format(f1_score(y_test, predictions, average="weighted")),
        ),
        columns=3,
    )
    return metrics_block


# In[8]:


def build_narrative_block(clf_name):
    narrative_block = dp.Text(file=f"./assets/discussion/{clf_name}.md").format(
        clf_name=clf_name.lower(),
        repo=dp.Code(
            code=f"git clone https://github.com/datapane/{clf_name.lower()}-digits.git",
            language="bash",
        ),
    )
    return narrative_block


# In[9]:


def build_visualization_blocks(plt_cm, df_predictions, plt_preview):
    visualization_blocks = dp.Select(
        blocks=[
            dp.Plot(plt_cm, label="Confusion Matrix"),
            dp.DataTable(df_predictions, label="Predictions"),
            dp.Plot(plt_preview, label="Preview"),
        ],
        label="Tabs",
        type=dp.SelectType.TABS,
    )
    return visualization_blocks


# ## Load and wrangle data

# In[10]:


with open("./assets/results.json", "r") as f:
    results = json.load(f)

X_test = results["X_test"]
y_test = results["y_test"]
id_test = results["id_test"]
predictions = results["predictions"]
class_labels = [str(x) for x in range(0, 10)]
df_tp_trade_offs = pd.DataFrame(columns=class_labels)


# ## Build classifier pages

# In[11]:


classifier_pages = {}

for clf_name in predictions.keys():
    # wrangle results into dataframe
    df_predictions = predictions_to_df(id_test, y_test, predictions[clf_name])

    # generate confusion matrix
    plt_cm, cm = plot_confusion_matrix(y_test, predictions[clf_name], class_labels)

    # assign TP vector
    df_tp_trade_offs.loc[clf_name, class_labels] = pd.Series(cm.diagonal()).values

    # generate preview image
    plt_preview = plot_preview(X_test, predictions[clf_name], y_test)

    # build page
    classifier_pages[clf_name] = dp.Group(
        build_metrics_group(y_test, predictions[clf_name]),
        dp.Group(
            dp.Group(
                build_narrative_block(clf_name),
                build_visualization_blocks(plt_cm, df_predictions, plt_preview),
                columns=2,
            )
        ),
        label=clf_name,
    )


# ## Build header and overview blocks

# In[12]:


# build banner block
banner_block = dp.Plot(plot_banner(X_test, y_test))

# generate trade-off plot
trade_offs_block = dp.Plot(plot_tp_trade_offs(df_tp_trade_offs, class_labels))


# ## Build report

# In[15]:


v = dp.Blocks(
    # header material
    banner_block,
    "# Classifier Performance Dashboard",
    "This dashboard highlights the performance of multiple classifiers on the [Optical Recognition of Handwritten Digits Data Set](https://archive.ics.uci.edu/ml/datasets/Optical+Recognition+of+Handwritten+Digits).",
    # performance overview
    trade_offs_block,
    # performance breakdown page per classifier
    dp.Select(
        blocks=classifier_pages.values(),
        type=dp.SelectType.TABS,
    ),
)

dp.save_report(v, path="template.html", open=True)
