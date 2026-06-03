from app.services.llm import call_llm


REWRITE_PROMPT = """当前文本的定位：
体裁：{genre}
意图：{intent}

对文本中空隙的诊断：
{analysis}

请带着以上理解重新修改文章。注意：
- 如果空隙被判定为"有意识留白"，不需要修改
- 如果空隙被判定为"无意识忽略"，针对性地补写
- 保持原文的风格和节奏

输出格式：直接输出修改后的完整文章。

原文：
{text}"""


def cmd_rewrite(text: str, genre: str = "", intent: str = "", analysis: list[dict] | None = None) -> str:
    if not analysis:
        return text
    analysis_text = "\n".join(
        f"{i+1}. [{a['gap_type']}] {a.get('detail', '')}\n"
        f"   叙事结构: {a.get('structure', '')}\n"
        f"   人物心理: {a.get('psychology', '')}\n"
        f"   读者期待: {a.get('reader', '')}\n"
        f"   写作技法: {a.get('craft', '')}\n"
        f"   根本原因: {a.get('root_cause', '')}"
        for i, a in enumerate(analysis)
    )
    prompt = REWRITE_PROMPT.format(genre=genre, intent=intent, analysis=analysis_text, text=text)
    return call_llm(prompt, system="你是一个写作改写助手。")
