"""
Inter-annotator agreement and comparison for the HUMAN gold standard.

    # agreement between two independent annotators
    python experiments/annotation_agreement.py data/annotation/gold_blind_A.csv data/annotation/gold_blind_B.csv

    # compare adjudicated human labels with the LLM-generated gold
    python experiments/annotation_agreement.py data/annotation/gold_adjudicated.csv data/gold_standard_v3.csv \
        --col-b gold_segmentation

Reports exact-match agreement over all words and Cohen's kappa over
inter-character boundary decisions (surface slots, see eval_metrics.canonical_to_surface).
Words whose canonical form cannot be mapped to the surface (reduplication, hidden
affixes) count for exact agreement only; their number is reported.

This script only MEASURES agreement. Filling in labels is human work.
"""
import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))

from eval_metrics import boundaries, canonical_to_surface  # noqa: E402


def boundary_slots(word: str, canonical: str) -> Optional[List[int]]:
    segs = canonical_to_surface(word, canonical)
    if segs is None:
        return None
    n = len("".join(segs))
    b = boundaries(segs)
    return [1 if i in b else 0 for i in range(1, n)]


def cohen_kappa_binary(a: List[int], b: List[int]) -> float:
    n = len(a)
    po = sum(x == y for x, y in zip(a, b)) / n
    pa, pb = sum(a) / n, sum(b) / n
    pe = pa * pb + (1 - pa) * (1 - pb)
    if pe == 1.0:
        return 1.0 if po == 1.0 else 0.0
    return (po - pe) / (1 - pe)


def agreement(a: Dict[str, str], b: Dict[str, str]) -> Dict:
    words = [w for w in a if w in b and a[w].strip() and b[w].strip()]
    exact = [a[w].strip() == b[w].strip() for w in words]
    slots_a, slots_b, kappa_words = [], [], 0
    for w in words:
        sa, sb = boundary_slots(w, a[w].strip()), boundary_slots(w, b[w].strip())
        if sa is not None and sb is not None and len(sa) == len(sb):
            slots_a.extend(sa)
            slots_b.extend(sb)
            kappa_words += 1
    return {
        "n_words": len(words),
        "exact_agreement": sum(exact) / len(words) if words else 0.0,
        "boundary_kappa": cohen_kappa_binary(slots_a, slots_b) if slots_a else None,
        "boundary_kappa_words": kappa_words,
        "boundary_slots": len(slots_a),
        "disagreements": [{"word": w, "a": a[w].strip(), "b": b[w].strip()}
                          for w, e in zip(words, exact) if not e],
    }


def read(path: str, col: str) -> Dict[str, str]:
    with open(path, encoding="utf-8") as f:
        return {r["word"]: (r.get(col) or "") for r in csv.DictReader(f)}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("file_a")
    p.add_argument("file_b")
    p.add_argument("--col-a", default="annotator_segmentation")
    p.add_argument("--col-b", default="annotator_segmentation")
    p.add_argument("-o", "--output")
    args = p.parse_args()
    rep = agreement(read(args.file_a, args.col_a), read(args.file_b, args.col_b))
    text = json.dumps(rep, indent=2, ensure_ascii=False)
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
    summary = {k: v for k, v in rep.items() if k != "disagreements"}
    summary["n_disagreements"] = len(rep["disagreements"])
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
