#!/usr/bin/env python
# -*- coding: utf-8 -*-

from scrapy.item import Item, Field
import scrapy

class AcordaoItem(Item):
    acordaoId   = Field()
    acordaoType = Field()
    localSigla  = Field()
    local       = Field()
    cabecalho   = Field()
    publicacao  = Field()
    dataPublic  = Field()
    relator     = Field()
    orgaoJulg   = Field()
    dataJulg    = Field()
    fontePublic = Field()
    ementa      = Field()
    decisao     = Field()
    citacoes    = Field()
    legislacao  = Field()
    legislacaoTexto  = Field()
    observacao  = Field()
    doutrinas   = Field()
    resumo      = Field()
    tags        = Field()
    partes      = Field()
    partesTexto = Field()
    tribunal    = Field()
    index       = Field()
    notas       = Field()
    similaresTexto = Field()
    similares   = Field()
    file_urls = scrapy.Field()
    files = scrapy.Field()

class LawItem(Item):
    sigla  = Field()
    descricao = Field()
    tipo   = Field()
    ano    = Field()
    refs   = Field()
