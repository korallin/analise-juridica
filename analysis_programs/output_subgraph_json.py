#!/usr/bin/python
# -*- coding: utf-8 -*-

# Cria arquivo json com rede de decisões do ano de 2016 do grafo de citações entre decisões.
# Fazer o mesmo para grafo de citações entre relatores

# Contar quantos acórdãos contém dataPublic não nulo e quantos são nulos
# Fazer isso para decisões monocráticas e acórdãos
import json
import datetime
import pymongo
from pymongo import MongoClient
client = MongoClient()

db = client.DJs
grafo_citacoes_decisoes = db.grafo_citacoes_decisoes

nodes = {"items": []}
for doc in grafo_citacoes_decisoes.find({}):
    if doc["decisoesCitadasObs"] != []:
        if doc["dataPublic"] != None and doc["dataPublic"] != "" and doc["dataPublic"].year >= 2001:
            doc["dataPublic"] = doc["dataPublic"].strftime("%Y-%m-%d")
        else:
            print doc["dataPublic"]
            doc["dataPublic"] = ""

        del doc['_id']
        nodes['items'].append(doc)

with open('decisoes.json', 'w') as outfile:
    json.dump(nodes, outfile)

nodes_gte_2016 = {"items": []}
for doc in grafo_citacoes_decisoes.find({'dataPublic': {'$gte': datetime.datetime(2016, 1, 1)}}):
    if doc["decisoesCitadasObs"] != []:
        if doc["dataPublic"] != None and doc["dataPublic"] != "" and doc["dataPublic"].year >= 2001:
            doc["dataPublic"] = doc["dataPublic"].strftime("%Y-%m-%d")
        else:
            print doc["dataPublic"]
            doc["dataPublic"] = ""

        del doc['_id']
        nodes_gte_2016['items'].append(doc)

with open('decisoes_gte_2016.json', 'w') as outfile:
    json.dump(nodes_gte_2016, outfile)
