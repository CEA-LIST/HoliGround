from __future__ import annotations

import engine.ontology.concepts as ontology_concepts
from engine.reasoning.context import ReasoningStep, StepContext
from engine.reasoning.operations.base import OperationHandler
from engine.utils.exceptions import AttributeNotFound, OperationNotSupported
from engine.utils.utils import get_object_from_dependency_step
from engine.utils.capabilities import Capabilities


class FilterHandler(OperationHandler):
    def matches(self, operation: str) -> bool:
        return 'filter' in operation

    def handle(self, ctx: StepContext) -> ReasoningStep:
        category = ctx.operation.split('filter')[1].strip()            

        if category in ontology_concepts.action_concepts:
            return self._handle_action_concepts(ctx)

        elif category in ontology_concepts.localization_concepts:
            return self._handle_localization_concepts(ctx, category)   

        elif category in ontology_concepts.concepts:
            return self._handle_concepts(ctx, category) 
                
        else:
            return self._handle_others(ctx)  

    def _handle_others(self, ctx: StepContext) -> ReasoningStep:
        dep_step = ctx.reasoning_steps[ctx.dependencies[0]]

        if dep_step.operation == 'select':
            dep_step.skip = True

        for obj in dep_step.objects:
            obj.complexity = "2"

        return ReasoningStep(
            operation="filter other",
            argument=ctx.argument,
            atomic_vc=[Capabilities.ObjectLocalization, Capabilities.AttributeRecognition],
            objects=dep_step.objects,
        )

    def _handle_action_concepts(self, ctx: StepContext) -> ReasoningStep:
        dep_step = ctx.reasoning_steps[ctx.dependencies[0]]

        if dep_step.operation == 'select':
            dep_step.skip = True

        for obj in dep_step.objects:
            obj.complexity = "2"

        return ReasoningStep(
            operation="filter action",
            argument=ctx.argument,
            atomic_vc=[Capabilities.ObjectLocalization, Capabilities.ActionRecognition],
            objects=dep_step.objects,
        )

    def _handle_concepts(self, ctx: StepContext, attr_key: str) -> ReasoningStep:
        dep_step = ctx.reasoning_steps[ctx.dependencies[0]]
       
        if dep_step.operation == 'select':
            dep_step.skip = True

        for obj in dep_step.objects:
            obj.complexity = "2"

        return ReasoningStep(
            operation="filter concepts",
            argument=ctx.argument,
            atomic_vc=[Capabilities.ObjectLocalization, Capabilities.AttributeRecognition],
            objects=dep_step.objects,
        )

    def _handle_localization_concepts(self, ctx: StepContext, attr_key: str) -> ReasoningStep:
        dep_step = ctx.reasoning_steps[ctx.dependencies[0]]

        if dep_step.operation == 'select':
            dep_step.skip = True

        for obj in dep_step.objects:
            obj.complexity = "2"
            
        return ReasoningStep(
            operation=f"filter localization",
            argument=ctx.argument,
            atomic_vc=[Capabilities.ObjectLocalization, Capabilities.SpatialRecognition],
            objects=dep_step.objects,
        )