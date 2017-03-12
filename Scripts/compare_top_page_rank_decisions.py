#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pymongo import MongoClient


# python compare_top_page_rank_decisions.py DJs stf_pr_1_acordaos
# python compare_top_page_rank_decisions.py DJs stf_pr_2_acordaos

dbName = sys.argv[1]
collection_name = sys.argv[2]

client = MongoClient('localhost', 27017)
db = client[dbName]


def get_columns_len_tup(page_ranks_iter, data_type):

    if len(page_ranks_iter) == 0:
        return ()

    if data_type is dict:
        dec_id_len = max([len(pr["acordaoId"]) for pr in page_ranks_iter])
        relator_len = max([len(pr["relator"]) for pr in page_ranks_iter])
    elif data_type is list:
        dec_id_len = max([len(pr[0]) for pr in page_ranks_iter])
        relator_len = max([len(pr[1]) for pr in page_ranks_iter])
    else:
        dec_id_len = max([len(k) for k, v in page_ranks_iter])
        relator_len = max([len(v[1]) for k, v in page_ranks_iter])

    # 3° parâmetro corresponde a tamanho do espaço usado para marcar atributo como virtual
    return (dec_id_len, relator_len, 1)


def construct_string(values, lengths):
    string = ""
    for v, l in zip(values, lengths):
        v_str = str(v.encode('utf-8'))
        string += " %s" % v_str + " " * (l - len(v)) + " |"

    return string


removed_decisions_iters = []
page_ranks_iters = []

for i in xrange(1, 11):
    coll_rank = collection_name + "_%d" % i
    coll_removed = collection_name + "_removed_%d" % i

    page_ranks_cursor = db[coll_rank].find({}, {"acordaoId": 1, "pageRank": 1, 'virtual': 1, 'relator': 1}).sort([("pageRank", -1)]).limit(100)
    page_ranks_iters.append(list(page_ranks_cursor))

    removed_decisions_cursor = db[coll_removed].find({})
    removed_decisions_iters.append(list(removed_decisions_cursor)[0]['removed_decisions'])



# DESCRIÇÃO GERAL antes da por iteração
page_rank_ids_relatores_lists = [[(pr['acordaoId'], pr['relator'], pr['virtual']) for pr in pr_list] for pr_list in page_ranks_iters]

print "Descrição de informações da simulação do page rank por iteração\n"
# DESCRIÇÃO POR ITERAÇÃO
decisoes_removidas_no_top100 = []
for i in xrange(10):

    columns = get_columns_len_tup(decisoes_removidas_no_top100, list)

    print "Iteração %d" % (i+1)
    print "IDs presentes na iteraçao anterior e que foram removidos na simulação da iteração atual"
    print "DECISION ID | RELATOR | VIRTUAL"
    for pr_it in decisoes_removidas_no_top100:
        virtual = "S" if pr_it[2] is True else "N"
        string = construct_string([pr_it[0], pr_it[1], virtual], columns)
        print string[:-2]
    print ""
    
    columns = get_columns_len_tup(page_ranks_iters[i], dict)
    print "RANK | DECISION ID | RELATOR | VIRTUAL | PAGE RANK"
    for j, pr_it in enumerate(page_ranks_iters[i]):
        virtual = "S" if pr_it['virtual'] is True else "N"
        string = construct_string([pr_it['acordaoId'], pr_it['relator'], virtual], columns)
        string = " {}{} |".format(j+1, " " * (4 - len(str(j+1)))) + string + " {0:.6f}".format(pr_it['pageRank'])
        print string

    if (i+1) < 10:
        decisoes_removidas_no_top100 = filter(lambda v: v[0] in removed_decisions_iters[i+1], page_rank_ids_relatores_lists[i])

    print "\n"


# DESCRIÇÃO GERAL após da por iteração
# intersecção de tuplas (ID, relator) presentes no page rank em todas as iterações
ids_relatores_intersect = reduce(set.intersection, map(set, page_rank_ids_relatores_lists))
columns = get_columns_len_tup(ids_relatores_intersect, list)
print "\nDecisões presentes em todos as iterações do page rank"
print "DECISION ID | RELATOR | VIRTUAL"
for pr_it in ids_relatores_intersect:
    virtual = "S" if pr_it[2] is True else "N"
    string = construct_string([pr_it[0], pr_it[1], virtual], columns)
    print string[:-2]
print "\n"


decisions_occurance = {}
for i, pr_list in enumerate(page_ranks_iters):
    for j, pr_it in enumerate(pr_list):
        dec_id = pr_it['acordaoId']
        if dec_id in decisions_occurance:
            decisions_occurance[dec_id][-1] += 1
            decisions_occurance[dec_id][0].append((i+1,j+1))
        else:
            decisions_occurance[dec_id] = [[(i+1, j+1)], pr_it['relator'], pr_it['virtual'], 1]

frequent_decisions = filter(lambda (k, v): v[-1] > 1, decisions_occurance.iteritems())

frequent_decisions_sorted = sorted(frequent_decisions, key=lambda x: x[1][-1], reverse=True)

print "Number of items whose frequency is higher than 1: %d" % len(frequent_decisions)

# precisa ver tipo exato aqui
columns = get_columns_len_tup(frequent_decisions_sorted, None)
print "Most frequent decisions by invserse order"
print "RANK | DECISION ID | RELATOR | VIRTUAL | NUMBER OF OCCURANCES"
# apesar de também serem armazenadas as iterações nas quais
# os IDs aparecem ache que a informação não era tão relevante 
for i, (key, value) in enumerate(frequent_decisions_sorted):
    virtual = "S" if value[2] is True else "N"
    string = construct_string([key, value[1], virtual], columns)
    string = " {}{} |".format(i+1, " " * (4 - len(str(j)))) + string + " {}".format(value[3])
    print string


# -----  ver como a ordem dos acórdãos se alterna em cada iteração do page rank
# talvez adicionar informação (tupla) referente a iteração e último rank em que acórdão apareceu
# pode ser usado um dict para armazenar ambas as informações

# Exibir quantos acórdãos possuem determinada frequência - soma das frequências deve ser = 1000