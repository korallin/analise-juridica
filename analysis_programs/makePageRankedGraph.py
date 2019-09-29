#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
from math import ceil
from random import randint
from datetime import datetime
from multiprocessing import Pool
from pymongo import MongoClient
from GraphMaker import GraphMaker
from PageRanker import PageRanker


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


def run_page_rank_iteration(args):
    try:
        i, query, collections_name, percentage, compute_similars, collection_out_iter_name, page_rank_mode = args

        decisions_ids, collections = get_decisions_ids(
            collections_name, query
        )

        MONGO_URI = os.getenv("MONGO_URI")
        MONGO_DATABASE = os.getenv("MONGO_DATABASE")
        graphMaker = GraphMaker(
            MONGO_URI,
            MONGO_DATABASE,
            collections,
            collection_out_iter_name,
        )
        if i == 1:
            removed_decisions = []
        else:
            removed_decisions = get_removed_decisions(decisions_ids, percentage)

        graphMaker.save_removed_decisions(i, removed_decisions, collection_out_iter_name)
        [acordaos, quotes, quotedBy, similars] = graphMaker.buildDicts(
            query, removed_decisions, compute_similars
        )
        [quotes, quotedBy] = graphMaker.removeInvalidAcordaosFromDicts(
            acordaos, quotes, quotedBy
        )

        with open("page_ranking_status_{}.log".format(collection_out_iter_name), "a") as f:
            f.write("Number of decisions in DB: %d\n" % len(decisions_ids))
            total_quotes = sum([len(q) for q in quotes.values()])
            f.write("Number of decisions been pointed (links): %d\n" % total_quotes)
            f.write(
                """
                    Decisions from DB used in calculations %d + REMOVED DECISIONS %d (%d)
                    = total decisions from DB %d \n
                """
                % (
                    len(quotes),
                    len(removed_decisions),
                    len(quotes) + len(removed_decisions),
                    len(decisions_ids),
                )
            )

        t1 = datetime.now()
        pageRanker = PageRanker()
        print("Início da execução do page rank:", len(acordaos))
        pageRanks = pageRanker.calculatePageRanks(
            acordaos, quotes, quotedBy, int(page_rank_mode)
        )
        with open("page_ranking_status_{}.log".format(collection_out_iter_name), "a") as f:
            f.write(
                "calculated page rank in iteration %d in %d seconds\n"
                % (i, (datetime.now() - t1).seconds)
            )

        print("fim da execução do page rank:", collection_out_iter_name + "_{}".format(i))
        graphMaker.set_collections_out(collection_out_iter_name + "_{}".format(i))

        t1 = datetime.now()
        graphMaker.insertNodes(acordaos, quotes, quotedBy, similars, pageRanks)
        with open("page_ranking_status_{}.log".format(collection_out_iter_name), "a") as f:
            f.write("Time to insert nodes %d\n" % (datetime.now() - t1).seconds)
    except Exception as e:
        print("Ocorreu o erro:", e)


def run_acordaos_pagerank_experiments():
    # parâmetros
    # relatores: "S" ou "N"
    query = {}
    collections_name = "acordaos"
    compute_similars = "S"
    page_rank_iters = []

    # experimento page rank todas as decisões
    percentages = [10, 20, 30]
    page_ranks = [1, 2]
    for percentage in percentages:
        for page_rank in page_ranks:
            collection_out_iter_name = "stf_pr_{}_acordaos_{}".format(page_rank, percentage)
            page_rank_iters.extend([
                (i, query, collections_name, percentage, compute_similars, collection_out_iter_name, page_rank)
                for i in range(1, 11)
            ])

    compute_similars = "N"
    percentage = 10
    for page_rank in page_ranks:
        collection_out_iter_name = "stf_pr_{}_acordaos_{}_no_similars".format(page_rank, percentage)
        page_rank_iters.extend([
            (i, query, collections_name, percentage, compute_similars, collection_out_iter_name, page_rank)
            for i in range(1, 11)
        ])

    compute_similars = "S"
    percentage = 10
    relatores = get_top_10_relatores()
    for j, rel in enumerate(relatores):
        new_query = query.copy()
        new_query["relator"] = rel
        for page_rank in page_ranks:
            collection_out_iter_name = "stf_pr_{}_acordaos_{}_rel_{}".format(page_rank, percentage, (j + 1))
            page_rank_iters.extend([
                (i, new_query, collections_name, percentage, compute_similars, collection_out_iter_name, page_rank)
                for i in range(1, 11)
            ])


    processes = 12
    pool = Pool(processes=processes)
    pool.map(run_page_rank_iteration, page_rank_iters)
    pool.close()
    pool.join()


if __name__ == '__main__':
    try:
        tini = datetime.now()
        run_acordaos_pagerank_experiments()

        with open("page_ranking_status.log", "a") as f:
            f.write(
                "PageRank simulation took %d seconds to run\n"
                % (datetime.now() - tini).seconds
            )

        os.system(
            'echo "Page ranker acabou com sucesso =)!" | mail -s "Page ranker acabou!" -r "Jackson<jackson@ime.usp.br>" jackson@ime.usp.br'
        )

    except Exception as e:
        os.system(
            'echo %s | mail -s "Page ranker falhou!" -r "Jackson<jackson@ime.usp.br>" jackson@ime.usp.br'
            % e
        )
        with open("page_ranking_error.log", "a") as f:
            f.write("%d: %s\n\n" % ((datetime.now() - tini).seconds, e))
