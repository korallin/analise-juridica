#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import re
from collections import defaultdict
import pymongo
from pymongo import MongoClient
client = MongoClient()

classes_processuais_dict = {
    "AC": "AÇÃO CAUTELAR",
    "ACO": "AÇÃO CÍVEL ORDINÁRIA",
    "ADC": "AÇÃO DECLARATÓRIA DE CONSTITUCIONALIDADE",
    "ADI": "AÇÃO DIRETA DE INCONSTITUCIONALIDADE",
    "ADO": "AÇÃO DIRETA DE INCONSTITUCIONALIDADE POR OMISSÃO",
    "AO": "AÇÃO ORIGINÁRIA",
    "AOE": "AÇÃO ORIGINÁRIA ESPECIAL",
    "AP": "AÇÃO PENAL",
    "AR": "AÇÃO RECISÓRIA",
    "AI": "AGRAVO DE INSTRUMENTO",
    "ACI": "APELAÇÃO CÍVEL",
    "ADPF": "ARGUIÇÃO DE DESCUMPRIMENTO DE PRECEITO FUNDAMENTAL",
    "AIMP": "ARGUIÇÃO DE IMPEDIMENTO",
    "ARV": "ARGUIÇÃO DE RELEVÂNCIA",
    "AS": "ARGUIÇÃO DE SUSPEIÇÃO",
    "CR": "CARTA ROGATÓRIA",
    "CM": "COMUNICAÇÃO",
    "CA": "CONFLITO DE ATRIBUIÇÕES",
    "CC": "CONFLITO DE COMPETÊNCIA",
    "CJ": "CONFLITO DE JURISDIÇÃO",
    "ED": "EMBARGO DECLARATÓRIO",
    "EV": "EXCEÇÃO DA VERDADE",
    "EI": "EXCEÇÃO DE INCOMPETÊNCIA",
    "EL": "EXCEÇÃO DE LITISPENDÊNCIA",
    "ES": "EXCEÇÃO DE SUSPEIÇÃO",
    "EXT": "EXTRADIÇÃO",
    "HC": "HABEAS CORPUS",
    "HD": "HABEAS DATA",
    "INQ": "INQUÉRITO",
    "IF": "INTERVENÇÃO FEDERAL",
    "MI": "MANDADO DE INJUNÇÃO",
    "MS": "MANDADO DE SEGURANÇA",
    "OACO": "OPOSIÇÃO EM AÇÃO CIVIL ORIGINÁRIA",
    "PET": "PETIÇÃO",
    "PETA": "PETIÇÃO AVULSA",
    "PETAV": "PETIÇÃO AVULSA",
    "PPE": "PRISÃO PREVETIVA PARA EXTRADIÇÃO",
    "PA": "PROCESSO ADMINISTRATIVO",
    "PSV": "PROPOSTA DE SÚMULA VINCULANTE",
    "QC": "QUEIXA-CRIME",
    "RCL": "RECLAMAÇÃO",
    "RC": "RECURSO CRIME",
    "RE": "RECURSO EXTRAORDINÁRIO",
    "ARE": "RECURSO EXTRAORDINÁRIO COM AGRAVO",
    "EP": "EXECUÇÃO PENAL",
    "RHC": "RECURSO ORDINÁRIO EM HABEAS CORPUS",
    "RHD": "RECURSO ORDINÁRIO EM HABEAS DATA",
    "RMI": "RECURSO ORDINÁRIO EM MANDADO DE INJUNÇÃO",
    "RMS": "RECURSO ORDINÁRIO EM MANDADO DE SEGURANÇA",
    "RP": "REPRESENTAÇÃO",
    "RVC": "REVISÃO CRIMINAL",
    "SE": "SENTENÇA ESTRANGEIRA",
    "SEC": "SENTENÇA ESTRANGEIRA CONTESTADA",
    "SL": "SUSPENÇÃO DE LIMINAR",
    "SS": "SUSPENÇÃO DE SEGURANÇA",
    "STA": "SUSPENÇÃO DE TUTELA ANTECIPADA",
}

words_black_list_regex = ['OFÍCIO', 'LEI', 'ARTIGO', 'SÚMULA', 'DJ']
words_black_list_absolut = ['DE', 'EM', 'MP', 'DO']

acao_orig_dict = defaultdict(int)

# TESTAR

# db.decisoes_monocraticas.find({}, {citacoesDec:1, acordaoId:1})
def get_acao_originaria(acao_originaria):
    global acao_orig_dict
    existe_ac_orig = True
    if acao_originaria not in classes_processuais_dict:
        existe_ac_orig = False
        # checa se acao_originaria é uma sigla e se ela possui
        # correspondência idêntica nas chaves do dicionário
        for value in classes_processuais_dict.values():
            if re.search(value.split(" ")[-1], acao_originaria, re.UNICODE):
                existe_ac_orig = True
                break

        # verifica se possivel ação originária é na verdade um
        # ente que não é classe processual
        if not existe_ac_orig:
            for word in words_black_list_regex:
                if re.search(word, acao_originaria, re.UNICODE):
                    return ""

            for word in words_black_list_absolut:
                if re.search(acao_originaria, word, re.UNICODE):
                    return ""

    if existe_ac_orig is False:
        acao_orig_dict[acao_originaria] += 1

    return acao_originaria


db = client.DJTest
acordaos = db.acordaos
decisoes_monocraticas = db.decisoes_monocraticas

contador = 0
for coll, atributo in zip([acordaos, decisoes_monocraticas], ['ementa', 'decisao']):
    for doc in coll.find({}):
        citacoes = re.findall(r"([A-Z]\w+)\s+([nN].\s+)?([0-9]+((\.[0-9]{3})+)?)(((\/\s*[A-Z]+)?((\-|–|\s+)[A-Z]\w+(((\-|–)[A-Z]\w+)+)?)?))(?!\/\d+|\.|\d+)", doc[atributo], re.UNICODE)

        citacoesDec = set()
        for citacao in citacoes:
            acao_originaria = get_acao_originaria(citacao[0].strip().upper())
            if acao_originaria == '':
                continue

            decisao_numero = citacao[2].replace('.', '')
            classes_processuais_str = re.sub('^(\/[A-Z]+\s*(\-|–)|(\-|–|\s+))|(\/[A-Z]+\s*)$', '', citacao[8])
            if classes_processuais_str == "":
                classes_processuais_str = re.sub('^(\/[A-Z]+\s*(\-|–)|(\-|–|\s+))|(\/[A-Z]+\s*)$', '', citacao[10])

            classes_processuais_list = classes_processuais_str.split('-')[::-1]

            decisao_codigo = " ".join([s.upper() for s in classes_processuais_list]) + " " + acao_originaria + " " + decisao_numero
            citacoesDec.add(decisao_codigo.strip())

        coll.update_one({ "_id" : doc['_id']},
                        {
                            "$set": {
                                "citacoesDec": list(citacoesDec)
                            }
                        })

        contador += 1
        if contador % 10000 == 0:
            print contador

with open("decisoes_extracao.json", 'w') as outfile:
    json.dump(acao_orig_dict, outfile)
