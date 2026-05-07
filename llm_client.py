import httpx
from typing import Optional
from config import config


class LLMClient:
    def __init__(self):
        self.api_key = config.llm.api_key
        self.api_base = config.llm.api_base.rstrip('/')
        self.model = config.llm.model
        self.client = httpx.Client(timeout=60.0)

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.0,
    ) -> str:
        try:
            url = f"{self.api_base}/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "temperature": temperature,
            }
            response = self.client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            raise Exception(f"LLM API 调用失败: {str(e)}")

    def generate_sql(self, table_context: str, question: str) -> str:
        from prompts import SYSTEM_PROMPT, GENERATE_SQL_PROMPT

        user_prompt = GENERATE_SQL_PROMPT.format(
            table_context=table_context, question=question
        )
        response = self.generate(SYSTEM_PROMPT, user_prompt)
        return self._extract_sql(response)

    def fix_sql(
        self,
        table_context: str,
        question: str,
        previous_sql: str,
        error_message: str,
    ) -> str:
        from prompts import SYSTEM_PROMPT, FIX_SQL_PROMPT

        user_prompt = FIX_SQL_PROMPT.format(
            table_context=table_context,
            question=question,
            previous_sql=previous_sql,
            error_message=error_message,
        )
        response = self.generate(SYSTEM_PROMPT, user_prompt)
        return self._extract_sql(response)

    def _extract_sql(self, response: str) -> str:
        if "```sql" in response:
            start = response.find("```sql") + 6
            end = response.find("```", start)
            return response[start:end].strip()
        elif "```" in response:
            start = response.find("```") + 3
            end = response.find("```", start)
            return response[start:end].strip()
        return response.strip()
