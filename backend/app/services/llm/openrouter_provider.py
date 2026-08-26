import os
from typing import Any, Type

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel

from app.services.llm.base import LLMProvider

load_dotenv()



class OpenRouterProvider(LLMProvider):

    def __init__(self):
        api_key = os.getenv("OPENROUTER_API_KEY")

        if not api_key:
            raise ValueError(
                "OPENROUTER_API_KEY is not configured"
            )

        self.client = OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1"
        )

        self.model = os.getenv(
            "OPENROUTER_MODEL",
            "openrouter/free"
        )

    def generate(
        self,
        system_prompt: str,
        input_context: dict[str, Any],
        response_model: Type[BaseModel]
    ) -> dict[str, Any]:

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": str(input_context)
                }
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": response_model.__name__,
                    "strict": True,
                    "schema": response_model.model_json_schema()
                }
            }
        )

        choice = response.choices[0]

        return {
            "raw_response": choice.message.content,
            "model": response.model,
            "input_tokens": (
                response.usage.prompt_tokens
                if response.usage
                else None
            ),
            "output_tokens": (
                response.usage.completion_tokens
                if response.usage
                else None
            )
        }