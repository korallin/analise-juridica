#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pymongo import MongoClient
import os.path
import urllib2
import shutil
import re
import os

def download_inteiro_teor(url, dir_path):
    # a expressão regular ainda precisa melhorar
    url = re.sub(ur"([^\s%]+)([\s%.\\]|[^\W_])*", ur"\1", url)
    file_name = url.split('asp?')[-1]
    
    new_dir_path = dir_path + "full/"
    if os.path.exists(new_dir_path + file_name):
        return "full/" + file_name

    u = urllib2.urlopen(url)
    f = open(file_name, 'wb')
    meta = u.info()
    if meta.getheaders("Content-Length"):
        file_size = int(meta.getheaders("Content-Length")[0])
        print "Downloading: %s Bytes: %s" % (file_name, file_size)
    else:
        file_size = 1

    file_size_dl = 0
    block_sz = 8192
    while True:
        buffer = u.read(block_sz)
        if not buffer:
            break

        file_size_dl += len(buffer)
        f.write(buffer)
        status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
        status = status + chr(8)*(len(status)+1)
        print status,

    f.close()

    shutil.move(os.getcwd() + "/" + file_name, new_dir_path)

    return "full/" + file_name



client = MongoClient('mongodb://localhost:27017')
db = client['DJs']
coll = db['acordaos']

dir_path = '/home/jackson/analise-juridica/scrapy/inteiros_teores/'

cursor = coll.find({"files":{"$exists":True}})
print "There are {} inteiros teores".format(cursor.count())
for document in cursor:
    if not os.path.exists(dir_path + document['files']):
        print u"Doesn't exists the inteiro teor {} for acórdão {}".format(document['files'], document['acordaoId']).encode('utf-8')


cursor = coll.find({"file_urls":{"$exists":True}})
print "There are {} urls".format(cursor.count())
for document in cursor:
    file_path = download_inteiro_teor(document['file_urls'][0], dir_path)

    coll.replace_one(
        {"_id": document['_id']},
        {
            "$set": {
                "files": file_path
            }
        }
    )

cursor = coll.find(
            {
                "$and": [{"file_urls":{"$exists":True}}, {"files":{"$exists":True}}]
            }
        )
for document in cursor:
    coll.replace_one(
        {"_id": document['_id']},
        {
            "$unset": {
                "file_urls": ""
            }
        }
    )
