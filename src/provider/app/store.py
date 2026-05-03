from app.models import Article


class StyleStore:
    """In-memory style accumulation."""

    def __init__(self):
        self._good_articles: list[Article] = []

    def add_good(self, article: Article):
        self._good_articles.append(article)

    @property
    def is_available(self) -> bool:
        return len(self._good_articles) > 0

    @property
    def good_articles(self) -> list[Article]:
        return list(self._good_articles)

    @property
    def count(self) -> int:
        return len(self._good_articles)


style_store = StyleStore()
