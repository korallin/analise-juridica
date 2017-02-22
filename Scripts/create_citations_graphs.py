#!/usr/bin/python
# -*- coding: utf-8 -*-

import pymongo
from pymongo import MongoClient
client = MongoClient()

db = client.DJs
acordaos = db.acordaos
decisoes_monocraticas = db.decisoes_monocraticas

db.grafo_citacoes_decisoes.drop()
grafo_citacoes_decisoes = db.grafo_citacoes_decisoes

for coll, coll_abrev in zip([acordaos, decisoes_monocraticas], ["A", "DM"]):
    for doc in coll.find({}):
        citacao_doc = { "decisaoId": doc['acordaoId'],              # acórdão que cita
                        "decisoesCitadasObs": doc['citacoesObs'],   # acórdãos citados na seção observação
                        "acordaosCitadosDec": doc['citacoes'],      # acórdãos citados na seção decisão
                        "decisaoFonteDecTipo": coll_abrev,          # tipo de decisão de origem da decisão citante
                                                                    # (A - acórdão ou DM - decisão monocrática)
                        "dataPublic": doc['dataPublic']             # Foi adotada a data de publicação de acórdão
                                                                    # porque é quando ele passa a valer
                    }

        grafo_citacoes_decisoes.insert_one(citacao_doc)


# criar um grafo de citações entre relatores
# no momento da análise diferenciar acórdãos de decisões monocráticas
# para ver se o fato de haver mais ministros participando das decisões
# influencia em citar decisões de outros relatores
