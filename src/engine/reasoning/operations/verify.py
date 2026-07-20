from __future__ import annotations


import engine.ontology.concepts as ontology_concepts
import engine.ontology.relationships as ontology_relationships

from engine.reasoning.context import ReasoningStep, SceneObject, StepContext
from engine.reasoning.operations.base import OperationHandler
from engine.reasoning.operations.helpers import load_scene_object
from engine.utils.utils import get_object_from_dependency_step, relation_parser
from engine.utils.capabilities import Capabilities


class VerifyHandler(OperationHandler):
    def matches(self, operation: str) -> bool:
        return 'verify' in operation

    def handle(self, ctx: StepContext) -> ReasoningStep:
        category = ctx.operation.split('verify')[1].strip()

        
        if category in ontology_concepts.global_concepts:
            return self._handle_global_concepts(ctx)

        elif category in ontology_concepts.concepts:
            return self._handle_conepts(ctx, category, ontology_concepts.concepts[category])

        elif category in ontology_concepts.localization_concepts:
            return self._handle_localization_concepts(ctx, category)

        elif category in ontology_concepts.action_concepts:
            return self._handle_action_concepts(ctx, category)

        elif category == 'rel':
            return self._handle_relation(ctx)

        else:
            return self._handle_others(ctx)

    def _handle_others(self, ctx: StepContext) -> ReasoningStep:
        dep_step = ctx.reasoning_steps[ctx.dependencies[0]]
        
        return ReasoningStep(
            operation=ctx.operation,
            argument=ctx.argument,
            atomic_vc=[],
            objects=dep_step.objects,
        )

    def _handle_action_concepts(self, ctx: StepContext, category: str) -> ReasoningStep:
        dep_step = ctx.reasoning_steps[ctx.dependencies[0]]
        
        return ReasoningStep(
            operation=ctx.operation,
            argument=ctx.argument,
            atomic_vc=[Capabilities.ActionRecognition],
            objects=dep_step.objects,
        )

    def _handle_global_concepts(self, ctx: StepContext) -> ReasoningStep:
        dep_step = ctx.reasoning_steps[ctx.dependencies[0]]
      
        return ReasoningStep(
            operation=ctx.operation,
            argument=ctx.argument,
            atomic_vc=[Capabilities.SceneUnderstanding],
            objects=dep_step.objects,
        )

    def _handle_conepts(self, ctx: StepContext, attr_key: str, attr_label: str) -> ReasoningStep:
        dep_step = ctx.reasoning_steps[ctx.dependencies[0]]
      
        return ReasoningStep(
            operation=ctx.operation,
            argument=ctx.argument,
            atomic_vc=[Capabilities.AttributeRecognition],
            objects=dep_step.objects,
        )

    def _handle_localization_concepts(self, ctx: StepContext, attr_key: str) -> ReasoningStep:
        dep_step = ctx.reasoning_steps[ctx.dependencies[0]]
      
        return ReasoningStep(
            operation=ctx.operation,
            argument=ctx.argument,
            atomic_vc=[Capabilities.SpatialRecognition],
            objects=dep_step.objects,
        )

    def _handle_relation(self, ctx: StepContext) -> ReasoningStep:
        obj_name, relation, id_type, obj_id = relation_parser(ctx.argument)

        if id_type == 'o':
            obj: SceneObject = load_scene_object(ctx, obj_id, obj_name)
            obj.complexity = "2"
            subj = get_object_from_dependency_step(ctx.reasoning_steps[ctx.dependencies[0]])
        else:
            subj: SceneObject = load_scene_object(ctx, obj_id, obj_name)
            subj. complexity = "2"
            obj = get_object_from_dependency_step(ctx.reasoning_steps[ctx.dependencies[0]])

        return ReasoningStep(
            operation=ctx.operation,
            argument=ctx.argument,
            atomic_vc=[Capabilities.SpatialRelation if relation in ontology_relationships.spatial_relationships else Capabilities.PhysicalRelation],
            objects=[obj, subj],
        )