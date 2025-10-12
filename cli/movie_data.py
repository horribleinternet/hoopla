import json

def read_data():
    what = None
    with open("data/movies.json", "r") as f:
        what = json.load(f)
    return what["movies"]

def search_data(data, term):
    out = []
    for i, movie in enumerate(data):
        if term in movie["title"]:
            out.append(movie)
    return out

def execute_query(term, limit=5):
    movies = read_data()
    found = search_data(movies, term)
    found.sort(key=lambda item: int(item["id"]))
    limit = min(limit, len(found))
    return found[:limit]
