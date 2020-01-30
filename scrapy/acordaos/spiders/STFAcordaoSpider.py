#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import time
from datetime import datetime, timedelta
import logging
from scrapy.selector import Selector
from scrapy.spiders import Spider
from scrapy.http import Request
from acordaos.spiders.STFDecisaoParser import STFDecisaoParser
from acordaos.items import AcordaoItem
from acordaos.items import LawItem


class STFAcordaoSpider(Spider):

    name = "stf_acordao"
    custom_settings = {
        "MONGO_COLLECTION": "acordaos",
        "ITEM_PIPELINES": {
            # "acordaos.pipelines.InteiroTeorPipeline": 1,
            "acordaos.pipelines.MongoDBPipeline": 2
        },
    }

    def __init__(self, iDate, fDate, page, index):
        self.domain = "stf.jus.br"
        self.index = self.fIndex = int(index)
        self.iDate = iDate
        self.fDate = fDate
        self.page = int(page)
        self.start_urls = [self.urlPage(page)]
        self.parser = STFDecisaoParser()

    def parse(self, response):
        npagesFound = 0
        sel = Selector(response)
        body = sel.xpath(
            '/html/body/div[@id="pagina"]'
            + '/div[@id="conteiner"]'
            + '/div[@id="corpo"]'
            + '/div[@class="conteudo"]'
            + '/div[@id="divNaoImprimir"][2]'
            + "/table[1]/tr/td[2]/text()"
        ).extract()
        r = re.search(r"([0-9]+)", str(body))
        if r:
            npagesFound = int(int(r.group(1)) / 10 + 1)

        for p in range(self.page, npagesFound + 1):
            yield Request(self.urlPage(p), callback=self.parsePage)

    def getAcompProcBody(self, response):
        try:
            sel = Selector(response)
            item = response.meta["item"]
            acom_proc_path = './/div[@class="abasAcompanhamento"]/table[@class="resultadoAndamentoProcesso"]/tr/td[1]/span/text()'
            item["acompProcData"] = sel.xpath(acom_proc_path).extract()
            acom_proc_path = './/div[@class="abasAcompanhamento"]/table[@class="resultadoAndamentoProcesso"]/tr/td[2]/span/text()'
            item["acompProcAndamento"] = sel.xpath(acom_proc_path).extract()
            acom_proc_path = './/div[@class="abasAcompanhamento"]/table[@class="resultadoAndamentoProcesso"]/tr/td[3]/span'
            orgJulg = sel.xpath(acom_proc_path).extract()
            item["acompProcOrgJulg"] = [
                oj.replace("<span>", "").replace("</span>", "") for oj in orgJulg
            ]
        except Exception as e:
            print(
                "Houve um problema na extração de acompanhamento processual {}".format(
                    e
                )
            )
            item = response.meta["item"]

        return item

    def parsePage(self, response):
        sel = Selector(response)
        body = sel.xpath(
            '/html/body/div[@id="pagina"]'
            + '/div[@id="conteiner"]'
            + '/div[@id="corpo"]'
            + '/div[@class="conteudo"]'
            + '/div[@id="divImpressao"]'
            + '/div[@class="abasAcompanhamento"]'
        )

        if len(body) < 10:
            logging.warning(
                "Acórdão possui menos de 10 documentos na página {}".format(
                    response.url
                )
            )

        for doc in body:
            item = self.parseDoc(doc, response)
            acomp_proc_url = (
                "http://www.stf.jus.br/portal/"
                + doc.xpath('ul[@class="abas"]/li/a/@href').extract()[0][3:]
            )

            yield Request(
                acomp_proc_url, callback=self.getAcompProcBody, meta={"item": item}
            )

    def parseDoc(self, doc, response):
        parser = self.parser
        law_fields_dict = {}
        self.fIndex += 1

        textDoc = doc.xpath('div[@class="processosJurisprudenciaAcordaos"]')
        law_fields_dict["docHeader"] = parser.joinId(
            parser.make_string(textDoc.xpath("p[1]/strong//text()").extract())
        )

        law_fields_dict["acordaoId"] = parser.parseId(law_fields_dict["docHeader"][0])
        law_fields_dict["acordaoType"] = parser.parseType(law_fields_dict["acordaoId"])

        dh_relator_index = 7 if textDoc.xpath("p[1]/strong/a").extract() == [] else 8
        law_fields_dict["ufShort"] = parser.parseUfShort(
            "".join(law_fields_dict["docHeader"][:2])
        )
        law_fields_dict["uf"] = parser.parseUf(
            "".join(law_fields_dict["docHeader"][:2])
        )
        law_fields_dict["relator"] = parser.parseRelator(
            law_fields_dict["docHeader"][dh_relator_index]
        )
        law_fields_dict["relator_para_acordao"] = parser.parseRelatorParaAcordao(
            law_fields_dict["docHeader"][dh_relator_index + 1]
        )
        law_fields_dict["revisor"] = parser.parseRevisor(
            law_fields_dict["docHeader"][-3]
        )
        law_fields_dict["dataJulg"] = parser.parseDataJulgamento(
            "".join(law_fields_dict["docHeader"][1:])
        )
        law_fields_dict["orgaoJulg"] = parser.parseOrgaoJulgador(
            "".join(law_fields_dict["docHeader"][1:])
        )

        law_fields_dict["publicacao"] = parser.make_string(
            " ".join(textDoc.xpath("pre[1]//text()").extract()).strip()
        )

        law_fields_dict["ementa"] = " ".join(
            parser.make_string(textDoc.xpath("strong[1]/div//text()").extract())
        ).strip()

        headers = parser.make_string(
            textDoc.xpath("p/strong//text()").extract()[
                len(law_fields_dict["docHeader"]) + 1 : -1
            ]
        )

        if "Publicação" in headers:
            while headers.pop(0) != "Publicação":
                continue

        bodies = parser.make_string(textDoc.xpath("pre/text()").extract()[1:])
        if re.search("\sDIVULG\-?\s?|\sREPUBLICAÇÃO\s*|\sPUBLIC\-?\s+", bodies[0]):
            bodies.pop(0)

        body_sec_text = parser.parse_section(
            parser.make_string(textDoc.xpath("div/text()").extract())
        ).strip()
        # insert in decision in the bodies list in the same index it is in the headers list
        if "Decisão" in headers:
            dec_index = headers.index("Decisão")
            bodies.insert(dec_index, body_sec_text)
        elif body_sec_text != "":
            bodies.append(dec_body)

        body_sec_text = parser.parse_section(
            parser.make_string(textDoc.xpath("div/div/text()").extract())
        )

        bodies.append(body_sec_text) if body_sec_text != "" else None
        headers_supplement = parser.make_string(
            textDoc.xpath("div/p//text()").extract()
        )
        for i in range(1, len(headers_supplement)):
            body_sec_text = parser.parse_section(
                parser.make_string(
                    textDoc.xpath("div/pre[{}]//text()".format(i)).extract()
                )
            )
            bodies.append(body_sec_text)

        headers.extend(headers_supplement)
        sections = zip(headers, bodies)

        # método para descobrir se há alguma seção desconhecida/imprevista presente no documento
        self.new_section(sections, law_fields_dict["acordaoId"])

        # usar regra que considera adição de dados até atingir item da lista que contém "-"
        law_fields_dict["partesRaw"] = self.getSectionBodyByHeader(
            "Parte", headers, bodies
        )
        law_fields_dict["decision"] = self.getSectionBodyByHeader(
            "Decisão", headers, bodies
        )
        law_fields_dict["tagsRaw"] = self.getSectionBodyByHeader(
            "Indexação", headers, bodies
        )
        law_fields_dict["lawsRaw"] = self.getSectionBodyByHeader(
            "Legislação", headers, bodies
        )
        law_fields_dict["obs"] = self.getSectionBodyByHeader(
            "Observação", headers, bodies
        )
        law_fields_dict["similarRaw"] = self.getSectionBodyByHeader(
            "Acórdãos no mesmo", headers, bodies
        )
        law_fields_dict["doutrines"] = self.getSectionBodyByHeader(
            "Doutrina", headers, bodies
        )
        law_fields_dict["tema"] = self.getSectionBodyByHeader("Tema", headers, bodies)
        law_fields_dict["tese"] = self.getSectionBodyByHeader("Tese", headers, bodies)

        law_fields_dict["partes"] = parser.parsePartes(law_fields_dict["partesRaw"])
        law_fields_dict["citacoes_revistas"] = parser.parse_citacoes_revistas(
            law_fields_dict["publicacao"]
        )
        law_fields_dict["tags"] = parser.parseTags(law_fields_dict["tagsRaw"])
        law_fields_dict["quotes"] = parser.parseAcordaosQuotes(
            law_fields_dict["obs"], dec_type="acordaos"
        )
        law_fields_dict["quotes_dec_monoc"] = parser.parseAcordaosQuotes(
            law_fields_dict["obs"], dec_type="decisoes_monocraticas"
        )
        law_fields_dict["decision_quotes"] = parser.parseAcordaosDecisionQuotes(
            law_fields_dict["ementa"]
        )
        law_fields_dict["laws"] = parser.parseLaws(law_fields_dict["lawsRaw"])
        law_fields_dict["similarAcordaos"] = parser.parseSimilarAcordaos(
            law_fields_dict["similarRaw"]
        )
        law_fields_dict["dataPublic"] = parser.parseDataPublicacao(
            law_fields_dict["publicacao"]
        )

        law_fields_dict["inteiro_teor"] = [
            response.urljoin(
                re.sub(r"([^\s%]+)([\s%.\\]|[^\W_])*", r"\1", inteiro_teor.strip())
            )
            for inteiro_teor in doc.xpath('ul[@class="abas"]/li[2]/a/@href').extract()
        ]

        item = self.buildItem(law_fields_dict)
        return item

    def buildItem(self, law_fields_dict):
        parser = self.parser
        item = AcordaoItem(
            cabecalho=parser.removeExtraSpaces(" ".join(law_fields_dict["docHeader"])),
            acordaoType=law_fields_dict["acordaoType"],
            acordaoId=law_fields_dict["acordaoId"],
            local=law_fields_dict["uf"],
            localSigla=law_fields_dict["ufShort"],
            relator=law_fields_dict["relator"],
            relator_para_acordao=law_fields_dict["relator_para_acordao"],
            revisor=law_fields_dict["revisor"],
            dataJulg=law_fields_dict["dataJulg"],
            orgaoJulg=law_fields_dict["orgaoJulg"],
            publicacao=law_fields_dict["publicacao"],
            citacoes_revistas=law_fields_dict["citacoes_revistas"],
            dataPublic=law_fields_dict["dataPublic"],
            partesTexto=re.sub("[\r\t ]+", " ", law_fields_dict["partesRaw"]).strip(),
            partes=law_fields_dict["partes"],
            ementa=parser.removeExtraSpaces(law_fields_dict["ementa"]),
            citacoesDec=law_fields_dict["decision_quotes"],
            decisao=parser.removeExtraSpaces(law_fields_dict["decision"]),
            tema=law_fields_dict["tema"],
            tese=law_fields_dict["tese"],
            tagsTexto=law_fields_dict["tagsRaw"],
            tags=law_fields_dict["tags"],
            legislacaoTexto=parser.removeExtraSpaces(law_fields_dict["lawsRaw"]),
            legislacao=law_fields_dict["laws"],
            observacao=parser.removeExtraSpaces(law_fields_dict["obs"]),
            citacoesObs=law_fields_dict["quotes"],
            citacoesObsDecMonoc=law_fields_dict["quotes_dec_monoc"],
            doutrinas=law_fields_dict["doutrines"],
            similaresTexto=re.sub(
                "[\r\t ]+", " ", law_fields_dict["similarRaw"]
            ).strip(),
            similares=law_fields_dict["similarAcordaos"],
            tribunal="STF",
            index=self.fIndex,
            file_urls=law_fields_dict["inteiro_teor"],
        )
        return item

    def urlPage(self, n):
        return (
            "http://www.stf.jus.br/portal/jurisprudencia/listarJurisprudencia.asp?"
            + "s1=%28%40JULG+%3E%3D+"
            + self.iDate
            + "%29%28%40JULG+%3C%3D+"
            + self.fDate
            + "%29"
            + "&pagina="
            + str(n)
            + "&base=baseAcordaos"
        )

    def getSectionBodyByHeader(self, header_to_match, headers, bodies):
        for header, body in zip(headers, bodies):
            if header.startswith(header_to_match):
                return body
        return ""

    # método para descobrir se há alguma seção desconhecida/imprevista presente no documento
    def new_section(self, sections, decisionId):
        for s in sections:
            new_section = True
            for header in (
                "Parte",
                "Decisão",
                "Legislação",
                "Observação",
                "Indexação",
                "Acórdãos no mesmo",
                "Doutrina",
            ):
                if s[0].startswith(header):
                    new_section = False

            if new_section:
                logging.warning(
                    "We have a new section called {} at decision {}".format(
                        s, decisionId
                    )
                )


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
