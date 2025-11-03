#!/usr/bin/env python3

import argparse
from movie_data import execute_query, read_data, tokenize
from inverted_index import InvertedIndex

def main() -> None:
    parser = argparse.ArgumentParser(description="Keyword Search CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    build_parser = subparsers.add_parser("build", help="Build indexes for searching")

    search_parser = subparsers.add_parser("search", help="Search movies using BM25")
    search_parser.add_argument("query", type=str, help="Search query")

    tf_parser = subparsers.add_parser("tf", help="The thre frequency of a term in a movie description")
    tf_parser.add_argument("movie_id", type=int, help="Id number of movie")
    tf_parser.add_argument("term", type=str, help="Term to count")

    idf_parser = subparsers.add_parser("idf", help="Find the inverse document frequency of a term")
    idf_parser.add_argument("term", type=str, help="Term to find")
                           
    args = parser.parse_args()

    match args.command:
        case "search":
            print(f"Searching for: {args.query}")
            indexer = InvertedIndex()
            try:
                indexer.load()
            except Exception as e:
                print("Indexes not built.")
                print(e)
                return
            out = []
            tokens = tokenize(args.query)
            for token in tokens:
                out.extend(indexer.get_document(token))
                if len(out) > 5:
                    break
            for id in out[:5]:
                print(id, indexer.docmap[id]["title"])
        case "build":
            print(f"Building database")
            data = read_data()
            indexer = InvertedIndex()
            indexer.build(data)
            indexer.save()
        case "tf":
            try:
                indexer = InvertedIndex()
                indexer.load()
                print(indexer.get_tf(str(args.movie_id), args.term))
            except Exception as e:
                print(e)
            return
        case "idf":
            try:
                indexer = InvertedIndex()
                indexer.load()
                idf = indexer.get_idf(args.term)
                print(f"Inverse document frequency of '{args.term}': {idf:.2f}")
            except Exception as e:
                print(e)
        case _:
            parser.print_help()

def print_search(term, limit=5):
    found = execute_query(term, limit)
    for movie in found:
        print(f"{movie["id"]}. {movie["title"]}")


if __name__ == "__main__":
    main()
