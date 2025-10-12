#!/usr/bin/env python3

import argparse
from movie_data import execute_query

def main() -> None:
    parser = argparse.ArgumentParser(description="Keyword Search CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    search_parser = subparsers.add_parser("search", help="Search movies using BM25")
    search_parser.add_argument("query", type=str, help="Search query")

    args = parser.parse_args()

    match args.command:
        case "search":
            print(f"Searching for: {args.query}")
            print_search(args.query)
        case _:
            parser.print_help()

def print_search(term, limit=5):
    found = execute_query(term, limit)
    for movie in found:
        print(f"{movie["id"]}. {movie["title"]}")


if __name__ == "__main__":
    main()
