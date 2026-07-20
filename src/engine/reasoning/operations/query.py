from __future__ import annotations

import engine.ontology.concepts as ontology_concepts
from engine.reasoning.context import ReasoningStep, StepContext
from engine.reasoning.operations.base import OperationHandler
from engine.utils.exceptions import StopQuestionProcessing
from engine.utils.utils import get_object_from_dependency_step
from engine.utils.capabilities import Capabilities


class QueryHandler(OperationHandler):
    def matches(self, operation: str) -> bool:
        return operation == 'query'

    def handle(self, ctx: StepContext) -> ReasoningStep:
        if ctx.argument in ontology_concepts.localization_concepts:
            return self._handle_localization(ctx)
        if ctx.argument in ontology_concepts.concepts:
            return self._handle_concepts(ctx)
        if ctx.argument in ontology_concepts.action_concepts:
            return self._handle_action_concepts(ctx)
        if ctx.argument in ontology_concepts.global_concepts:
            return self._handle_global(ctx)
        if ctx.argument == 'name':
            return self._handle_name(ctx)

        raise StopQuestionProcessing(f"query{ctx.argument}") 

    def _handle_action_concepts(self, ctx: StepContext) -> ReasoningStep:
        dep_step = ctx.reasoning_steps[ctx.dependencies[0]]

        return ReasoningStep(
            operation=ctx.operation,
            argument=ctx.argument,
            atomic_vc=[],
            objects=dep_step.objects,
        )

    def _handle_name(self, ctx: StepContext) -> ReasoningStep:
        dep_step = ctx.reasoning_steps[ctx.dependencies[0]]

        return ReasoningStep(
            operation=ctx.operation,
            argument=ctx.argument,
            atomic_vc=[],
            objects=dep_step.objects,
        )

    
    def _handle_global(self, ctx: StepContext) -> ReasoningStep:
        dep_step = ctx.reasoning_steps[ctx.dependencies[0]]

        return ReasoningStep(
            operation=ctx.operation,
            argument=ctx.argument,
            atomic_vc=[Capabilities.SceneUnderstanding],
            objects=dep_step.objects,
        )

    def _handle_concepts(self, ctx: StepContext) -> ReasoningStep:
        dep_step = ctx.reasoning_steps[ctx.dependencies[0]]

        return ReasoningStep(
            operation=ctx.operation,
            argument=ctx.argument,
            atomic_vc=[Capabilities.AttributeRecognition],
            objects=dep_step.objects,
        )

    def _handle_localization(self, ctx: StepContext) -> ReasoningStep:
        dep_step = ctx.reasoning_steps[ctx.dependencies[0]] 

        return ReasoningStep(
            operation=ctx.operation,
            argument=ctx.argument,
            atomic_vc=[Capabilities.SpatialRecognition],
            objects=dep_step.objects,
        )