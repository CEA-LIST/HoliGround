from __future__ import annotations

from engine.reasoning.context import ReasoningStep, StepContext
from engine.reasoning.operations.base import OperationHandler
from engine.utils.utils import get_object_from_dependency_step


class ExistHandler(OperationHandler):
    def matches(self, operation: str) -> bool:
        return operation == 'exist'

    def handle(self, ctx: StepContext) -> ReasoningStep:
        dep_step = ctx.reasoning_steps[ctx.dependencies[0]]

        return ReasoningStep(
            operation=ctx.operation,
            argument=ctx.argument,
            atomic_vc=[],
            objects=dep_step.objects,
            skip=True,
        )


