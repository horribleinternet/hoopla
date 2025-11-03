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
        case _:
            parser.print_help()

def print_search(term, limit=5):
    found = execute_query(term, limit)
    for movie in found:
        print(f"{movie["id"]}. {movie["title"]}")


if __name__ == "__main__":
    main()
