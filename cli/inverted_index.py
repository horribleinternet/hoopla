from movie_data import tokenize
from pickle import dump, load
from collections import Counter
import os
import math

class InvertedIndex:
    def __init__(self):
        self.index = dict()
        self.docmap = dict()
        self.term_frequencies = dict()

    def __add_document(self, doc_id, text):
        id_num = int(doc_id)
        if id_num not in self.term_frequencies:
            self.term_frequencies[id_num] = Counter()
        counter = self.term_frequencies[id_num]
        tokens = tokenize(text)
        for token in tokens:
            if token not in self.index:
                self.index[token] = {id_num,}
            else:
                self.index[token].add(id_num)
            counter[token] += 1

    def get_document(self, term):
        term = term.lower()
        if term in self.index:
            out = list(self.index[term])
            out.sort()
            return out
        return []

    def get_tf(self, doc_id: str, term: str) -> int:
        id_num = int(doc_id)
        tokens = tokenize(term)
        if len(tokens) != 1:
            raise Exception("Only one term allowd")
        if id_num not in self.term_frequencies:
            raise Exception("Invalid document id")
        return self.term_frequencies[id_num][tokens[0]]

    def get_tfidf(self, doc_id: str, term: str) -> int:
        return self.get_tf(doc_id, term) * self.get_idf(term)

    def get_idf(self, term):
        return math.log((len(self.term_frequencies) + 1) / (self.__get_term_count(term) + 1))

    def get_bm25_idf(self, term: str) -> float:
        df = self.__get_term_count(term)
        return math.log((len(self.term_frequencies) - df + 0.5) / (df + 0.5) + 1)
        
    def __get_term_count(self, term):
        tokens = tokenize(term)
        if len(tokens) != 1:
            raise Exception("Only one term allowd")
        term_num = 0
        for val in self.term_frequencies.values():
            if val[tokens[0]] > 0:
                term_num += 1
        return term_num

    def build(self, data):
        for movie in data:
            desc = f"{movie["title"]} {movie["description"]}"
            self.__add_document(movie["id"], desc)
            self.docmap[int(movie["id"])] = movie

    def save(self):
        try:
            os.stat("cache")
        except:
            os.mkdir("cache")
        with open("cache/index.pkl", "wb") as f:
            dump(self.index, f)
        with open("cache/docmap.pkl", "wb") as f:
            dump(self.docmap, f)
        with open("cache/term_frequencies.pkl", "wb") as f:
            dump(self.term_frequencies, f)

    def load(self):
        with open("cache/index.pkl", "rb") as f:
            self.index = load(f)
        with open("cache/docmap.pkl", "rb") as f:
            self.docmap = load(f)
        with open("cache/term_frequencies.pkl", "rb") as f:
            self.term_frequencies = load(f)
