#!/usr/bin/env python
# -*- coding: utf-8 -*-

from scrapy.item import Item, Field
import scrapy

class DecisaoItem(Item):
    acordaoId   = Field()
    acordaoType = Field()
    localSigla  = Field()
    local       = Field()
    cabecalho   = Field()
    publicacao  = Field()
    relator     = Field()
    dataPublic  = Field()
    dataJulg    = Field()
    decisao     = Field()
    partes      = Field()
    partesTexto = Field()
    tribunal    = Field()
    index       = Field()
    legislacao  = Field()
    acompProcData = Field()
    acompProcAndamento = Field()
    acompProcOrgJulg = Field()
    legislacaoTexto  = Field()
    citacoesObs    = Field()
    citacoesDec    = Field()
    observacao  = Field()
    similaresTexto = Field()
    similares   = Field()

class AcordaoItem(DecisaoItem):
    orgaoJulg   = Field()
    # fontePublic = Field() -> não é usada de fato
    ementa      = Field()
    doutrinas   = Field()
    # resumo      = Field() -> não é usado de fato
    tagsTexto = Field()
    tags        = Field()
    # notas       = Field() -> não é usado de fato
    file_urls = scrapy.Field()
    # files = scrapy.Field() -> não é usado de fato


class LawItem(Item):
    sigla  = Field()
    descricao = Field()
    tipo   = Field()
    ano    = Field()
    refs   = Field()
