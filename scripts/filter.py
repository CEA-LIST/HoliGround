#!/usr/bin/env python3
"""Filter questions by complexity 5–8 and randomly sample a subset for a mix of complexity levels."""

import json
import random
from pathlib import Path

MIN_COMPLEXITY = 5
MAX_COMPLEXITY = 8


def load_jsonl(file_path: Path):
    """Load all records from a JSONL file."""
    records = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))
    return records


def filter_by_complexity(input_file: Path, output_file: Path, n: int):
    """Keep only samples with complexity in [MIN_COMPLEXITY, MAX_COMPLEXITY], then randomly select n."""
    print(f"Loading data from {input_file}...")
    records = load_jsonl(input_file)
    print(f"Loaded {len(records)} records")
    
    # Keep only complexity 5–8
    filtered = [
        r for r in records
        if MIN_COMPLEXITY <= r.get('question_complexity', 0) <= MAX_COMPLEXITY
    ]
    print(f"Samples with complexity {MIN_COMPLEXITY}–{MAX_COMPLEXITY}: {len(filtered)}")
    
    # Randomly select n for a mix of complexity levels
    k = min(n, len(filtered))
    selected = random.sample(filtered, k)
    print(f"Randomly selected {len(selected)} questions")
    
    if selected:
        complexities = [r.get('question_complexity', 0) for r in selected]
        print(f"Complexity range in subset: {min(complexities)} – {max(complexities)}")
    
    # Write to output file
    print(f"Writing to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        for record in selected:
            f.write(json.dumps(record) + '\n')
    
    print(f"Done! Created subset with {len(selected)} questions")


def main():
    N = 500  # Number of questions to select
    input_file = Path("output/val_balanced/annotations.jsonl")
    output_file = Path("output/val_balanced/complex.jsonl")
    
    if not input_file.exists():
        print(f"Error: Input file not found: {input_file}")
        return
    
    filter_by_complexity(input_file, output_file, N)


if __name__ == '__main__':
    main()

