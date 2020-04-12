#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from Acordao import Acordao
from pymongo import MongoClient
import networkx as nx


class NetworkXDigraph:
    def __init__(
        self,
        mongo_uri,
        db_name,
        collection_in,
        collection_out_name,
    ):
        client = MongoClient(mongo_uri)
        self.db = client[db_name]
        self.collection_in = collection_in
        self.collection_out = self.db[collection_out_name]
        self.collection_out.drop()
        self.one_percent = sum([coll.count() for coll in self.collection_in]) / 100

    def save_removed_decisions(self, i, removed_decisions, collection_out_name):
        removed_coll = self.db[collection_out_name + "_removed_%d" % i]
        removed_coll.drop()

        removed_coll.insert_one(
            {"iteration": i, "removed_decisions": removed_decisions}
        )

    def set_collections_out(self, collection_out_name):
        self.collection_out = self.db[collection_out_name]
        self.collection_out.drop()

    def build_graph(self, query, removed_decisions, compute_similars):
        acordaos = {}
        G = nx.DiGraph()

        print("building map")

        self.count = self.progress = 0

        for coll in self.collection_in:
            docsFound = coll.find(query, no_cursor_timeout=True)
            for doc in docsFound:
                if doc["acordaoId"] in removed_decisions:
                    continue

                # ADICIONA NÓ
                docId = doc["acordaoId"]
                G.add_node(docId) if docId not in acordaos else None
                acordaos[docId] = Acordao(docId, doc["tribunal"], doc["relator"], False)
                # ADICIONA ARCOS
                for ac_cit in doc["citacoesObs"]:
                    if ac_cit not in acordaos:
                        G.add_node(ac_cit)
                        acordaos[ac_cit] = Acordao(ac_cit, "", "", False)

                    G.add_edge(docId, ac_cit)

                if compute_similars == "S":
                    for similar in doc["similares"]:
                        similarId = similar["acordaoId"]
                        if similarId not in removed_decisions:
                            for quotedId in doc["citacoesObs"]:
                                if similarId not in acordaos:
                                    G.add_node(similarId)
                                    acordaos[similarId] = Acordao(
                                        similarId, doc["tribunal"], similar["relator"], True
                                    )

                                G.add_edge(similarId, quotedId)

                self.__print_progress()

            print("")

        return [G, acordaos]

    # Insert nodes and authority and hub node values
    def insert_nodes(self, G, acordaos, authorities, hubs):
        n_docs = len(acordaos)
        self.one_percent = n_docs / 100
        self.count = self.progress = 0
        insert_step = n_docs
        if n_docs > 10000:
            insert_step = 10000

        print("n acordaos %s to be inserted" % n_docs)

        i = 0
        docs_to_insert = []
        for docId, doc in acordaos.items():
            docs_to_insert.append(
                {
                    "acordaoId": docId,
                    # "citacoes": doc.getCitacoes(),
                    "citadoPor": [tup[0] for tup in G.out_edges(docId)],
                    # "similares": doc.getSimilares(),
                    "relator": doc.getRelator(),
                    "tribunal": doc.getTribunal(),
                    "authority": authorities[docId],
                    "hub": hubs[docId],
                    "virtual": doc.getVirtual(),
                }
            )
            i += 1
            self.__print_progress()
            if i >= insert_step:
                self.collection_out.insert_many(docs_to_insert)
                docs_to_insert = []
                i = 0

        print("")
        if i > 0:
            self.collection_out.insert_one(docs_to_insert)


    def __print_progress(self):
        self.count += 1
        if self.count >= self.one_percent:
            self.count = 0
            self.progress += 1
            sys.stdout.write("\r%d%%" % self.progress)
            sys.stdout.flush()
