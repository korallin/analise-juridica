# -*- coding: utf-8 -*-

from DecisaoParser import DecisaoParser

import re
from datetime import datetime, timedelta


class STFDecisaoParser(DecisaoParser):

    classes_processuais_dict = {
        u"AC": u"AÇÃO CAUTELAR",
        u"ACO": u"AÇÃO CÍVEL ORDINÁRIA",
        u"ADC": u"AÇÃO DECLARATÓRIA DE CONSTITUCIONALIDADE",
        u"ADI": u"AÇÃO DIRETA DE INCONSTITUCIONALIDADE",
        u"ADO": u"AÇÃO DIRETA DE INCONSTITUCIONALIDADE POR OMISSÃO",
        u"AO": u"AÇÃO ORIGINÁRIA",
        u"AOE": u"AÇÃO ORIGINÁRIA ESPECIAL",
        u"AP": u"AÇÃO PENAL",
        u"AR": u"AÇÃO RECISÓRIA",
        u"AI": u"AGRAVO DE INSTRUMENTO",
        u"ACI": u"APELAÇÃO CÍVEL",
        u"ADPF": u"ARGUIÇÃO DE DESCUMPRIMENTO DE PRECEITO FUNDAMENTAL",
        u"AIMP": u"ARGUIÇÃO DE IMPEDIMENTO",
        u"ARV": u"ARGUIÇÃO DE RELEVÂNCIA",
        u"AS": u"ARGUIÇÃO DE SUSPEIÇÃO",
        u"CR": u"CARTA ROGATÓRIA",
        u"CM": u"COMUNICAÇÃO",
        u"CA": u"CONFLITO DE ATRIBUIÇÕES",
        u"CC": u"CONFLITO DE COMPETÊNCIA",
        u"CJ": u"CONFLITO DE JURISDIÇÃO",
        u"ED": u"EMBARGO DECLARATÓRIO",
        u"EV": u"EXCEÇÃO DA VERDADE",
        u"EI": u"EXCEÇÃO DE INCOMPETÊNCIA",
        u"EL": u"EXCEÇÃO DE LITISPENDÊNCIA",
        u"ES": u"EXCEÇÃO DE SUSPEIÇÃO",
        u"EXT": u"EXTRADIÇÃO",
        u"HC": u"HABEAS CORPUS",
        u"HD": u"HABEAS DATA",
        u"INQ": u"INQUÉRITO",
        u"IF": u"INTERVENÇÃO FEDERAL",
        u"MI": u"MANDADO DE INJUNÇÃO",
        u"MS": u"MANDADO DE SEGURANÇA",
        u"OACO": u"OPOSIÇÃO EM AÇÃO CIVIL ORIGINÁRIA",
        u"PET": u"PETIÇÃO",
        u"PETA": u"PETIÇÃO AVULSA",
        u"PETAV": u"PETIÇÃO AVULSA",
        u"PPE": u"PRISÃO PREVETIVA PARA EXTRADIÇÃO",
        u"PA": u"PROCESSO ADMINISTRATIVO",
        u"PSV": u"PROPOSTA DE SÚMULA VINCULANTE",
        u"QC": u"QUEIXA-CRIME",
        u"RCL": u"RECLAMAÇÃO",
        u"RC": u"RECURSO CRIME",
        u"RE": u"RECURSO EXTRAORDINÁRIO",
        u"ARE": u"RECURSO EXTRAORDINÁRIO COM AGRAVO",
        u"EP": u"EXECUÇÃO PENAL",
        u"RHC": u"RECURSO ORDINÁRIO EM HABEAS CORPUS",
        u"RHD": u"RECURSO ORDINÁRIO EM HABEAS DATA",
        u"RMI": u"RECURSO ORDINÁRIO EM MANDADO DE INJUNÇÃO",
        u"RMS": u"RECURSO ORDINÁRIO EM MANDADO DE SEGURANÇA",
        u"RP": u"REPRESENTAÇÃO",
        u"RVC": u"REVISÃO CRIMINAL",
        u"SE": u"SENTENÇA ESTRANGEIRA",
        u"SEC": u"SENTENÇA ESTRANGEIRA CONTESTADA",
        u"SL": u"SUSPENÇÃO DE LIMINAR",
        u"SS": u"SUSPENÇÃO DE SEGURANÇA",
        u"STA": u"SUSPENÇÃO DE TUTELA ANTECIPADA",
    }

    words_black_list_regex = [u"OFÍCIO", u"LEI", u"ARTIGO", u"SÚMULA", u"DJ"]
    words_black_list_absolut = [u"DE", u"EM", u"MP", u"DO"]

    def get_acao_originaria(self, acao_originaria):
        existe_ac_orig = True
        if acao_originaria not in self.classes_processuais_dict:
            existe_ac_orig = False
            # checa se acao_originaria é uma sigla e se ela possui
            # correspondência idêntica nas chaves do dicionário
            for value in self.classes_processuais_dict.values():
                if re.search(value.split(" ")[-1], acao_originaria, re.UNICODE):
                    existe_ac_orig = True
                    break

            # verifica se possivel ação originária é na verdade um
            # ente que não é classe processual
            if not existe_ac_orig:
                for word in self.words_black_list_regex:
                    if re.search(word, acao_originaria, re.UNICODE):
                        return ""

                for word in self.words_black_list_absolut:
                    if re.search(acao_originaria, word, re.UNICODE):
                        return ""

        return acao_originaria

    def normalizeId(self, Id):
        acNo = self.getMatchText(Id, "[A-Z]+\s+(\d+)\s*.*")
        typeInv = Id.replace(acNo, " ").upper().strip()
        idList = typeInv.split()
        Id = " ".join(reversed(idList))
        return Id + " " + acNo

    def parseId(self, text):
        idRaw = self.getMatchText(text, "\s*([^\/]+).*").upper()
        idRaw = idRaw.replace("-", " ").strip()
        return self.normalizeId(idRaw)

    def joinId(self, doc_header_lst):
        acordao_id = ""
        for i, header_item in enumerate(doc_header_lst):
            if "/" not in header_item:
                acordao_id += " " + header_item
            else:
                break

        doc_header = [acordao_id]
        doc_header.extend(doc_header_lst[i:])
        return doc_header

    def parseType(self, idNormalized):
        acNo = self.getMatchText(idNormalized, "[A-Z]+(\s+\d+)")
        return idNormalized.replace(acNo, "").strip()

    def parseUfShort(self, text):
        return self.getMatchText(text, ".*/\s*(\w*).*").upper().strip()

    def parseRelator(self, text):
        return (
            self.getMatchText(text, "\s*Relator\(a\):.+[Mm][Ii][Nn].\s*(.+)")
            .upper()
            .strip()
        )

    def parseRelatorParaAcordao(self, text):
        return (
            self.getMatchText(text, "\s*Relator\(a\)\s+p\/\s+Acórdão:.+[Mm][Ii][Nn].\s*(.+)")
            .upper()
            .strip()
        )

    def parseRevisor(self, text):
        return (
            self.getMatchText(text, "\s*Revisor\(a\):.+[Mm][Ii][Nn].\s*([^\.]+)")
            .upper()
            .strip()
        )

    def parseDataJulgamento(self, text):
        text = text.replace("&nbsp", "").strip()
        date = re.search("Julgamento:\s*(\d{2})\/(\d{2})\/(\d{4})", text)
        if date:
            return datetime(int(date.group(3)), int(date.group(2)), int(date.group(1)))
        return ""

    def parseDataPublicacao(self, text):
        text = text.replace("&nbsp", "").strip()
        date = re.search("(PUBLIC|DJ)\s+(\d+)[-\/](\d+)[-\/](\d{4})", text)
        try:
            if date:
                date = datetime(
                    int(date.group(4)), int(date.group(3)), int(date.group(2))
                )
            else:
                date = ""
        except Exception as e:
            date = ""

        return date

    def parseOrgaoJulgador(self, text):
        text = text.replace("&nbsp", "").strip()
        match = re.search("Julgador:\s*(.*)\s*", text)
        if match:
            return match.group(1).upper().strip()
        return ""

    def parseAcordaosDecisionQuotes(self, txt):
        citacoes = re.findall(
            r"([A-Z]\w+)\s+([nN].\s+)?([0-9]+((\.[0-9]{3})+)?)(((\/\s*[A-Z]+)?((\-|–|\s+)[A-Z]\w+(((\-|–)[A-Z]\w+)+)?)?))(?!\/\d+|\.|\d+)",
            txt,
            re.UNICODE,
        )

        citacoesDec = set()
        for citacao in citacoes:
            acao_originaria = self.get_acao_originaria(citacao[0].strip().upper())
            if acao_originaria == "":
                continue

            decisao_numero = citacao[2].replace(".", "")
            classes_processuais_str = re.sub(
                "^(\/[A-Z]+\s*(\-|–)|(\-|–|\s+))|(\/[A-Z]+\s*)$", "", citacao[8]
            )
            if classes_processuais_str == "":
                classes_processuais_str = re.sub(
                    "^(\/[A-Z]+\s*(\-|–)|(\-|–|\s+))|(\/[A-Z]+\s*)$", "", citacao[10]
                )

            classes_processuais_list = classes_processuais_str.split("-")[::-1]

            decisao_codigo = (
                " ".join([s.upper() for s in classes_processuais_list])
                + " "
                + acao_originaria
                + " "
                + decisao_numero
            )
            citacoesDec.add(decisao_codigo.strip())

        return list(citacoesDec)

    def parseAcordaosQuotes(self, txt):
        quotes = []
        data = []
        # O ideal é que as classes processuais fossem todas conhecidas para que apenas elas fossem reconhecidas

        # quando decisões do STF são prefixadas por pela string "STF:" a expressão regular abaixo não funciona.
        # Então remove-se a string sem prejuízo para a detecção das decisões citadas em txt
        txt = txt.replace("STF:", "")
        # remoção de citações a revista trimestral de jurisprudência do STF
        txt = re.sub(r"RTJ(\-|\s+)?\d+\/\d+", "", txt)
        decisoes_monoc = re.search(
            (
                "[Dd]ecis(?:ão|ões) monocráticas? citada(?:\s*\(?s\)?)?\s*:\s*([^:]*)(?=\.[^:])"
            ).decode("utf-8"),
            txt,
        )
        acordaos = re.search(
            (
                "[Aa]córdão(?:\s*\(?s\)?)? citado(?:\s*\(?s\)?)?\s*:\s*([^:]*)(?=\.[^:])"
            ).decode("utf-8"),
            txt,
        )

        if decisoes_monoc:
            data.append(decisoes_monoc)
        if acordaos:
            data.append(acordaos)

        if data:
            for dec in data:
                dec = dec.group(1)
                dec = re.split("[;,.()]", dec)
                for q in dec:
                    q = q.strip()
                    q = re.match("([a-zA-Z]{2,}[ -]\d+[a-zA-Z]*).*", q)
                    if q:
                        q = q.group(1)
                        q = q.replace("-", " ")
                        q = q.strip().upper()
                        quotes.append(self.normalizeId(q))
        return quotes

    def parseSimilarAcordaos(self, raw):
        similar = []
        lines = raw.split("\n")
        if len(lines) <= 1:
            return []
        for i in range(0, len(lines)):
            if lines[i].startswith(" "):
                continue
            similarAcordaoId = (
                lines[i].replace(" PROCESSO ELETRÔNICO".decode("utf8"), "").strip()
            )
            similarAcordaoId = similarAcordaoId.replace(
                " ACÓRDÃO ELETRÔNICO".decode("utf8"), ""
            ).strip()
            similarAcordaoId = similarAcordaoId.replace("-", " ").strip()
            similarAcordaoId = self.normalizeId(similarAcordaoId)
            dataJulg = orgaoJulg = relator = ""
            if len(lines) > i + 1:
                dataJulg = self.getMatchText(
                    lines[i + 1], r".*(?:JULG|ANO)-([\d\-\/]+).*"
                )
                ufShort = self.getMatchText(lines[i + 1], r".*UF-(\w\w).*")
                orgaoJulg = self.getMatchText(lines[i + 1], r".*TURMA-([\w\d]+).*")
                relator = self.getMatchText(lines[i + 1], r".*M[Ii][Nn][-. ]+([^\.]+)")
                relator = relator.replace(" N", "").strip()
                #                if not dataJulg and not ufShort and not relator:
                #                   print "doesn't match"
                #                  print(lines[i:i+3])
                #                 continue
                dataJulg = dataJulg.split("-")
                if len(dataJulg) > 1:
                    dataJulg = datetime(
                        int(dataJulg[2]), int(dataJulg[1]), int(dataJulg[0])
                    )
            similarAc = {
                "acordaoId": similarAcordaoId,
                "localSigla": ufShort,
                "dataJulg": dataJulg,
                "relator": relator,
                "orgaoJulg": orgaoJulg,
            }
            similar.append(dict(similarAc))
        return similar

    def parseSimilarDecisoes(self, raw):
        similar = []
        lines = raw.split("\n")
        if len(lines) <= 1:
            return []

        for i in range(0, len(lines)):
            if lines[i].startswith(" "):
                continue
            similarDecisaoId = (
                lines[i].replace(" PROCESSO ELETRÔNICO".decode("utf8"), "").strip()
            )
            similarDecisaoId = similarDecisaoId.replace(
                " ACÓRDÃO ELETRÔNICO".decode("utf8"), ""
            ).strip()
            similarDecisaoId = similarDecisaoId.replace("-", " ").strip()
            similarDecisaoId = self.normalizeId(similarDecisaoId)
            dataJulg = relator = ""

            if len(lines) > i + 1:
                dataJulg = self.getMatchText(
                    lines[i + 1], r".*(?:JULG|ANO)-([\d\-\/]+).*"
                )
                ufShort = self.getMatchText(lines[i + 1], r".*UF-(\w\w).*")
                relator = self.getMatchText(lines[i + 1], r".*M[Ii][Nn][-. ]+([^\\]+)")
                relator = relator.strip()
                dataJulg = dataJulg.split("-")

                if len(dataJulg) > 1:
                    dataJulg = datetime(
                        int(dataJulg[2]), int(dataJulg[1]), int(dataJulg[0])
                    )
            similarDec = {
                "acordaoId": similarDecisaoId,
                "localSigla": ufShort,
                "dataJulg": dataJulg,
                "relator": relator,
            }
            similar.append(dict(similarDec))

        return similar

    def printLaw(self, law):
        print("-------------------------------------------------------------")
        print("sigla: " + law["sigla"])
        print("desc: " + law["descricao"])
        print("tipo: " + law["tipo"])
        print("ano: " + law["ano"])
        print("refs: ")
        #       print(law["refs"]
        for i, a in enumerate(law["refs"]):
            print(a)
        print("-------------------------------------------------------------")
