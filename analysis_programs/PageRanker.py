#!/usr/bin/env python
# -*- coding: utf-8 -*-
import gmpy2
from gmpy2 import mpfr
from Acordao import Acordao
from datetime import datetime


class PageRanker:

    epsilon = mpfr(1.0e-8)
    p = mpfr(0.85)

    def __euclidianDistance(self, pMap, qMap):
        # soma do quadrado das diferenças de paga ranking entre iteração anterior
        # e atual do algoritmo page ranking
        pr_iter_square_diffs_sum = sum(
            [pow(p - qMap[docId], 2) for docId, p in pMap.items()]
        )
        return gmpy2.sqrt(pr_iter_square_diffs_sum)

    def __lengthArray(self, array):
        return {x: len(s) for x, s in array.items()}

    def pageRank1sum(self, quotingAcordaos, pageRanks, quotesLen):
        totalSum = mpfr(0)
        for docId in quotingAcordaos:
            pr = pageRanks.get(docId, 0.0)
            l = quotesLen.get(docId, 1)
            term = pr / l
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

        pageRanks = {docId: mpfr(1.0) / mpfr(nDocs) for docId in acordaos}
        newPageRanks = {}
        rounds = 0

        while True:
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
                    newPageRanks[docId] = pr / prSum

                rounds += 1

                if self.__euclidianDistance(pageRanks, newPageRanks) < epsilon:
                    print("rounds: %d" % (rounds))
                    return newPageRanks

                pageRanks = newPageRanks
                newPageRanks = {}

            except Exception as e:
                with open("page_ranking_error.log", "ab") as f:
                    f.write("%d: %s" % ((datetime.now() - t1).microseconds, e))

        print("rounds: %d" % (rounds))
        return pageRanks
