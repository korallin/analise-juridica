#!/usr/bin/env python
# -*- coding: utf-8 -*-

from scrapy.selector import Selector
from scrapy.spiders import Spider
from acordaos.items import AcordaoItem
from acordaos.items import LawItem
import re
import time
from datetime import datetime, timedelta
from scrapy.http import Request
from STFDecisaoParser import STFDecisaoParser
import logging


class STFAcordaoSpider(Spider):

    name = 'stf_acordao'
    custom_settings = {'MONGO_COLLECTION': "acordaos",
        'ITEM_PIPELINES': {
                'acordaos.pipelines.InteiroTeorPipeline': 1,
                'acordaos.pipelines.MongoDBPipeline': 2
            }
    }

    def __init__ (self, iDate, fDate, page, index):
        self.domain = 'stf.jus.br'
        self.index  = self.fIndex = int(index)
        self.iDate  = iDate
        self.fDate  = fDate
        self.page   = int(page)
        self.start_urls = [self.urlPage(page)]
        self.parser = STFDecisaoParser()

    def parse(self, response):
        npagesFound = 0
        sel = Selector(response)
        body = sel.xpath(
            '/html/body/div[@id="pagina"]'+
            '/div[@id="conteiner"]'+
            '/div[@id="corpo"]'+
            '/div[@class="conteudo"]'+
            '/div[@id="divNaoImprimir"][2]'+
            '/table[1]/tr/td[2]/text()').extract()
        r = re.search(r"([0-9]+)", str(body))
        if r:
            npagesFound = int(r.group(1))/10 + 1

        for p in range(self.page, npagesFound+1):
            yield Request(self.urlPage(p), callback = self.parsePage)


    def parsePage(self, response):
        unicode(response.body.decode(response.encoding)).encode('utf-8')
        sel = Selector(response)
        body = sel.xpath(
            '/html/body/div[@id="pagina"]'+
            '/div[@id="conteiner"]'+
            '/div[@id="corpo"]'+
            '/div[@class="conteudo"]'+
            '/div[@id="divImpressao"]'+
            '/div[@class="abasAcompanhamento"]'
        )

        if len(body) < 10:
            logging.warning(u"Acórdão possui menos de 10 documentos na página {}".format(unicode(response.url, 'utf-8')))

        for doc in body:
            yield self.parseDoc(doc, response)

    def parseDoc(self, doc, response):
        parser = self.parser
        law_fields_dict = {}
        self.fIndex += 1
        
        textDoc = doc.xpath('div[@class="processosJurisprudenciaAcordaos"]')
        law_fields_dict['docHeader'] = textDoc.xpath('p[1]/strong/text()').extract()

        law_fields_dict['acordaoId']    = parser.parseId(law_fields_dict['docHeader'][0])
        law_fields_dict['acordaoType']  = parser.parseType(law_fields_dict['acordaoId'])
        law_fields_dict['ufShort']      = parser.parseUfShort(law_fields_dict['docHeader'][0])
        law_fields_dict['uf']           = parser.parseUf(law_fields_dict['docHeader'][0])
        law_fields_dict['relator']      = parser.parseRelator(law_fields_dict['docHeader'][7])
        law_fields_dict['dataJulg']     = parser.parseDataJulgamento(''.join(law_fields_dict['docHeader'][1:]))
        law_fields_dict['orgaoJulg']    = parser.parseOrgaoJulgador(''.join(law_fields_dict['docHeader'][1:]))

        law_fields_dict['publicacao']   = textDoc.xpath('pre[1]/text()').extract()[0].strip()
        law_fields_dict['ementa']       = textDoc.xpath('strong[1]/p/text()').extract()[1].strip()

        headers = textDoc.xpath('p/strong/text()').extract()[len(law_fields_dict['docHeader'])+1:-1]

        if u'Publicação' in headers:
            while headers.pop(0) != u'Publicação':
                continue
        
        bodies  = textDoc.xpath('pre/text()').extract()[1:]
        sections = zip(headers, bodies)

        # método para descobrir se há alguma seção desconhecida/imprevista presente no documento
        self.new_section(sections, law_fields_dict['acordaoId'])

        law_fields_dict['partesRaw']  = self.getSectionBodyByHeader(u"Parte", sections).encode("utf8")
        law_fields_dict['decision']   = self.getSectionBodyByHeader(u"Decisão", sections)
        law_fields_dict['tagsRaw']    = self.getSectionBodyByHeader(u"Indexação", sections)
        law_fields_dict['lawsRaw']    = self.getSectionBodyByHeader(u"Legislação", sections)
        law_fields_dict['obs']        = self.getSectionBodyByHeader(u"Observação", sections)
        law_fields_dict['similarRaw'] = self.getSectionBodyByHeader(u"Acórdãos no mesmo", sections)
        law_fields_dict['doutrines']  = self.getSectionBodyByHeader(u"Doutrina", sections)

        law_fields_dict['partes'] = parser.parsePartes(law_fields_dict['partesRaw'])
        law_fields_dict['tags']   = parser.parseTags(law_fields_dict['tagsRaw'])
        law_fields_dict['quotes'] = parser.parseAcordaosQuotes(law_fields_dict['obs'])
        law_fields_dict['laws']   = parser.parseLaws(law_fields_dict['lawsRaw'])
        law_fields_dict['similarAcordaos'] = parser.parseSimilarAcordaos(law_fields_dict['similarRaw'])
        law_fields_dict['dataPublic']  = parser.parseDataPublicacao(law_fields_dict['publicacao'])

        law_fields_dict['inteiro_teor'] = \
            [response.urljoin(re.sub(r"([^\s%]+)([\s%.\\]|[^\W_])*", r"\1", inteiro_teor.strip())) 
                for inteiro_teor in doc.xpath('ul[@class="abas"]/li[2]/a/@href').extract()
            ]

        item = self.buildItem(law_fields_dict)
        return item


    def buildItem(self, law_fields_dict):
        parser = self.parser
        item = AcordaoItem(
            cabecalho   = parser.removeExtraSpaces(' '.join(law_fields_dict['docHeader'])),
            acordaoId   = law_fields_dict['acordaoId'],
            acordaoType = law_fields_dict['acordaoType'],
            relator     = law_fields_dict['relator'],
            localSigla  = law_fields_dict['ufShort'],
            local       = law_fields_dict['uf'],

            partes = law_fields_dict['partes'],
            partesTexto = re.sub('[\r\t ]+', ' ', law_fields_dict['partesRaw']).strip(),

            publicacao = law_fields_dict['publicacao'],
            orgaoJulg   = law_fields_dict['orgaoJulg'],
            dataJulg    = law_fields_dict['dataJulg'],
            dataPublic = law_fields_dict['dataPublic'],

            legislacao  = law_fields_dict['laws'],
            legislacaoTexto = parser.removeExtraSpaces(law_fields_dict['lawsRaw']),

            ementa      = parser.removeExtraSpaces(law_fields_dict['ementa']),
            decisao     = parser.removeExtraSpaces(law_fields_dict['decision']),

            observacao  = parser.removeExtraSpaces(law_fields_dict['obs']),
            citacoes    = law_fields_dict['quotes'],
            doutrinas   = law_fields_dict['doutrines'],
            tags        = law_fields_dict['tags'],
            tagsTexto   = law_fields_dict['tagsRaw'],

            similaresTexto = re.sub('[\r\t ]+', ' ', law_fields_dict['similarRaw']).strip(),
	        similares   = law_fields_dict['similarAcordaos'],

            tribunal    = "STF",
            index       = self.fIndex,
            file_urls = law_fields_dict['inteiro_teor']
        )
        return item


    def urlPage(self, n):
        return (
               'http://www.stf.jus.br/portal/jurisprudencia/listarJurisprudencia.asp?'+
               's1=%28%40JULG+%3E%3D+'+
                self.iDate +                 
               '%29%28%40JULG+%3C%3D+'+
                self.fDate +                 
               '%29'+
               '&pagina='+ str(n) +
               '&base=baseAcordaos')


    def getSectionBodyByHeader(self, header, sections):
        for s in sections:
            if s[0].startswith(header):
                return s[1]
        return ''

    # método para descobrir se há alguma seção desconhecida/imprevista presente no documento
    def new_section(self, sections, decisionId):
        for s in sections:
            new_section = True
            for header in (u'Parte', u'Decisão', u'Legislação', u'Observação',
                            u'Indexação', u'Acórdãos no mesmo', u'Doutrina'):
                if s[0].startswith(header):
                    new_section = False

            if new_section:
                logging.warning("We have a new section called {} at decision {}".format(s, decisionId))

#     def printItem(self, item):
#         print '-------------------------------------------------------------'
#         print 'relator:\n'+item['relator']
#         print '\nId:\n'+item['acordaoId']
#         print '\nlocal:\n'+item['local']
#         print '\ndataJulg:\n'+item['dataJulg']
# #        print '\norgaoJulg:\n'+item['orgaoJulg']
# #        print '\npublic:\n'+item.publicacao
#         print '\npartes:\n'+item['partes']
#         print '\nementa:\n'+item['ementa']
#         print '\ndecisao:\n'+item['decisao']
#         print '\nindexacao:\n'
#         print item['tags']
#         print '\nleis:\n'+item['legislacao']
#         print '\ndoutrinas:\n'+item['doutrinas']
#         print '\nobs:\n'+item['observacao']
# #        print '\nresult:\n'+result
#         print '\n\nquotes:\n'
#         print item['citacoes']
#         print '-------------------------------------------------------------'
