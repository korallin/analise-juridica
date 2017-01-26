#!/usr/bin/python
# -*- coding: utf-8 -*-

import pymongo
from pymongo import MongoClient
client = MongoClient()

db = client.DJs
acordaos = db.acordaos
decisoes_monocraticas = db.decisoes_monocraticas

db.citacoes_grafo.drop()
citacoes_grafo = db.citacoes_grafo

for coll, coll_abrev in zip([acordaos, decisoes_monocraticas], ["A", "DM"]):
    for doc in coll.find({}):
        citacao_doc = { "decisaoId": doc['acordaoId'],              # acórdão que cita
                        "decisoesCitadasObs": doc['citacoes'],      # acórdãos citados na seção observação
                        # "acordaosCitadosDec": doc['citacoes'],    # acórdãos citados na seção decisão
                        "decisaoFonteDecTipo": coll_abrev,          # tipo de decisão de origem da decisão citante
                                                                    # (A - acórdão ou DM - decisão monocrática)
                        "dataPublic": doc['dataPublic']             # Foi adotada a data de publicação de acórdão
                                                                    # porque é quando ele passa a valer
                        # Necessário alterar scrapper para refletir adição de atributo de citações de observação
                    }
        citacoes_grafo.insert_one(citacao_doc)


# Contar quantos acórdãos contém dataPublic não nulo e quantos são nulos
# Fazer isso para decisões monocráticas e acórdãos
# Corrigir scraper de dataPublic

import json
import datetime
nodes = {"items": []}
for doc in citacoes_grafo.find({}):
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
for doc in citacoes_grafo.find({'dataPublic': {'$gte': datetime.datetime(2016, 1, 1)}}):
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


# conferir quantas instâncias de cada tipo de decisão são nulas antes e depois
import re
from datetime import datetime, timedelta

import pymongo
from pymongo import MongoClient
client = MongoClient()

db = client.DJs
acordaos = db.acordaos
decisoes_monocraticas = db.decisoes_monocraticas

for doc in acordaos.find({"dataPublic": ""}):

    text = doc['publicacao'].strip()
    date = re.search('(PUBLIC|DJ)\s+(\d+)[-\/](\d+)[-\/](\d{4})', text)
    try:
        if date:
            date = datetime(int(date.group(4)), int(date.group(3)), int(date.group(2)))
        else:
            date = ""
    except Exception as e:
        date = ""

    db.acordaos.update_one({ "_id" : doc['_id']},
                            {
                                "$set": {
                                    "dataPublic": date
                                }
                            })

for doc in decisoes_monocraticas.find({"dataPublic": ""}):

    text = doc['publicacao'].strip()
    date = re.search('(PUBLIC|DJ)\s+(\d+)[-\/](\d+)[-\/](\d{4})', text)
    try:
        if date:
            date = datetime(int(date.group(4)), int(date.group(3)), int(date.group(2)))
        else:
            date = ""
    except Exception as e:
        date = ""
        from IPython import embed; embed()

    db.decisoes_monocraticas.update_one({ "_id" : doc['_id']},
                            {
                                "$set": {
                                    "dataPublic": date
                                }
                            })