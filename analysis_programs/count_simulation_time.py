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
coll_names_begin = sorted([name for name in db.collection_names() if re.search(r"(^[^l]+_removed_1$)", name) != None])
coll_names_begin.extend(sorted([name for name in db.collection_names() if re.search(r"(.+l.+_removed_1$)", name) != None]))
coll_names_end = sorted([name for name in db.collection_names() if re.search(r"(^[^l]+[^d]_10$)", name) != None])
coll_names_end.extend(sorted([name for name in db.collection_names() if re.search(r"(.+l[^d]+_10$)", name) != None]))

days = 0
seconds = 0
for coll_begin, coll_end in zip(coll_names_begin, coll_names_end):
    begin_entry = db[coll_begin].find().sort([("_id", 1)]).limit(1)[0]
    end_entry = db[coll_end].find().sort([("_id", -1)]).limit(1)[0]

    delta_time = end_entry['_id'].generation_time - begin_entry['_id'].generation_time
    days += delta_time.days
    seconds += delta_time.days

hours = days * 24 + seconds/3600.

# 33 horas