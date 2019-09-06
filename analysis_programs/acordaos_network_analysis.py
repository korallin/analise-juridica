#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import numpy as np
import pandas as pd
import seaborn as sns
from pymongo import MongoClient
from GraphMaker import GraphMaker


def preprocess_query(query_raw):
    query = {}
    if query_raw:
        queryPairs = query_raw.split(",")
        if not queryPairs:
            queryPairs = query_raw
        for pair in queryPairs:
            pairSplit = pair.split(":")
            field = pairSplit[0].strip()
            value = pairSplit[1].strip()
            query[field] = value
    return query


def get_decisions_ids(db_name, user, password, port, collections, query):
    client = MongoClient("mongodb://{}:{}@127.0.0.1:{}".format(user, password, port))
    db = client[db_name]

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
            # decisions_ids.append([doc["acordaoId"], doc["observacao"], doc["similaresTexto"]])

    return decisions_ids, colls


def run_page_rank_iteration(query, collections_name, mongo_user, mongo_password, mongo_port, db_name):
    decisions_ids, collections = get_decisions_ids(
        db_name, mongo_user, mongo_password, mongo_port, collections_name, query
    )

    collection_out_iter_name = "_fake_coll"
    graphMaker = GraphMaker(
        mongo_user,
        mongo_password,
        mongo_port,
        db_name,
        collections,
        collection_out_iter_name,
    )

    removed_decisions = []
    compute_similars = "S"
    [acordaos, quotes, quotedBy, similars] = graphMaker.buildDicts(
        query, removed_decisions, compute_similars
    )
    [quotes, quotedBy] = graphMaker.removeInvalidAcordaosFromDicts(
        acordaos, quotes, quotedBy
    )
    # faz grafo ficar sem direção
    new_quotes = {}
    for k, vals in quotes.items():
        new_quotes[k] = vals
        for v in vals:
            if v not in new_quotes:
                new_quotes[v] = set([k])
            elif k not in new_quotes[v]:
                new_quotes[v].update([k])

    return quotes


if __name__ == '__main__':
    query_raw = ""
    query = preprocess_query(query_raw)
    new_quotes = run_page_rank_iteration(query, collections_name, mongo_user, mongo_password, mongo_port, db_name)

    nodes_degrees = [len(v) for k, v in new_quotes.items()]
    df = pd.DataFrame(nodes_degrees, columns=["count"])
    df_counts = df["count"].value_counts().reset_index()
    df_counts = df_counts.rename(columns={"index": "K"})
    N = df_counts["count"].sum()
    df_counts["log P(K)"] = df_counts["count"].apply(lambda x: np.log(x/N))
    df_counts["log K"] = df_counts["K"].apply(lambda x: np.log(x))
    df_counts["log P(K) / log K"] = - df_counts["log P(K)"] / df_counts["log K"]

    sns.lmplot(data=df_counts[df_counts["K"] > 1], y="log P(K)", x="log K")
    sns.lmplot(data=df_counts, y="count", x="K")

    sns.distplot(df["K"].value_counts(), hist=False, rug=True);
    import matplotlib.pyplot as plt
    plt.show();


    # client = MongoClient("mongodb://{}:{}@127.0.0.1:{}".format(mongo_user, mongo_password, mongo_port))
    # db = client[db_name]
    # query_raw = [{"observacao":{"$ne": ""}}, {"acordaoId": 1}]
    # db["acordaos"].find(*query_raw).count()
