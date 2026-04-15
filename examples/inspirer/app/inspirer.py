from datetime import datetime
from pathlib import Path
from typing import Optional


class Inspir:
    def __init__(self, journal_path: str = "sample/journal.md"):
        self.journal_path = Path(journal_path)
        self.entries = []

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

    def extract_themes(self, content: str) -> list[str]:
        keywords = []
        if "创作" in content or "写" in content:
            keywords.append("创作")
        if "灵感" in content:
            keywords.append("灵感")
        if "男女" in content or "男主" in content or "女主" in content:
            keywords.append("人物")
        if "情绪" in content or "心情" in content:
            keywords.append("情绪")
        if "重写" in content:
            keywords.append("重写")
        return keywords

    def find_related_entries(self, theme: str, limit: int = 3) -> list[dict]:
        related = []
        for entry in self.entries:
            themes = self.extract_themes(" ".join(entry["content"]))
            if theme in themes:
                related.append(entry)
            if len(related) >= limit:
                break
        return related

    def suggest(self, current_theme: Optional[str] = None) -> dict:
        if not self.entries:
            return {"status": "no_entries", "message": "请先添加创作日记"}

        latest = self.entries[0]
        themes = self.extract_themes(" ".join(latest["content"]))

        if current_theme:
            target_theme = current_theme
        else:
            target_theme = themes[0] if themes else "创作"

        related = self.find_related_entries(target_theme)

        return {
            "status": "ok",
            "current_entry": latest,
            "detected_themes": themes,
            "related_entries": related,
            "suggestion": self.generate_suggestion(target_theme, related),
        }

    def generate_suggestion(self, theme: str, related: list[dict]) -> str:
        if not related:
            return f"最近没有关于「{theme}」的记录，建议开始记录相关灵感"

        messages = {
            "创作": "可以参考过去的创作状态，调整当前创作节奏",
            "灵感": "这些片段可能触发新的灵感火花",
            "人物": "可以进一步发展这些人物关系",
            "情绪": "这种情绪状态值得在作品中表达",
            "重写": "这是一个重写旧作的好时机",
        }
        return messages.get(theme, f"可以继续探索「{theme}」相关的主题")


if __name__ == "__main__":
    inspir = Inspir()
    inspir.load()
    result = inspir.suggest()

    print(f"状态: {result['status']}")
    print(f"最新日记: {result['current_entry']['date']}")
    print(f"检测到主题: {result['detected_themes']}")
    print(f"建议: {result['suggestion']}")
    print(f"相关记录数: {len(result['related_entries'])}")
