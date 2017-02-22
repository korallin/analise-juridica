#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pymongo import MongoClient
from collections import defaultdict

# Nome do script é auto explicativo


# ver onde encaixar ED (embargo declaratório) e EDv (embargo de divergência)

# {
#     "AC": "AÇÃO CAUTELAR",
#     "ACO": "AÇÃO CÍVEL ORDINÁRIA",
#     "ADC": "AÇÃO DECLARATÓRIA DE CONSTITUCIONALIDADE",
#     "ADI": "AÇÃO DIRETA DE INCONSTITUCIONALIDADE",
#     "ADO": "AÇÃO DIRETA DE INCONSTITUCIONALIDADE POR OMISSÃO",
#     "AO": "AÇÃO ORIGINÁRIA",
#     "AOE": "AÇÃO ORIGINÁRIA ESPECIAL",
#     "AP": "AÇÃO PENAL",
#     "AR": "AÇÃO RECISÓRIA",
#     "AI": "AGRAVO DE INSTRUMENTO",
#     "Aci": "APELAÇÃO CÍVEL",
#     "ADPF": "ARGUIÇÃO DE DESCUMPRIMENTO DE PRECEITO FUNDAMENTAL",
#     "Aimp": "ARGUIÇÃO DE IMPEDIMENTO",
#     "Arv": "ARGUIÇÃO DE RELEVÂNCIA",
#     "AS": "ARGUIÇÃO DE SUSPEIÇÃO",
#     "CR": "CARTA ROGATÓRIA",
#     "Cm": "COMUNICAÇÃO",
#     "CA": "CONFLITO DE ATRIBUIÇÕES",
#     "CC": "CONFLITO DE COMPETÊNCIA",
#     "CJ": "CONFLITO DE JURISDIÇÃO",
#     "ED": "EMBARGO DECLARATÓRIO",
#     "EV": "EXCEÇÃO DA VERDADE",
#     "EI": "EXCEÇÃO DE INCOMPETÊNCIA",
#     "EL": "EXCEÇÃO DE LITISPENDÊNCIA",
#     "ES": "EXCEÇÃO DE SUSPEIÇÃO",
#     "Ext": "EXTRADIÇÃO",
#     "HC": "HABEAS CORPUS",
#     "HD": "HABEAS DATA",
#     "Inq": "INQUÉRITO",
#     "IF": "INTERVENÇÃO FEDERAL",
#     "MI": "MANDADO DE INJUNÇÃO",
#     "MS": "MANDADO DE SEGURANÇA",
#     "OACO": "OPOSIÇÃO EM AÇÃO CIVIL ORIGINÁRIA",
#     "Pet": "PETIÇÃO",
#     "PETA": "PETIÇÃO AVULSA",
#     "PETAV": "PETIÇÃO AVULSA",
#     "PPE": "PRISÃO PREVETIVA PARA EXTRADIÇÃO",
#     "PA": "PROCESSO ADMINISTRATIVO",
#     "PSV": "PROPOSTA DE SÚMULA VINCULANTE",
#     "QC": "QUEIXA-CRIME",
#     "Rcl": "RECLAMAÇÃO",
#     "RC": "RECURSO CRIME",
#     "RE": "RECURSO EXTRAORDINÁRIO",
#     "ARE": "RECURSO EXTRAORDINÁRIO COM AGRAVO",
#     "EP": "EXECUÇÃO PENAL",
#     "RHC": "RECURSO ORDINÁRIO EM HABEAS CORPUS",
#     "RHD": "RECURSO ORDINÁRIO EM HABEAS DATA",
#     "RMI": "RECURSO ORDINÁRIO EM MANDADO DE INJUNÇÃO",
#     "RMS": "RECURSO ORDINÁRIO EM MANDADO DE SEGURANÇA",
#     "Rp": "REPRESENTAÇÃO",
#     "RvC": "REVISÃO CRIMINAL",
#     "SE": "SENTENÇA ESTRANGEIRA",
#     "SEC": "SENTENÇA ESTRANGEIRA CONTESTADA",
#     "SL": "SUSPENÇÃO DE LIMINAR",
#     "SS": "SUSPENÇÃO DE SEGURANÇA",
#     "STA": "SUSPENÇÃO DE TUTELA ANTECIPADA",
# }

fgv_dict = {
    "AC": "PROCESSOS ORDINÁRIOS",
    "ACO": "PROCESSOS ORDINÁRIOS",
    "ADC": "PROCESSOS CONSTITUCIONAIS",
    "ADI": "PROCESSOS CONSTITUCIONAIS",
    "ADO": "PROCESSOS CONSTITUCIONAIS",
    "AO": "PROCESSOS ORDINÁRIOS",
    "AOE": "PROCESSOS ORDINÁRIOS",
    "AP": "PROCESSOS ORDINÁRIOS",
    "AR": "PROCESSOS ORDINÁRIOS",
    "AI": "PROCESSOS RECURSAIS",
    "ACI": "PROCESSOS ORDINÁRIOS",
    "ADPF": "PROCESSOS CONSTITUCIONAIS",
    "AIMP": "PROCESSOS ORDINÁRIOS",
    "ARV": "PROCESSOS ORDINÁRIOS",
    "AS": "PROCESSOS ORDINÁRIOS",
    "CR": "PROCESSOS ORDINÁRIOS",
    "CM": "PROCESSOS ORDINÁRIOS",
    "CA": "PROCESSOS ORDINÁRIOS",
    "CC": "PROCESSOS ORDINÁRIOS",
    "CJ": "PROCESSOS ORDINÁRIOS",
    "EV": "PROCESSOS ORDINÁRIOS",
    "EI": "PROCESSOS ORDINÁRIOS",
    "EL": "PROCESSOS ORDINÁRIOS",
    "ES": "PROCESSOS ORDINÁRIOS",
    "EXT": "PROCESSOS ORDINÁRIOS",
    "HC": "PROCESSOS ORDINÁRIOS",
    "HD": "PROCESSOS ORDINÁRIOS",
    "INQ": "PROCESSOS ORDINÁRIOS",
    "IF": "PROCESSOS ORDINÁRIOS",
    "MI": "PROCESSOS CONSTITUCIONAIS",
    "MS": "PROCESSOS ORDINÁRIOS",
    "OACO": "PROCESSOS ORDINÁRIOS",
    "PET": "PROCESSOS ORDINÁRIOS",
    "PETA": "PROCESSOS ORDINÁRIOS",
    "PETAV": "PROCESSOS ORDINÁRIOS",
    "PPE": "PROCESSOS ORDINÁRIOS",
    "PA": "PROCESSOS ORDINÁRIOS",
    "PSV": "PROCESSOS CONSTITUCIONAIS",
    "QC": "PROCESSOS ORDINÁRIOS",
    "RCL": "PROCESSOS ORDINÁRIOS",
    "RC": "PROCESSOS ORDINÁRIOS",
    "RE": "PROCESSOS RECURSAIS",
    "ARE": "PROCESSOS ORDINÁRIOS",
    "EP": "PROCESSOS ORDINÁRIOS",
    "RHC": "PROCESSOS ORDINÁRIOS",
    "RHD": "PROCESSOS ORDINÁRIOS",
    "RMI": "PROCESSOS ORDINÁRIOS",
    "RMS": "PROCESSOS ORDINÁRIOS",
    "RP": "PROCESSOS ORDINÁRIOS",
    "RVC": "PROCESSOS ORDINÁRIOS",
    "SE": "PROCESSOS ORDINÁRIOS",
    "SEC": "PROCESSOS ORDINÁRIOS",
    "SL": "PROCESSOS ORDINÁRIOS",
    "SS": "PROCESSOS ORDINÁRIOS",
    "STA": "PROCESSOS ORDINÁRIOS",
}
# Fonte: III Relatório Supremo em Números - O Supremo e o Tempo

# Alterado
not_fgv_dict = {
    "AC": "PROCESSOS ORDINÁRIOS",
    "ACO": "PROCESSOS ORDINÁRIOS",
    "ADC": "PROCESSOS CONSTITUCIONAIS",
    "ADI": "PROCESSOS CONSTITUCIONAIS",
    "ADO": "PROCESSOS CONSTITUCIONAIS",
    "AO": "PROCESSOS ORDINÁRIOS",
    "AOE": "PROCESSOS ORDINÁRIOS",
    "AP": "PROCESSOS ORDINÁRIOS",
    "AR": "PROCESSOS ORDINÁRIOS",
    "AI": "PROCESSOS RECURSAIS",
    "ACI": "PROCESSOS RECURSAIS",
    "ADPF": "PROCESSOS CONSTITUCIONAIS",
    "AIMP": "PROCESSOS ORDINÁRIOS",
    "ARV": "PROCESSOS ORDINÁRIOS",
    "AS": "PROCESSOS ORDINÁRIOS",
    "CR": "PROCESSOS ORDINÁRIOS",
    "CM": "PROCESSOS ORDINÁRIOS",
    "CA": "PROCESSOS ORDINÁRIOS",
    "CC": "PROCESSOS ORDINÁRIOS",
    "CJ": "PROCESSOS ORDINÁRIOS",
    "ED": "PROCESSOS RECURSAIS",
    "EV": "PROCESSOS ORDINÁRIOS",
    "EI": "PROCESSOS ORDINÁRIOS",
    "EL": "PROCESSOS ORDINÁRIOS",
    "ES": "PROCESSOS ORDINÁRIOS",
    "EXT": "PROCESSOS ORDINÁRIOS",
    "HC": "PROCESSOS ORDINÁRIOS",
    "HD": "PROCESSOS ORDINÁRIOS",
    "INQ": "PROCESSOS ORDINÁRIOS",
    "IF": "PROCESSOS ORDINÁRIOS",
    "MI": "PROCESSOS CONSTITUCIONAIS",
    "MS": "PROCESSOS ORDINÁRIOS",
    "OACO": "PROCESSOS ORDINÁRIOS",
    "PET": "PROCESSOS ORDINÁRIOS",
    "PETA": "PROCESSOS ORDINÁRIOS",
    "PETAV": "PROCESSOS ORDINÁRIOS",
    "PPE": "PROCESSOS ORDINÁRIOS",
    "PA": "PROCESSOS ORDINÁRIOS",
    "PSV": "PROCESSOS CONSTITUCIONAIS",
    "QC": "PROCESSOS ORDINÁRIOS",
    "RCL": "PROCESSOS ORDINÁRIOS",
    "RC": "PROCESSOS RECURSAIS",
    "RE": "PROCESSOS RECURSAIS",
    "ARE": "PROCESSOS RECURSAIS",
    "EP": "PROCESSOS ORDINÁRIOS",
    "RHC": "PROCESSOS RECURSAIS",
    "RHD": "PROCESSOS RECURSAIS",
    "RMI": "PROCESSOS RECURSAIS",
    "RMS": "PROCESSOS RECURSAIS",
    "RP": "PROCESSOS ORDINÁRIOS",
    "RVC": "PROCESSOS ORDINÁRIOS",
    "SE": "PROCESSOS ORDINÁRIOS",
    "SEC": "PROCESSOS ORDINÁRIOS",
    "SL": "PROCESSOS ORDINÁRIOS",
    "SS": "PROCESSOS ORDINÁRIOS",
    "STA": "PROCESSOS ORDINÁRIOS",
}


client = MongoClient('mongodb://localhost:27017')
db = client['DJs']

coll_a = db['acordaos']
cursor = coll_a.find({})
acordaos_total = cursor.count()

cortes_fgv_acordaos = defaultdict(lambda: defaultdict(int))
cortes_not_fgv_acordaos = defaultdict(lambda: defaultdict(int))

cortes_sum_fgv = defaultdict(int)
cortes_sum_not_fgv = defaultdict(int)

matriz_file = open("matriz_perplexidade.txt", 'w')

for doc in cursor:
    # pegar similares se houver
    # lista de similares cuja ação é primária
    if doc['acordaoType'] in fgv_dict:
        prim_types = [sim['acordaoId'].split()[0] for sim in doc['similares'] if len(sim['acordaoId'].split()) == 2]
        for dec_type in prim_types:
            if dec_type in fgv_dict:
                cortes_sum_fgv[fgv_dict[dec_type]] += 1
                cortes_sum_not_fgv[not_fgv_dict[dec_type]] += 1
                cortes_fgv_acordaos[fgv_dict[dec_type]][fgv_dict[doc['acordaoType']]] += 1
                cortes_not_fgv_acordaos[not_fgv_dict[dec_type]][not_fgv_dict[doc['acordaoType']]] += 1

cortes = cortes_fgv_acordaos.keys()
matriz_file.write("                     {} | {} | {}\n".format(cortes[0], cortes[1], cortes[2]))
for corte_1 in cortes:
    matriz_file.write(corte_1)
    for corte_2 in cortes:
        matriz_file.write("| {0:g} ({1:.2f}%)".format(cortes_fgv_acordaos[corte_1][corte_2], 100*(cortes_fgv_acordaos[corte_1][corte_2]/float(cortes_sum_fgv[corte_1]))))
    matriz_file.write("\n")

cortes = cortes_not_fgv_acordaos.keys()
matriz_file.write("                     {} | {} | {}".format(cortes[0], cortes[1], cortes[2]))
for corte_1 in cortes:
    matriz_file.write(corte_1)
    for corte_2 in cortes:
        matriz_file.write("| {0:g} ({1:.2f}%)".format(cortes_not_fgv_acordaos[corte_1][corte_2], 100*(cortes_not_fgv_acordaos[corte_1][corte_2]/float(cortes_sum_not_fgv[corte_1]))))
    matriz_file.write("\n")


coll_dc = db['decisoes_monocraticas']
cursor = coll_dc.find({})
decisoes_monocraticas_total = cursor.count()

cortes_fgv_dec_monoc = defaultdict(lambda: defaultdict(int))
cortes_not_fgv_dec_monoc = defaultdict(lambda: defaultdict(int))

cortes_sum_fgv = defaultdict(int)
cortes_sum_not_fgv = defaultdict(int)
for doc in cursor:
    # pegar similares se houver
    # lista de similares cuja ação é primária
    if doc['acordaoType'] in fgv_dict:
        prim_types = [sim['acordaoId'].split()[0] for sim in doc['similares'] if len(sim['acordaoId'].split()) == 2]
        for dec_type in prim_types:
            if dec_type in fgv_dict:
                cortes_sum_fgv[fgv_dict[dec_type]] += 1
                cortes_sum_not_fgv[not_fgv_dict[dec_type]] += 1
                cortes_fgv_dec_monoc[fgv_dict[dec_type]][fgv_dict[doc['acordaoType']]] += 1
                cortes_not_fgv_dec_monoc[not_fgv_dict[dec_type]][not_fgv_dict[doc['acordaoType']]] += 1

cortes = cortes_fgv_dec_monoc.keys()
matriz_file.write("                     {} | {} | {}".format(cortes[0], cortes[1], cortes[2]))
for corte_1 in cortes:
    matriz_file.write(corte_1)
    for corte_2 in cortes:
        matriz_file.write("| {0:g} ({1:.2f}%)".format(cortes_fgv_dec_monoc[corte_1][corte_2], 100*(cortes_fgv_dec_monoc[corte_1][corte_2]/float(cortes_sum_fgv[corte_1]))))
    matriz_file.write("\n")

cortes = cortes_not_fgv_dec_monoc.keys()
matriz_file.write("                     {} | {} | {}".format(cortes[0], cortes[1], cortes[2]))
for corte_1 in cortes:
    matriz_file.write(corte_1)
    for corte_2 in cortes:
        matriz_file.write("| {0:g} ({1:.2f}%)".format(cortes_not_fgv_dec_monoc[corte_1][corte_2], 100*(cortes_not_fgv_dec_monoc[corte_1][corte_2]/float(cortes_sum_not_fgv[corte_1]))))
    matriz_file.write("\n")
