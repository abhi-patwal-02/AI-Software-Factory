from abc import ABC, abstractmethod
from typing import Any, Type

from pydantic import BaseModel


class LLMProvider(ABC):

    @abstractmethod
    def generate(
        self,
        system_prompt: str,
        input_context: dict[str, Any],
        response_model: Type[BaseModel] | None = None
    ) -> dict[str, Any]:
        """
        Generate a structured response from the LLM.
        """
        raise NotImplementedError