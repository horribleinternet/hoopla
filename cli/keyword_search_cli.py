#!/usr/bin/env python3

import argparse
from movie_data import execute_query, read_data, tokenize, BM25_K1, BM25_B
from inverted_index import InvertedIndex

def main() -> None:
    parser = argparse.ArgumentParser(description="Keyword Search CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    build_parser = subparsers.add_parser("build", help="Build indexes for searching")

    search_parser = subparsers.add_parser("search", help="Search movies using BM25")
    search_parser.add_argument("query", type=str, help="Search query")

    tf_parser = subparsers.add_parser("tf", help="The frequency of a term in a movie description")
    tf_parser.add_argument("movie_id", type=int, help="Id number of movie")
    tf_parser.add_argument("term", type=str, help="Term to count")

    tfidf_parser = subparsers.add_parser("tfidf", help="The frequency of a term in a movie description times its rarity")
    tfidf_parser.add_argument("movie_id", type=int, help="Id number of movie")
    tfidf_parser.add_argument("term", type=str, help="Term to count")

    idf_parser = subparsers.add_parser("idf", help="Find the inverse document frequency of a term")
    idf_parser.add_argument("term", type=str, help="Term to find")

    bm35idf_parser = subparsers.add_parser("bm25idf", help="Find the BM25 inverse document frequency of a term")
    bm35idf_parser.add_argument("term", type=str, help="Term to find")

    bm25_tf_parser = subparsers.add_parser("bm25tf", help="Get BM25 TF score for a given document ID and term")
    bm25_tf_parser.add_argument("doc_id", type=int, help="Document ID")
    bm25_tf_parser.add_argument("term", type=str, help="Term to get BM25 TF score for")
    bm25_tf_parser.add_argument("k1", type=float, nargs='?', default=BM25_K1, help="Tunable BM25 K1 parameter")
    bm25_tf_parser.add_argument("b", type=float, nargs='?', default=BM25_B, help="Tunable BM25 b parameter")

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
        case "tfidf":
            try:
                indexer = InvertedIndex()
                indexer.load()
                tf_idf = indexer.get_tfidf(str(args.movie_id), args.term)
                print(f"TF-IDF score of '{args.term}' in document '{args.movie_id}': {tf_idf:.2f}")
            except Exception as e:
                print(e)
        case "idf":
            try:
                indexer = InvertedIndex()
                indexer.load()
                idf = indexer.get_idf(args.term)
                print(f"Inverse document frequency of '{args.term}': {idf:.2f}")
            except Exception as e:
                print(e)
        case "bm25idf":
            try:
                bm25idf = bm25_idf_command(args.term)
                print(f"BM25 IDF score of '{args.term}': {bm25idf:.2f}")
            except Exception as e:
                print(e)
        case "bm25tf":
            try:
                bm25tf = bm25_tf_command(args.doc_id, args.term, args.k1, args.b)
                print(f"BM25 TF score of '{args.term}' in document '{args.doc_id}': {bm25tf:.2f}")
            except Exception as e:
                print(e)
        case _:
            parser.print_help()

def bm25_idf_command(term):
    indexer = InvertedIndex()
    indexer.load()
    return indexer.get_bm25_idf(term)

def bm25_tf_command(doc_id, term, k1, b):
    indexer = InvertedIndex()
    indexer.load()
    return indexer.get_bm25_tf(str(doc_id), term, k1, b)

def print_search(term, limit=5):
    found = execute_query(term, limit)
    for movie in found:
        print(f"{movie["id"]}. {movie["title"]}")


if __name__ == "__main__":
    main()
