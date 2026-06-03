import json
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


def _check_api_key():
    settings = get_settings()
    if not settings.llm_api_key:
        raise ValueError("请配置 LLM_API_KEY 或 DEEPSEEK_API_KEY 环境变量，或在 .env 文件中填入")


def call_llm(prompt: str, system: str = "", temperature: float = 0.3) -> str:
    """Simple LLM call — for 3R commands (reflect/rewrite)."""
    _check_api_key()
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    try:
        response = _get_client().complete(messages, temperature=temperature)
        return response.content
    except Exception as e:
        raise RuntimeError(f"LLM 调用失败: {e}") from e


def analyze_paragraph(paragraph: str, position: int, total: int, article_tag: str) -> dict:
    settings = get_settings()
    if not settings.llm_api_key:
        raise ValueError("llm_api_key 未配置，请在 .env 中设置 DeepSeek API Key")

    prompt = _build_analyze_prompt(paragraph, position, total, article_tag)
    response = _get_client().complete(
        [
            {"role": "system", "content": "你是一个专业的叙事结构分析助手。请根据用户输入的段落，分析其叙事功能。"},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
        response_format={"type": "json_object"},
    )
    return _parse_analyze_response(response.content, paragraph)


def compare_with_style(paragraph: str, tag: str, style_examples: list[Article]) -> Comparison | None:
    if not style_examples:
        return None

    settings = get_settings()
    if not settings.llm_api_key:
        return None

    prompt = _build_compare_prompt(paragraph, tag, style_examples)
    response = _get_client().complete(
        [
            {"role": "system", "content": "你是一个专业的写作风格评审专家。请对比分析给定段落与风格范例的差异。"},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
        response_format={"type": "json_object"},
    )
    return _parse_compare_response(response.content)


def _build_analyze_prompt(paragraph: str, position: int, total: int, article_tag: str) -> str:
    return f"""请分析以下段落的叙事功能。

段落原文：{paragraph}

段落位置：第 {position + 1} 段 / 共 {total} 段
文章类型：{article_tag}

请返回 JSON，格式如下：
{{
  "analysis": "对该段落叙事功能的详细分析",
  "tag": "起" 或 "承" 或 "转" 或 "合"
}}

tag 含义：
- 起：开篇引入，交代背景、场景、人物
- 承：承接发展，推进情节、展开论述
- 转：转折变化，引入冲突、矛盾、新视角
- 合：收束总结，得出结论、点明主题"""


def _parse_analyze_response(response_content: str, paragraph: str) -> dict:
    try:
        data = json.loads(response_content)
    except json.JSONDecodeError:
        data = {}
    return {
        "original": paragraph,
        "analysis": data.get("analysis", ""),
        "tag": data.get("tag", "承") if data.get("tag") in ("起", "承", "转", "合") else "承",
    }


def _build_compare_prompt(paragraph: str, tag: str, style_examples: list[Article]) -> str:
    style_text = "\n\n".join(
        f"范例文章 {i + 1}：《a.title》\n" + "\n".join(a.paragraphs)
        for i, a in enumerate(style_examples)
    )
    return f"""请对比下列段落与风格范例，判断其写作风格是否一致。

待评估段落（{tag}）：{paragraph}

风格范例：
{style_text}

请返回 JSON，格式如下：
{{
  "type": "good" 或 "bad" 或 "pass",
  "issue": "如果 type 为 bad，说明问题所在",
  "demo": "如果 type 为 bad，示范好的写法"
}}

判断依据：
- good：风格与范例一致，叙事手法成熟
- bad：风格与范例差异显著，存在明显问题
- pass：无法判断或风格中立"""


def _parse_compare_response(response_content: str) -> Comparison | None:
    try:
        data = json.loads(response_content)
    except json.JSONDecodeError:
        return None
    ctype = data.get("type")
    if ctype not in ("good", "bad", "pass"):
        return None
    return Comparison(
        type=ctype,
        issue=data.get("issue"),
        demo=data.get("demo"),
    )
