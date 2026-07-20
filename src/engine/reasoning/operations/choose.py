from __future__ import annotations

import engine.ontology.concepts as ontology_concepts
import engine.ontology.relationships as ontology_relationships
from engine.reasoning.context import ReasoningStep, SceneObject, StepContext
from engine.reasoning.operations.base import OperationHandler
from engine.reasoning.operations.helpers import load_scene_object
from engine.utils.exceptions import AttributeNotFound
from engine.utils.utils import get_object_from_dependency_step, relation_parser
from engine.utils.capabilities import Capabilities


class ChooseHandler(OperationHandler):
    def matches(self, operation: str) -> bool:
        return 'choose' in operation

    def handle(self, ctx: StepContext) -> ReasoningStep:
        category = ctx.operation.split('choose')[1].strip()

            
        if category in ontology_concepts.comparison_concepts:
            return self._handle_comparison(ctx, ontology_concepts.comparison_concepts[category])
        
        elif category == 'name':
            return self._handle_name_choice(ctx)

        elif category in ontology_concepts.concepts:
            return self._handle_attribute_choice(ctx, ontology_concepts.concepts[category])

        elif category in ontology_concepts.global_concepts:
            return self._handle_global_choice(ctx)

        elif category in ontology_concepts.localization_concepts:
            return self._handle_localization_choice(ctx, category)

        elif category in ontology_concepts.action_concepts:
            return self._handle_action_concepts(ctx, category)

        # if category in ontology_concepts.spatial_relationship_concepts:
        #     return self._handle_spatial_attribute_choice(ctx, ontology_concepts.spatial_relationship_concepts[category])
        
        elif category == 'rel':
            return self._handle_relation_choice(ctx)

        else:
            return self._handle_binary_choice(ctx)

    def _handle_action_concepts(self, ctx: StepContext, category: str) -> ReasoningStep:
        dep_step = ctx.reasoning_steps[ctx.dependencies[0]]
        obj = get_object_from_dependency_step(dep_step)
        
        return ReasoningStep(
            operation=ctx.operation,
            argument=ctx.argument,
            atomic_vc=[Capabilities.ActionRecognition],
            objects=dep_step.objects,
        )

    def _handle_binary_choice(self, ctx: StepContext) -> ReasoningStep:
        c1, c2 = ctx.argument.split('|')
        dep_step = ctx.reasoning_steps[ctx.dependencies[0]]
     
        return ReasoningStep(
            operation=ctx.operation,
            argument=ctx.argument,
            atomic_vc=[],
            objects=dep_step.objects
        )

    def _handle_comparison(self, ctx: StepContext, label: str) -> ReasoningStep:
        dep_step = ctx.reasoning_steps[ctx.dependencies[0]]
        return ReasoningStep(
            operation=ctx.operation,
            argument=ctx.argument,
            atomic_vc=[],
            objects=dep_step.objects
        )

    def _handle_name_choice(self, ctx: StepContext) -> ReasoningStep:
        c1, c2 = ctx.argument.split('|')
        dep_step = ctx.reasoning_steps[ctx.dependencies[0]]

        return ReasoningStep(
            operation=ctx.operation,
            argument=ctx.argument,
            atomic_vc=[],
            objects=dep_step.objects,
        )

    def _handle_attribute_choice(self, ctx: StepContext, attr_label: str) -> ReasoningStep:
        c1, c2 = ctx.argument.split('|')
        dep_step = ctx.reasoning_steps[ctx.dependencies[0]]

        return ReasoningStep(
            operation=ctx.operation,
            argument=ctx.argument,
            atomic_vc=[Capabilities.AttributeRecognition],
            objects=dep_step.objects
        )

    def _handle_global_choice(self, ctx: StepContext) -> ReasoningStep:
        c1, c2 = ctx.argument.split('|')
        dep_step = ctx.reasoning_steps[ctx.dependencies[0]]
        
        return ReasoningStep(
            operation=ctx.operation,
            argument=ctx.argument,
            atomic_vc=[Capabilities.SceneUnderstanding],
            objects=dep_step.objects
        )

    def _handle_localization_choice(self, ctx: StepContext, attr_key: str) -> ReasoningStep:
        c1, c2 = ctx.argument.split('|')
        dep_step = ctx.reasoning_steps[ctx.dependencies[0]]

        return ReasoningStep(
            operation=ctx.operation,
            argument=ctx.argument,
            atomic_vc=[Capabilities.SpatialRecognition],
            objects=dep_step.objects,
        )

    def _handle_relation_choice(self, ctx: StepContext) -> ReasoningStep:
        obj_name, relation, id_type, obj_id = relation_parser(ctx.argument)
        c1, c2 = relation.split('|')

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