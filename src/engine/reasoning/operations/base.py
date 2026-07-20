from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from engine.reasoning.context import ReasoningStep, StepContext
from engine.utils.exceptions import OperationNotSupported


class OperationHandler(ABC):
    """Interface for all operation handlers."""

    @abstractmethod
    def matches(self, operation: str) -> bool:
        """Return True if the handler supports the given operation string."""

    @abstractmethod
    def handle(self, ctx: StepContext) -> ReasoningStep:
        """Build a reasoning step for the provided context."""


class OperationRegistry:
    """Registry that maps operations to handlers."""

    def __init__(self) -> None:
        self._handlers: List[OperationHandler] = []

    def register(self, handler: OperationHandler) -> None:
        self._handlers.append(handler)

    def resolve(self, operation: str) -> OperationHandler:
        for handler in self._handlers:
            if handler.matches(operation):
                return handler
        raise OperationNotSupported(operation)


