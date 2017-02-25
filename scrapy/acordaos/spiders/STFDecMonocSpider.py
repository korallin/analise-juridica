#!/usr/bin/env python
# -*- coding: utf-8 -*-

from scrapy.selector import Selector
from scrapy.spiders import Spider
from acordaos.items import DecisaoItem
import re
import time
from datetime import datetime, timedelta
from scrapy.http import Request
from STFDecisaoParser import STFDecisaoParser
import logging

class STFDecMonocSpider(Spider):

    name = 'stf_decisao_monocratica'
    custom_settings = {'MONGO_COLLECTION': "decisoes_monocraticas",
        'ITEM_PIPELINES': {
                'acordaos.pipelines.MongoDBPipeline': 1
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


    def getAcompProcBody(self, response):
        sel = Selector(response)
        item = response.meta['item']
        acom_proc_path = './/div[@class="abasAcompanhamento"]/table[@class="resultadoAndamentoProcesso"]/tr/td[2]/span/text()'
        item['acompanhamentoProcessual'] = sel.xpath(acom_proc_path).extract()

        return item


    def parsePage(self, response):
        unicode(response.body.decode(response.encoding)).encode('utf-8')
        sel = Selector(response)
        body = sel.xpath(
            '/html/body/div[@id="pagina"]'+
            '/div[@id="conteiner"]'+
            '/div[@id="corpo"]'+
            '/div[@class="conteudo"]'+
            '/div[@id="divImpressao"]'
        )

        corrected_body = body.xpath('.//div[@class="abasAcompanhamento"]')
        if len(corrected_body) > 10:
            logging.warning(u"Decisões monocráticas possui mais de 10 documentos na página {}".format(unicode(response.url, 'utf-8')))
            corrected_body = body.xpath('div[@class="abasAcompanhamento"]')
        
        if len(corrected_body) < 10:
            logging.warning(u"Acórdão possui menos de 10 documentos na página {}".format(unicode(response.url, 'utf-8')))

        for doc in corrected_body:
            item = self.parseDoc(doc, response)
            acomp_proc_url = 'http://www.stf.jus.br/portal/' + doc.xpath('ul[@class="abas"]/li/a/@href').extract()[0][3:]

            yield Request(acomp_proc_url, callback = self.getAcompProcBody, meta={'item': item})


    def parseDoc(self, doc, response):
        parser = self.parser
        law_fields_dict = {}
        self.fIndex += 1

        textDoc = doc.xpath('div[@class="processosJurisprudenciaAcordaos"]')
        
        law_fields_dict['docHeader'] = textDoc.xpath('p[1]/strong//text()').extract()

        law_fields_dict['acordaoId']    = parser.parseId(law_fields_dict['docHeader'][0])
        law_fields_dict['acordaoType']  = parser.parseType(law_fields_dict['acordaoId'])
        law_fields_dict['ufShort']      = parser.parseUfShort(''.join(law_fields_dict['docHeader'][:2]))
        law_fields_dict['uf']           = parser.parseUf(''.join(law_fields_dict['docHeader'][:2]))

        dh_relator_index = 2 if textDoc.xpath('p[1]/strong/a').extract() == [] else 3
        law_fields_dict['relator']      = parser.parseRelator(law_fields_dict['docHeader'][2])
        law_fields_dict['dataJulg']     = parser.parseDataJulgamento(''.join(law_fields_dict['docHeader'][1:]))

        law_fields_dict['publicacao']   = textDoc.xpath('pre[1]/text()').extract()[0].strip()

        headers = textDoc.xpath('p/strong/text()').extract()[len(law_fields_dict['docHeader'])+1:-1]

        if u'Publicação' in headers:
            while headers.pop(0) != u'Publicação':
                continue

        if u"Decisões no mesmo" in headers[-1]:
            bodies = textDoc.xpath('pre/text()').extract()[1:len(headers)]
            similares = textDoc.xpath('pre')[-1]
            bodies.append(similares.xpath('.//text()').extract())

            # if this line doesn't end with '\n it's necessary add to the end of each duple
            if bodies[1][-1] == "\n":
                for i in xrange(1, len(bodies[-1]) - 1, 2):
                    bodies[-1][i] += "\n"

            bodies[-1] = "".join(bodies[-1])
        else:
            bodies = textDoc.xpath('pre/text()').extract()[1:len(headers)+1]


        sections = zip(headers, bodies)

        # método para descobrir se há alguma seção desconhecida/imprevista presente no documento
        self.new_section(sections, law_fields_dict['acordaoId'])

        law_fields_dict['partesRaw']  = self.getSectionBodyByHeader(u"Parte", sections).encode("utf8")
        law_fields_dict['decision']   = self.getSectionBodyByHeader(u"Decisão", sections)
        law_fields_dict['lawsRaw']    = self.getSectionBodyByHeader(u"Legislação", sections)
        law_fields_dict['obs']        = self.getSectionBodyByHeader(u"Observação", sections)
        law_fields_dict['similarRaw'] = self.getSectionBodyByHeader(u"Decisões no mesmo", sections)

        law_fields_dict['partes'] = parser.parsePartes(law_fields_dict['partesRaw'])
        law_fields_dict['quotes'] = parser.parseAcordaosQuotes(law_fields_dict['obs'])
        law_fields_dict['decision_quotes'] = parser.parseAcordaosDecisionQuotes(law_fields_dict['decision'])
        law_fields_dict['laws']   = parser.parseLaws(law_fields_dict['lawsRaw'])
        law_fields_dict['dataPublic']  = parser.parseDataPublicacao(law_fields_dict['publicacao'])

        law_fields_dict['similarDecisoes'] = parser.parseSimilarDecisoes(law_fields_dict['similarRaw'])

        item = self.buildItem(law_fields_dict)

        return item


    def buildItem(self, law_fields_dict):
        parser = self.parser
        item = DecisaoItem(
            acordaoId   = law_fields_dict['acordaoId'],
            cabecalho   = parser.removeExtraSpaces(' '.join(law_fields_dict['docHeader'])),
            acordaoType = law_fields_dict['acordaoType'],
            relator     = law_fields_dict['relator'],
            localSigla  = law_fields_dict['ufShort'],
            local       = law_fields_dict['uf'],

            partes = law_fields_dict['partes'],
            partesTexto = re.sub('[\r\t ]+', ' ', law_fields_dict['partesRaw']).strip(),

            publicacao = law_fields_dict['publicacao'],
            dataJulg    = law_fields_dict['dataJulg'],
            dataPublic = law_fields_dict['dataPublic'],

            legislacao  = law_fields_dict['laws'],
            legislacaoTexto = parser.removeExtraSpaces(law_fields_dict['lawsRaw']),

            decisao     = parser.removeExtraSpaces(law_fields_dict['decision']),

            observacao  = parser.removeExtraSpaces(law_fields_dict['obs']),
            citacoesObs = law_fields_dict['quotes'],
            citacoesDec = law_fields_dict['decision_quotes'],

            similaresTexto = re.sub('[\r\t ]+', ' ', law_fields_dict['similarRaw']).strip(),
            similares   = law_fields_dict['similarDecisoes'],

            tribunal    = "STF",
            index       = self.fIndex
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
               '+NAO+S.PRES.'
               '&pagina='+ str(n) +
               '&base=baseMonocraticas')


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
                            u'Decisões'):
                if s[0].startswith(header):
                    new_section = False

            if new_section:
                logging.warning("We have a new section called {} at decision {}".format(s, decisionId))
