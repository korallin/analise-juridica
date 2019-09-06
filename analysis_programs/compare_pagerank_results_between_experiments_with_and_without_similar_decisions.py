#!/usr/bin/python
# -*- coding: utf-8 -*-
from pymongo import MongoClient
import pandas as pd


def compare_number_decs_between_experiments(db):
    """
    Checar se número de decisões no banco de dados é coerente com a não inclusão das decisões similares
    Fazer isso comparando número de decisões de experimentos com e sem similares para ambos os PageRanks
    """
    ancient_collections = ["stf_pr_1_acordaos_90_replaced_col_1", "stf_pr_2_acordaos_90_par_1"]
    new_collections = ["stf_pr_1_acordaos_90_no_similars_1", "stf_pr_2_acordaos_90_no_similars_1"]
    print("Number of decisions of experimentos with and without similar decisions")
    for col_ancient, col_new in zip(ancient_collections, new_collections):
        print(col_ancient, col_new)
        print(db[col_ancient].find({}).count(), db[col_new].find({}).count())


def get_db_object():
    """
    """
    client = MongoClient(
        "mongodb://{}:{}@127.0.0.1:57017".format(mongo_user, mongo_password)
    )
    db = client[dbName]
    return db


def get_decisions_collection(db, collection_name):
    """
    """
    page_ranks_iters = []
    selected_keys = {"acordaoId": 1, "pageRank": 1}
    df_collection = pd.DataFrame()
    for i in range(1, 11):
        coll_name_iter_i = collection_name + "_%d" % i
        page_ranks_cursor = db[coll_name_iter_i].find({}, selected_keys).sort([("pageRank", -1)]).limit(100)
        df = pd.DataFrame(page_ranks_cursor)
        df["collection_iter"] = i
        df.drop("_id", axis=1, inplace=True)
        df_collection = df_collection.append(df)

    return df_collection


def get_intersection_decisions(df1, df2):
    """
    """
    return df1[df1["acordaoId"].isin(df2["acordaoId"])]


def get_intersection_decisions_first_iter(df1, df2):
    """
    """
    df1_iter1 = df1[df1["collection_iter"] == 1]
    df2_iter1 = df2[df2["collection_iter"] == 1]

    df_intersection_decs = get_intersection_decisions(df1_iter1, df2_iter1)
    df_intersection_decs.drop("collection_iter", axis=1, inplace=True)
    return df_intersection_decs


def get_decisions_in_at_least_8_iters_of_10(df_collection):
    """
    """
    df_collection_ids = df_collection["acordaoId"].value_counts()
    df_ids_in_8_to_10_iters = df_collection_ids[df_collection_ids >= 8].reset_index()
    df_ids_in_8_to_10_iters.drop("acordaoId", axis=1, inplace=True)
    df_ids_in_8_to_10_iters = df_ids_in_8_to_10_iters.rename(columns={"index": "acordaoId"})
    return df_ids_in_8_to_10_iters


if __name__ == '__main__':
    db = get_db_object()
    compare_number_decs_between_experiments(db)

    df_with_sim_pr1 = get_decisions_collection(db, "stf_pr_1_acordaos_90_replaced_col")
    df_with_sim_pr2 = get_decisions_collection(db, "stf_pr_2_acordaos_90_par")
    df_without_sim_pr1 = get_decisions_collection(db, "stf_pr_1_acordaos_90_no_similars")
    df_without_sim_pr2 = get_decisions_collection(db, "stf_pr_2_acordaos_90_no_similars")

    df_intersec_with_sim_dec_number = get_intersection_decisions_first_iter(df_with_sim_pr1, df_with_sim_pr2)
    df_intersec_without_sim_dec_number = get_intersection_decisions_first_iter(df_without_sim_pr1, df_without_sim_pr2)
    df_intersec_between_with_and_without_sim_pr1 = get_intersection_decisions_first_iter(df_with_sim_pr1, df_without_sim_pr1)
    df_intersec_between_with_and_without_sim_pr2 = get_intersection_decisions_first_iter(df_with_sim_pr2, df_without_sim_pr2)

    df_ids_in_8_to_10_iters_with_sim_pr1 = get_decisions_in_at_least_8_iters_of_10(df_with_sim_pr1)
    df_ids_in_8_to_10_iters_with_sim_pr2 = get_decisions_in_at_least_8_iters_of_10(df_with_sim_pr2)
    df_ids_in_8_to_10_iters_without_sim_pr1 = get_decisions_in_at_least_8_iters_of_10(df_without_sim_pr1)
    df_ids_in_8_to_10_iters_without_sim_pr2 = get_decisions_in_at_least_8_iters_of_10(df_without_sim_pr2)

    df_robutness_results_pr1_pr2_with_sim = get_intersection_decisions(df_ids_in_8_to_10_iters_with_sim_pr1, df_ids_in_8_to_10_iters_with_sim_pr2)
    df_robutness_results_pr1_pr2_without_sim = get_intersection_decisions(df_ids_in_8_to_10_iters_without_sim_pr1, df_ids_in_8_to_10_iters_without_sim_pr2)
    df_robutness_results_pr1_with_and_without_sim = get_intersection_decisions(df_ids_in_8_to_10_iters_with_sim_pr1, df_ids_in_8_to_10_iters_without_sim_pr1)
    df_robutness_results_pr2_with_and_without_sim = get_intersection_decisions(df_ids_in_8_to_10_iters_with_sim_pr2, df_ids_in_8_to_10_iters_without_sim_pr2)

    with pd.ExcelWriter("comparacao_execucoes_pagerank_com_similares_e_sem.xlsx") as writer:
        df_intersec_with_sim_dec_number.to_excel(writer, sheet_name="pr1 pr2 c sim e todas dec", index=False)
        df_intersec_without_sim_dec_number.to_excel(writer, sheet_name="pr1 pr2 só citac e todas dec", index=False)
        df_intersec_between_with_and_without_sim_pr1.to_excel(writer, sheet_name="pr1 sim vs só cit todas dec", index=False)
        df_intersec_between_with_and_without_sim_pr2.to_excel(writer, sheet_name="pr2 sim vs só cit todas dec", index=False)
        df_robutness_results_pr1_pr2_with_sim.to_excel(writer, sheet_name="dec em 8 a 10 ex pr1 pr2 c sim", index=False)
        df_robutness_results_pr1_pr2_without_sim.to_excel(writer, sheet_name="dec em 8 a 10 ex pr1 pr2 só cit", index=False)
        df_robutness_results_pr1_with_and_without_sim.to_excel(writer, sheet_name="dec em 8 a 10 pr1 sim vs só cit", index=False)
        df_robutness_results_pr2_with_and_without_sim.to_excel(writer, sheet_name="dec em 8 a 10 pr2 sim vs só cit", index=False)
