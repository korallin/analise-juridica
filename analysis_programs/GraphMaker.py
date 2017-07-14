#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pymongo import MongoClient
from Acordao import Acordao
import sys


class GraphMaker:

    def __init__(self, mongo_user, mongo_password, dbName, collections_in, collectionOutName):
        client = MongoClient('mongodb://{}:{}@127.0.0.1:57017'.format(mongo_user, mongo_password))
        self.db = client[dbName]
        self.collectionsIn = collections_in
        self.collectionOut = self.db[collectionOutName]
        self.collectionOut.drop()
        self.onePercent = sum([coll.count() for coll in self.collectionsIn])/100
        self.count = 0
        self.progress = 0

    def set_collections_out(self, collection_out_name):
        self.collectionOut = self.db[collection_out_name]
        self.collectionOut.drop()


    def save_removed_decisions(self, i, removed_decisions, collection_out_name):
        removed_coll = self.db[collection_out_name + "_removed_%d" % i]
        removed_coll.drop()

        removed_coll.insert_one({
                            'iteration': i,
                            'removed_decisions': removed_decisions
                            })


    def __addElemSetToDict( self, aDict, elemKey, elemValue):
        if elemKey not in aDict:
            aDict[elemKey] = set()

        aDict[elemKey].add(elemValue)
        return aDict


    def removeInvalidAcordaosFromDicts(self, validAcordaos, quotes, quotedBy):
        """
            Remove do 'quotedBy' acórdãos que não estão presentes no BD ou nos similares apontados
            por decisões do BD. 'quotes' fica apenas com decisões citadas presentes no BD ou nos
            similares de uma determinada decisão.
        """
        for docId, quotesId in quotes.items():
            newQuotesId = set()
            for q in quotesId:
                if q in validAcordaos:
                    newQuotesId.add(q)
                else:
                    quotedBy.pop(q, 0)

            quotes[docId] = newQuotesId
        
        return [quotes, quotedBy]


    def buildDicts(self, query, removed_decisions):
        acordaos = {}
        quotes = {}
        quotedBy = {}
        similars = {}

        print "building map"

        self.count = self.progress = 0

        for coll in self.collectionsIn:
            docsFound = coll.find(query, no_cursor_timeout=True)
            for doc in docsFound:
                if doc['acordaoId'] in removed_decisions:
                    continue

                docId = doc['acordaoId']
                for quotedId in doc['citacoesObs']:
                    # queryWithId = query.copy()
                    # queryWithId['acordaoId'] = quotedId
                    # if self.collectionsIn.find_one( queryWithId):
                    if quotedId not in removed_decisions:
                        quotes = self.__addElemSetToDict(quotes, docId, quotedId)
                        quotedBy = self.__addElemSetToDict(quotedBy, quotedId, docId)

                # similares são decisões (nós) virtuais que apontam para citacoes de 'docId' 
                for similar in doc['similares']:
                    similarId = similar['acordaoId']
                    if similarId not in removed_decisions:
                        for quotedId in doc['citacoesObs']:
                            quotes = self.__addElemSetToDict(quotes, similarId, quotedId)
                            quotedBy = self.__addElemSetToDict(quotedBy, quotedId, similarId)

                            similars = self.__addElemSetToDict(similars, similarId, docId)
                            similars = self.__addElemSetToDict(similars, docId, similarId)

                        if similarId not in acordaos:
                            acordaos[similarId] = Acordao(similarId, doc['tribunal'], similar['relator'], True)

                acordaos[docId] = Acordao(docId, doc['tribunal'], doc['relator'], False)
                self.__printProgress()

            print ""

        return [acordaos, quotes, quotedBy, similars]


    def insertNodes(self, acordaos, quotes, quotedBy, similars, pageRanks):
        nDocs = len(acordaos)
        self.onePercent = nDocs/100
        self.count = self.progress = 0
        insertStep = nDocs
        if nDocs > 10000:
            insertStep = 10000

        print "n acordaos %s to be inserted" % nDocs

        i = 0
        docs2Insert = []
        for docId, doc in acordaos.iteritems():
            docQuotedBy = list(quotedBy.get(docId, set()))
            docQuotes = list(quotes.get(docId, set()))
            docSimilars = list(similars.get(docId, set()))
            docPageRank = float(pageRanks.get(docId, 0.0))
            docs2Insert.append({
                                'acordaoId': docId,
                                'citacoes' : docQuotes,
                                'citadoPor': docQuotedBy,
                                'similares': docSimilars,
                                'relator':  doc.getRelator(),
                                'tribunal': doc.getTribunal(),
                                'pageRank': docPageRank,
                                'virtual': doc.getVirtual()
                        })
            i += 1
            self.__printProgress()
            if i >= insertStep:
                self.collectionOut.insert(docs2Insert)
                docs2Insert = []
                i = 0

        print ""
        if i > 0:
            self.collectionOut.insert(docs2Insert)
        

    def __printProgress( self):
        self.count += 1
        if self.count >= self.onePercent:
            self.count = 0
            self.progress += 1
            sys.stdout.write("\r%d%%" % self.progress)
            sys.stdout.flush()

