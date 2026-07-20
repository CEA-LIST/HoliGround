from __future__ import annotations

import engine.ontology.relationships as ontology_relationships
from engine.reasoning.context import ReasoningStep, SceneObject, StepContext
from engine.reasoning.operations.base import OperationHandler
from engine.reasoning.operations.helpers import load_scene_object
from engine.utils.utils import get_object_from_dependency_step, relation_parser
from engine.utils.capabilities import Capabilities


class RelateHandler(OperationHandler):
    def matches(self, operation: str) -> bool:
        return operation == 'relate'

    def handle(self, ctx: StepContext) -> ReasoningStep:
        obj_name, relation, id_type, obj_id = relation_parser(ctx.argument)

        if id_type == 'o':
            obj: SceneObject = load_scene_object(ctx, obj_id, obj_name)
            obj.complexity = "2"
            subj = get_object_from_dependency_step(ctx.reasoning_steps[ctx.dependencies[0]])
        else:
            subj: SceneObject = load_scene_object(ctx, obj_id, obj_name)
            subj.complexity = "2"
            obj = get_object_from_dependency_step(ctx.reasoning_steps[ctx.dependencies[0]])
       
        return ReasoningStep(
            operation=ctx.operation,
            argument=ctx.argument,
            atomic_vc=[Capabilities.ObjectLocalization, Capabilities.SpatialRelation if relation in ontology_relationships.spatial_relationships else Capabilities.PhysicalRelation],
            objects=[obj, subj], # Object is the primary object, subject is the secondary object
        )


