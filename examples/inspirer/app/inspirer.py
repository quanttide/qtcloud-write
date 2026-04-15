import os
import json
from pathlib import Path
from typing import Optional
from collections import Counter
import math


class TFIDF:
    def __init__(self):
        self.corpus = []
        self.vocab = set()
        self.idf = {}

    def tokenize(self, text: str) -> list[str]:
        return list(text)

    def fit(self, texts: list[str]):
        self.corpus = texts
        for text in texts:
            self.vocab.update(self.tokenize(text))

        df = Counter()
        for text in texts:
            for word in set(self.tokenize(text)):
                df[word] += 1

        n = len(texts)
        for word, freq in df.items():
            self.idf[word] = math.log(n / freq)

    def get_vector(self, text: str) -> dict[str, float]:
        tokens = self.tokenize(text)
        tf = Counter(tokens)
        vec = {}
        for word, freq in tf.items():
            if word in self.idf:
                vec[word] = freq * self.idf[word]
        return vec

    def cosine_similarity(self, a: dict[str, float], b: dict[str, float]) -> float:
        common = set(a.keys()) & set(b.keys())
        if not common:
            return 0.0

        dot = sum(a[w] * b[w] for w in common)
        norm_a = math.sqrt(sum(v * v for v in a.values()))
        norm_b = math.sqrt(sum(v * v for v in b.values()))

        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)


class Inspir:
    def __init__(self, journal_path: str = "sample/archive.md"):
        self.journal_path = Path(journal_path)
        self.cache_path = Path("sample/tfidf_cache.json")
        self.entries = []
        self.tfidf = TFIDF()
        self._use_embedding = False

    def load(self):
        content = self.journal_path.read_text()
        self.entries = []
        current_entry = None
        current_date = None

        for line in content.split("\n"):
            if line.startswith("## "):
                if current_entry and current_date:
                    self.entries.append(current_entry)
                current_date = line.replace("## ", "").strip()
                current_entry = {"date": current_date, "content": []}
            elif line.startswith("# "):
                continue
            elif current_entry is not None and line.strip():
                current_entry["content"].append(line.strip())

        if current_entry and current_date:
            self.entries.append(current_entry)

        self._init_search()

    def _init_search(self):
        texts = [" ".join(e["content"]) for e in self.entries]
        self.tfidf.fit(texts)

        for entry in self.entries:
            text = " ".join(entry["content"])
            entry["vector"] = self.tfidf.get_vector(text)

    def find_related_entries(self, query: str, limit: int = 3) -> list[dict]:
        query_vec = self.tfidf.get_vector(query)

        scored = []
        for entry in self.entries:
            sim = self.tfidf.cosine_similarity(query_vec, entry.get("vector", {}))
            scored.append((sim, entry))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [entry for _, entry in scored[:limit]]

    def suggest(self, current_theme: Optional[str] = None) -> dict:
        if not self.entries:
            return {"status": "no_entries", "message": "请先添加创作日记"}

        latest = self.entries[0]
        latest_text = " ".join(latest["content"])

        related = self.find_related_entries(latest_text)

        return {
            "status": "ok",
            "current_entry": latest,
            "related_entries": related,
            "related_count": len(related),
            "method": "tfidf" if not self._use_embedding else "embedding",
        }


if __name__ == "__main__":
    inspir = Inspir()
    inspir.load()
    result = inspir.suggest()

    print(f"状态: {result['status']}")
    print(f"最新日记: {result['current_entry']['date']}")
    print(f"方法: {result['method']}")
    print(f"相关记录数: {result['related_count']}")
    if result.get("related_entries"):
        print("相关记录:")
        for entry in result["related_entries"]:
            print(f"  - {entry['date']}")
