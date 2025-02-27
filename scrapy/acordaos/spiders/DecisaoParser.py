#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import logging


class DecisaoParser:
    def extendAbv(self, abrev):
        abv = abrev.replace(".", "").lower()
        abv = re.sub("\(.*\)", "", abv)
        word = re.sub(r"([ao]?s?)$", "", abv, flags=re.IGNORECASE)
        word = self.abbreviationsTable.get(word, abv)

        if word == abv:
            logging.warning("[NEW ABV] Doesn't exist abreviation for {}".format(abrev))

        return word

    def make_string(self, byte_object):
        if isinstance(byte_object, bytes):
            return str(byte_object, "utf-8")
        elif isinstance(byte_object, list):
            return [self.make_string(b) for b in byte_object]
        elif isinstance(byte_object, tuple):
            return [self.make_string(b) for b in byte_object]
        elif isinstance(byte_object, set):
            return [self.make_string(b) for b in byte_object]

        return byte_object

    def parse_section(self, object):
        if isinstance(object, str):
            return object
        if isinstance(object, list):
            return " ".join(object)
        elif isinstance(object, tuple):
            return " ".join(object)
        elif isinstance(object, set):
            return " ".join(object)

        return object

    def parseUf(self, text):
        return (
            self.getMatchText(text, "\/\s*\w{,2}?[^\w]*\-?\s*([\w\s]{3,}\w)")
            .upper()
            .strip()
        )

    def parseType(self, acordaoId):
        return re.sub("\d+\s*", "", acordaoId).strip()

    def parseTags(self, text):
        tags = []
        if text:
            tagsRaw = re.split(r"[,\-.]+", text)
            for tag in tagsRaw:
                t = (re.sub("\s+", " ", tag)).strip()
                tags.append(t.upper())
            return list(filter(None, tags))
        return []

    def parsePartes(self, text):
        text = text.lstrip() + "\n"
        text = re.sub(r"\\n\s+", r"\n", text)
        partes = [
            match[0]
            for match in re.findall("([^\\n]+(;|:| {3,}).+?\\n([^\\n:;]+\\n)*)", text)
        ]
        partesDict = {}

        for parte in partes:
            temp = re.split("(;|:| {3,})", parte)
            t = temp[0].strip()

            if t.find(".") == -1:
                logging.warning(
                    "[LOOK ABBRV] A abreviação {} não possui ponto".format(t)
                )

            tipo = self.extendAbv(t)
            nome = re.sub(r"([\n\r]| {2,})", " ", temp[-1].strip())

            if tipo in partesDict:
                partesDict[tipo].append(nome)
            else:
                partesDict[tipo] = [nome]

        return dict(partesDict)

    def parseLawReferences(self, text):
        refs = re.split("((?:INC|PAR|LET|ART)[- :][\w\d]+)\s*", text)
        ref = {}
        lawRefs = []
        nCaputs = nArt = nPar = nInc = nAli = 0
        refs = list(filter(None, refs))

        for r in refs:
            r = r.strip()
            if r.startswith("ART"):
                if nArt or nCaputs:
                    lawRefs.append(dict(ref))
                    ref.pop("inciso", None)
                    ref.pop("alinea", None)
                    ref.pop("paragrafo", None)
                    ref.pop("caput", None)
                    ref.pop("redacao", None)
                    ref.pop("incluido", None)
                    nInc = nCaputs = nPar = nAli = 0
                ref["artigo"] = self.getMatchText(r, "ART[-: ]+(.+)")
                nArt = 1
            elif r.startswith("PAR"):
                if nPar or nAli or nCaputs:
                    lawRefs.append(dict(ref))
                    ref.pop("inciso", None)
                    ref.pop("alinea", None)
                    ref.pop("caput", None)
                    nInc = nAli = nCaputs = 0
                ref["paragrafo"] = self.getMatchText(r, "PAR[-: ]+(.+)")
                nPar = 1
            elif r.startswith("INC"):
                if nInc or nAli or nCaputs:
                    lawRefs.append(dict(ref))
                    ref.pop("alinea", None)
                    ref.pop("caput", None)
                    nAli = nCaputs = 0
                ref["inciso"] = self.getMatchText(r, "INC[- :]+(.+)")
                nInc = 1
            elif r.startswith("LET"):
                if nAli or nCaputs:
                    lawRefs.append(dict(ref))
                    ref.pop("caput", None)
                    nCaputs = 0
                nAli = 1
                ref["alinea"] = self.getMatchText(r, "LET[-: ]+(.+)")
            elif r.startswith('"CAPUT'):
                ref["caput"] = 1
                nAli = nInc = nPar = nLet = 0
                nCaputs = 1
                ref.pop("inciso", None)
                ref.pop("alinea", None)
                ref.pop("paragrafo", None)
            elif r.startswith("REDAÇÃO"):
                ref["redacao"] = self.getMatchText(r, "REDAÇÃO\s*(.+)")
            elif r.startswith("INCLUÍDO"):
                ref["incluido"] = self.getMatchText(r, "INCLUÍDO\s*(.+)")
        if ref:
            lawRefs.append(dict(ref))
        return lawRefs

    def parseLawDescription(self, text):
        if re.match("\s*(PAR|INC|ART|CAP|LET).*", text):
            return ""
        desc = re.sub("[\*]+", "", text)
        return desc.strip()

    def parseLaws(self, text):
        laws = []
        law = {}
        refs = {}
        lawLines = []
        text = text.replace("\r", " ")
        lines = text.split("\n")

        for l in lines:
            l = l.upper()
            if l.startswith("LEG"):
                if lawLines:
                    description = self.parseLawDescription(lawLines[-1])
                    if description:
                        law["descricao"] = description
                        lawLines.pop()
                    law["refs"] = self.parseLawReferences("".join(lawLines))
                if any(law):
                    laws.append(law)
                    law = {}
                lawLines = []
                law["descricao"] = ""
                law["refs"] = []
                law["sigla"] = self.getMatchText(l, r"\s*LEG[-:]\w+\s+([^\s]+).*")
                law["tipo"] = self.getMatchText(l, r"\s*LEG[-:](\w+).*")
                law["ano"] = self.getMatchText(l, r".*ANO[-:](\d+).*")
            elif l.startswith("***"):
                law["descricao"] = l
            else:
                lawLines.append(" " + l.strip())
        # append last law
        if law:
            if lawLines:
                description = self.parseLawDescription(lawLines[-1])
                law["descricao"] = description
                if description:
                    lawLines.pop()
            law["refs"] = self.parseLawReferences("".join(lawLines))
            laws.append(law)
        return laws

    def getMatchText(self, text, regexExp):
        match = re.search(regexExp, text)
        if match == None:
            return ""
        else:
            return (match.group(1)).strip()

    def removeExtraSpaces(self, text):
        return re.sub("\s+", " ", text).strip()

    abbreviationsTable = {
        "advd": "advogado",
        "adv": "advogado",
        "agd": "agravado",
        "agdv": "agravado",
        "agte": "agravante",
        "autore": "autor",
        "coator": "coator",
        "embd": "embargado",
        "embgd": "embargado",
        "embte": "embargante",
        "impd": "impetrado",
        "imptd": "impetrado",
        "impt": "impetrado",
        "impte": "impetrante",
        "intd": "intimado",
        "pacte": "paciente",
        "proc": "procurador",
        "recd": "recorrido",
        "recld": "reclamado",
        "reclte": "reclamante",
        "recte": "recorrente",
        "relator": "relator",
        "reqte": "requerente"
        # acusante
        # acusado
    }
