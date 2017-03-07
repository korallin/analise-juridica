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


# python makePageRankedGraph.py DJs acordaos "" stf_pr_1_acordaos 1
# python makePageRankedGraph.py DJs decisoes "" stf_pr_1_decisoes 1
# python makePageRankedGraph.py DJs acordaos "" stf_pr_2_acordaos 2
# python makePageRankedGraph.py DJs decisoes "" stf_pr_2_decisoes 2

dbName = sys.argv[1]
collections_name = sys.argv[2]
queryRaw = sys.argv[3]
collectionOutName = sys.argv[4]
pageRankMode = sys.argv[5]
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


def get_decisions_ids(dbName, collections):
    client = MongoClient('localhost', 27017)
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
    decisions_ids, collections = get_decisions_ids(dbName, collections_name)

    graphMaker = GraphMaker(dbName, collections, collectionOutName)
    pageRanker = PageRanker()

    removed_decisions = []

    tini = datetime.now()

    with open('page_ranking_status.log', 'a') as f:
        f.write("cálculo do page rank o tipo de decisões: %s \n" % collections_name)

    for i in xrange(1, 11):
        graphMaker.save_removed_decisions(i, removed_decisions, collectionOutName)

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
        pageRanks = pageRanker.calculatePageRanks(acordaos, quotes, quotedBy, pageRankMode)
        with open('page_ranking_status.log', 'a') as f:
            f.write("calculated page rank in iteration %d in %d seconds\n" % (i, (datetime.now() - t1).seconds))

        graphMaker.set_collections_out(collectionOutName + "_{}".format(i))

        t1 = datetime.now()
        graphMaker.insertNodes(acordaos, quotes, quotedBy, similars, pageRanks)
        with open('page_ranking_status.log', 'a') as f:
            f.write("Time to insert nodes %d" % (datetime.now() - t1).seconds)

        removed_decisions = get_removed_decisions(decisions_ids, 10)

    os.system('echo "Page ranker finalizou!" | mail -s "Page ranker finalizou!" -r "Jackson<jackson@ime.usp.br>" jackson@ime.usp.br')

except Exception as e:
    os.system('echo %s | mail -s "Page ranker falhou!" -r "Jackson<jackson@ime.usp.br>" jackson@ime.usp.br' % e)

    with open('page_ranking_error.log', 'a') as f:
        f.write("%d: %s"%( (datetime.now()-tini).seconds, e))
