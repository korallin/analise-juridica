#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pymongo import MongoClient
from sklearn.metrics import mean_squared_error
import pandas as pd
import sys


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


def get_decisions_top100(collection_name, db, iterations):
    selected_keys = {
        "acordaoId": 1,
        "pageRank": 1,
        "virtual": 1,
        "relator": 1,
        "citacoes": 1,
        "citadoPor": 1,
    }
    page_ranks_iters = []
    for i in iterations:
        coll_rank = collection_name + "_%d" % i

        page_ranks_cursor = (
            db[coll_rank].find({}, selected_keys).sort([("pageRank", -1)]).limit(100)
        )
        page_ranks_iters.append(list(page_ranks_cursor))

    acordao_ids_iter_lst = [
        [pr["acordaoId"] for pr in pr_list] for pr_list in page_ranks_iters
    ]
    return acordao_ids_iter_lst


def get_mse_pr_top100(db, df_pr_1, df_pr_2, collections_pr_1, collections_pr_2):
    mse_pr1_lst = []
    mse_pr2_lst = []
    for i, (coll_pr_1, coll_pr_2) in enumerate(zip(collections_pr_1, collections_pr_2)):
        acordao_ids_iter_pr_1_lst = get_decisions_top100(coll_pr_1, db, range(1, 11))
        dec_8_or_more_times_pr_1_iter_lst = [
            sum(df_pr_1[i]["DECISION ID"].isin(acordao_ids))
            for acordao_ids in acordao_ids_iter_pr_1_lst
        ]
        acordao_ids_iter_pr_2_lst = get_decisions_top100(coll_pr_2, db, range(1, 11))
        dec_8_or_more_times_pr_2_iter_lst = [
            sum(df_pr_2[i]["DECISION ID"].isin(acordao_ids))
            for acordao_ids in acordao_ids_iter_pr_2_lst
        ]

        mse_pr_1 = mean_squared_error(
            [len(df_pr_1[i])] * len(dec_8_or_more_times_pr_1_iter_lst),
            dec_8_or_more_times_pr_1_iter_lst,
        )
        mse_pr_2 = mean_squared_error(
            [len(df_pr_2[i])] * len(dec_8_or_more_times_pr_2_iter_lst),
            dec_8_or_more_times_pr_2_iter_lst,
        )
        mse_pr1_lst.append(mse_pr_1)
        mse_pr2_lst.append(mse_pr_2)

    return mse_pr1_lst, mse_pr2_lst


if __name__ == "__main__":

    # python calc_page_rank_top_100_mse.py jackson 632799saozei DJs sandbox/page_ranker_analysis.xlsx

    mongo_user = sys.argv[1]
    mongo_password = sys.argv[2]
    dbName = sys.argv[3]
    dataset_spreadsheet_filename = sys.argv[4]

    client = MongoClient(
        "mongodb://{}:{}@127.0.0.1:57017".format(mongo_user, mongo_password)
    )
    db = client[dbName]

    page_rank_perc_kept_dec = [90, 80, 70]
    ministers_index = range(1, 11)
    collections_pr_1 = [
        "stf_pr_1_acordaos_%s_replaced_col" % (perc) for perc in page_rank_perc_kept_dec
    ]
    collections_pr_2 = [
        "stf_pr_2_acordaos_%s_par" % (perc) for perc in page_rank_perc_kept_dec
    ]
    collections_min_pr_1 = [
        "stf_pr_1_acordaos_90_replaced_col_rel_%s" % (i) for i in ministers_index
    ]
    collections_min_pr_2 = [
        "stf_pr_2_acordaos_90_par_rel_%s" % (i) for i in ministers_index
    ]

    df_pr_1_total, df_pr_2_total = get_decisions_on_top_page_rank_lst(
        dataset_spreadsheet_filename,
        page_rank_perc_kept_dec,
        "stf_pr_1_acordaos_%s_replaced_col",
        "stf_pr_2_acordaos_%s_par",
    )
    df_pr_1_ministers, df_pr_2_ministers = get_decisions_on_top_page_rank_lst(
        dataset_spreadsheet_filename,
        ministers_index,
        "stf_pr_1_acordaos_90_replaced_col_rel_%s",
        "stf_pr_2_acordaos_90_par_rel_%s",
    )

    mse_total_pr1_lst, mse_total_pr2_lst = get_mse_pr_top100(
        db, df_pr_1_total, df_pr_2_total, collections_pr_1, collections_pr_2
    )
    mse_min_pr1_lst, mse_min_pr2_lst = get_mse_pr_top100(
        db,
        df_pr_1_ministers,
        df_pr_2_ministers,
        collections_min_pr_1,
        collections_min_pr_2,
    )

    coll_pr_1_lst = []
    coll_pr_2_lst = []
    for (perc, coll_pr_1, coll_pr_2) in zip(
        page_rank_perc_kept_dec, collections_pr_1, collections_pr_2
    ):
        ids_coll_1 = get_decisions_top100(coll_pr_1, db, range(1, 2))[0]
        ids_coll_2 = get_decisions_top100(coll_pr_2, db, range(1, 2))[0]
        intersection = len(set(ids_coll_1).intersection(set(ids_coll_2)))
        print(
            "Intersecção de decisões na primeira iteração para %s:" % (perc),
            intersection,
        )
        coll_pr_1_lst.append(ids_coll_1)
        coll_pr_2_lst.append(ids_coll_2)

    for i, (coll_pr_1, coll_pr_2) in enumerate(
        zip(collections_min_pr_1, collections_min_pr_2)
    ):
        ids_coll_1 = get_decisions_top100(coll_pr_1, db, range(1, 2))[0]
        ids_coll_2 = get_decisions_top100(coll_pr_2, db, range(1, 2))[0]
        intersection = len(set(ids_coll_1).intersection(set(ids_coll_2)))
        print(
            "Intersecção de decisões apenas de ministro %s na primeira iteração:" % (i),
            intersection,
        )

    df_total_pr = pd.DataFrame()
    df_min_pr = pd.DataFrame()
