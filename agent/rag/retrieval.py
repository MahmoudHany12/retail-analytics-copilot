# agent/rag/retrieval.py
import os
import re
import json
from typing import List, Dict, Tuple
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

DOCS_PATH = Path(__file__).resolve().parents[2] / "docs"


class Chunk:
    def __init__(self, source: str, idx: int, text: str):
        self.source = source  # filename
        self.idx = idx  # chunk index (int)
        self.text = text
        self.chunk_id = f"{Path(source).stem}::chunk{idx}"

    def to_dict(self):
        return {"chunk_id": self.chunk_id, "source": self.source, "idx": self.idx, "text": self.text}


class Retriever:
    """
    Deterministic TF-IDF retriever with simple chunking.
    Exposes:
      - build_index()  -> scans docs/, chunks, computes tfidf matrix
      - retrieve(query, k=3) -> returns list of {"chunk_id","source","idx","text","score"}
    """

    def __init__(self, docs_path: str = None, chunk_size: int = 200, chunk_overlap: int = 40):
        self.docs_path = Path(docs_path) if docs_path else DOCS_PATH
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.chunks: List[Chunk] = []
        self.tfidf = None
        self.vectorizer = None
        self._built = False

    def _read_docs(self) -> List[Tuple[str, str]]:
        files = sorted([p for p in self.docs_path.glob("*.md")])
        data = []
        for p in files:
            text = p.read_text(encoding="utf-8")
            data.append((str(p.name), text))
        return data

    def _chunk_text(self, text: str) -> List[str]:
        # naive paragraph / sliding window chunker; deterministic
        paragraphs = [p.strip() for p in re.split(r"\n{2,}", text) if p.strip()]
        # break long paragraphs into windowed chunks
        chunks = []
        for para in paragraphs:
            if len(para) <= self.chunk_size:
                chunks.append(para)
            else:
                # sliding window
                i = 0
                while i < len(para):
                    chunk = para[i : i + self.chunk_size]
                    chunks.append(chunk.strip())
                    i += self.chunk_size - self.chunk_overlap
        return chunks

    def build_index(self):
        self.chunks = []
        docs = self._read_docs()
        for fname, content in docs:
            cts = self._chunk_text(content)
            for i, c in enumerate(cts):
                chunk = Chunk(source=fname, idx=i, text=c)
                self.chunks.append(chunk)

        corpus = [c.text for c in self.chunks]
        if not corpus:
            # empty corpus edge-case
            self.vectorizer = TfidfVectorizer().fit([" "])
            self.tfidf = self.vectorizer.transform([" "])
        else:
            self.vectorizer = TfidfVectorizer(norm="l2", use_idf=True, smooth_idf=True, sublinear_tf=False)
            self.tfidf = self.vectorizer.fit_transform(corpus)
        self._built = True

    def retrieve(self, query: str, k: int = 3) -> List[Dict]:
        if not self._built:
            self.build_index()

        qvec = self.vectorizer.transform([query])
        scores = (self.tfidf @ qvec.T).toarray().squeeze()  # cosine-like via tfidf dot
        # deterministic tie-break: sort by score desc then chunk_id asc
        indices = np.argsort(-scores)  # descending
        results = []
        added = 0
        for idx in indices:
            if scores[idx] <= 0 and added >= k:
                break
            if added >= k:
                break
            chunk = self.chunks[int(idx)]
            results.append(
                {
                    "chunk_id": chunk.chunk_id,
                    "source": chunk.source,
                    "idx": chunk.idx,
                    "text": chunk.text,
                    "score": float(scores[idx]),
                }
            )
            added += 1
        return results


# Simple CLI test
if __name__ == "__main__":
    r = Retriever()
    r.build_index()
    res = r.retrieve("return window beverages unopened days", k=3)
    print(json.dumps(res, indent=2))
