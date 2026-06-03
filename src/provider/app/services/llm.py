from quanttide_agent import LLM

from app.config import get_settings


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
        raise ValueError("请配置 LLM_API_KEY 或 DEEPSEEK_API_KEY 环境变量")


def call_llm(prompt: str, system: str = "", temperature: float = 0.3) -> str:
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
