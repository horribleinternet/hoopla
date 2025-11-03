from movie_data import tokenize
from pickle import dump, load
import os

class InvertedIndex:
    def __init__(self):
        self.index = dict()
        self.docmap = dict()

    def __add_document(self, doc_id, text):
        tokens = tokenize(text)
        for token in tokens:
            if token not in self.index:
                self.index[token] = {int(doc_id),}
            else:
                self.index[token].add(int(doc_id))

    def get_document(self, term):
        term = term.lower()
        if term in self.index:
            out = list(self.index[term])
            out.sort()
            return out
        return []

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

    def load(self):
        with open("cache/index.pkl", "rb") as f:
            self.index = load(f)
        with open("cache/docmap.pkl", "rb") as f:
            self.docmap = load(f)
