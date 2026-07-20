from __future__ import annotations

from re import L
import traceback
from typing import Any, Dict, Iterable, List

from tqdm import tqdm

from engine.reasoning.context import Config, ReasoningStep, StepContext
from engine.reasoning.operations.base import OperationRegistry
from engine.utils.exceptions import OperationNotSupported, StopQuestionProcessing
from engine.utils.indexer import IndexedJSONL
from engine.utils.utils import get_answer_complexity


class QuestionProcessor:
    """Iterates through questions and delegates reasoning steps to handlers."""

    def __init__(
        self,
        scene_graphs: IndexedJSONL,
        questions: IndexedJSONL,
        registry: OperationRegistry,
        config: Config,
    ) -> None:
        self.scene_graphs = scene_graphs
        self.questions = questions
        self.registry = registry
        self.config = config

        self.skipped = 0
        self.error_categories: Dict[str, int] = {}
        self.ops_not_supported: Dict[str, int] = {}

    def run(self) -> Iterable[Dict[str, Any]]:
        """Process all questions."""
        for question_id, data in tqdm(self.questions.items(), total=len(self.questions)):
            reasoning_steps: list[ReasoningStep] = []
            try:
                annotations, reasoning_steps = self._process_question(question_id, data, reasoning_steps)
                record = self._build_record(annotations, reasoning_steps)
                yield record
                
            except Exception as exc:  # pylint: disable=broad-except
                self._record_exception(exc, data)

    def _process_question(self, question_id, data, reasoning_steps):
        image_id = data.get('imageId')
        scene_graph = self.scene_graphs.get(image_id)
        annotations = {
            'width': scene_graph.get('width'),
            'height': scene_graph.get('height'),
            'question_id': question_id,
            'image_id': image_id,
            'question': data["question"],
            'answer': data['answer'],
            "answer_complexity": get_answer_complexity(data['types']["structural"])
        }

        for idx, raw_step in enumerate(data['semantic']):
            operation = raw_step['operation']
            argument = raw_step['argument'].strip()
            dependencies = raw_step['dependencies']

            ctx = StepContext(
                question_data=data,
                operation=operation,
                argument=argument,
                dependencies=dependencies,
                scene_graph=scene_graph,
                config=self.config,
                annotations=annotations,
                reasoning_steps=reasoning_steps,
            )

            handler = self._resolve_handler(operation)
            try:
                reasoning_step = handler.handle(ctx)
    
            except StopQuestionProcessing:
                break
                        
            reasoning_steps.append(reasoning_step)

        reasoning_steps = self._skip_steps(reasoning_steps)
        return annotations, reasoning_steps

    def _skip_steps(self, reasoning_steps: List[ReasoningStep]) -> List[ReasoningStep]:
        return [step for step in reasoning_steps if not step.skip]

    def _resolve_handler(self, operation: str):
        try:
            return self.registry.resolve(operation)
        except OperationNotSupported:
            self.ops_not_supported[operation] = self.ops_not_supported.get(operation, 0) + 1
            raise

    def _record_exception(self, exc: Exception, data: Dict[str, Any]) -> None:
        err_name = type(exc).__name__
        self.error_categories[err_name] = self.error_categories.get(err_name, 0) + 1
        self.skipped += 1
        
        # if err_name == 'OperationNotSupported':
        #     pass
        # else:
        #     print(err_name, exc)
        #     print(data.get('semanticStr'), data.get('answer'), data.get('question_id'))
            
        #     print(traceback.format_exc())

        # print(err_name, exc, data.get('semanticStr'), data.get('imageId'), data.get('question_id'))
        # print(traceback.format_exc())


    def _build_record(self, annotations: Dict[str, Any], reasoning_steps) -> Dict[str, Any]:
        record = dict(annotations)

        # get all unique objects, keep logical order
        all_objects = []
        for step in reasoning_steps: 
            step_dict = step.to_dict()
            all_objects.extend(step_dict["objects"])
        
    
        unique_objs = list({obj["id"]: obj for obj in all_objects}.values())
    
        record["unique_objs"] = unique_objs
       
        record["question_complexity"] = int(record["answer_complexity"]) + sum(int(obj["complexity"]) for obj in unique_objs)
        return record