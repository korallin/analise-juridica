#!/usr/bin/env python
# -*- coding: utf-8 -*-

# import subprocess

# quando der algum problema na matplotlib relacionado a 'DISPLAY is undefined' executar:
import matplotlib
matplotlib.use('Agg')

import operator
import matplotlib.pyplot as plt
import numpy as np
from math import sqrt
from pymongo import MongoClient
from scipy import stats
from collections import defaultdict

# trecho de código usado para evitar erro do tipo:
# UnicodeDecodeError: 'ascii' codec can't decode byte 0xc3 in position 2: ordinal not in range(128)
import sys
reload(sys)  
sys.setdefaultencoding('utf8')

def generate_graph(total, array, mean, median, std, min, max, mode, info_t, dec_t):
    fig, ax = plt.subplots(1)

    result = ax.hist(array, bins=400, color='c')
    textstr = '$\mu=%.2f$\n$\mathrm{median}=%.2f$\n$\sigma=%.2f$\n$max=%.2f$\n$min=%.2f$\n$moda=%.2f, freq=%.2f$'%(mean,
                                                                                            median, std, max, min, mode[0], mode[1])
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    ax.text(0.95, 0.95, textstr, transform=ax.transAxes, fontsize=14,
            verticalalignment='top', horizontalalignment='right', bbox=props)
    plt.axvline(mean, color='r', linestyle='dashed', linewidth=2)
    plt.axvline(median, color='g', linestyle='dotted', linewidth=2)

    plt.title("{0} (Núm. de {0}: {1} )".format(dec_t, total))
    plt.xlabel('Número de {0} (decisões com 0 {0} foram removidas do gráfico)'.format(info_t))
    plt.ylabel('Número de {}'.format(dec_t))
    plt.savefig('graficos/{}_{}.png'.format(dec_t, info_t))

# encontrar acórdãos mais citados dentro de cada universo (decs. monocs. e acórdaõs)
# número de decisões por corte
# tipos de decisão por corte
# número de cada tipo de decisão
# usar um dicionário cuja chave principal é o tipo de corte (orgaoJulg)
#     chave secundária -> tipo de acórdão (acordaoType)
#         número de decisões por tipo de acórdão


client = MongoClient('mongodb://localhost:27017')
db = client['DJTest']

coll_a = db['acordaos']
cursor = coll_a.find({})
total_a = cursor.count()

citac_a = np.zeros(total_a)
citac_dec = np.zeros(total_a)
simil_a = np.zeros(total_a)
legis_a = np.zeros(total_a)
decision_types_a = defaultdict(int)
org_julg = defaultdict(lambda: defaultdict(int))

citados_a = defaultdict(int)
citados_dec = defaultdict(int)
for i, document in enumerate(cursor):
    try:
        simil_a[i] += len(document['similares'])
        citac_a[i] += len(document['citacoes'])
        citac_dec[i] += len(document['citacoesDec'])

        legis_a[i] += len(document['legislacao'])

        decision_types_a[document['acordaoType']] += 1
        for acordaoId in document['citacoes']:
            citados_a[acordaoId] += 1

        for acordaoId in document['citacoesDec']:
            citados_dec[acordaoId] += 1

        # tipo de corte
        org_julg[document['orgaoJulg']][document['acordaoType']] += 1
    except:
        from IPython import embed; embed()


# imprimir tabela de dados relacionados a dicionarios
sorted(citados_a.items(), key=operator.itemgetter(1))[-40:]
print sorted(citados_dec.items(), key=operator.itemgetter(1))[-40:]
sorted(decision_types_a.items(), key=operator.itemgetter(1))

# ver quais dos tipos aqui estão previstos nos relatórios
for key, dict_vals in org_julg.iteritems():
    print key
    for k, v in sorted(dict_vals.items(), key=operator.itemgetter(1), reverse=True)[:40]:
        print "    {} | {}".format(k, v)


# número de acórdãos sem citações, legislação e similares
print "Número de acórdãos sem legislação, citações e similares: ", len(filter(lambda (x, y, z): x == y == z == 0, zip(simil_a, citac_a, legis_a)))
print "Número de acórdãos com apenas legislação ou citações ou similares: ", len(filter(lambda (x, y, z): (x == y == 0) or (y == z == 0) or (x == z == 0), zip(simil_a, citac_a, legis_a)))
print "Número de acórdãos com legislação, citações e similares: ", len(filter(lambda (x, y, z): (x != 0) and (y != 0) and (x != 0), zip(simil_a, citac_a, legis_a)))
# número de acórdãos em que pelo menos dois tipos de dados são não zeros
print "Número de acórdãos em que apenas um dos tipos de dados (legislação, citações e similares) não está presente: ", total_a - len(filter(lambda (x, y, z): (x == y == 0) or (y == z == 0) or (x == z == 0), zip(simil_a, citac_a, legis_a)))

print "Número de acórdãos sem legislação, citações de DECISAO e similares: ", len(filter(lambda (x, y, z): x == y == z == 0, zip(simil_a, citac_dec, legis_a)))
print "Número de acórdãos com apenas legislação ou citações de DECISAO ou similares: ", len(filter(lambda (x, y, z): (x == y == 0) or (y == z == 0) or (x == z == 0), zip(simil_a, citac_dec, legis_a)))
print "Número de acórdãos com legislação, citações de DECISAO e similares: ", len(filter(lambda (x, y, z): (x != 0) and (y != 0) and (x != 0), zip(simil_a, citac_dec, legis_a)))
# número de acórdãos em que pelo menos dois tipos de dados são não zeros
print "Número de acórdãos em que apenas um dos tipos de dados (legislação, citações de DECISAO e similares) não está presente: ", total_a - len(filter(lambda (x, y, z): (x == y == 0) or (y == z == 0) or (x == z == 0), zip(simil_a, citac_dec, legis_a)))


for list_t, info_t in zip([simil_a, citac_a, citac_dec, legis_a], ['Similares', 'Citacoes', 'Citacoes DEC', 'Legislacao']):
    mean = np.mean(list_t)
    std = np.std(list_t)
    median = np.median(list_t)
    min_ = np.amin(list_t)
    max_ = np.amax(list_t)
    # [moda, moda_freq]
    mode = [val[0] for val in stats.mode(list_t)]

    array = np.array([a for a in list_t if a > 0])
    generate_graph(total_a, array, mean, median, std, min_, max_, mode, info_t, 'Acórdãos')


coll_dc = db['decisoes_monocraticas']
cursor = coll_dc.find({})
total_dc = cursor.count()

simil_dc = np.zeros(total_dc)
legis_dc = np.zeros(total_dc)
citac_dc = np.zeros(total_dc)

decision_types_dc = defaultdict(int)
for i, document in enumerate(cursor):
    simil_dc[i] += len(document['similares'])
    legis_dc[i] += len(document['legislacao'])
    citac_dc[i] += len(document['citacoesDec'])

    decision_types_dc[document['acordaoType']] += 1

print sorted(decision_types_dc.items(), key=operator.itemgetter(1))

# número de acórdãos sem legislação e similares
print "Número de dec. monocs. sem legislação, citacoes de DECISÃO e similares: ", len(filter(lambda (x, y, z): x == z == y == 0, zip(simil_dc,  citac_dc, legis_dc)))
print "Número de dec. monocs. apenas com legislação ou citacoes de DECISÃO ou similares: ", len(filter(lambda (x, y, z): (x == y == 0) or (y == z == 0) or (x == z == 0), zip(simil_dc, citac_dc, legis_dc)))
print "Número de dec. monocs. com legislação citacoes de DECISÃO e similares: ", len(filter(lambda (x, y, z): (x != 0) and (y != 0) and (x != 0), zip(simil_dc, citac_dc, legis_dc)))
print "Número de acórdãos em que apenas um dos tipos de dados (legislação, citações de DECISAO e similares) não está presente: ", total_dc - len(filter(lambda (x, y, z): (x == y == 0) or (y == z == 0) or (x == z == 0), zip(simil_dc, citac_dc, legis_dc)))

for list_t, info_t in zip([simil_dc, citac_dc, legis_dc], ['Similares', 'Citacoes Dec', 'Legislacao']):
    mean = np.mean(list_t)
    std = np.std(list_t)
    median = np.median(list_t)
    min_ = np.amin(list_t)
    max_ = np.amax(list_t)
    # [moda, moda_freq]
    mode = [val[0] for val in stats.mode(list_t)]

    array = np.array([a for a in list_t if a > 0])
    generate_graph(total_dc, array, mean, median, std, min_, max_, mode, info_t, 'Decisões Monocráticas')


# pegar informações das tags
# usar ano de publicação do acórdão -> decisão monocrática pode não ter ano de publicação
# fazer análises por tipos de controle:
    # controle concentrado em abstrato de onstitucionalidade (Processos constitucionais)
    # controle de constitucionalidade a partir de casos individuais, concretos (Processos recursais)

# no clustering seria interessante primeiro criar 3 clusters para separar as classes processuais