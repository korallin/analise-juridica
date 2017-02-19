#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
from operator import itemgetter
from collections import defaultdict
import pymongo
from pymongo import MongoClient
client = MongoClient()

classes_processuais_dict = {
    u"AC": u"AÇÃO CAUTELAR",
    u"ACO": u"AÇÃO CÍVEL ORDINÁRIA",
    u"ADC": u"AÇÃO DECLARATÓRIA DE CONSTITUCIONALIDADE",
    u"ADI": u"AÇÃO DIRETA DE INCONSTITUCIONALIDADE",
    u"ADO": u"AÇÃO DIRETA DE INCONSTITUCIONALIDADE POR OMISSÃO",
    u"AO": u"AÇÃO ORIGINÁRIA",
    u"AOE": u"AÇÃO ORIGINÁRIA ESPECIAL",
    u"AP": u"AÇÃO PENAL",
    u"AR": u"AÇÃO RECISÓRIA",
    u"AI": u"AGRAVO DE INSTRUMENTO",
    u"ACI": u"APELAÇÃO CÍVEL",
    u"ADPF": u"ARGUIÇÃO DE DESCUMPRIMENTO DE PRECEITO FUNDAMENTAL",
    u"AIMP": u"ARGUIÇÃO DE IMPEDIMENTO",
    u"ARV": u"ARGUIÇÃO DE RELEVÂNCIA",
    u"AS": u"ARGUIÇÃO DE SUSPEIÇÃO",
    u"CR": u"CARTA ROGATÓRIA",
    u"CM": u"COMUNICAÇÃO",
    u"CA": u"CONFLITO DE ATRIBUIÇÕES",
    u"CC": u"CONFLITO DE COMPETÊNCIA",
    u"CJ": u"CONFLITO DE JURISDIÇÃO",
    u"ED": u"EMBARGO DECLARATÓRIO",
    u"EV": u"EXCEÇÃO DA VERDADE",
    u"EI": u"EXCEÇÃO DE INCOMPETÊNCIA",
    u"EL": u"EXCEÇÃO DE LITISPENDÊNCIA",
    u"ES": u"EXCEÇÃO DE SUSPEIÇÃO",
    u"EXT": u"EXTRADIÇÃO",
    u"HC": u"HABEAS CORPUS",
    u"HD": u"HABEAS DATA",
    u"INQ": u"INQUÉRITO",
    u"IF": u"INTERVENÇÃO FEDERAL",
    u"MI": u"MANDADO DE INJUNÇÃO",
    u"MS": u"MANDADO DE SEGURANÇA",
    u"OACO": u"OPOSIÇÃO EM AÇÃO CIVIL ORIGINÁRIA",
    u"PET": u"PETIÇÃO",
    u"PETA": u"PETIÇÃO AVULSA",
    u"PETAV": u"PETIÇÃO AVULSA",
    u"PPE": u"PRISÃO PREVETIVA PARA EXTRADIÇÃO",
    u"PA": u"PROCESSO ADMINISTRATIVO",
    u"PSV": u"PROPOSTA DE SÚMULA VINCULANTE",
    u"QC": u"QUEIXA-CRIME",
    u"RCL": u"RECLAMAÇÃO",
    u"RC": u"RECURSO CRIME",
    u"RE": u"RECURSO EXTRAORDINÁRIO",
    u"ARE": u"RECURSO EXTRAORDINÁRIO COM AGRAVO",
    u"EP": u"EXECUÇÃO PENAL",
    u"RHC": u"RECURSO ORDINÁRIO EM HABEAS CORPUS",
    u"RHD": u"RECURSO ORDINÁRIO EM HABEAS DATA",
    u"RMI": u"RECURSO ORDINÁRIO EM MANDADO DE INJUNÇÃO",
    u"RMS": u"RECURSO ORDINÁRIO EM MANDADO DE SEGURANÇA",
    u"RP": u"REPRESENTAÇÃO",
    u"RVC": u"REVISÃO CRIMINAL",
    u"SE": u"SENTENÇA ESTRANGEIRA",
    u"SEC": u"SENTENÇA ESTRANGEIRA CONTESTADA",
    u"SL": u"SUSPENÇÃO DE LIMINAR",
    u"SS": u"SUSPENÇÃO DE SEGURANÇA",
    u"STA": u"SUSPENÇÃO DE TUTELA ANTECIPADA",
}

words_black_list_regex = [u'OFÍCIO', u'LEI', u'ARTIGO', u'SÚMULA', u'DJ']
words_black_list_absolut = [u'DE', u'EM', u'MP', u'DO']

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


with open("decisoes_extracao.txt", 'w') as outfile:
    for key, value in sorted(acao_orig_dict.iteritems(), key=itemgetter(1), reverse=True):
        outfile.write("{}: {}\n".format(key, value))

