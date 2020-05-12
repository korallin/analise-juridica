#!/usr/bin/env python
# -*- coding: utf-8 -*-

from acordaos.spiders.DecisaoParser import DecisaoParser

import re
from datetime import datetime, timedelta


MAGAZINES = [
    "MAG-CD",
    "MAG-DVD",
    "RGJ-CD",
    "JTARS",
    "BIBJURID-DVD",
    "JCSTF",
    "JPSTF",
    "JPO-DVD",
    "JBCC",
    "JBC",
    "JBT",
    "JC",
    "JTJ",
    "JTJ-CD",
    "JURISonline-INT",
    "JurisSíntese-DVD",
    "JurisSíntese-INT",
    "LEXJTACSP",
    "LEXSTF",
    "LEXSTF-CD",
    "MAG-INT",
    "NRDF",
    "PLENUMonline-INT",
    "REPIOB",
    "RADCOAST",
    "RB",
    "RCJ",
    "RDA",
    "RDC",
    "RDP",
    "RDTAPET",
    "RDJTJDFT",
    "RDJ",
    "RET",
    "RJDTACSP",
    "RJADCOAS",
    "RJTJRS",
    "RJTJRS-INT",
    "RDECTRAB",
    "RDDP",
    "RDDT",
    "RMP",
    "RT",
    "RF",
    "RIP",
    "RIOBTP",
    "RJTS",
    "RJSP",
    "RJMG",
    "RJP",
    "RJP-CD",
    "REVJMG",
    "REVJMG-INT",
    "RLTR",
    "RMDPPP",
    "RNDJ",
    "RPTGJ",
    "RSJADV",
    "RST",
    "RSTP",
    "RTFP",
    "RTJ",
    "RTJE",
    "SINTESE-INT",
    "COAD-INT",
]


class STFDecisaoParser(DecisaoParser):

    classes_processuais_dict = {
        "AC": "AÇÃO CAUTELAR",
        "ACO": "AÇÃO CÍVEL ORDINÁRIA",
        "ADC": "AÇÃO DECLARATÓRIA DE CONSTITUCIONALIDADE",
        "ADI": "AÇÃO DIRETA DE INCONSTITUCIONALIDADE",
        "ADO": "AÇÃO DIRETA DE INCONSTITUCIONALIDADE POR OMISSÃO",
        "AO": "AÇÃO ORIGINÁRIA",
        "AOE": "AÇÃO ORIGINÁRIA ESPECIAL",
        "AP": "AÇÃO PENAL",
        "AR": "AÇÃO RECISÓRIA",
        "AI": "AGRAVO DE INSTRUMENTO",
        "ACI": "APELAÇÃO CÍVEL",
        "ADPF": "ARGUIÇÃO DE DESCUMPRIMENTO DE PRECEITO FUNDAMENTAL",
        "AIMP": "ARGUIÇÃO DE IMPEDIMENTO",
        "ARV": "ARGUIÇÃO DE RELEVÂNCIA",
        "AS": "ARGUIÇÃO DE SUSPEIÇÃO",
        "CR": "CARTA ROGATÓRIA",
        "CM": "COMUNICAÇÃO",
        "CA": "CONFLITO DE ATRIBUIÇÕES",
        "CC": "CONFLITO DE COMPETÊNCIA",
        "CJ": "CONFLITO DE JURISDIÇÃO",
        "ED": "EMBARGO DECLARATÓRIO",
        "EV": "EXCEÇÃO DA VERDADE",
        "EI": "EXCEÇÃO DE INCOMPETÊNCIA",
        "EL": "EXCEÇÃO DE LITISPENDÊNCIA",
        "ES": "EXCEÇÃO DE SUSPEIÇÃO",
        "EXT": "EXTRADIÇÃO",
        "HC": "HABEAS CORPUS",
        "HD": "HABEAS DATA",
        "INQ": "INQUÉRITO",
        "IF": "INTERVENÇÃO FEDERAL",
        "MI": "MANDADO DE INJUNÇÃO",
        "MS": "MANDADO DE SEGURANÇA",
        "OACO": "OPOSIÇÃO EM AÇÃO CIVIL ORIGINÁRIA",
        "PET": "PETIÇÃO",
        "PETA": "PETIÇÃO AVULSA",
        "PETAV": "PETIÇÃO AVULSA",
        "PPE": "PRISÃO PREVETIVA PARA EXTRADIÇÃO",
        "PA": "PROCESSO ADMINISTRATIVO",
        "PSV": "PROPOSTA DE SÚMULA VINCULANTE",
        "QC": "QUEIXA-CRIME",
        "RCL": "RECLAMAÇÃO",
        "RC": "RECURSO CRIME",
        "RE": "RECURSO EXTRAORDINÁRIO",
        "ARE": "RECURSO EXTRAORDINÁRIO COM AGRAVO",
        "EP": "EXECUÇÃO PENAL",
        "RHC": "RECURSO ORDINÁRIO EM HABEAS CORPUS",
        "RHD": "RECURSO ORDINÁRIO EM HABEAS DATA",
        "RMI": "RECURSO ORDINÁRIO EM MANDADO DE INJUNÇÃO",
        "RMS": "RECURSO ORDINÁRIO EM MANDADO DE SEGURANÇA",
        "RP": "REPRESENTAÇÃO",
        "RVC": "REVISÃO CRIMINAL",
        "SE": "SENTENÇA ESTRANGEIRA",
        "SEC": "SENTENÇA ESTRANGEIRA CONTESTADA",
        "SL": "SUSPENÇÃO DE LIMINAR",
        "SS": "SUSPENÇÃO DE SEGURANÇA",
        "STA": "SUSPENÇÃO DE TUTELA ANTECIPADA",
    }

    words_black_list_regex = ["OFÍCIO", "LEI", "ARTIGO", "SÚMULA", "DJ"]
    words_black_list_absolut = ["DE", "EM", "MP", "DO"]

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
        return self.getMatchText(text, ".*/\s*(\w{2})[^A-Za-z]+\-?").upper().strip()

    def parseRelator(self, text):
        return (
            self.getMatchText(text, "\s*Relator\(a\):.+[Mm][Ii][Nn].\s*(.+)")
            .upper()
            .strip()
        )

    def parseRelatorParaAcordao(self, text):
        return (
            self.getMatchText(
                text, "\s*Relator\(a\)\s+p\/\s+Acórdão:.+[Mm][Ii][Nn].\s*(.+)"
            )
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

    def parse_citacoes_revistas(self, publication):
        mag_citations = []
        for mag in MAGAZINES:
            match = re.search(
                "\s+" + mag + "[^\w]+.*VOL\-?\s*0*(\d+)\-?\d*\s*PP\-?0*(\d+)",
                publication,
            )
            if match is None:
                match = re.search(
                    "\s+" + mag + "[^\w]+.*n\.\s*(\d+).*[pP]\.[^\d]*(\d+)", publication
                )

            # complementary patterns
            # RJADCOAS v. 61, 2005, p. 548-553
            if match is None:
                match = re.search(
                    "\s+" + mag + "[^\w]+.*v\.\s*(\d+).*[pP]\.[^\d]*(\d+)", publication
                )

            # RSJADV jul., 2012, p. 40-43
            # RSJADV maio, 2012, p. 40-43
            if match is None:
                match = re.search(
                    "\s+" + mag + "[^\w]+(\w{3,4})\.?.*p\.[^\d]*(\d+)", publication
                )

            # RJP v. 8, n. 45, 2012, 105-107
            if match is None:
                match = re.search(
                    "\s+" + mag + "[^\w]+v\.\s*(\d+)\s*[^n]+n\..*,\s*(\d+)\-",
                    publication,
                )

            if match is not None:
                mag_citations.append(mag + " " + "/".join(match.groups()))

        return mag_citations

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

    def parseAcordaosQuotes(self, txt, dec_type):
        """
        https://pt.stackoverflow.com/questions/13598/significado-de-em-uma-regex
        """
        quotes = []
        # Quando decisões do STF são prefixadas por pela string "STF:" a expressão regular abaixo não funciona.
        # Então remove-se a string sem prejuízo para a detecção das decisões citadas em txt
        txt = re.sub(r"art\.", "art", txt, flags=re.IGNORECASE)
        txt = re.sub("(STF:|\-?\s*(t|p)\w*\s*pleno|CASO\s+LÍDER)", "", txt, flags=re.IGNORECASE)
        # Verificar se é usado o padrão que remove o máximo possível de caracteres após modificar o padrão aqui
        # Em alguns espelhos o padrão que aparece no final acaba aparecendo no começo.
        # Então não é possível remover todo o texto que vem depois.
        txt = re.sub(
            r"((Número\s*de\s*p[aá]ginas|Altera[aç][aã]o|Revis[aã]o|Inclus[aã]o|An[aá]lise|Obs\.|Vota[cç][aã]o|Resultado):)[^\.]*\.", "", txt, flags=re.IGNORECASE
        )
        # Além disso, uma decisão específica começa com a string “Veja” Será feita uma exceção para este caso.
        veja_pattern = r"(^Veja[^\.]*\.)?(.*)\-?\s*Veja.*"
        while re.search(veja_pattern, txt, flags=re.IGNORECASE):
            txt = re.sub(
                veja_pattern, r"\2", txt, flags=re.IGNORECASE
            )

        # ver posteriormente que tipo de informação é inserida entre '()' nas citações
        txt = re.sub(r"(STJ|TSE|TRE|TST|TRF\s*\-?[\s\w]*)\s*:.+[;\.]\s*", "", txt)

        search_pattern = (
            "[Dd]ecis(?:ão|ões)\s*monocráticas?\s*citada(?:\s*\(?s\)?)?\s*:\s*([^:]*)(?=\.[^:])"
            if dec_type == "decisoes_monocraticas"
            else "[Aa]c[óo]rd[ãa]o\s*\(?\s*s?\s*\)?\s+[Cc]itado\s*\(?\s*s?\s*\)?\s*[:;,]\s*(\.(?!\s)*|[^:]*)?"
        )
        #     Acórdão seguido eventualmente de espaços, seguido eventualmente de (s) com eventuais espaços dentro,
        #     seguido de espaços, seguido de Citado, seguido eventualmente de espaços, seguido eventualmente de (s)
        #     com eventuais espaços dentro seguido de eventuais espaços e eventualmente ':', seguido de caracteres
        #     que não sejam ':'. A última sequência (caracteres que não sejam ':') é que o que seve ser capturado.
        dec = re.search((search_pattern), txt, flags=re.IGNORECASE)

        if dec:
            dec = dec.group(1)
            dec = re.sub(r"[Dd]ecis(?:ão|ões)\s*monocráticas?\s*citada\s*\(?\s*s?\s*\)?\s*", "", dec, flags=re.IGNORECASE)
            if (len(dec) > 2) and (dec[-2] == "."):
                dec = dec[:-2]

            dec = re.sub(r"\..+(apensado|a).+aos.+autos[^\.]+\.", "", dec, flags=re.IGNORECASE)
            dec = re.sub(r"\.[^\.]+[AO]s?[^:]+(foram|foi).+objeto.+(rejeitado|conhecido|recebido|acolhido)s[^\.]+\.", "",
                         dec, flags=re.IGNORECASE)

            dec = re.sub(r"(\d+)\.(\d+)", r"\1\2", dec)
            dec = re.sub(r"[,;]?[\w\d\s\.\/\-]+\((STJ|TSE|TST|TRE|TRF\s*\-?[\s\w]*)\)", "", dec)
            # remover menções a revistas entre parênteses porque isso significa que o próprio
            # id do acórdão citado já é referenciado
            dec = re.sub("\(([A-Z]+\-?[\s\d]+\/\d+\-?\d*,?\s*)+\)", ",", dec)
            dec = re.sub("\-\s*[A-Z]+\-?[\s\d]+\/\d+\-?\d*", ",", dec)
            # manter citação à decisão e não à revista como no exemplo: 'TJ 169/557 (HC 73801)'
            dec = re.sub(r"(\w+\-?[\s\d]+\/\d+\-?\d*)\s+\(([^\d]{2,}[\s-]+\d+[^\d\)]*)\)", r"\2,", dec)

            # REMOVER CONTEÚDO ENTRE PARÊNTESES AQUI
            while re.search(r"\([^\(\)]+\)", dec):
                dec = re.sub(r"\([^\(\)]+\)", ",", dec)

            # VER O EFEITO DO SPLIT NO PARÊNTESES PARA ENTENDER QUE PADRÃO É EXTRAÍDO
            dec = re.split("[;,.()]", dec)
            for q in dec:
                # SIGNIFICA QUE ACABOU O PADRÃO DE DECISÕES
                if re.search(r"embargos?\sde|(de|em)\sembargos?|RISTF|ESTRANGEIRA|(\-\s*STJ|\s+STJ|STJ\s+\-|TRF)", q, flags=re.IGNORECASE):
                    return quotes
                q = q.strip()

                acordaoId_pattern = "([^\d\s]{2,}[\s-]+\d+[^\d\/]*)$"
                m = re.search(acordaoId_pattern, q)
                if m is None:
                    n = re.search("([A-Z]+)\-?\s*(\d+\/\d+)", q)
                    if (n is not None) and (not q.startswith("-")):
                        n = " ".join(n.groups())
                        # REPLACE CODE BELOW FOR SEARCH FOR TARNSLATING MAGAZINE IDS TO DECISION IDS
                        if n in revistas_to_acordao_id_dict:
                            quotes.append(revistas_to_acordao_id_dict[n])
                        else:
                            quotes.append(n)

                while m:
                    m = m.group()
                    q = q.replace(m, "")
                    m = m.replace("-", " ")
                    m = m.strip().upper()
                    m = " ".join(m.split())
                    m = normalizeId(m)
                    quotes.append(m)
                    m = re.search(acordaoId_pattern, q)
        return sorted(set(quotes))



    def parseSimilarAcordaos(self, raw):
        similar = []
        lines = raw.split("\n")
        if len(lines) <= 1:
            return []
        for i in range(0, len(lines)):
            if lines[i].startswith(" "):
                continue
            similarAcordaoId = lines[i].replace(" PROCESSO ELETRÔNICO", "").strip()
            similarAcordaoId = similarAcordaoId.replace(
                " ACÓRDÃO ELETRÔNICO", ""
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
            similarDecisaoId = lines[i].replace(" PROCESSO ELETRÔNICO", "").strip()
            similarDecisaoId = similarDecisaoId.replace(
                " ACÓRDÃO ELETRÔNICO", ""
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
