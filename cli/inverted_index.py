from movie_data import tokenize, BM25_K1, BM25_B
from pickle import dump, load
from collections import Counter
import os
import math

CACHE_DIR="cache"
INDEX_FILENAME="index.pkl"
DOCMAP_FILENAME="docmap.pkl"
TF_FILENAME="term_frequencies.pkl"
LENGTHS_FILENAME="doc_lengths.pkl"

class InvertedIndex:
    def __init__(self):
        self.index = dict()
        self.docmap = dict()
        self.term_frequencies = dict()
        self.doc_lengths = dict()
        self.avg_len = -1

    def __add_document(self, doc_id, text):
        id_num = int(doc_id)
        if id_num not in self.term_frequencies:
            self.term_frequencies[id_num] = Counter()
        counter = self.term_frequencies[id_num]
        tokens = tokenize(text)
        self.doc_lengths[id_num] = len(tokens)
        for token in tokens:
            if token not in self.index:
                self.index[token] = {id_num,}
            else:
                self.index[token].add(id_num)
            counter[token] += 1

    def __get_avg_doc_length(self) -> float:
        if self.avg_len < 0:
            self.avg_len = 0.0
            if len(self.doc_lengths) > 0:
                total = 0.0
                for doc_len in self.doc_lengths.values():
                    total = total + doc_len
                self.avg_len = total / len(self.doc_lengths)
        return self.avg_len

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

    def get_bm25_tf(self, doc_id, term, k1 = BM25_K1, b = BM25_B):
        tf = self.get_tf(doc_id, term)
        norm = 1 - BM25_B + BM25_B * (self.doc_lengths[int(doc_id)] / self.__get_avg_doc_length())
        return (tf * (BM25_K1 + 1)) / (tf + BM25_K1 * norm)
        #return (tf * (k1 + 1)) / (tf + k1)

    def bm25(self, doc_id, term):
        return self.get_bm25_tf(doc_id, term) * self.get_bm25_idf(term)

    def bm25_search(self, query, limit):
        tokens = tokenize(query)
        scores = dict()
        for doc_id in self.docmap:
            doc_score = 0
            for token in tokens:
                doc_score = doc_score + self.bm25(doc_id, token)
            scores[doc_id] = doc_score
        top_scores = sorted(scores.items(), key=lambda item: item[1], reverse=True)
        return top_scores[:limit]

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
        self.avg_len = -1

    def save(self):
        try:
            os.stat("cache")
        except:
            os.mkdir("cache")
        with open(os.path.join(CACHE_DIR, INDEX_FILENAME), "wb") as f:
            dump(self.index, f)
        with open(os.path.join(CACHE_DIR, DOCMAP_FILENAME), "wb") as f:
            dump(self.docmap, f)
        with open(os.path.join(CACHE_DIR, TF_FILENAME), "wb") as f:
            dump(self.term_frequencies, f)
        with open(os.path.join(CACHE_DIR, LENGTHS_FILENAME), "wb") as f:
            dump(self.doc_lengths, f)

    def load(self):
        with open(os.path.join(CACHE_DIR, INDEX_FILENAME), "rb") as f:
            self.index = load(f)
        with open(os.path.join(CACHE_DIR, DOCMAP_FILENAME), "rb") as f:
            self.docmap = load(f)
        with open(os.path.join(CACHE_DIR, TF_FILENAME), "rb") as f:
            self.term_frequencies = load(f)
        with open(os.path.join(CACHE_DIR, LENGTHS_FILENAME), "rb") as f:
            self.doc_lengths = load(f)
        self.avg_len = -1
