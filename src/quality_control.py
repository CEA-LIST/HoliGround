from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

import kenlm
import yaml

from engine.utils.indexer import IndexedJSONL


@dataclass(frozen=True)
class AnnotationConfig:
    """Configuration for a single annotation file and its associated scene graph."""
    file: Path
    scene_graphs: Path
    scene_graphs_key: str
    annotations_key: str = "question_id"


@dataclass(frozen=True)
class QualityControlConfig:
    """Configuration for quality control using kenlm."""
    model_path: Path
    threshold: float
    annotations: Sequence[AnnotationConfig]


def coerce_path(value: str | Path) -> Path:
    """Resolve a path relative to the current working directory (project root)."""
    path = Path(value)
    if path.is_absolute():
        return path
    return path.resolve()


def load_config(config_path: str | Path) -> QualityControlConfig:
    """Load quality control configuration from YAML file."""
    config_file = Path(config_path)
    if not config_file.exists():
        raise FileNotFoundError(f"Config file not found: {config_file}")
    
    data = yaml.safe_load(config_file.read_text(encoding="utf-8")) or {}
    
    model_path = coerce_path(data["model_path"])
    threshold = float(data.get("threshold", 1000.0))
    
    annotations_raw = data["annotations"]
    annotations = []

    # Nested structure: annotations organized by split
    for split_name, split_config in annotations_raw.items():
        
        # Split has dict with scene_graphs and files
        if "scene_graphs" not in split_config:
            raise ValueError(f"Split '{split_name}': 'scene_graphs' is required at split level")
        
        split_scene_graphs = coerce_path(split_config["scene_graphs"])
        split_scene_graphs_key = split_config.get("scene_graphs_key", "image_id")
        split_annotations_key = split_config.get("annotations_key", "question_id")
        files = split_config.get("files", [])
        
        for file_item in files:
            ann_file = coerce_path(file_item)
            annotations.append(
                AnnotationConfig(
                    file=ann_file,
                    scene_graphs=split_scene_graphs,
                    scene_graphs_key=split_scene_graphs_key,
                    annotations_key=split_annotations_key,
                )
            )
    
    return QualityControlConfig(
        model_path=model_path,
        threshold=threshold,
        annotations=tuple(annotations),
    )


def calculate_perplexity(model: kenlm.Model, text: str) -> float:
    """Calculate perplexity score for a given text using kenlm model."""
    if not text or not text.strip():
        return float('inf')
    return model.perplexity(text)


def main(config_path: str | None = None) -> None:
    """
    Check question quality using kenlm and output questions below threshold.
    
    Args:
        config_path: Path to YAML configuration file.
    """
    if config_path is None:
        raise ValueError("config_path is required. Please provide a path to a YAML config file.")
    
    config = load_config(config_path)
    
    # Load kenlm model
    if not config.model_path.exists():
        raise FileNotFoundError(f"KenLM model file not found: {config.model_path}")
    
    print(f"Loading kenlm model from: {config.model_path}")
    model = kenlm.Model(str(config.model_path))
    print(f"Model loaded. Using perplexity threshold: {config.threshold}")
    
    total_poorly_formulated = 0
    total_count = 0

    for idx, ann_config in enumerate(config.annotations):
        print(f"\nProcessing annotation from: {ann_config.file.stem} ({idx+1}/{len(config.annotations)})")
        
        # Load scene graphs for this annotation file
        scene_graphs = IndexedJSONL(
            ann_config.scene_graphs,
            primary_key=ann_config.scene_graphs_key,
        )
        
        # Load annotations
        if not ann_config.file.exists():
            print(f"  Warning: Annotation file not found: {ann_config.file}, skipping...")
            continue
        
        annotations = IndexedJSONL(
            ann_config.file,
            primary_key=ann_config.annotations_key,
        )

        # Main control loop
    
        poorly_formulated_count = 0
        file_total_count = 0

        for qid, annotation in annotations.items():
            question = annotation['question']
            file_total_count += 1
            total_count += 1
            
            perplexity = calculate_perplexity(model, question)
            
            if perplexity > config.threshold:
                print(f"  {qid}: {question} (perplexity: {perplexity:.2f})")
                poorly_formulated_count += 1
                total_poorly_formulated += 1
        
        print(f"  → {poorly_formulated_count}/{file_total_count} questions below threshold in this file")
    
    print(f"\n{'='*60}")
    print(f"Summary: {total_poorly_formulated}/{total_count} questions below threshold (perplexity > {config.threshold})")
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check question quality using kenlm")
    parser.add_argument(
        "--config",
        type=str,
        default="configs/quality/default.yaml",
        help="Path to YAML configuration file"
    )
    args = parser.parse_args()
    
    main(config_path=args.config)
