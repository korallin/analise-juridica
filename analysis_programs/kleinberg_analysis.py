#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from math import ceil
from random import randint
import datetime
import traceback
from multiprocessing import Pool
from pymongo import MongoClient
from NetworkXDigraph import NetworkXDigraph
import networkx as nx


def get_decisions_ids(collections, query):
    MONGO_URI = os.getenv("MONGO_URI")
    MONGO_DATABASE = os.getenv("MONGO_DATABASE")

    client = MongoClient(MONGO_URI)
    db = client[MONGO_DATABASE]

    decisions_ids = []
    colls = []
    if collections == "acordaos":
        colls.append(db["acordaos"])
    elif collections == "decisoes_monocraticas":
        colls.append(db["decisoes_monocraticas"])
    elif collections == "decisoes":
        colls.append(db["acordaos"])
        colls.append(db["decisoes_monocraticas"])

    for coll in colls:
        docs = coll.find(query, no_cursor_timeout=True)
        for doc in docs:
            decisions_ids.append(doc["acordaoId"])

    return decisions_ids, colls


def get_removed_decisions(decisions_ids, percentage):
    removed_decisons_len = ceil(len(decisions_ids) * (percentage / 100.0))
    decisions_ids_len = len(decisions_ids)
    removed_decisions = []
    i = 0
    while i < removed_decisons_len:
        x = randint(0, decisions_ids_len - 1)
        if decisions_ids[x] not in removed_decisions:
            removed_decisions.append(decisions_ids[x])
            i += 1

    return removed_decisions


def get_top_10_relatores():
    MONGO_URI = os.getenv("MONGO_URI")
    MONGO_DATABASE = os.getenv("MONGO_DATABASE")
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DATABASE]
    docs = db["acordaos"].aggregate(
        [
            {"$group": {"_id": "$relator", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 10},
        ]
    )
    relatores = [doc["_id"] for doc in docs]

    return relatores


def run_hits_execution(args):
    (
        i,
        query,
        collections_name,
        percentage,
        compute_similars,
        collection_out_iter_name,
    ) = args
    print("execution: ", i, collection_out_iter_name)

    decisions_ids, collections = get_decisions_ids(collections_name, query)

    MONGO_URI = os.getenv("MONGO_URI")
    MONGO_DATABASE = os.getenv("MONGO_DATABASE")
    graph = NetworkXDigraph(
        MONGO_URI, MONGO_DATABASE, collections, collection_out_iter_name,
    )
    if i == 1:
        removed_decisions = []
    else:
        removed_decisions = get_removed_decisions(decisions_ids, percentage)

    graph.save_removed_decisions(i, removed_decisions, collection_out_iter_name)

    # Construct graph
    [G, acordaos] = graph.build_graph(query, removed_decisions, compute_similars)

    # Se esta função fosse executada seriam removidos acórdãos fora do intervalo temporal
    # [quotes, quotedBy] = graph.removeInvalidAcordaosFromDicts(
    #     acordaos, quotes, quotedBy
    # )

    print("Início da execução do kleinberg:", len(acordaos))
    # KLEINBERG authorities and hubs
    try:
        hubs, authorities = nx.hits(G, max_iter=1000)
        graph.set_collections_out(collection_out_iter_name + "_{}".format(i))

        print(
            "Execução:",
            collection_out_iter_name + "_{}".format(i),
            "está pronta para ser inserida no banco",
        )
        # Insert results
        graph.insert_nodes(G, acordaos, authorities, hubs)
        print(collection_out_iter_name + "_{}".format(i), "finalizada")
    except Exception as e:
        traceback.print_exc()


def run_acordaos_kleinberg_experiments():
    # parâmetros
    # relatores: "S" ou "N"
    query = {}
    collections_name = "acordaos"
    compute_similars = "S"
    kleinberg_iters = []

    # experimento kleinberg todas as decisões
    percentages = [10, 20, 30]
    for percentage in percentages:
        collection_out_iter_name = "stf_kleinberg_acordaos_{}".format(percentage)
        kleinberg_iters.extend(
            [
                (
                    i,
                    query,
                    collections_name,
                    percentage,
                    compute_similars,
                    collection_out_iter_name,
                )
                for i in range(1, 11)
            ]
        )

    compute_similars = "N"
    percentage = 10
    collection_out_iter_name = "stf_kleinberg_acordaos_{}_no_similars".format(
        percentage
    )
    kleinberg_iters.extend(
        [
            (
                i,
                query,
                collections_name,
                percentage,
                compute_similars,
                collection_out_iter_name,
            )
            for i in range(1, 11)
        ]
    )

    compute_similars = "S"
    percentage = 10
    relatores = get_top_10_relatores()
    for j, rel in enumerate(relatores):
        new_query = query.copy()
        new_query["relator"] = rel
        collection_out_iter_name = "stf_kleinberg_acordaos_{}_rel_{}".format(
            percentage, (j + 1)
        )
        kleinberg_iters.extend(
            [
                (
                    i,
                    new_query,
                    collections_name,
                    percentage,
                    compute_similars,
                    collection_out_iter_name,
                )
                for i in range(1, 11)
            ]
        )

    processes = 3
    pool = Pool(processes=processes)
    pool.map(run_hits_execution, kleinberg_iters)
    pool.close()
    pool.join()


if __name__ == "__main__":
    try:
        tini = datetime.datetime.now()
        run_acordaos_kleinberg_experiments()

        os.system(
            'echo "Kleinberg acabou com sucesso =)!" | mail -s "Kleinberg acabou!" -r "Jackson<jackson@ime.usp.br>" jackson@ime.usp.br'
        )

    except Exception as e:
        os.system(
            'echo %s | mail -s "Kleinberg falhou!" -r "Jackson<jackson@ime.usp.br>" jackson@ime.usp.br'
            % e
        )
        with open("kleinberg_error.log", "a") as f:
            f.write("%d: %s\n\n" % ((datetime.datetime.now() - tini).seconds, e))
