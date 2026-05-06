from openai import OpenAI
from app.config import get_settings
from app.models import Article, Comparison

_client = None


def _get_client() -> OpenAI:
    """懒加载 OpenAI 客户端"""
    global _client
    if _client is None:
        settings = get_settings()
        _client = OpenAI(
            api_key=settings.llm_api_key,
            base_url=settings.llm_base_url,
        )
    return _client


def analyze_paragraph(paragraph: str, position: int, total: int, article_tag: str) -> dict:
    """
    用 DeepSeek 分析单个段落，返回标签和分析结果。
    """
    settings = get_settings()
    if not settings.llm_api_key:
        raise ValueError("llm_api_key 未配置，请在 .env 中设置 DeepSeek API Key")

    prompt = _build_analyze_prompt(paragraph, position, total, article_tag)
    response = _get_client().chat.completions.create(
        model="deepseek-chat",
        messages=[
            {
                "role": "system",
                "content": "你是一个专业的叙事结构分析助手。请根据用户输入的段落，分析其叙事功能。"
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3,
    )
    content = response.choices[0].message.content
    return _parse_analyze_response(content, paragraph)


def compare_with_style(paragraph: str, tag: str, style_examples: list[Article]) -> Comparison | None:
    """
    用 DeepSeek 对比段落与风格库，返回对比结果。
    """
    if not style_examples:
        return None

    settings = get_settings()
    if not settings.llm_api_key:
        return None

    prompt = _build_compare_prompt(paragraph, tag, style_examples)
    response = _get_client().chat.completions.create(
        model="deepseek-chat",
        messages=[
            {
                "role": "system",
                "content": "你是一个专业的写作风格评审专家。请对比分析给定段落与风格范例的差异。"
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3,
    )
    content = response.choices[0].message.content
    return _parse_compare_response(content)


def _build_analyze_prompt(paragraph: str, position: int, total: int, article_tag: str) -> str:
    if position == 0:
        position_hint = "开头段落"
    elif position == 1:
        position_hint = "第二段"
    elif position == total - 1:
        position_hint = "结尾段落"
    elif position == total - 2:
        position_hint = "倒数第二段"
    else:
        position_hint = f"第{position + 1}段（共{total}段）"

    return f"""分析以下段落：

段落内容：{paragraph}
段落位置：{position_hint}

请以 JSON 格式返回分析结果：
{{
    "tag": "起"|"承"|"转"|"合"  // 叙事结构标签
    "analysis": "一段简洁的分析说明"  // 20字以内的分析
}}

规则：
- "起"：个人困境驱动，而非外部热点
- "承"：承接上文，认知转折或深化
- "转"：视角转换或论域推入深层
- "合"：认知闭环，不以CTA收束

只返回 JSON，不要有其他内容。"""


def _build_compare_prompt(paragraph: str, tag: str, style_examples: list[Article]) -> str:
    examples_text = "\n\n".join([
        f"范例{i+1}（{a.title}）：\n" + "\n".join(a.paragraphs)
        for i, a in enumerate(style_examples)
    ])

    return f"""对比分析以下段落与风格范例的差异：

待分析段落：{paragraph}
段落标签：{tag}

风格范例：
{examples_text}

请以 JSON 格式返回对比结果：
{{
    "type": "pass"|"bad"  // pass=符合风格，bad=不符合风格
    "issue": "如果不符合，具体问题是什么"  // 如无问题则不返回
    "demo": "改进建议"  // 如有问题则返回
}}

只返回 JSON，不要有其他内容。"""


def _parse_analyze_response(content: str, original: str) -> dict:
    import json
    import re

    match = re.search(r"```(?:json)?\s*([\s\S]*?)```", content)
    if match:
        text = match.group(1)
    else:
        text = content.strip()

    try:
        data = json.loads(text)
        return {
            "tag": data.get("tag", ""),
            "analysis": data.get("analysis", ""),
            "original": original,
        }
    except json.JSONDecodeError:
        return {
            "tag": "",
            "analysis": f"解析失败: {content[:50]}",
            "original": original,
        }


def _parse_compare_response(content: str) -> Comparison | None:
    import json
    import re

    match = re.search(r"```(?:json)?\s*([\s\S]*?)```", content)
    if match:
        text = match.group(1)
    else:
        text = content.strip()

    try:
        data = json.loads(text)
        return Comparison(
            type=data.get("type", "pass"),
            issue=data.get("issue"),
            demo=data.get("demo"),
        )
    except json.JSONDecodeError:
        return Comparison(type="pass")
