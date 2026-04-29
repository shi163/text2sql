from openai import OpenAI
from typing import Optional
from config import config


class LLMClient:
    def __init__(self):
        self.client = OpenAI(
            api_key=config.llm.api_key,
            base_url=config.llm.api_base,
        )
        self.model = config.llm.model

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.0,
    ) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=temperature,
            )
            return response.choices[0].message.content.strip()
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
