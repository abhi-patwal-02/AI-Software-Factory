import json
import os
from typing import Any, Type

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
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

        self.model = os.getenv(
            "OPENROUTER_MODEL",
            "openrouter/free"
        )

        self.llm = ChatOpenAI(
            model=self.model,
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1"
        )

    def generate(
        self,
        system_prompt: str,
        input_context: dict[str, Any],
        response_model: Type[BaseModel] | None = None
    ) -> dict[str, Any]:

        messages = [
            (
                "system",
                system_prompt
            ),
            (
                "user",
                str(input_context)
            )
        ]

        response = self.llm.invoke(
            messages
        )

        raw_response = response.content

        if not raw_response:
            raise ValueError(
                "OpenRouter returned an empty response"
            )

        clean_response = raw_response.strip()

        # Remove Markdown code fences if the model adds them.
        if clean_response.startswith("```"):

            lines = clean_response.splitlines()

            if lines and lines[0].startswith("```"):
                lines = lines[1:]

            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]

            clean_response = "\n".join(lines).strip()

        # Validate JSON when a response model is expected.
        if response_model is not None:

            try:
                json.loads(clean_response)

            except json.JSONDecodeError as exc:

                raise ValueError(
                    "LLM response is not valid JSON"
                ) from exc

        usage = response.usage_metadata or {}

        return {
            "raw_response": clean_response,
            "model": self.model,
            "input_tokens": usage.get(
                "input_tokens"
            ),
            "output_tokens": usage.get(
                "output_tokens"
            )
        }