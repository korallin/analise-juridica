#!/usr/bin/env python
# -*- coding: utf-8 -*-

# import subprocess
import matplotlib.pyplot as plt
import numpy as np
from math import sqrt
from pymongo import MongoClient
from scipy import stats


# encontrar acórdãos mais citados dentro de cada universo (decs. monocs. e acórdaõs)
# número de decisões por corte
# tipos de decisão por corte
# número de cada tipo de decisão
usar um dicionário cuja chave principal é o tipo de corte (orgaoJulg)
    chave secundária -> tipo de acórdão (acordaoType)
        número de decisões por tipo de acórdão

# estatísticas básicas sobre atributos legislação, similares, citações
np.amax()
np.amin()
stats.mode() -> valor e quantidade

np.std()
np.mean()
np.median()


client = MongoClient('mongodb://localhost:27017')
db = client['DJs']

coll_a = db['acordaos']
cursor = coll.find({})
total_a = cursor.count()

simil_a = np.zeros(total_a)
citac_a = np.zeros(total_a)
legis_a = np.zeros(total_a)
for i, document in enumerate(cursor):
    simil_a[i] += len(document['similares'])
    citac_a[i] += len(document['citacoes'])
    legis_a[i] += len(document['legislacao'])

    # tipo de corte
    document['orgaoJulg']    


