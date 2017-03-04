#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gmpy2

from gmpy2 import mpfr
from pymongo import MongoClient
from Acordao import Acordao
from datetime import datetime

# def chunks(l, n):
#     return [l[i:i+n] for i in range(0, len(l), n)]

# proc_number = 8

# total = len(acordaos_keys)
# chunk_size = int(ceil(total / float(proc_number)))
# slice = chunks(acordaos_keys, chunk_size)

class PageRanker:
    
    epsilon = mpfr(1.0E-8)
    p = mpfr(0.85)

    def __euclidianDistance(self, pMap, qMap):
        # soma do quadrado das diferenças de paga ranking entre iteração anterior
        # e atual do algoritmo page ranking
        pr_iter_square_diffs_sum = sum([pow(p - qMap[docId], 2) for docId, p in pMap.iteritems()])

        return gmpy2.sqrt(pr_iter_square_diffs_sum)
#         totalSum = 0.0
#         for docId, p in pMap.items():
#             q = qMap[ docId]
# #            print "diff %f" % (p-q)
#             term = math.pow( (p-q) , 2)
#             totalSum += term
#         dist = math.sqrt( totalSum)
#         print dist
#         return dist

    def __lengthArray(self, array):
        return {x: len(s) for x, s in array.iteritems()}


    def pageRank1sum(self, quotingAcordaos, pageRanks, quotesLen):
        totalSum = mpfr(0)
        for docId in quotingAcordaos:
            pr = pageRanks.get(docId, 0.0)
            l = quotesLen.get(docId, 1)
            term = pr/l
            totalSum += term
        return totalSum


    def pageRank2sum(self, quotingAcordaos, pageRanks, quotesLen):
        return sum([pageRanks.get(docId, 0.0) for docId in quotingAcordaos])


    def calculatePageRanks(self, acordaos, quotes, quotedBy, mode):
        epsilon = self.epsilon
        p = self.p

        nDocs = len(acordaos)
        prSumFunc = self.pageRank2sum if mode == 2 else self.pageRank1sum
        quotesLen = self.__lengthArray(quotes)

        pageRanks = {docId: mpfr(1.0)/mpfr(nDocs) for docId in acordaos}
        newPageRanks = {}
        rounds = 0

        while (True):
            # t1 = datetime.now()
            try:
                prSum = mpfr(0.0)

                for docId in acordaos:
                    quotingAcordaos = quotedBy.get(docId, [])
                    totalSum = prSumFunc(quotingAcordaos, pageRanks, quotesLen)
                    pr = ((mpfr(1.0) - p) / mpfr(nDocs)) + (p * totalSum)
                    newPageRanks[docId] = pr
                    prSum += pr

                for docId in newPageRanks:
                    pr = newPageRanks[docId]
                    newPageRanks[docId] = pr/prSum
    
                rounds += 1

                # t2 = datetime.now()
                # print "calculando pr %d" % ((t2-t1).seconds)

                if (self.__euclidianDistance(pageRanks, newPageRanks) < epsilon):
                    print("rounds: %d" %(rounds))
                    return newPageRanks

                # t3 = datetime.now()
                # print "euclidian distance %d" % ((t3-t1).seconds)

                pageRanks = newPageRanks
                newPageRanks = {}

                # t4 = datetime.now()
                # print "copying newpr %d" % ((t4-t1).seconds)
            except Exception as e:
                with open('page_ranking_error.log', 'ab') as f:
                    f.write('%d: %s' %((datetime.now()-t1).microseconds, e))

        print("rounds: %d" %(rounds))
        return pageRanks


# com atributos compartilhados:      cálculo de 300 rodadas do page rank tomou 1769 segundos
# com atributos não compartilhados:  cálculo de 300 rodadas do page rank tomou 22 segundos
# com pool e não compartilhados:     
# com pool e atributos globais:      