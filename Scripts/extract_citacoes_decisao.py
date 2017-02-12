#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import pymongo
from pymongo import MongoClient
client = MongoClient()

db = client.DJs
acordaos = db.acordaos
decisoes_monocraticas = db.decisoes_monocraticas


for coll in [acordaos, decisoes_monocraticas]:
    for doc in coll.find({}):
        citacoes = re.findall(r"([A-Z][a-zA-Z]+)\s+([nN].\s+)?([0-9]+((\.[0-9]{3})+)?)((\/[A-Z]+)((\s+|\-|–)[A-Z][a-zA-Z]+(((\-|–)[A-Z][a-zA-Z]+)+)?)?|((\-|–|\s+)[A-Z][a-zA-Z]+(((\-|–)[A-Z][a-zA-Z]+)+)?))", doc['decisao'])

        citacoesDec = set()
        for citacao in citacoes:
            acao_originaria = citacao[0]
            decisao_numero = citacao[2].replace('.', '')
            classes_processuais_str = re.sub('^(\/[A-Z]+\s*(\-|–)|(\-|–|\s+))', '', citacao[7])
            if classes_processuais_str == "":
                classes_processuais_str = re.sub('^(\/[A-Z]+\s*(\-|–)|(\-|–|\s+))', '', citacao[12])

            classes_processuais_list = classes_processuais_str.split('-')[::-1]

            decisao_codigo = " ".join(classes_processuais_list) + " " + acao_originaria + " " + decisao_numero
            citacoesDec.append(decisao_codigo.strip())

        db.coll.update_one({ "_id" : doc['_id']},
                        {
                            "$set": {
                                "citacoesDec": list(citacoesDec)
                            }
                        })



