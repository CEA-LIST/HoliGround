from __future__ import annotations

from engine.reasoning.context import ReasoningStep, SceneObject, StepContext
from engine.reasoning.operations.base import OperationHandler
from engine.reasoning.operations.helpers import load_scene_object
from engine.utils.exceptions import OperationNotSupported
from engine.utils.utils import get_dummy_object, select_parser
from engine.utils.capabilities import Capabilities


class SelectHandler(OperationHandler):
    def matches(self, operation: str) -> bool:
        return operation == 'select'

    def handle(self, ctx: StepContext) -> ReasoningStep:
        obj_name, obj_id = select_parser(ctx.argument)
        
        if len(obj_id.split(',')) != 1: # Special case: multiple object ids
            raise OperationNotSupported(f"Invalid argument: {ctx.argument}")
        else:
            obj = load_scene_object(ctx, obj_id, obj_name)
      
        return ReasoningStep(
            operation=ctx.operation,
            argument=ctx.argument,
            atomic_vc=[Capabilities.ObjectLocalization],
            objects=[obj],
        )


