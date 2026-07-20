from __future__ import annotations

from dataclasses import asdict, dataclass, is_dataclass
from pathlib import Path
from typing import Any, Iterable, Sequence

import yaml


@dataclass(frozen=True)
class DataPaths:
    scene_graphs: Path
    scene_graphs_key: str
    questions: Sequence[Path]
    questions_key: str


@dataclass(frozen=True)
class OutputPaths:
    annotations_dir: Path

    @property
    def root(self) -> Path:
        return self.annotations_dir


@dataclass(frozen=True)
class EngineConfig:
    data: DataPaths
    output: OutputPaths
    normalize_bbox: bool
    round_to_decimal_places: int

def _coerce_path(value: str | Path) -> Path:
    """Resolve a path relative to the current working directory (project root)."""
    path = Path(value)
    if path.is_absolute():
        return path
    return path.resolve()


def load_config(config_path: str | Path) -> EngineConfig:
    config_file = Path(config_path)
    data = yaml.safe_load(config_file.read_text(encoding="utf-8")) or {}

    data_section = data["data"]
    scene_graphs = _coerce_path(data_section["scene_graphs"])
    scene_graphs_key = data_section["scene_graphs_key"]
    questions_raw = data_section["questions"]
    if isinstance(questions_raw, list):
        questions = tuple(_coerce_path(p) for p in questions_raw)
    else:
        # Single item: wrap in tuple
        questions = (_coerce_path(questions_raw),)
    questions_key = data_section["questions_key"]

    data_paths = DataPaths(
        scene_graphs=scene_graphs,
        scene_graphs_key=scene_graphs_key,
        questions=questions,
        questions_key=questions_key,
    )

    output_section = data["output"]
    annotations_dir = _coerce_path(output_section["annotations"])

    output_paths = OutputPaths(annotations_dir=annotations_dir)

    normalize_bbox = data["normalize_bbox"]
    round_to_decimal_places = data["round_to_decimal_places"]
    
    return EngineConfig(
        data=data_paths,
        output=output_paths,
        normalize_bbox=normalize_bbox,
        round_to_decimal_places=round_to_decimal_places,
    )


def _convert_to_dict(obj: Any) -> Any:
    """Recursively convert dataclass instances and Path objects to dict/str."""
    if isinstance(obj, Path):
        # Convert Path to string, keeping relative paths as-is
        return str(obj)
    elif is_dataclass(obj):
        # It's a dataclass instance
        result = {}
        for key, value in asdict(obj).items():
            result[key] = _convert_to_dict(value)
        return result
    elif isinstance(obj, (list, tuple)):
        return [_convert_to_dict(item) for item in obj]
    elif isinstance(obj, set):
        return list(_convert_to_dict(item) for item in obj)
    elif isinstance(obj, dict):
        return {k: _convert_to_dict(v) for k, v in obj.items()}
    else:
        return obj


def config_to_dict(config: EngineConfig) -> dict[str, Any]:
    """Convert an EngineConfig instance to a dictionary suitable for YAML serialization."""
    return _convert_to_dict(config)


def save_config(config: EngineConfig, output_path: str | Path) -> None:
    """Save an EngineConfig instance to a YAML file."""
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    config_dict = config_to_dict(config)
    
    with output_file.open("w", encoding="utf-8") as f:
        yaml.dump(config_dict, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

