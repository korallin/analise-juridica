#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import pymongo
from pymongo import MongoClient
import sys


client = MongoClient('mongodb://{}:{}@127.0.0.1:57017'.format(sys.argv[1], sys.argv[2]))

db = client.DJs

# Por questões de ordenação pareada entre nomes de
# collections em coll_names_begin e 'coll_names_end'
# primeiro é feita a inserção ordenada de nomes de collections
# para todos os processos e depois são inseridos os nomes de
# collections de processos de determinados ministros
# coll_names_begin = sorted([name for name in db.collection_names() if re.search(r"(^[^l]+par_removed_1$)", name) != None])
# coll_names_begin.extend(sorted([name for name in db.collection_names() if re.search(r"(.+par_rel.+_removed_1$)", name) != None]))
# coll_names_end = sorted([name for name in db.collection_names() if re.search(r"(^[^l]+[^d]par_10$)", name) != None])
# coll_names_end.extend(sorted([name for name in db.collection_names() if re.search(r"(.+par_rel[^d]+_10$)", name) != None]))

coll_names_begin = sorted([name for name in db.collection_names() if re.search(r"(^[^l]+_removed_1$)", name) != None])
coll_names_begin.extend(sorted([name for name in db.collection_names() if re.search(r"(.+l.+_removed_1$)", name) != None]))
coll_names_end = sorted([name for name in db.collection_names() 
                        if (re.search(r"(^[^l]+_10$)", name) != None) and ("removed" not in name)])
coll_names_end.extend(sorted([name for name in db.collection_names()
                        if (re.search(r"(.+l.+_10$)", name) != None) and ("removed" not in name)]))



days = 0
seconds = 0
# max_days = 0
# coll_max = ""
for coll_begin, coll_end in zip(coll_names_begin, coll_names_end):
    begin_entry = db[coll_begin].find().sort([("_id", 1)]).limit(1)[0]
    end_entry = db[coll_end].find().sort([("_id", -1)]).limit(1)[0]

    delta_time = end_entry['_id'].generation_time - begin_entry['_id'].generation_time
    print(coll_begin, delta_time.days * 24 + delta_time.seconds/3600.)
    # print delta_time.days, coll_begin
    # if delta_time.days > max_days:
    #     max_days = delta_time.days
    #     coll_max = coll_begin

    days += delta_time.days
    seconds += delta_time.seconds

hours = days * 24 + seconds/3600.

# 847.17 horas
# 35.29 dias