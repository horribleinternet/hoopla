import json, string
from nltk.stem import PorterStemmer

BM25_K1 = 1.5
BM25_B = 0.75

def read_data():
    what = None
    with open("data/movies.json", "r") as f:
        what = json.load(f)
    return what["movies"]

def search_data(data, terms):
    out = []
    for i, movie in enumerate(data):
        title_words = tokenize(movie["title"])
        done = False
        for term in terms:
            for word in title_words:
                if term in word:
                    out.append(movie)
                    done = True
                    break
            if done:
                break
    return out

def execute_query(term, limit=5):
    movies = read_data()
    terms = tokenize(term)
    found = search_data(movies, terms)
    found.sort(key=lambda item: int(item["id"]))
    limit = min(limit, len(found))
    return found[:limit]

def get_translation():
    return str.maketrans("", "", string.punctuation)

def tokenize(words):
    terms = words.split()
    terms = [item for item in terms if len(item) > 0]
    trans = get_translation()
    terms = [term.lower().translate(trans) for term in terms]
    stopwords = read_stopwords()
    terms = [item for item in terms if item not in stopwords]
    stemmer = PorterStemmer()
    return [stemmer.stem(item, True) for item in terms]

def read_stopwords():
        stopwords = []
        with open("data/stopwords.txt", "r") as f:
            all = f.read()
            stopwords = all.splitlines()
        return [item for item in stopwords if len(item) > 0]
