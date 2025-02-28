# -*- coding: utf-8 -*-
from scrapy.selector import Selector
from scrapy.spiders import Spider
from scrapy.http import FormRequest, Request
from scrapy.utils.response import open_in_browser
from acordaos.items import AcordaoItem
from acordaos.spiders.STJParser import STJParser
import urllib.parse
import re
from scrapy.shell import inspect_response
from datetime import datetime, timedelta
import time


class STJSpider(Spider):

    name = "stj"

    def nextDay(self, date):
        nextDay = datetime(int(date[0:4]), int(date[4:6]), int(date[6:8]))
        nextDay += timedelta(days=1)
        d = str(nextDay.day).zfill(2)
        m = str(nextDay.month).zfill(2)
        y = str(nextDay.year)
        return y + m + d

    def getParametersFromFile(self):
        print("getting initial date and num previous acordaos from file")
        file = open("../update_settings", "r")
        prevIndex = file.readline()
        prevFinalDate = file.readline()
        if prevIndex and prevFinalDate:
            self.iIndex = int(prevIndex) + 1
            self.iDate = self.nextDay(str(prevFinalDate))
        else:
            print("cannot read settings file")

    def saveSearchInfo(self):
        print("saving search parameters on file update_settings")
        file = open("../update_settings", "w")
        file.write(str(self.fIndex - 1) + "\n")
        file.write(self.fDate + "\n")
        file.write(str(self.iIndex))
        file.close()

    def __init__(self, iDate, fDate, update):
        self.domain = "stj.jus.br"
        self.start_urls = ["http://www.stj.jus.br/SCON/"]
        self.iDate = str(iDate).zfill(5)
        self.fDate = str(fDate).zfill(5)
        self.iIndex = 1
        if int(update) == 1:
            self.getParametersFromFile()
        self.fIndex = self.iIndex
        print("starting to scrape from index " + str(self.iIndex))
        print("Acordaos from " + self.iDate + " to " + self.fDate)
        print("\n\n\n")

    def parse(self, response):
        yield FormRequest.from_response(
            response,
            formname="frmConsulta",
            formdata={
                "data": '(@DTDE >="'
                + self.iDate
                + '") E (@DTDE <="'
                + self.fDate
                + '")',
                "b": "ACOR",
            },
            callback=self.parseSearchResults,
        )

    def parseDoc(self, doc):
        relator = dataJulg = dataPublic = ementa = decisao = ""
        laws = []
        citacoes = []
        similares = []
        parser = STJParser()
        notas = lawsRaw = publicacao = observacao = doutrinas = similaresRaw = ""

        sectionsSel = doc.xpath('.//div[@class="paragrafoBRS"]')
        # Permanent order sections
        header = sectionsSel[0].xpath('./div[@class="docTexto"]/text()').extract()
        acordaoId = parser.parseId(header[0])
        localSigla = parser.parseUfShort(header[0])
        header = " ".join(header).strip()

        relatorRaw = sectionsSel[1].xpath("./pre/text()").extract()[0]
        dataJulgSel = self.getSectionSelectorByHeader(
            sectionsSel, "Data do Julg"
        )  # Data do Julgamento
        dataJulg = parser.parseDataJulgamento(
            dataJulgSel.xpath("./pre/span/text()").extract()[0]
        )
        publicSel = self.getSectionSelectorByHeader(
            sectionsSel, "Data da Publ"
        )  # Data de Publicação/Fonte
        ementa = self.getSectionBodyByHeader("Ementa", sectionsSel)
        decisao = self.getSectionBodyByHeader("Ac", sectionsSel)  # Acórdao
        doutrinas = self.getSectionBodyByHeader("Refer", sectionsSel)  #
        resumo = self.getSectionBodyByHeader(
            "Resumo", sectionsSel
        )  # Resumo estruturado
        notas = self.getSectionBodyByHeader("Nota", sectionsSel)
        lawSel = self.getSectionSelectorByHeader(
            sectionsSel, "Refer"
        )  # Referência Legislativa
        obsSel = self.getSectionSelectorByHeader(sectionsSel, "Veja")

        similaresSel = self.getSectionSelectorByHeader(
            sectionsSel, "Sucess"
        )  # Sucessivos

        if similaresSel:
            similaresRaw = similaresSel.xpath('pre[@class="docTexto"]/text()').extract()
            similares = parser.parseSimilarAcordaos(similaresRaw)
            similaresRaw = ". ".join(similaresRaw)

        relator = parser.parseRelator(relatorRaw)
        tags = parser.parseTags(resumo)

        if publicSel:
            publicacao = "".join(publicSel.xpath("./pre/text()").extract()).strip()
            dataPublic = parser.parseDataPublicacao(publicacao)

        if lawSel:
            lawsRaw = lawSel.xpath("./pre//text()|./pre/a/text()").extract()
            laws = parser.parseLaws(lawsRaw)
            lawsRaw = " ".join(lawsRaw)

        if obsSel:
            observacao = "".join(
                obsSel.xpath("./pre//text()|./pre/a/text()").extract()
            ).strip()
            citacoes = parser.parseAcordaoQuotes(obsSel)

        return AcordaoItem(
            acordaoId=acordaoId,
            acordaoType=parser.parseType(acordaoId),
            localSigla=localSigla,
            local=localSigla,
            cabecalho=header,
            publicacao=publicacao,
            dataPublic=dataPublic,
            relator=relator,
            orgaoJulg="",
            dataJulg=dataJulg,
            fontePublic="",
            ementa=parser.removeExtraSpaces(ementa),
            decisao=parser.removeExtraSpaces(decisao),
            citacoes=citacoes,
            legislacao=laws,
            legislacaoTexto=lawsRaw,
            observacao=observacao,
            doutrinas=doutrinas,
            resumo=resumo,
            tags=tags,
            partes="",
            partesTexto="",
            tribunal="STJ",
            index=self.fIndex,
            notas=notas,
            similaresTexto=similaresRaw,
            similares=similares,
        )

    def getSectionBodyByHeader(self, header, sectionsSel):
        for s in sectionsSel:
            h = s.xpath("./h4/text()").extract()[0]
            body = " ".join(
                s.xpath("./pre/text()|./pre/a/text()|./pre/span/text()").extract()
            )
            if h.startswith(header):
                return body
        return ""

    def getSectionSelectorByHeader(self, selectors, header):
        for s in selectors:
            h = s.xpath("./h4/text()").extract()[0]
            if h.startswith(header):
                return s
        return None

    def parseSearchResults(self, response):
        sel = Selector(response)
        resultsLines = sel.xpath(
            '/html/body/div[@id="divprincipal"]'
            + '/div[@class="minwidth"]'
            + '/div[@id="idInternetBlocoEmpacotador"]'
            + '/div[@class="incenter_interno"]'
            + '/div[@id="idDivContainer"]'
            + '/div[@id="idAreaBlocoExterno"]'
            + '/div[@id="idArea"]'
            + '/div[@id="corpopaginajurisprudencia"]'
            + '/div[@id="resumopesquisa"]'
            + '//div[@id="itemlistaresultados"]'
        )
        for line in resultsLines:
            if ((line.xpath("./span[1]/text()").extract()[0]).strip()) == "Acórdãos":
                resultsLink = line.xpath("./span[2]/a/@href").extract()[0]
        yield Request(
            urllib.parse.urljoin("http://www.stj.jus.br/", resultsLink),
            callback=self.parsePage,
        )

    def parsePage(self, response):
        sel = Selector(response)
        doclist = sel.xpath(
            '/html/body/div[@id="divprincipal"]'
            + '/div[@class="minwidth"]'
            + '/div[@id="idInternetBlocoEmpacotador"]'
            + '/div[@class="incenter_interno"]'
            + '/div[@id="idDivContainer"]'
            + '/div[@id="idAreaBlocoExterno"]'
            + '/div[@id="idArea"]'
            + '/div[@id="corpopaginajurisprudencia"]'
            + '/div[@id="listadocumentos"]'
            + '/div[@style="position: relative;"]'
        )
        for doc in doclist:
            yield self.parseDoc(doc)
            self.fIndex = self.fIndex + 1
        nextPage = sel.xpath('//*[@id="navegacao"][1]/a[@class="iconeProximaPagina"]')
        if nextPage:
            yield Request(
                urllib.parse.urljoin(
                    "http://www.stj.jus.br/", nextPage.xpath("@href").extract()[0]
                ),
                callback=self.parsePage,
            )
        else:
            self.saveSearchInfo()
