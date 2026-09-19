from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from app.models.task import Task


class AgentRunner(ABC):

    @abstractmethod
    def run(
        self,
        task: Task,
        db: Session
    ) -> str:
        """
        Execute a task and return a textual result.
        """
        raise NotImplementedError