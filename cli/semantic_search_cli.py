#!/usr/bin/env python3

import argparse
from lib.semantic_search import verify_model, embed_text, verify_embeddings, embed_query_text, search, chunk, semantic_chunk

def main():
    parser = argparse.ArgumentParser(description="Semantic Search CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    subparsers.add_parser("verify", help="Display model information")
    embed_text_parser = subparsers.add_parser("embed_text", help="Get embedding information")
    embed_text_parser.add_argument("text", type=str, help="Search text")
    subparsers.add_parser("verify_embeddings", help="Generate all embedding information")
    embed_text_parser = subparsers.add_parser("embedquery", help="Get embedding information about query")
    embed_text_parser.add_argument("query", type=str, help="Search query")
    search_parser = subparsers.add_parser("search", help="Search for relevant movies")
    search_parser.add_argument("query", type=str, help="Search query")
    search_parser.add_argument("--limit", type=int, help="Number of movies to find", required=False, default=5)
    chunk_parser = subparsers.add_parser("chunk", help="Chunk input text")
    chunk_parser.add_argument("text", type=str, help="Text to chunk")
    chunk_parser.add_argument("--chunk-size", type=int, help="Number of words per chunk", required=False, default=200)
    chunk_parser.add_argument("--overlap", type=int, help="Number of words to overlap from previous chunk", required=False, default=200)
    semantic_chunk_parser = subparsers.add_parser("semantic_chunk", help="Chunk input text by sentences")
    semantic_chunk_parser.add_argument("text", type=str, help="Text to chunk")
    semantic_chunk_parser.add_argument("--max-chunk-size", type=int, help="Number of sentences per chunk", required=False, default=4)
    semantic_chunk_parser.add_argument("--overlap", type=int, help="Number of sentences to overlap from previous chunk", required=False, default=0)

    args = parser.parse_args()

    match args.command:
        case "verify":
            verify_model()
        case "embed_text":
            embed_text(args.text)
        case "verify_embeddings":
            verify_embeddings()
        case "embedquery":
            embed_query_text(args.query)
        case "search":
            search(args.query, args.limit)
        case "chunk":
            chunk(args.text, args.chunk_size, args.overlap)
        case "semantic_chunk":
            semantic_chunk(args.text, args.max_chunk_size, args.overlap)
        case _:
            parser.print_help()

if __name__ == "__main__":
    main()
