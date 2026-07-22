from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, TypeVar

T = TypeVar("T")

class BaseCommand(ABC, Generic[T]):
    """
    Abstract Base Class for all system commands.
    All business logic must inherit from this class.
    """

    @abstractmethod
    def execute(self, **kwargs) -> T:
        """
        Executes the command logic.
        
        Args:
            **kwargs: Arguments required for the command execution.
            
        Returns:
            The result of the command execution.
        """
        pass

    def validate(self, **kwargs) -> bool:
        """
        Optional method to validate inputs before execution.
        """
        return True
