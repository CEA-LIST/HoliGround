from __future__ import annotations

from engine.reasoning.context import ReasoningStep, StepContext
from engine.reasoning.operations.base import OperationHandler
from engine.utils.exceptions import LogicalOperationNotSupported
from engine.utils.utils import get_object_from_dependency_step
from engine.utils.capabilities import Capabilities


class LogicalHandler(OperationHandler):
    def matches(self, operation: str) -> bool:
        return operation in ('and', 'or')

    def handle(self, ctx: StepContext) -> ReasoningStep:
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

    def _handle_and(self, ctx, dep_step1, dep_step2, obj1, obj2, op_dep1, op_dep2):
        if op_dep1 == 'exist' and op_dep2 == 'exist':
            rationale = ctx.template_store.render(
                'logical.and.exist.base',
                object1=obj1.name_in_question,
                object2=obj2.name_in_question,
            )
            if dep_step1.intermediate_answer and dep_step2.intermediate_answer:
                rationale += ctx.template_store.render(
                    'logical.and.exist.both',
                    object1=obj1.name_in_question,
                    object2=obj2.name_in_question,
                )
            elif not dep_step1.intermediate_answer and dep_step2.intermediate_answer:
                rationale += ctx.template_store.render(
                    'logical.and.exist.first_missing',
                    object1=obj1.name_in_question,
                    object2=obj2.name_in_question,
                )
            elif dep_step1.intermediate_answer and not dep_step2.intermediate_answer:
                rationale += ctx.template_store.render(
                    'logical.and.exist.second_missing',
                    object1=obj1.name_in_question,
                    object2=obj2.name_in_question,
                )
            else:
                rationale += ctx.template_store.render(
                    'logical.and.exist.both_missing',
                    object1=obj1.name_in_question,
                    object2=obj2.name_in_question,
                )
            return rationale

        if 'verify' in op_dep1 and 'verify' in op_dep2:
            attr1, attr2 = dep_step1.argument, dep_step2.argument
            rationale = ctx.template_store.render(
                'logical.and.verify.base',
                object=obj1.name_in_question,
                attr1=attr1,
                attr2=attr2,
            )
            if dep_step1.intermediate_answer and dep_step2.intermediate_answer:
                rationale += ctx.template_store.render(
                    'logical.and.verify.both',
                    object=obj1.name_in_question,
                    attr1=attr1,
                    attr2=attr2,
                )
            elif not dep_step1.intermediate_answer and dep_step2.intermediate_answer:
                rationale += ctx.template_store.render(
                    'logical.and.verify.first_missing',
                    object=obj1.name_in_question,
                    attr1=attr1,
                    attr2=attr2,
                )
            elif dep_step1.intermediate_answer and not dep_step2.intermediate_answer:
                rationale += ctx.template_store.render(
                    'logical.and.verify.second_missing',
                    object=obj1.name_in_question,
                    attr1=attr1,
                    attr2=attr2,
                )
            else:
                rationale += ctx.template_store.render(
                    'logical.and.verify.both_missing',
                    object=obj1.name_in_question,
                    attr1=attr1,
                    attr2=attr2,
                )
            return rationale

        raise LogicalOperationNotSupported(ctx.operation)

    def _handle_or(self, ctx, dep_step1, dep_step2, obj1, obj2, op_dep1, op_dep2):
        if op_dep1 == 'exist' and op_dep2 == 'exist':
            rationale = ctx.template_store.render(
                'logical.or.exist.base',
                object1=obj1.name_in_question,
                object2=obj2.name_in_question,
            )
            if dep_step1.intermediate_answer and dep_step2.intermediate_answer:
                rationale += ctx.template_store.render(
                    'logical.or.exist.both',
                    object1=obj1.name_in_question,
                    object2=obj2.name_in_question,
                )
            elif dep_step1.intermediate_answer:
                rationale += ctx.template_store.render(
                    'logical.or.exist.first_present',
                    object1=obj1.name_in_question,
                    object2=obj2.name_in_question,
                )
            elif dep_step2.intermediate_answer:
                rationale += ctx.template_store.render(
                    'logical.or.exist.second_present',
                    object1=obj1.name_in_question,
                    object2=obj2.name_in_question,
                )
            else:
                rationale += ctx.template_store.render(
                    'logical.or.exist.both_missing',
                    object1=obj1.name_in_question,
                    object2=obj2.name_in_question,
                )
            return rationale

        if 'verify' in op_dep1 and 'verify' in op_dep2:
            rationale = ctx.template_store.render(
                'logical.or.verify.base',
                object1=obj1.name_in_question,
                object2=obj2.name_in_question,
                attribute1=dep_step1.argument,
                attribute2=dep_step2.argument,
            )
            if dep_step1.intermediate_answer and dep_step2.intermediate_answer:
                rationale += ctx.template_store.render(
                    'logical.or.verify.both',
                    object1=obj1.name_in_question,
                    object2=obj2.name_in_question,
                    attribute1=dep_step1.argument,
                )
            elif dep_step1.intermediate_answer:
                rationale += ctx.template_store.render(
                    'logical.or.verify.first_present',
                    object1=obj1.name_in_question,
                    object2=obj2.name_in_question,
                    attribute1=dep_step1.argument,
                )
            elif dep_step2.intermediate_answer:
                rationale += ctx.template_store.render(
                    'logical.or.verify.second_present',
                    object1=obj1.name_in_question,
                    object2=obj2.name_in_question,
                    attribute2=dep_step2.argument,
                )
            else:
                rationale += ctx.template_store.render(
                    'logical.or.verify.both_missing',
                    object1=obj1.name_in_question,
                    object2=obj2.name_in_question,
                    attribute1=dep_step1.argument,
                )
            return rationale

        raise LogicalOperationNotSupported(ctx.operation)


