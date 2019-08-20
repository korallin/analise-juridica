#!/usr/bin/python
# -*- coding: utf-8 -*-

import pandas as pd
import sys
from openpyxl import load_workbook


def get_top_decisions_8_or_more_times_on_top(file_name, sheet_name):
    df = pd.read_excel(
        file_name,
        sheet_name,
        names=[
            "RANK",
            "DECISION ID",
            "RELATOR",
            "VIRTUAL",
            "NUMBER OF OCCURANCES",
            "TIMES REMOVED",
        ],
    )
    df["RANK"] = pd.to_numeric(df["RANK"], errors="coerce")
    df = df.dropna()
    df = df[df["NUMBER OF OCCURANCES"] >= 8]

    return df


def get_decisions_on_top_page_rank_lst(
    file_name, iterator, pr1_sheet_name_pattern, pr2_sheet_name_pattern
):
    df_pr_1 = []
    df_pr_2 = []
    for i in iterator:
        df = get_top_decisions_8_or_more_times_on_top(
            file_name, pr1_sheet_name_pattern % (i)
        )
        df_pr_1.append(df)
        df = get_top_decisions_8_or_more_times_on_top(
            file_name, pr2_sheet_name_pattern % (i)
        )
        df_pr_2.append(df)

    return df_pr_1, df_pr_2


def get_intersection_dataframe(
    categories_str_column_name,
    iterator,
    decisions_df_pr1_intersect,
    decisions_df_pr2_intersect,
):
    intersection_decisions_data_table = [
        [
            "Intersection of decisions in the PageRankTop100 between PageRank versions 1 and 2",
            "",
        ],
        [categories_str_column_name, "Número de decisões na intersecção"],
    ]
    for i, df_pr_1, df_pr_2 in zip(
        iterator, decisions_df_pr1_intersect, decisions_df_pr2_intersect
    ):
        intersect_size = len(
            df_pr_1[df_pr_1["DECISION ID"].isin(df_pr_2["DECISION ID"])]
        )
        if categories_str_column_name == "Ministro":
            row = [df_pr_1["RELATOR"].unique()[0], intersect_size]
        else:
            row = ["{}% de decisões".format(i), intersect_size]

        intersection_decisions_data_table.append(row)

    df = pd.DataFrame(
        intersection_decisions_data_table[1:],
        columns=intersection_decisions_data_table[0],
    )
    return df


def pagerank_intersection_analysis():

    dataset_spreadsheet_filename = sys.argv[1]
    analysis_spreadsheet_filename = sys.argv[2]

    page_rank_perc_kept_dec = [90, 80, 70]
    df_pr_1_total, df_pr_2_total = get_decisions_on_top_page_rank_lst(
        dataset_spreadsheet_filename,
        page_rank_perc_kept_dec,
        "stf_pr_1_acordaos_%s_replaced_col",
        "stf_pr_2_acordaos_%s_par",
    )
    ministers_index = range(1, 11)
    df_pr_1_ministers, df_pr_2_ministers = get_decisions_on_top_page_rank_lst(
        dataset_spreadsheet_filename,
        ministers_index,
        "stf_pr_1_acordaos_90_replaced_col_rel_%s",
        "stf_pr_2_acordaos_90_par_rel_%s",
    )

    df_intersect_total_decs = get_intersection_dataframe(
        "Quantidade de decisões simuladas",
        page_rank_perc_kept_dec,
        df_pr_1_total,
        df_pr_2_total,
    )
    df_intersect_ministers_decs = get_intersection_dataframe(
        "Ministro", ministers_index, df_pr_1_ministers, df_pr_2_ministers
    )

    wb = load_workbook(analysis_spreadsheet_filename)
    writer = pd.ExcelWriter(analysis_spreadsheet_filename)
    writer.book = wb
    writer.sheets = dict((ws.title, ws) for ws in wb.worksheets)

    cols_shift = len(df_intersect_total_decs.columns) + 3
    df_intersect_total_decs.to_excel(
        writer, sheet_name="PageRank_versions_decisions_intersection", index=False
    )
    df_intersect_ministers_decs.to_excel(
        writer,
        sheet_name="PageRank_versions_decisions_intersection",
        index=False,
        startcol=cols_shift,
    )

    writer.save()


if __name__ == "__main__":
    pagerank_intersection_analysis()

# python analysis_programs/calc_intersection_top_decisions_between_pagerank_experiments.py /home/jackson/programming/ms_project/analise-juridica/sandbox/page_rank_analysis_results_v5/page_ranker_analysis.xlsx /home/jackson/programming/ms_project/analise-juridica/sandbox/page_rank_analysis_results_v5/page_rank_sumarized_data_post_processed.xlsx
