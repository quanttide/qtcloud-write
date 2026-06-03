import json
from app.services.llm import call_llm
from app.models import GapAnalysis


REFLECT_PROMPT = """你是一个写作诊断专家。以下是对当前文本的意图理解：

体裁：{genre}
意图：{intent}
阶段：{stage}

请检测文本中的写作空隙，给出具体的修改建议。

空隙类型（5 种）：
- time_jump：时间跳跃没有过渡标记
- dialog_gap：对话之间缺少反应或沉默描写
- action_gap：动作之间缺少衔接
- perspective_shift：视角切换缺少锚点
- transition：场景转换缺少桥梁

必须输出 JSON 数组，格式如下（不要额外文字）：
[
  {{
    "gap_id": "gap_001"（唯一标识，递增）,
    "gap_type": "action_gap",
    "location": {{
      "start_char": 12（问题起点的字符偏移）,
      "end_char": 34（问题终点的字符偏移）,
      "text_snippet": "问题所在位置的文本片段"
    }},
    "detail": "问题说明",
    "multi_dimensions": {{
      "structure": "叙事结构角度的归因",
      "psychology": "人物心理角度的归因",
      "reader": "读者期待角度的归因"
    }},
    "craft": "有意识留白 或 无意识忽略",
    "root_cause": "一句话总结根本原因",
    "suggested_fix": "具体的修改示范文本"
  }}
]

文本：
{text}"""


def cmd_reflect(text: str, genre: str = "", intent: str = "", stage: str = "") -> list[dict]:
    prompt = REFLECT_PROMPT.format(genre=genre, intent=intent, stage=stage, text=text)
    raw = call_llm(prompt, system="你是一个写作诊断专家。")
    result = json.loads(raw)
    if isinstance(result, list):
        return result
    if isinstance(result, dict) and "analysis" in result:
        return result["analysis"]
    return []
