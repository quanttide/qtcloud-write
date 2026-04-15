import os
import json
from pathlib import Path
from typing import Optional

try:
    import numpy as np
except ImportError:
    np = None

try:
    from openai import OpenAI
except ImportError:
    OpenClient = None


class Embedder:
    def __init__(self):
        self.client = None
        if os.getenv("OPENAI_API_KEY"):
            self.client = OpenClient()

    def get_embedding(self, text: str) -> list[float]:
        if not self.client:
            raise RuntimeError("OPENAI_API_KEY not set")

        resp = self.client.embeddings.create(
            model="text-embedding-3-small", input=text[:8000]
        )
        return resp.data[0].embedding

    def load_embeddings(self, cache_path: Path) -> dict:
        if cache_path.exists():
            with open(cache_path) as f:
                return json.load(f)
        return {}

    def save_embeddings(self, cache_path: Path, embeddings: dict):
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        with open(cache_path, "w") as f:
            json.dump(embeddings, f)


class Inspir:
    def __init__(self, journal_path: str = "sample/archive.md"):
        self.journal_path = Path(journal_path)
        self.cache_path = Path("sample/embeddings.json")
        self.entries = []
        self.embedder = Embedder()

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

        self._load_embeddings()

    def _load_embeddings(self):
        cached = self.embedder.load_embeddings(self.cache_path)
        for entry in self.entries:
            date = entry["date"]
            if date in cached:
                entry["embedding"] = cached[date]
            else:
                text = " ".join(entry["content"])
                try:
                    entry["embedding"] = self.embedder.get_embedding(text)
                except RuntimeError:
                    entry["embedding"] = None

        self._save_embeddings()

    def _save_embeddings(self):
        if np is None:
            return
        cached = {entry["date"]: entry.get("embedding") for entry in self.entries}
        cached = {k: v for k, v in cached.items() if v is not None}
        self.embedder.save_embeddings(self.cache_path, cached)

    def cosine_similarity(self, a: list[float], b: list[float]) -> float:
        if np is None:
            raise ImportError("numpy not installed")
        a = np.array(a)
        b = np.array(b)
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

    def find_related_entries(self, query: str, limit: int = 3) -> list[dict]:
        try:
            query_emb = self.embedder.get_embedding(query)
        except RuntimeError:
            return []

        scored = []
        for entry in self.entries:
            if entry.get("embedding"):
                sim = self.cosine_similarity(query_emb, entry["embedding"])
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
        }


if __name__ == "__main__":
    inspir = Inspir()
    inspir.load()
    result = inspir.suggest()

    print(f"状态: {result['status']}")
    print(f"最新日记: {result['current_entry']['date']}")
    print(f"相关记录数: {result['related_count']}")
    if result.get("related_entries"):
        print("相关记录:")
        for entry in result["related_entries"]:
            print(f"  - {entry['date']}")
