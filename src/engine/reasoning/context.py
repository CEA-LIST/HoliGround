from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence

from engine.utils.capabilities import Capabilities


@dataclass(frozen=True)
class Config:
    """Runtime flags that control normalization and formatting behavior."""

    normalize_bbox: bool = True
    round_to_decimal_places: int = 2

@dataclass
class SceneObject:
    """Represents an object referenced in a reasoning step."""

    id: Optional[str]
    name: Optional[str]
    name_in_question: str
    bbox: Optional[Sequence[float]]
    category: Optional[str]
    complexity: Optional[str]

    def exists(self) -> bool:
        """Whether the scene object is grounded in the scene graph."""
        return self.id is not None

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the object for JSON output."""
        return {
            'id': self.id,
            'name': self.name,
            'name_in_question': self.name_in_question,
            'bbox': list(self.bbox) if self.bbox is not None else None,
            'complexity': self.complexity
        }

    def template_repr(self) -> str:
        return f"{self.name_in_question}"


@dataclass
class ReasoningStep:
    """Normalized structure for each reasoning step the engine produces."""

    operation: str
    argument: str
    atomic_vc: List[Capabilities]
    objects: List[SceneObject] = field(default_factory=list) # Object is the primary object, subject is the secondary object
    
    skip: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            'capabilities': [repr(vc) for vc in self.atomic_vc],
            'objects': [obj.to_dict() for obj in self.objects if obj.id != "-1"],
        }


@dataclass
class StepContext:
    """
    Shared context passed to every operation handler.

    Attributes:
        question_data: Raw question payload (includes semantics, answer, etc.).
        dependencies: List of indices referencing previously computed steps.
        scene_graph: Scene graph entry for the current question/image.
        config: Global configuration toggles.
        annotations: Mutable dict storing per-question derived data (objects, stats).
        reasoning_steps: All steps built so far (allows handlers to inspect deps).
    """

    question_data: Dict[str, Any]
    operation: str
    argument: str
    dependencies: Sequence[int]
    scene_graph: Dict[str, Any]
    config: Config
    annotations: Dict[str, Any]
    reasoning_steps: List[ReasoningStep]