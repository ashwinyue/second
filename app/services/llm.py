"""
LLM 服务
"""
import logging
from volcenginesdkarkruntime import Ark
from ..config import get_settings

logger = logging.getLogger(__name__)


class LLMService:
    """LLM 服务"""

    def __init__(self):
        settings = get_settings()
        self.client = Ark(
            base_url="https://ark.cn-beijing.volces.com/api/v3",
            api_key=settings.ark_api_key,
        )

    async def generate(self, prompt: str, system_prompt: str | None = None) -> str:
        """生成文本"""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model="doubao-seed-1-8-251228",
            messages=messages,
            temperature=0.7,
            max_tokens=4000,
        )

        return response.choices[0].message.content

    async def generate_json(self, prompt: str, system_prompt: str | None = None) -> dict:
        """生成 JSON"""
        text = await self.generate(prompt + "\n\n输出 JSON 格式。", system_prompt)

        import json
        import re

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            match = re.search(r'```json\n(.*?)\n```', text, re.DOTALL)
            if match:
                return json.loads(match.group(1))
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if match:
                return json.loads(match.group(0))
            raise ValueError(f"无法解析 JSON: {text[:200]}")


_llm_service: LLMService | None = None


def get_llm_service() -> LLMService:
    """获取 LLM 服务单例"""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service
