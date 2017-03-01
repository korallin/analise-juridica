#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import math
import gmpy2

from gmpy2 import mpfr
from pymongo import MongoClient
from Acordao import Acordao
# from decimal import Decimal
from datetime import datetime

class PageRanker:
    
    epsilon = mpfr(1.0E-18)
    p = mpfr(0.85)

    def __euclidianDistance(self, pMap, qMap):
        # soma do quadrado das diferenças de paga ranking entre iteração anterior
        # e atual do algoritmo page ranking
        pr_iter_square_diffs_sum = sum([pow(p-qMap[docId], 2) for docId, p in pMap.iteritems()])

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
        # lengthArray = {}
        # for x, s in array.items():
        #     lengthArray[x] = len(s)
        # return lengthArray
        return {x: len(s) for x, s in array.iteritems()}

    def __pageRank1sum(self, quotingAcordaos, pageRanks, quotesLen):
        totalSum = mpfr(0)
        for docId in quotingAcordaos:
            pr = pageRanks.get(docId, 0.0)
            l = quotesLen.get(docId, 1)
            term = pr/l
#            terms.append( pr/l)
            totalSum += term
        return totalSum

    def __pageRank2sum(self, quotingAcordaos, pageRanks, quotesLen):
        # totalSum = mpfr(0.0)
        # for docId in quotingAcordaos:
        #     totalSum += pageRanks.get( docId, 0.0)
        # return totalSum
        return sum([pageRanks.get(docId, 0.0) for docId in quotingAcordaos])

    def calculatePageRanks(self, acordaos, quotes, quotedBy, mode):
        epsilon = self.epsilon
        p = self.p
        nDocs = len(acordaos)
        # pageRanks = {}

        # for docId in acordaos:
        #     pageRanks[ docId] = mpfr(1.0)/mpfr(nDocs)
        # BEGIN PARALLELIZABLE
        pageRanks = {docId: mpfr(1.0)/mpfr(nDocs) for docId in acordaos}
        # END PARALLELIZABLE

        rounds = 0
        newPageRanks = {}
        prSumFunc = self.__pageRank2sum if mode == 2 else self.__pageRank1sum
        quotesLen = self.__lengthArray(quotes)

        while (True):
            t1 = datetime.now()
            try:
                prSum = mpfr(0)

                # BEGIN PARALLELIZABLE
                for docId in acordaos:
                    quotingAcordaos = quotedBy.get(docId, [])
                    totalSum = prSumFunc(quotingAcordaos, pageRanks, quotesLen)
                    pr = ((mpfr(1.0) - p) / mpfr(nDocs)) + (p * totalSum)
                    newPageRanks[docId] = pr
                    # cuidado com a soma do atributo abaixo
                    prSum += pr
                # END PARALLELIZABLE

                # BEGIN PARALLELIZABLE
                for docId in newPageRanks:
                    pr = newPageRanks[docId]
                    newPageRanks[docId] = pr/prSum
                # END PARALLELIZABLE
    
                rounds += 1

                t2 = datetime.now()
                print "calculando pr %d" % ((t2-t1).seconds)

                if (self.__euclidianDistance(pageRanks, newPageRanks) < epsilon):
                    print("rounds: %d" %(rounds))
                    return newPageRanks

                t3 = datetime.now()
                print "euclidian distance %d" % ((t3-t1).seconds)

                pageRanks.clear()
                pageRanks = newPageRanks.copy()

                t4 = datetime.now()
                print "copying newpr %d" % ((t4-t1).seconds)
            except Exception as e:
                with open('pageRankerReport', 'ab') as f:
                    f.write('%d: %s' %((datetime.now()-t1).microseconds, e))

        print("rounds: %d" %(rounds))
        return pageRanks
