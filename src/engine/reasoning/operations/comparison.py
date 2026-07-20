from __future__ import annotations

from engine.reasoning.context import ReasoningStep, StepContext
from engine.reasoning.operations.base import OperationHandler
from engine.utils.exceptions import OperationNotSupported
from engine.utils.utils import get_object_from_dependency_step


class ComparisonHandler(OperationHandler):
    OPS = ["different", "same", "common", "same color", "same material", "same shape", "different color", "different material", "different shape"]

    def matches(self, operation: str) -> bool:
        return operation in self.OPS

    def handle(self, ctx: StepContext) -> ReasoningStep:
        parts = ctx.operation.split(' ')
        if len(parts) == 2:
            operation, attr_key = parts
        else:
            operation = ctx.operation
            attr_key = ctx.argument

        if operation == "different":
            if attr_key in ["type", "gender"]:
                raise OperationNotSupported(f"Invalid argument: {ctx.argument}")
            return self._handle_different(ctx, attr_key)
        if operation == "same":
            if attr_key in ["type", "gender"]:
                raise OperationNotSupported(f"Invalid argument: {ctx.argument}")
            return self._handle_same(ctx, attr_key)
        if operation == "common":
            return self._handle_common(ctx)

        raise OperationNotSupported(ctx.operation)

    def _handle_different(self, ctx, attr_key):
        dep_step1 = ctx.reasoning_steps[ctx.dependencies[0]]
        dep_step2 = ctx.reasoning_steps[ctx.dependencies[1]]
        obj1 = get_object_from_dependency_step(dep_step1)
        obj2 = get_object_from_dependency_step(dep_step2)

        return ReasoningStep(
            operation=ctx.operation,
            argument=ctx.argument,
            atomic_vc=[],
            objects=[obj1, obj2],
        )

    def _handle_same(self, ctx, attr_key):
        dep_step1 = ctx.reasoning_steps[ctx.dependencies[0]]
        dep_step2 = ctx.reasoning_steps[ctx.dependencies[1]]
        obj1 = get_object_from_dependency_step(dep_step1)
        obj2 = get_object_from_dependency_step(dep_step2)

        return ReasoningStep(
            operation=ctx.operation,
            argument=ctx.argument,
            atomic_vc=[],
            objects=[obj1, obj2],
        )
   
    def _handle_common(self, ctx):
        dep_step1 = ctx.reasoning_steps[ctx.dependencies[0]]
        dep_step2 = ctx.reasoning_steps[ctx.dependencies[1]]
        obj1 = get_object_from_dependency_step(dep_step1)
        obj2 = get_object_from_dependency_step(dep_step2)

        return ReasoningStep(
            operation=ctx.operation,
            argument=ctx.argument,
            atomic_vc=[],
            objects=[obj1, obj2],
        )