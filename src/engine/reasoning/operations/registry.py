from __future__ import annotations

from engine.reasoning.operations.base import OperationRegistry
from engine.reasoning.operations.choose import ChooseHandler
from engine.reasoning.operations.comparison import ComparisonHandler
from engine.reasoning.operations.exist import ExistHandler
from engine.reasoning.operations.filter import FilterHandler
from engine.reasoning.operations.logical import LogicalHandler
from engine.reasoning.operations.query import QueryHandler
from engine.reasoning.operations.relate import RelateHandler
from engine.reasoning.operations.select import SelectHandler
from engine.reasoning.operations.verify import VerifyHandler


def create_operation_registry() -> OperationRegistry:
    registry = OperationRegistry()
    registry.register(SelectHandler())
    registry.register(ExistHandler())
    registry.register(ChooseHandler())
    registry.register(VerifyHandler())
    registry.register(FilterHandler())
    registry.register(RelateHandler())
    registry.register(QueryHandler())
    registry.register(LogicalHandler())
    registry.register(ComparisonHandler())
    return registry


