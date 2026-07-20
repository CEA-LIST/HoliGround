# HoliGround: Holistic Assessment for Grounded Chain-of-Thought

[**Paper**](https://openaccess.thecvf.com/content/CVPR2026W/MAR/papers/Hodemon_HoliGround_Holistic_Assessment_for_Grounded_Chain-of-Thought_CVPRW_2026_paper.pdf) | [**Dataset**](https://huggingface.co/datasets/tomhodemon/HoliGround)

## Abstract

Grounded Chain-of-Thought (GCoT) has emerged as a promising approach to promote the use of Multimodal Large Language Models (MLLMs) in critical applications by bringing interpretability and mitigating visual hallucinations. However, the faithfulness of these intermediate rationales is rarely assessed, as current evaluation protocols focus almost exclusively on final answer accuracy. This divergence can translate into real harm if users over-trust unfaithful rationales. Thus, we must establish evaluation protocols that move beyond simple accuracy to provide stronger empirical validation of a model's faithfulness, ensuring it is correct for the right reasons. To bridge this critical gap, we introduce HoliGround, a comprehensive benchmark designed to evaluate GCoT-capable models beyond their final predictions. We propose a novel, low-constraint metric that aggregates three fundamental dimensions: Logic Quality, which assesses the relevance and ordinal consistency of the reasoning sequence; Complexity Awareness, which weights evaluation based on step-level visual task difficulty; and Holistic Assessment, which integrates intermediate grounding fidelity with final answer correctness. Furthermore, we develop a deterministic, rule-based synthesis pipeline to construct HoliGround, offering a highly cost-effective and scalable method for generating GCoT annotations. By releasing both the benchmark and our synthesis framework, HoliGround establishes a new standard for rigorously validating the underlying reasoning of multimodal models.




## Benchmark Construction

The following steps reproduce the exact benchmark as synthesized from the GQA balanced validation split (`val_balanced`). The benchmark is produced in two steps.

### Data

Images and annotations are sourced from **GQA**, a large-scale visual reasoning dataset.  
Download the required files from: https://cs.stanford.edu/people/dorarad/gqa/download.html

You need:
- `val_sceneGraphs.jsonl` — scene graphs with per-image object bounding boxes and attributes
- `val_balanced_questions.jsonl` — balanced validation questions with structured semantic programs

Place them under `data/gqa/` following the paths in `configs/val.yaml`.

### Step 1 — Generate annotations

The engine processes each GQA question by executing its semantic program against the scene graph. For every reasoning step (select, filter, relate, query, etc.) it identifies which objects are involved, normalizes their bounding boxes, assigns vision capabilities (e.g. `ObjectLocalization`, `AttributeRecognition`, `SpatialRelation`), and computes a per-question complexity score. All annotated questions are written to `output/val_balanced/annotations.jsonl`.

```bash
uv run src/main.py --config configs/val.yaml
```

### Step 2 — Filter to the benchmark subset

The actual benchmark (`complex.jsonl`) is a randomly sampled subset of questions with complexity scores in the range **5–8** (default: 500 questions). This filters out trivial single-step questions and retains those requiring multi-object, multi-capability reasoning.

```bash
python scripts/filter.py
```

Output: `output/val_balanced/complex.jsonl`

---

## Evaluation

Evaluation runs in four sequential stages against `complex.jsonl`.

### 1. Query a VLM

Send each question and its image to a vision-language model via the OpenRouter API. Responses are saved to `evals/out/raw/`.

```bash
OPENROUTER_API_KEY=<key> python evals/main.py
```

### 2. Parse model output

Extract the model's final answer and the bounding boxes it grounded from the raw text responses.

```bash
python evals/parse.py
```

### 3. Match predictions to ground truth

Semantically match predicted objects and answers to ground-truth annotations, computing IoU for each bounding box pair.

```bash
python evals/match.py
```

### 4. Compute HoliGround Score

Aggregate grounding quality and answer accuracy into the HGS metric.

```bash
python evals/score.py
```

---

## Extending the Benchmark

The pipeline is fully compatible with the GQA annotation format. Any GQA split or question file can be used as input by pointing `configs/val.yaml` to the relevant scene graph and question files. This makes it straightforward to extend the benchmark — for example by running the engine on the GQA training split or other question subsets — and produce additional annotated benchmarks following the same structure.

## Citation

```bibtex
@InProceedings{Hodemon_2026_CVPR,
    author    = {Hodemon, Tom and Chaouch, Mohamed and Tuo, Aboubacar and Loesch, Angelique},
    title     = {HoliGround: Holistic Assessment for Grounded Chain-of-Thought},
    booktitle = {Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR) Workshops},
    month     = {June},
    year      = {2026},
    pages     = {11516-11522}
}
```
