#!/usr/bin/python
# -*- coding: utf-8 -*-

import pymongo
from pymongo import MongoClient
client = MongoClient()

db_djs = client.DJs
db_testedjs = client.DJTest

coll_djs = db_djs.acordaos
coll_testedjs = db_testedjs.acordaos

acordao_id_list_testedjs = {resp['acordaoId'] for resp in coll_testedjs.find({"acordaoId":{"$exists": True}}, {"acordaoId":1})}
acordao_id_list_djs = {resp['acordaoId'] for resp in coll_djs.find({"acordaoId":{"$exists": True}}, {"acordaoId":1})}

intersect_ids = acordao_id_list_testedjs.intersection(acordao_id_list_djs)
intersect_ids = list(intersect_ids)

import sys
print sys.stdout.encoding
# val_testedjs = list(coll_testedjs.find({"acordaoId":{"$eq": intersect_ids[0]}}, {"legislacao":1, "citacoes":1, "tags":1}))
# val_djs = list(coll_djs.find({"acordaoId":{"$eq": intersect_ids[0]}}, {"legislacao":1, "citacoes":1, "tags":1}))

# if val_testedjs[0]['legislacao'] != val_djs[0]['legislacao']:
#     print 'LEGISLAÇÃO\n\tTESTE:', val_testedjs[0]['legislacao']
#     print '\tORIGINAL:', val_djs[0]['legislacao']

# if val_testedjs[0]['citacoes'] != val_djs[0]['citacoes']:
#     print 'CITAÇÕES\n\tTESTE:', val_testedjs[0]['citacoes']
#     print '\tORIGINAL:', val_djs[0]['citacoes']

# if ('tags' in val_djs[0]) and ('tags' in val_testedjs[0]):
#     if val_djs[0]['tags'] != val_testedjs[0]['tags']:
#         print 'TAGS\n\tTESTE:', val_testedjs[0]['tags']
#         print '\tORIGINAL:', val_djs[0]['tags']
# elif 'tags' in val_testedjs[0]:
#     print 'TAGS\n\tTESTE:',  val_testedjs[0]['tags']
# elif 'tags' in val_djs[0]:
#     print 'TAGS\n\tORIGINAL:',  val_djs[0]['tags']

fp = open('acordao_differences.txt', 'w') 
for id in intersect_ids:
    val_testedjs = list(coll_testedjs.find({"acordaoId":{"$eq": id}}, {"legislacao":1, "citacoes":1, "tags":1}))
    val_djs = list(coll_djs.find({"acordaoId":{"$eq": id}}, {"legislacao":1, "citacoes":1, "tags":1}))

    try:
        if {} in val_djs[0]['legislacao']:
            val_djs[0]['legislacao'].remove({})

        if val_testedjs[0]['legislacao'] != val_djs[0]['legislacao']:
            fp.write("ACÓRDÃO: {}\n".format(id))
            fp.write('LEGISLAÇÃO\n\tTESTE: {}\n'.format(val_testedjs[0]['legislacao']))
            fp.write('\tORIGINAL: {}\n'.format(val_djs[0]['legislacao']))

        if val_testedjs[0]['citacoes'] != val_djs[0]['citacoes']:
            fp.write("ACÓRDÃO: {}\n".format(id))
            fp.write('CITAÇÕES\n\tTESTE: {}\n'.format(val_testedjs[0]['citacoes']))
            fp.write('\tORIGINAL: {}\n'.format(val_djs[0]['citacoes']))

        if ('tags' in val_djs[0]) and ('tags' in val_testedjs[0]):
            if val_djs[0]['tags'] != val_testedjs[0]['tags']:
                fp.write("ACÓRDÃO: {}\n".format(id))
                fp.write('TAGS\n\tTESTE: {}\n'.format(val_testedjs[0]['tags']))
                fp.write('\tORIGINAL: {}\n'.format(val_djs[0]['tags']))
        elif 'tags' in val_testedjs[0]:
            fp.write("ACÓRDÃO: {}\n".format(id))
            fp.write('TAGS\n\tTESTE: {}\n'.format(val_testedjs[0]['tags']))
        elif 'tags' in val_djs[0]:
            fp.write("ACÓRDÃO: {}\n".format(id))
            fp.write('TAGS\n\tORIGINAL: {}\n'.format(val_djs[0]['tags']))
    except Exception as e:
	print type(id)
        print id.encode('UTF8')

fp.close()
