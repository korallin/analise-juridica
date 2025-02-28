#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re


class PartesCorpusBuilder(CorpusBuilder):
    def addWords(self, text):
        keys = self.corpusDict.keys()
        for w in re.split(r"[\s,.?;:\"\']+", text):
            w = w.lower()
            if w in keys:
                self.corpusDict[w] += 1
            else:
                if self.validWord(w):
                    self.corpusDict[w] = 1

    def validWord(self, word):
        if len(word) < 3:
            return 0
        if re.match(r"[\d]+", word):
            return 0
        if re.match(r"qu[e(?:ai)(?:al)]", word):
            return 0
        if re.match(r"d[aeio][s]?", word):
            return 0
        if word in self.stopListWords:
            return 0
        if re.match(r"p[(?:ara)(?:elo)(?:or)][s]?", word):
            return 0
        if re.match(r"[\d\s\/]+", word):
            return 0
        return 1

    def print2File(self, filename):
        file = open(filename, "a")
        file.seek(0)
        file.truncate()
        i = 0
        for w in sorted(self.corpusDict, key=self.corpusDict.get, reverse=True):
            file.write("%20s ==> %10d\n" % (w, self.corpusDict[w]))
            i += 1
            if i >= 1000:
                break
        file.close()
