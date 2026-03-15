from sentence_transformers import SentenceTransformer
import numpy as np
import os
import json
import  re

EMBEDDINGS_CACHE = "cache/movie_embeddings.npy"
MOVIE_DATA = "data/movies.json"

class SemanticSearch:
    def __init__(self) -> None:
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.embeddings = None
        self.documents = None
        self.document_map = dict()

    def generate_embedding(self, text):
        text = str.strip(text)
        if len(text) == 0:
            raise ValueError("generate_embedding: text is empty")
        return self.model.encode([text])[0]

    def build_embeddings(self, documents):
        self.documents = documents
        movies = []
        for document in self.documents:
            self.document_map[document['id']] = document
            movies.append(f"{document['title']}: {document['description']}")
        self.embeddings = self.model.encode(movies, show_progress_bar=True)
        np.save(EMBEDDINGS_CACHE, self.embeddings)
        return self.embeddings

    def load_or_create_embeddings(self, documents):
        if os.path.exists(EMBEDDINGS_CACHE):
            self.embeddings = np.load(EMBEDDINGS_CACHE)
            if len(self.embeddings) == len(documents):
                self.documents = documents
                return self.embeddings
        self.embeddings = self.build_embeddings(documents)
        return self.embeddings

    def search(self, query, limit):
        if self.embeddings is None:
            raise ValueError("No embeddings loaded. Call `load_or_create_embeddings` first.")
        if limit < 1:
            raise ValueError("Invalid limit")
        embedding = self.generate_embedding(query)
        similarities = [(cosine_similarity(embedding, self.embeddings[i]), self.documents[i]) for i in range(0, len(self.embeddings))]
        similarities.sort(key=lambda x: x[0],reverse=True)
        return [{'score': similarity[0], 'title': similarity[1]['title'], 'description': similarity[1]['description']} for similarity in similarities[:min(limit, len(similarities))]]

def verify_embeddings():
    ss = SemanticSearch()
    data = None
    with open(MOVIE_DATA, "r") as f:
        data = json.load(f)
    embeddings = ss.load_or_create_embeddings(data["movies"])
    print(f"Number of docs:   {len(data["movies"])}")
    print(f"Embeddings shape: {embeddings.shape[0]} vectors in {embeddings.shape[1]} dimensions")

def verify_model() -> None:
    ss = SemanticSearch()
    print(f"Model loaded: {ss.model}")
    print(f"Max sequence length: {ss.model.max_seq_length}")

def embed_text(text):
    ss = SemanticSearch()
    embedding = ss.generate_embedding(text)
    print(f"Text: {text}")
    print(f"First 3 dimensions: {embedding[:3]}")
    print(f"Dimensions: {embedding.shape[0]}")

def embed_query_text(text):
    ss = SemanticSearch()
    embedding = ss.generate_embedding(text)
    print(f"Query: {text}")
    print(f"First 5 dimensions: {embedding[:5]}")
    print(f"Shape: {embedding.shape}")

def search(query, limit):
    ss = SemanticSearch()
    with open(MOVIE_DATA, "r") as f:
        data = json.load(f)
    ss.load_or_create_embeddings(data["movies"])
    movies = ss.search(query, limit)
    for i, entry in enumerate(movies):
        print(f"{i+1}. {entry['title']} (score: {entry['score']:.4f})")
        print(f"{entry['description']}\n")

def chunk(text, size, overlap):
    overlap = max(0, min(overlap, size-1))
    print(f"Chunking {len(text)} characters")
    strings = chunk_text(text, size, overlap)
    for i, string in enumerate(strings):
        print(f"{i+1}. {string}")

def chunk_text(text, size, overlap):
    chunks = []
    words = text.split()
    start = 0
    while True:
        chunks.append(" ".join(words[start:start+size]))
        start = start + size
        if (start >= len(words)):
            break
        start = start - overlap
    return chunks

def semantic_chunk(text, size, overlap):
    overlap = max(0, min(overlap, size-1))
    print(f"Semantically chunking {len(text)} characters")
    strings = semantic_chunk_text(text, size, overlap)
    for i, string in enumerate(strings):
        print(f"{i+1}. {string}")

def semantic_chunk_text(text, size, overlap):
    chunks = []
    words = re.split(r"(?<=[.!?])\s+", text)
    start = 0
    while True:
        chunks.append(" ".join(words[start:start+size]))
        start = start + size
        if (start >= len(words)):
            break
        start = start - overlap
    return chunks

def cosine_similarity(vec1, vec2):
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)

    if norm1 == 0 or norm2 == 0:
        return 0.0

    return dot_product / (norm1 * norm2)