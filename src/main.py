from __future__ import annotations

import argparse

from engine.config import load_config, save_config
from engine.processors.question import QuestionProcessor
from engine.reasoning.context import Config
from engine.reasoning.operations.registry import create_operation_registry
from engine.services.jsonl_writer import JsonlWriter
from engine.utils.indexer import IndexedJSONL


def main(config_path: str | None = None) -> None:
    print(f"Loading config from {config_path}")
    settings = load_config(config_path)

    settings.output.root.mkdir(parents=True, exist_ok=True)
    save_config(settings, settings.output.root / "config.yaml")

    scene_graphs = IndexedJSONL(
        settings.data.scene_graphs,
        primary_key=settings.data.scene_graphs_key,
    )

    config = Config(
        normalize_bbox=settings.normalize_bbox,
        round_to_decimal_places=settings.round_to_decimal_places,
    )
    registry = create_operation_registry()

    total_processed = 0
    total_skipped = 0
    all_error_categories: dict[str, int] = {}
    all_ops_not_supported: dict[str, int] = {}

    # Process each question file separately
    for idx, question_file in enumerate(settings.data.questions):
        print(f"\nProcessing questions from: {question_file.stem} ({idx+1}/{len(settings.data.questions)})")
        questions = IndexedJSONL(
            question_file,
            primary_key=settings.data.questions_key,
        )

        # Derive output annotation file name from question file name
        annotation_file = settings.output.root / "annotations.jsonl"

        writer = JsonlWriter(annotation_file)
        processor = QuestionProcessor(
            scene_graphs=scene_graphs,
            questions=questions,
            registry=registry,
            config=config,
        )

        for record in processor.run():
            writer.write(record)

        writer.close()

        total_processed += len(questions)
        total_skipped += processor.skipped

        # Merge error categories
        for error, count in processor.error_categories.items():
            all_error_categories[error] = all_error_categories.get(error, 0) + count

        # Merge unsupported operations
        for op, count in processor.ops_not_supported.items():
            all_ops_not_supported[op] = all_ops_not_supported.get(op, 0) + count

        print(f"  → Wrote {total_processed - total_skipped} annotations to {annotation_file}")

    _print_stats(total_skipped, total_processed, all_error_categories, all_ops_not_supported)


def _print_stats(
    total_skipped: int,
    total_questions: int,
    error_categories: dict[str, int],
    ops_not_supported: dict[str, int],
) -> None:
    skipped_pct = (total_skipped / total_questions) * 100 if total_questions else 0
    print(f"\n{'='*60}")
    print(f"Total questions processed: {total_questions}")
    print(f"Total questions skipped due to errors: {total_skipped} ({skipped_pct:.2f}%)")
    if error_categories:
        print("Error categories:")
        for error, count in error_categories.items():
            print(f"\t{error}: {count}")

    total_ops_not_supported = sum(ops_not_supported.values())
    if total_ops_not_supported > 0:
        print(f"Operations not supported: (total: {total_ops_not_supported})")
        for op, count in ops_not_supported.items():
            percentage = (count / total_ops_not_supported * 100) if total_ops_not_supported else 0
            print(f"\t{op}: {count} ({percentage:.2f}%)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        help="Path to a JSON config file defining data/output paths and runtime flags.",
        default="configs/default.yaml",
    )
    args = parser.parse_args()
    main(args.config)
