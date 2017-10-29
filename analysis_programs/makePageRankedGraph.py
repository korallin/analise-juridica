#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os

from math import ceil
from random import randint
from datetime import datetime
from pymongo import MongoClient
from GraphMaker import GraphMaker
from PageRanker import PageRanker

# example of command line command
#makePageRankedGraph DJs acordaos "tribunal: STF, localSigla: SP" STF_SP_PR1 1


# python makePageRankedGraph.py $mongo_user $mongo_password DJs acordaos 90 S "" stf_pr_1_acordaos_90 1
# dbName = "DJTest"
# collections_name = "acordaos"
# percentage = "90"
# all_relatores = "N"
# queryRaw = ""
# collectionOutName = "stf_pr_1_acordaos_90"
# pageRankMode = "1"

mongo_user = sys.argv[1]
mongo_password = sys.argv[2]
dbName = sys.argv[3]
collections_name = sys.argv[4]
percentage = int(sys.argv[5])
all_relatores = sys.argv[6]
queryRaw = sys.argv[7]
collectionOutName = sys.argv[8]
pageRankMode = sys.argv[9]
query = {}

if queryRaw:
    queryPairs = queryRaw.split(',')
    if not queryPairs:
        queryPairs = queryRaw
    for pair in queryPairs:
        pairSplit = pair.split(':')
        field = pairSplit[0].strip()
        value = pairSplit[1].strip()
        query[field] = value

quotes = {}
quotedBy = {}
similars = {}
acordaos = {}


# def mergeDictsSets(h1, h2):
#     for k in h2:
#         if k in h1:
#             h1[k] = h1[k].union(h2[k])
#     return h1


def get_decisions_ids(dbName, user, password, collections, query):
    client = MongoClient('mongodb://{}:{}@127.0.0.1:57017'.format(user, password))
    db = client[dbName]

    decisions_ids = []
    colls = []
    if collections == 'acordaos':
        colls.append(db['acordaos'])
    elif collections == 'decisoes_monocraticas':
        colls.append(db['decisoes_monocraticas'])
    elif collections == 'decisoes':
        colls.append(db['acordaos'])
        colls.append(db['decisoes_monocraticas'])

    for coll in colls:
        docs = coll.find(query, no_cursor_timeout=True)
        for doc in docs:
            decisions_ids.append(doc['acordaoId'])

    return decisions_ids, colls

def get_top_10_relatores(dbName, user, password):
    client = MongoClient('mongodb://{}:{}@127.0.0.1:57017'.format(user, password))
    db = client[dbName]
    docs = db['acordaos'].aggregate([{"$group" : {"_id": '$relator', "count": {"$sum": 1}}}, {"$sort": {"count": -1}}, {"$limit": 10}])
    relatores = [doc['_id'] for doc in docs]

    return relatores

def get_removed_decisions(decisions_ids, percentage):
    removed_decisons_len = ceil(len(decisions_ids) * (percentage/100.))
    decisions_ids_len = len(decisions_ids)
    removed_decisions = []
    i = 0
    while (i < removed_decisons_len):
        x = randint(0, decisions_ids_len - 1)
        if decisions_ids[x] not in removed_decisions:
            removed_decisions.append(decisions_ids[x])
            i += 1

    return removed_decisions

try:
    # o referencial adotado aqui para calcular maiores relatores é o
    # número de acórdãos em que os ministros são relatores
    if all_relatores == 'S':
        relatores = [None]
    elif all_relatores == 'N':
        relatores = get_top_10_relatores(dbName, mongo_user, mongo_password)
    else:
        print "parâmetro Nº 5 deve ser 'S' ou 'N'"
        exit(1)

    with open('page_ranking_status.log', 'a') as f:
        f.write("\n\n\nBanco de dados: %s \n" % dbName)
        relats = "\n".join(relatores) if len(relatores) > 1 else "TODOS"
        f.write("Principais relatores:\n%s\n" % relats.encode('utf-8'))

    tini = datetime.now()

    for j, rel in enumerate(relatores):
        if rel != None:
            query['relator'] = rel
            collection_out_iter_name = collectionOutName + ('_rel_%d' % (j+1))
        else:
            collection_out_iter_name = collectionOutName

        decisions_ids, collections = get_decisions_ids(dbName, mongo_user, mongo_password, collections_name, query)
        graphMaker = GraphMaker(mongo_user, mongo_password, dbName, collections, collection_out_iter_name)
        pageRanker = PageRanker()

        removed_decisions = []

        with open('page_ranking_status.log', 'a') as f:
            f.write("Collection: %s \n\n" % collection_out_iter_name)

        for i in xrange(1, 11):
            graphMaker.save_removed_decisions(i, removed_decisions, collection_out_iter_name)

            [acordaos, quotes, quotedBy, similars] = graphMaker.buildDicts(query, removed_decisions)
            [quotes, quotedBy] = graphMaker.removeInvalidAcordaosFromDicts(acordaos, quotes, quotedBy)
            # quotesPlusSimilars = mergeDictsSets(quotes, similars)
            # quotedByPlusSimilars = mergeDictsSets(quotedBy, similars)

            with open('page_ranking_status.log', 'a') as f:
                f.write("Number of decisions in DB: %d\n" % len(decisions_ids))
                total_quotes = sum([len(q) for q in quotes.values()])
                f.write("Number of decisions been pointed (links): %d\n" % total_quotes)
                f.write("Decisions from DB used in calculations %d + REMOVED DECISIONS %d (%d) = total decisions from DB %d \n" %
                                    (len(quotes), len(removed_decisions), len(quotes) + len(removed_decisions), len(decisions_ids)))

            t1 = datetime.now()
            pageRanks = pageRanker.calculatePageRanks(acordaos, quotes, quotedBy, int(pageRankMode))
            with open('page_ranking_status.log', 'a') as f:
                f.write("calculated page rank in iteration %d in %d seconds\n" % (i, (datetime.now() - t1).seconds))

            graphMaker.set_collections_out(collection_out_iter_name + "_{}".format(i))

            t1 = datetime.now()
            graphMaker.insertNodes(acordaos, quotes, quotedBy, similars, pageRanks)
            with open('page_ranking_status.log', 'a') as f:
                f.write("Time to insert nodes %d\n" % (datetime.now() - t1).seconds)

            removed_decisions = get_removed_decisions(decisions_ids, 100-percentage)

        with open('page_ranking_status.log', 'a') as f:
            f.write("PageRank simulation took %d seconds to run\n" % (datetime.now() - tini).seconds)

        tini = datetime.now()


except Exception as e:
    # os.system('echo %s | mail -s "Page ranker falhou!" -r "Jackson<jackson@ime.usp.br>" jackson@ime.usp.br' % e)

    with open('page_ranking_error.log', 'a') as f:
        f.write("%d: %s\n\n"%( (datetime.now()-tini).seconds, e))
