import json
from app.services.llm import call_llm
from app.models import Change


REWRITE_PROMPT = """当前文本的定位：
体裁：{genre}
意图：{intent}

需要修复的空隙（已排除有意留白）：
{analysis}

针对每个空隙，请按以下格式输出修改：
{{
  "text": "修改后的完整文章",
  "changes": [
    {{
      "gap_id": "gap_001",
      "original_snippet": "原文中被替换的部分",
      "replaced_with": "替换后的文本"
    }}
  ]
}}

注意：
- 只修改上面列出的空隙，不改变其他部分
- 保持原文的风格和节奏
- 每个 change 的 original_snippet 必须在原文中能找到

原文：
{text}"""


def cmd_rewrite(
    text: str,
    genre: str = "",
    intent: str = "",
    analysis: list[dict] | None = None,
    gaps_to_fix: list[str] | None = None,
) -> tuple[str, list[Change], list[str]]:
    unfixed = []

    if not analysis:
        return text, [], []

    # 过滤要修复的空隙
    if gaps_to_fix is not None:
        to_fix = [a for a in analysis if a.get("gap_id") in gaps_to_fix]
        unfixed = [a.get("gap_id", "") for a in analysis if a.get("gap_id") not in gaps_to_fix and a["gap_id"]]
    else:
        to_fix = [a for a in analysis if a.get("craft") != "有意识留白"]
        unfixed = [a.get("gap_id", "") for a in analysis if a.get("craft") == "有意识留白"]

    if not to_fix:
        return text, [], unfixed

    analysis_text = "\n".join(
        f"- [{a.get('gap_id', '?')}] {a.get('gap_type', '?')}: {a.get('detail', '')}\n"
        f"  修改建议: {a.get('suggested_fix', '')}"
        for a in to_fix
    )

    prompt = REWRITE_PROMPT.format(genre=genre, intent=intent, analysis=analysis_text, text=text)
    raw = call_llm(prompt, system="你是一个写作改写助手。")

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        data = {"text": raw, "changes": []}

    changes = []
    for c in data.get("changes", []):
        changes.append(Change(
            gap_id=c.get("gap_id", ""),
            original_snippet=c.get("original_snippet", ""),
            replaced_with=c.get("replaced_with", ""),
        ))

    return data.get("text", text), changes, unfixed
