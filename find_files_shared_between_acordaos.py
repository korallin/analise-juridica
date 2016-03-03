#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pymongo import MongoClient
import shutil
import os

dir_path = "/home/jackson/analise-juridica/scrapy/inteiros_teores/"
dir_backup = "/home/jackson/analise-juridica/scrapy/inteiros_teores/full_backup"

client = MongoClient('mongodb://localhost:27017')
db = client['DJs']
coll = db['acordaos']

moved_files_dict = {}

cursor = coll.find({"files":{"$exists":True}})
for document in cursor:
    if not os.path.exists(dir_path + document['files']):
        print u"Doesn't exists the inteiro teor {} for acórdão {}".format(document['files'], document['acordaoId']).encode('utf-8')
    else:
        if moved_files_dict.has_key(document['files']):
            print u"inteiro teor do acórdão {} também é apontado por {}".format(document['acordaoId'], moved_files_dict[document['files']])
        else:
            moved_files_dict[document['files']] = document['acordaoId']
        # shutil.move(dir_path + document['files'], dir_backup)

