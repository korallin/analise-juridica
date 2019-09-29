#!/usr/bin/python
# -*- coding: utf-8 -*-

import pandas as pd
import seaborn as sns
import sys


def get_page_rank_relevance_measure(filename):
    """
    """
    # sheet_name = "conjunto de todas as informações"
    sheet_name = 0
    df = pd.read_excel(filename, sheet_name=sheet_name, skiprows=1, skipfooter=86)
    cols_to_keep = [2, 4]
    df = df[df.columns[cols_to_keep]]
    df.columns = ["$PR_1$", "$PR_2$"]
    return df


def get_intersection_decisions_dataframe(filename):
    """
    """
    sheet_name = "PageRank_versions_decisions_intersection"
    df = pd.read_excel(filename, sheet_name=sheet_name, skiprows=1, skipfooter=13)
    cols_to_keep = [1]
    df = df[df.columns[cols_to_keep]]
    df.columns = ["Intersection of $PR_1$ and $PR_2$"]
    return df


def plot_robustness_graph(df_perturbances, df_intersect):
    """
    """
    df = df_perturbances.join(df_intersect)
    df["Attack level"] = ["10%", "20%", "30%"]
    df.rename(columns={1: "$PR_1$", 2: "$PR_2$", "Intersect": "Intersection of $PR_1$ and $PR_2$"})
    df = df.set_index("Attack level")

    sns.set()
    ax = sns.lineplot(data=df, linewidth=2.5)
    ax.set(xlabel="Attack level", ylabel="PageRankTop100")
    fig = ax.get_figure()
    fig.savefig("PageRankTop100_disturbance.png")


if __name__ == "__main__":
    filename = sys.argv[1]

    plot_robustness_graph(filename)

    # "/home/jackson/programming/ms_project/analise-juridica/sandbox/page_rank_analysis_results_v5/page_rank_sumarized_data_post_processed.xlsx"
