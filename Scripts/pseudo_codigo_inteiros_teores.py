
import glob
from pymongo import MongoClient
import os
import re

# O script foi criado com o propósito de remover inteiros teores baixados que possuem
# nomes que possuem uma padrão estranho
# Incorporar este código no script de downalods de inteiros teores e dar nome parecido com
# auditoria/checagem de inteiros teores


path = "/home/jackson/analise-juridica/scrapy/inteiros_teores/full/*"
files = glob.glob(path)

files_dict = {}
for f in files:
    f_match = re.search(r"[^/]/([^/]+)$", f)
    files_dict[f_match.groups(1)[0]] = f


client = MongoClient('mongodb://localhost:27017')
db = client['DJs']
coll = db['acordaos']

for doc in coll.find({}, {"files": 1, "_id":0}):
	f_match = re.search(r"[^/]/([^/]+)$", doc["files"])
	files_dict[f_match.groups(1)[0]] = None

files_to_delete = filter(lambda value: value is not None, files_dict.values())

for complete_path in files_to_delete:
    os.remove(complete_path)
