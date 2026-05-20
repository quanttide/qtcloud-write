from quanttide_agent import LLM

from app.config import get_settings
from app.models import Article, Comparison

_client = None


def _get_client() -> LLM:
    global _client
    if _client is None:
        settings = get_settings()
        _client = LLM(
            model="deepseek-chat",
            base_url=settings.llm_base_url,
            api_key=settings.llm_api_key,
        )
    return _client


def analyze_paragraph(paragraph: str, position: int, total: int, article_tag: str) -> dict:
    settings = get_settings()
    if not settings.llm_api_key:
        raise ValueError("llm_api_key 未配置，请在 .env 中设置 DeepSeek API Key")

    prompt = _build_analyze_prompt(paragraph, position, total, article_tag)
    response = _get_client().chat(
        [
            {"role": "system", "content": "你是一个专业的叙事结构分析助手。请根据用户输入的段落，分析其叙事功能。"},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
    )
    return _parse_analyze_response(response.content, paragraph)


def compare_with_style(paragraph: str, tag: str, style_examples: list[Article]) -> Comparison | None:
    if not style_examples:
        return None

    settings = get_settings()
    if not settings.llm_api_key:
        return None

    prompt = _build_compare_prompt(paragraph, tag, style_examples)
    response = _get_client().chat(
        [
            {"role": "system", "content": "你是一个专业的写作风格评审专家。请对比分析给定段落与风格范例的差异。"},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
    )
    return _parse_compare_response(response.content)
