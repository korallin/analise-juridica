#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pymongo
from pymongo import MongoClient
import datetime
import getpass
import pandas as pd
import os
import sys


def write_count_list(lst, coll, query, field, criteria):
    """
        Esta função recebe uma lista em que cada elemento é uma lista contendo
        nome de campo, critério e contagem de documentos que satisfazem o
        critério definido pela query 'query' e adiciona uma nova lista com nome
        do campo, 'field', o nome do critério, 'criteria', e a quantidade de
        documentos que satisfazem a query.
    """
    count = coll.find(query).count()
    lst.append([field, criteria, count])


def decisoes_dataquality(coll, lst, decision_type):
    """
        A função recebe uma collection e uma lista em que cada elemento é uma
        lista contendo nome de campo, critério e contagem de documentos e preenche
        a lista lst com as quantidades que satisfazem os critérios definidos na
        função para decisões, incluindo acórdãos que são um tipo de decisão.
    """

    write_count_list(lst, coll, {}, decision_type, "Total")

    # Queries para checar qualidade dos dados a fim de melhorar a análise deles
    write_count_list(lst, coll, {"$where": "this.cabecalho.length > 0"},
                    "cabecalho", "Campo não vazio")
    write_count_list(lst, coll, {"$where": "this.acordaoId.length > 0"},
                    "acordaoId", "Campo não vazio")
    write_count_list(lst, coll, {"$where": "this.acordaoType.length > 0"},
                    "acordaoType", "Campo não vazio")
    write_count_list(lst, coll, {"$where": "this.localSigla.length == 2"},
                    "localSigla", "Campo possui dois caracteres")
    write_count_list(lst, coll, {"$where": "this.local.length > 0"},
                    "local", "Campo não vazio")
    write_count_list(lst, coll, {"$where": "this.relator.length > 0"},
                    "relator", "Campo não vazio")
    write_count_list(lst, coll, {"$where": "this.publicacao.length > 0"},
                    "publicacao", "Campo não vazio")
    write_count_list(lst, coll, { "$and": [ { "dataPublic": { "$type": "date" } },
                    { "dataPublic": { "$gte": init_extraction_date } } ] },
                    "dataPublic", "Data válida")
    write_count_list(lst, coll, { "$and": [ { "dataJulg": { "$type": "date" } },
                    { "dataJulg": { "$gte": init_julg_date } } ] },
                    "dataJulg", "Data válida")
    tribunal = 'STF'
    write_count_list(lst, coll, {"$where": "this.tribunal == '{}'".format(tribunal)},
                    "tribunal", "Tribunal escrito corretamente")
    write_count_list(lst, coll, {"$where": "this.partesTexto.length > 20"},
                    "partesTexto", "Campo com tamanho mínimo válido")
    count = len([partes for partes in coll.find({},
                                  {"partes": 1}) if len(partes["partes"]) >= 1])
    lst.append(["partes", "Número mínimo válido de partes na decisão", count])

    write_count_list(lst, coll, {"$where": "this.decisao.length > 100"},
                    "decisao", "Campo com tamanho mínimo válido")
    write_count_list(lst, coll, {"$where": "this.legislacaoTexto.length > 60"},
                    "legislacaoTexto", "Campo contém leis")
    write_count_list(lst, coll, {"$where": "this.legislacao.length > 0"},
                    "legislacao", "Campo contém lista não vazia")
    write_count_list(lst, coll, {"$where": "this.observacao.length > 100"},
                    "observacao", "Campo com tamanho mínimo extraível")
    write_count_list(lst, coll, {"$where": "this.similaresTexto.length > 0"},
                    "similaresTexto", "Campo não vazio")
    write_count_list(lst, coll, {"$where": "this.similares.length > 0"},
                    "similares", "Campo contém lista não vazia")
    write_count_list(lst, coll, {"$where": "this.citacoesObs.length > 0"},
                    "citacoesObs", "Campo contém lista não vazia")
    write_count_list(lst, coll, {"$where": "this.citacoesDec.length > 0"},
                    "citacoesDec", "Campo contém lista não vazia")
    write_count_list(lst, coll, {"$where": "this.acompProcData.length > 0"},
                    "acompProcData", "Campo contém lista não vazia")
    write_count_list(lst, coll, {"$where": "this.acompProcAndamento.length > 0"},
                    "acompProcAndamento", "Campo contém lista não vazia")
    write_count_list(lst, coll, {"$where": "this.acompProcOrgJulg.length > 0"},
                    "acompProcOrgJulg", "Campo contém lista não vazia")

    # Queries mais complexas para verificar qualidade da extração dos dados
    write_count_list(lst, coll, { "$and": [ { "$where": "this.publicacao.length > 0" },
                          { "dataPublic": { "$type": "date" } },
                          { "dataPublic": { "$gte": init_extraction_date } }
                        ] }, "publicacao e dataPublic",
                        "Datas de publicação extraídas corretamente")
    count = len([partes for partes in coll.find(
                                  {"$where": "this.partesTexto.length > 20"},
                                  {"partes": 1}) if len(partes["partes"]) >= 1])
    lst.append(["partes e partesTexto", "Número mínimo de partes extraídas adequadamente",
                count])

    write_count_list(lst, coll, { "$and": [ { "$where": "this.legislacao.length > 0" },
                                { "$where": "this.legislacaoTexto.length > 60" } ] },
                    "legislacao e legislacaoTexto", "Possui legislação extraída")
    write_count_list(lst, coll, { "$and": [ { "$where": "this.similares.length > 0" },
                                  { "$where": "this.similaresTexto.length > 0" } ] },
                    "similares e similaresTexto", "Possui similares extraída")
    write_count_list(lst, coll, { "$and": [
      { "$where": "this.acompProcData.length == this.acompProcAndamento.length" },
      { "$where": "this.acompProcAndamento.length == this.acompProcOrgJulg.length" }
      ] }, "dados de acompanhamento processual", "Processos com extração coerente do dado")
    write_count_list(lst, coll, { "$and": [ { "$where": "this.cabecalho.length > 0" },
                                            { "dataJulg": { "$type": "date" } },
                                            { "dataJulg": { "$gte": init_julg_date } } ] },
                    "cabecalho e dataJulg", "Datas de julgamento extraídas corretamente")
    write_count_list(lst, coll, { "$and": [ { "$where": "this.cabecalho.length > 0" },
                                            { "$where": "this.relator.length > 0" } ] },
                    "cabecalho e relator", "Relator extraído corretamente")
    write_count_list(lst, coll, { "$and": [ { "$where": "this.cabecalho.length > 0" },
                                            { "$where": "this.local.length > 0" } ] },
                    "cabecalho e local", "Local extraído corretamente")
    write_count_list(lst, coll, { "$and": [ { "$where": "this.observacao.length > 100" },
                                            { "$where": "this.citacoesObs.length > 0" } ] },
                      "observacao e citacoesObs", "Extração coerente de citações")
    write_count_list(lst, coll, { "$and": [ { "$where": "this.decisao.length > 500" },
                                            { "$where": "this.citacoesDec.length > 0" } ] },
                    "decisao e citacoesDec", "Extração coerente de citações")


def acordaos_dataquality(coll, lst, decision_type, int_teor_dirpath):
    """
        A função recebe uma collection e uma lista em que cada elemento é uma
        lista contendo nome de campo, critério e contagem de documentos e preenche
        a lista lst com as quantidades que satisfazem os critérios definidos na
        função para acórdãos.
    """
    decisoes_dataquality(coll, lst, decision_type)
    write_count_list(lst, coll, {"$where": "this.orgaoJulg.length > 0"},
                    "orgaoJulg", "Campo não vazio")
    write_count_list(lst, coll, {"$where": "this.ementa.length > 0"},
                    "ementa", "Campo não vazio")
    write_count_list(lst, coll, {"$where": "this.doutrinas.length > 0"},
                    "doutrinas", "Campo não vazio")
    write_count_list(lst, coll, {"$where": "this.tagsTexto.length > 0"},
                    "tagsTexto", "Campo não vazio")
    write_count_list(lst, coll, {"$where": "this.tags.length > 0"},
                    "tags", "Campo contém lista não vazia")

    # checa existência de inteiro teor
    count = len([int_teor for int_teor in coll.find({}, {"files": 1})
                                      if (int_teor.has_key("files") and (int_teor["files"] != ""))
                                  and os.path.isfile(os.path.join(int_teor_dirpath, int_teor["files"]))])
    lst.append(["files (inteiro teor)", "Inteiro teor armazenado", count])
    write_count_list(lst, coll, { "$and": [ { "$where": "this.tags.length > 0" },
                                            { "$where": "this.tagsTexto.length > 0" } ] },
                    "tags e tagsTexto", "Extração correta de tags")
    write_count_list(lst, coll, { "$and": [ { "$where": "this.cabecalho.length > 0" },
                                            { "$where": "this.orgaoJulg.length > 0" } ] },
                    "cabecalho e orgaoJulg", "Extração correta de órgão julgador")


def calc_dataquality_dec_quant(df):
    """
        A função recebe um dataframe e calcula a quantidade de documentos que não
        satisfazem aos critérios usados paa avaliar a qualidade dos dados, mas que
        deveriam/poderiam satisfazer para decisões, incluindo acórdãos.
    """

    df["Quantidade a se corrigir/checar"] = len(df) * list(df[df["Critério"] == "Total"]["Quantidade"].values) - df["Quantidade"]

    df.loc[df["Campo"] == "publicacao e dataPublic", "Quantidade a se corrigir/checar"] =\
            df[df["Campo"] == "publicacao"]["Quantidade"].values[0] -\
            df[df["Campo"] == "dataPublic"]["Quantidade"].values[0]

    df.loc[df["Campo"] == "partes e partesTexto", "Quantidade a se corrigir/checar"] =\
            df[df["Campo"] == "partes"]["Quantidade"].values[0] -\
            df[df["Campo"] == "partesTexto"]["Quantidade"].values[0]

    df.loc[df["Campo"] == "legislacao e legislacaoTexto", "Quantidade a se corrigir/checar"] =\
            df[df["Campo"] == "legislacaoTexto"]["Quantidade"].values[0] -\
            df[df["Campo"] == "legislacao"]["Quantidade"].values[0]

    df.loc[df["Campo"] == "similares e similaresTexto", "Quantidade a se corrigir/checar"] =\
            df[df["Campo"] == "similaresTexto"]["Quantidade"].values[0] -\
            df[df["Campo"] == "similares"]["Quantidade"].values[0]

    df.loc[df["Campo"] == "similares e similaresTexto", "Quantidade a se corrigir/checar"] =\
            df[df["Campo"].isin(["acompProcData", "acompProcAndamento",
                                    "acompProcOrgJulg"])]["Quantidade"].max() -\
            df[df["Campo"].isin(["acompProcData", "acompProcAndamento",
                                    "acompProcOrgJulg"])]["Quantidade"].min()

    df.loc[df["Campo"] == "cabecalho e dataJulg", "Quantidade a se corrigir/checar"] =\
            df[df["Campo"] == "cabecalho"]["Quantidade"].values[0] -\
            df[df["Campo"] == "dataJulg"]["Quantidade"].values[0]

    df.loc[df["Campo"] == "cabecalho e relator", "Quantidade a se corrigir/checar"] =\
            df[df["Campo"] == "cabecalho"]["Quantidade"].values[0] -\
            df[df["Campo"] == "relator"]["Quantidade"].values[0]

    df.loc[df["Campo"] == "cabecalho e local", "Quantidade a se corrigir/checar"] =\
            df[df["Campo"] == "cabecalho"]["Quantidade"].values[0] -\
            df[df["Campo"] == "local"]["Quantidade"].values[0]

    df.loc[df["Campo"] == "observacao e citacoesObs", "Quantidade a se corrigir/checar"] =\
            df[df["Campo"] == "observacao"]["Quantidade"].values[0] -\
            df[df["Campo"] == "citacoesObs"]["Quantidade"].values[0]

    df.loc[df["Campo"] == "decisao e citacoesDec", "Quantidade a se corrigir/checar"] =\
            df[df["Campo"] == "decisao"]["Quantidade"].values[0] -\
            df[df["Campo"] == "citacoesDec"]["Quantidade"].values[0]


def calc_dataquality_acordao_quant(df):
    """
        A função recebe um dataframe e calcula a quantidade de documentos que não
        satisfazem aos critérios usados paa avaliar a qualidade dos dados, mas que
        deveriam/poderiam satisfazer para acórdãos.
    """

    calc_dataquality_dec_quant(df)

    df.loc[df["Campo"] == "tags e tagsTexto", "Quantidade a se corrigir/checar"] =\
            df[df["Campo"] == "tags"]["Quantidade"].values[0] -\
            df[df["Campo"] == "tagsTexto"]["Quantidade"].values[0]

    df.loc[df["Campo"] == "cabecalho e orgaoJulg", "Quantidade a se corrigir/checar"] =\
            df[df["Campo"] == "cabecalho"]["Quantidade"].values[0] -\
            df[df["Campo"] == "orgaoJulg"]["Quantidade"].values[0]


if __name__ == '__main__':
    username = getpass.getpass("Username:\n")
    password = getpass.getpass("Password:\n")

    int_teor_dirpath = sys.argv[1]

    client = MongoClient("mongodb://{}:{}@127.0.0.1:57017".format(username, password))
    client.database_names()
    db = client.DJs

    init_extraction_date = datetime.datetime(2001, 1, 1)
    init_julg_date = datetime.datetime(2000, 1, 1)

    lst_decs_monocs = [["Campo", "Critério", "Quantidade"]]
    decisoes_dataquality(db.decisoes_monocraticas, lst_decs_monocs, "Decisões monocráticas")

    lst_acordaos = [["Campo", "Critério", "Quantidade"]]
    acordaos_dataquality(db.acordaos, lst_acordaos, "Acórdãos", int_teor_dirpath)

    df_decs_monocs = pd.DataFrame(lst_decs_monocs[1:], columns=lst_decs_monocs[0])
    df_acordaos = pd.DataFrame(lst_acordaos[1:], columns=lst_acordaos[0])

    calc_dataquality_dec_quant(df_decs_monocs)
    calc_dataquality_acordao_quant(df_acordaos)

    writer = pd.ExcelWriter("decisions_dataquality.xlsx")
    df_decs_monocs.to_excel(writer, u"decisões", index=False, startrow=3, startcol=3)
    df_acordaos.to_excel(writer, u"decisões", index=False, startrow=3, startcol=10)
    writer.save()


# from pprint import pprint
# coll = db.decisoes_monocraticas
#
# cursor = coll.find(query, {"cabecalho": 1})
# for document in cursor:
#     pprint(document)

# https://www.blog.pythonlibrary.org/2016/05/18/python-3-an-intro-to-encryption/
