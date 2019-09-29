#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import pandas as pd
from pymongo import MongoClient
import numpy as np
import scipy.stats as stats
import seaborn as sns


def compare_number_decs_between_experiments(db):
    """
    Checar se número de decisões no banco de dados é coerente com a não inclusão das decisões similares
    Fazer isso comparando número de decisões de experimentos com e sem similares para ambos os PageRanks
    """
    ancient_collections = [
        "stf_pr_1_acordaos_90_replaced_col_1",
        "stf_pr_2_acordaos_90_par_1",
    ]
    new_collections = [
        "stf_pr_1_acordaos_90_no_similars_1",
        "stf_pr_2_acordaos_90_no_similars_1",
    ]
    print("Number of decisions of experimentos with and without similar decisions")
    for col_ancient, col_new in zip(ancient_collections, new_collections):
        print(col_ancient, col_new)
        print(db[col_ancient].find({}).count(), db[col_new].find({}).count())


def get_db_object():
    """
    """
    MONGO_URI = os.getenv("MONGO_URI")
    MONGO_DATABASE = os.getenv("MONGO_DATABASE")

    client = MongoClient(MONGO_URI)
    db = client[MONGO_DATABASE]
    return db


def get_decisions_collection(db, collection_name):
    """
    """
    page_ranks_iters = []
    selected_keys = {"acordaoId": 1, "pageRank": 1, "relator": 1}
    df_collection = pd.DataFrame()
    for i in range(1, 11):
        coll_name_iter_i = collection_name + "_%d" % i
        page_ranks_cursor = (
            db[coll_name_iter_i]
            .find({}, selected_keys)
            .sort([("pageRank", -1)])
            .limit(100)
        )
        df = pd.DataFrame(page_ranks_cursor)
        df["collection_iter"] = i
        df.drop("_id", axis=1, inplace=True)
        df_collection = df_collection.append(df)

    return df_collection


def get_top_10_magistrates(df_magistrates_decs_lst):
    """
    """
    top_10_magistrates = []
    for df_magistrates_decs_pr_models in df_magistrates_decs_lst:
        relator = df_magistrates_decs_pr_models[0]["relator"].value_counts().index[0]
        top_10_magistrates.append(relator)

    return top_10_magistrates


def get_number_of_decisions_with_without_similars(db, coll_name, relatores=None):
    """
    """
    with_without_similars_sizes = []
    if relatores:
        for i, relator in enumerate(relatores):
            with_without_similars_sizes.append([i + 1, relator, db[coll_name.format(i+1)].find({}).count(), db["acordaos"].find({"relator": {"$eq": relator}}).count()])
        with_without_similars_sizes = sorted(with_without_similars_sizes, reverse=True, key=lambda x: x[3])
    else:
        with_without_similars_sizes.extend([db[coll_name].find({}).count(), db["acordaos"].find({}).count()])

    return with_without_similars_sizes


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
    df_ids_in_8_to_10_iters = df_ids_in_8_to_10_iters.rename(
        columns={"index": "acordaoId"}
    )
    df_ids_in_8_to_10_iters = df_collection[
        df_collection["acordaoId"].isin(df_ids_in_8_to_10_iters["acordaoId"])
    ].drop_duplicates("acordaoId")
    return df_ids_in_8_to_10_iters


def get_decisions_dataframes_tabulated(coll_name, perturbances, pr_models):
    """
    """
    coll_names = []
    for perturbance in perturbances:
        pr_models_coll_names = []
        for pr_model in pr_models:
            pr_models_coll_names.append(coll_name.format(pr_model, perturbance))
        coll_names.append(pr_models_coll_names)

    df_lst = []
    for i, perturbance in enumerate(perturbances):
        pr_models_dfs = []
        for j, pr_model in enumerate(pr_models):
            pr_models_dfs.append(get_decisions_collection(db, coll_names[i][j]))
        df_lst.append(pr_models_dfs)

    return df_lst


def get_network_robutness_tabulated(df_perturbations):
    """
    """
    df_robustness_lst = []
    for df_perturbation in df_perturbations:
        df_perturbation_lst = []
        for df_pr_model in df_perturbation:
            df_perturbation_lst.append(
                get_decisions_in_at_least_8_iters_of_10(df_pr_model)
            )
        df_robustness_lst.append(df_perturbation_lst)

    return df_robustness_lst


def get_intersection_decisions_tabulated(df_perturbations):
    """
    """
    df_intersect_lst = []
    for df_perturbation in df_perturbations:
        df_intersect_lst.append(get_intersection_decisions(*df_perturbation))

    return df_intersect_lst


def get_intersection_decisions_first_iter_tabulated(df_perturbations):
    """
    """
    df_intersect_lst = []
    for df_perturbation in df_perturbations:
        df_intersect_lst.append(get_intersection_decisions_first_iter(*df_perturbation))

    return df_intersect_lst


def get_absent_magistrates(df_perturbance_lst, top_10_magistrates):
    absent_relator_perturbances = []
    for df_perturbance in df_perturbance_lst:
        absent_relator_pr_models = []
        for pr_model in df_perturbance:
            absent_relator_pr_models.append(list(set(top_10_magistrates) - set(pr_model[pr_model["relator"].isin(top_10_magistrates)]["relator"])))
        absent_relator_perturbances.append(absent_relator_pr_models)

    return absent_relator_perturbances


def calc_qui_square_test(df):
    quisq_test, p_value, dof, _ = stats.chi2_contingency(df.values)

    print(quisq_test, p_value, dof, _)


def create_dataframe_from_list_of_list_sizes(dfs_lst, columns, index):
    """
    """
    df = pd.DataFrame(
        [[len(df) for df in dfs] for dfs in dfs_lst], columns=columns, index=index
    )
    return df


def create_dataframe_from_list_sizes(dfs, columns, index):
    """
    """
    df = pd.DataFrame([len(df) for df in dfs], columns=columns, index=index)
    return df


def plot_robustness_graph(df_perturbances, df_intersect):
    """
    """
    df = df_perturbances.join(df_intersect)
    df["Attack level"] = ["10%", "20%", "30%"]
    df = df.rename(columns={1: "$PR_1$", 2: "$PR_2$", "Intersect": "Intersection of $PR_1$ and $PR_2$"})
    df = df.set_index("Attack level")

    sns.set()
    ax = sns.lineplot(data=df, linewidth=2.5)
    ax.set(xlabel="Attack level", ylabel="PageRankTop100")
    fig = ax.get_figure()
    fig.savefig("PageRankTop100_disturbance.png")


if __name__ == "__main__":
    db = get_db_object()
    compare_number_decs_between_experiments(db)

    df_all_decs_lst = get_decisions_dataframes_tabulated(
        "stf_pr_{}_acordaos_{}", [10, 20, 30], [1, 2]
    )
    df_all_decs_no_similars_lst = get_decisions_dataframes_tabulated(
        "stf_pr_{}_acordaos_{}_no_similars", [10], [1, 2]
    )
    df_magistrates_decs_lst = []
    top_magistrates_n = 10
    for magistrate_i in range(top_magistrates_n):
        df_magistrates_decs_lst.extend(
            get_decisions_dataframes_tabulated(
                "stf_pr_{}_acordaos_{}_rel" + "_{mag}".format(mag=magistrate_i + 1),
                [10],
                [1, 2],
            )
        )

    top_10_magistrates = get_top_10_magistrates(df_magistrates_decs_lst)

    with_without_similars_all_decisions_size = get_number_of_decisions_with_without_similars(db, "stf_pr_1_acordaos_10_1")
    with_without_similars_magistrates_size = get_number_of_decisions_with_without_similars(db, "stf_pr_1_acordaos_10_rel_{}_1", top_10_magistrates)

    df_robustness_lst = get_network_robutness_tabulated(df_all_decs_lst)
    df_robustness_no_similars_lst = get_network_robutness_tabulated(
        df_all_decs_no_similars_lst
    )
    df_robustness_magistrates_lst = get_network_robutness_tabulated(
        df_magistrates_decs_lst
    )

    df_robustness_intersect_all_decs_lst = get_intersection_decisions_tabulated(
        df_robustness_lst
    )
    df_robustness_intersect_no_similars_lst = get_intersection_decisions_tabulated(
        df_robustness_no_similars_lst
    )
    df_robustness_intersect_magistrates_lst = get_intersection_decisions_tabulated(
        df_robustness_magistrates_lst
    )
    df_robustness_intersect_between_with_and_without_sim_pr1_lst = get_intersection_decisions_tabulated(
        [[df_robustness_lst[0][0], df_robustness_no_similars_lst[0][0]]]
    )
    df_robustness_intersect_between_with_and_without_sim_pr2_lst = get_intersection_decisions_tabulated(
        [[df_robustness_lst[0][1], df_robustness_no_similars_lst[0][1]]]
    )

    pr_models = [1, 2]
    df_robustness_decs_with_similars_vs_without_similars_lst = []
    for i, pr_model in enumerate(pr_models):
        df_robustness_decs_with_similars_vs_without_similars_lst.append(
            get_intersection_decisions(
                df_robustness_lst[0][i], df_robustness_no_similars_lst[0][i]
            )
        )

    df_all_decs_robustness_table = create_dataframe_from_list_of_list_sizes(
        df_robustness_lst, [1, 2], [10, 20, 30]
    )
    df_no_similars_robustness_table = create_dataframe_from_list_of_list_sizes(
        df_robustness_no_similars_lst, [1, 2], [10]
    )
    df_magistrates_robustness_table = create_dataframe_from_list_of_list_sizes(
        df_robustness_magistrates_lst, [1, 2], top_10_magistrates
    )
    df_decs_with_similars_vs_without_similars_robustness_table = create_dataframe_from_list_of_list_sizes(
        [df_robustness_decs_with_similars_vs_without_similars_lst], [1, 2], [10]
    )

    df_all_decs_intersection_table = create_dataframe_from_list_sizes(
        df_robustness_intersect_all_decs_lst, ["Intersect"], [10, 20, 30]
    )
    df_no_similars_intersect_table = create_dataframe_from_list_sizes(
        df_robustness_intersect_no_similars_lst, ["Intersect"], [10]
    )
    df_magistrates_intersection_table = create_dataframe_from_list_sizes(
        df_robustness_intersect_magistrates_lst,
        ["Intersect"],
        top_10_magistrates,
    )

    calc_qui_square_test(df_all_decs_robustness_table)
    calc_qui_square_test(df_magistrates_robustness_table)

    df_intersec_with_sim_dec_lst = get_intersection_decisions_first_iter_tabulated(
        df_all_decs_lst
    )
    df_intersec_without_sim_dec_lst = get_intersection_decisions_first_iter_tabulated(
        df_all_decs_no_similars_lst
    )
    df_intersec_magistrates_lst = get_intersection_decisions_first_iter_tabulated(
        df_magistrates_decs_lst
    )
    df_intersec_between_with_and_without_sim_pr1 = get_intersection_decisions_first_iter_tabulated(
        [[df_all_decs_lst[0][0], df_all_decs_no_similars_lst[0][0]]]
    )
    df_intersec_between_with_and_without_sim_pr2 = get_intersection_decisions_first_iter_tabulated(
        [[df_all_decs_lst[0][1], df_all_decs_no_similars_lst[0][1]]]
    )

    df_intersec_with_sim_dec_table = create_dataframe_from_list_sizes(
        df_intersec_with_sim_dec_lst, ["Intersect"], [10, 20, 30]
    )
    df_intersec_without_sim_dec_table = create_dataframe_from_list_sizes(
        df_intersec_without_sim_dec_lst, ["Intersect"], [10]
    )
    df_intersec_magistrates_table = create_dataframe_from_list_sizes(
        df_intersec_magistrates_lst, ["Intersect"], top_10_magistrates
    )
    df_intersec_between_with_and_without_sim_pr1_table = create_dataframe_from_list_sizes(
        df_intersec_between_with_and_without_sim_pr1, ["Intersect"], [1]
    )
    df_intersec_between_with_and_without_sim_pr2_table = create_dataframe_from_list_sizes(
        df_intersec_between_with_and_without_sim_pr2, ["Intersect"], [2]
    )

    df_intersec_magistrates_first_iter_table = create_dataframe_from_list_sizes(
        df_intersec_magistrates_lst, ["Intersect"], top_10_magistrates
    )

    absent_magistrates_lst = get_absent_magistrates(df_robustness_lst, top_10_magistrates)
    absent_magistrates_no_similars_lst = get_absent_magistrates(df_robustness_no_similars_lst, top_10_magistrates)

    plot_robustness_graph(df_all_decs_robustness_table, df_all_decs_intersection_table)

    calc_qui_square_test(pd.DataFrame(np.array([[36, 26], [26, 23]])))
    # with pd.ExcelWriter(
    #     "comparacao_execucoes_pagerank_com_similares_e_sem.xlsx"
    # ) as writer:
    #     df_intersec_with_sim_dec_number.to_excel(
    #         writer, sheet_name="pr1 pr2 c sim e todas dec", index=False
    #     )
    #     df_intersec_without_sim_dec_number.to_excel(
    #         writer, sheet_name="pr1 pr2 só citac e todas dec", index=False
    #     )
    #     df_intersec_between_with_and_without_sim_pr1.to_excel(
    #         writer, sheet_name="pr1 sim vs só cit todas dec", index=False
    #     )
    #     df_intersec_between_with_and_without_sim_pr2.to_excel(
    #         writer, sheet_name="pr2 sim vs só cit todas dec", index=False
    #     )
    #     df_robutness_results_pr1_pr2_with_sim.to_excel(
    #         writer, sheet_name="dec em 8 a 10 ex pr1 pr2 c sim", index=False
    #     )
    #     df_robutness_results_pr1_pr2_without_sim.to_excel(
    #         writer, sheet_name="dec em 8 a 10 ex pr1 pr2 só cit", index=False
    #     )
    #     df_robutness_results_pr1_with_and_without_sim.to_excel(
    #         writer, sheet_name="dec em 8 a 10 pr1 sim vs só cit", index=False
    #     )
    #     df_robutness_results_pr2_with_and_without_sim.to_excel(
    #         writer, sheet_name="dec em 8 a 10 pr2 sim vs só cit", index=False
    #     )
