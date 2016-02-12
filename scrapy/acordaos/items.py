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
    legislacaoTexto  = Field()
    citacoes    = Field()
    observacao  = Field()
    similaresTexto = Field()
    similares   = Field()

class AcordaoItem(DecisaoItem):
    orgaoJulg   = Field()
    fontePublic = Field()
    ementa      = Field()
    doutrinas   = Field()
    resumo      = Field()
    tags        = Field()
    notas       = Field()
    file_urls = scrapy.Field()
    files = scrapy.Field()


class LawItem(Item):
    sigla  = Field()
    descricao = Field()
    tipo   = Field()
    ano    = Field()
    refs   = Field()
