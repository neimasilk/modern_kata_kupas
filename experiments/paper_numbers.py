"""
Single source of truth for every number quoted in the paper (revision Sep 2026).

    python experiments/paper_numbers.py

Writes:
    experiments/results/paper_numbers.json          all numbers
    experiments/results/paper_predictions.csv       per-word predictions (gold eval)

Sections:
    gold        provenance/duplicate statistics of data/gold_standard_v3.csv
    intrinsic   MKK vs gold (canonical): word accuracy + bootstrap CI, multiset
                morpheme P/R/F1, stem/prefix/suffix accuracy, per-category
    boundary    MKK vs Morfessor vs no-split on SURFACE morpheme boundaries
                (fair comparison; Morfessor trained on running text, not on
                the root list and not on the test words)
    wikipedia   segmentation rate and root-based OOV on data/wikipedia_id_sample.txt

NOTE: the gold standard is LLM-generated and LLM-adjudicated (no human
validation yet). All intrinsic numbers are provisional until the human
annotation in data/annotation/ is completed.
"""
import csv
import json
import random
import re
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))

from modern_kata_kupas import ModernKataKupas  # noqa: E402
from eval_metrics import (  # noqa: E402
    boundaries, boundary_prf, bootstrap_ci, canonical_to_surface,
    mcnemar_exact, morpheme_prf,
)
from evaluate import MorphologicalEvaluator  # noqa: E402

GOLD = ROOT / "data" / "gold_standard_v3.csv"
WIKI = ROOT / "data" / "wikipedia_id_sample.txt"
SMSA_TRAIN = ROOT / "experiments" / "data" / "smsa_cache" / "train_preprocess.tsv"
OUT_JSON = ROOT / "experiments" / "results" / "paper_numbers.json"
OUT_PRED = ROOT / "experiments" / "results" / "paper_predictions.csv"

WORD_RE = re.compile(r"\b[a-z]+(?:-[a-z]+)*\b")
N_BOOT = 10000
SEED = 0


def load_gold():
    with open(GOLD, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    seen, unique = set(), []
    for r in rows:
        if r["word"] not in seen:
            seen.add(r["word"])
            unique.append(r)
    return rows, unique


def gold_stats(rows, unique):
    return {
        "file": str(GOLD.relative_to(ROOT)),
        "rows": len(rows),
        "unique_words": len(unique),
        "duplicate_rows": len(rows) - len(unique),
        "generated_by": dict(Counter(r["generated_by"] for r in rows)),
        "validated_flag": dict(Counter(r["validated"] for r in rows)),
        "human_validated": 0,
        "categories": len({r["category"] for r in rows}),
        "note": "validated=True comes from DeepSeek adjudication that was shown the system prediction "
                "(experiments/expand_gold_standard.py); no human validation.",
    }


def intrinsic(mkk, unique):
    words = [r["word"] for r in unique]
    gold = [r["gold_segmentation"] for r in unique]
    t0 = time.time()
    pred = [mkk.segment(w) for w in words]
    elapsed = time.time() - t0
    correct = [p == g for p, g in zip(pred, gold)]

    ev = MorphologicalEvaluator(mkk)
    m = ev.evaluate_dataset(unique, show_progress=False)

    per_cat = defaultdict(list)
    for r, c in zip(unique, correct):
        per_cat[r["category"]].append(c)
    categories = {}
    for cat, cs in sorted(per_cat.items()):
        ci = bootstrap_ci(cs, n_boot=N_BOOT, seed=SEED)
        categories[cat] = {"n": len(cs), "correct": int(sum(cs)), "accuracy": ci["mean"],
                           "ci_lower": ci["ci_lower"], "ci_upper": ci["ci_upper"]}

    no_split_correct = [w == g for w, g in zip(words, gold)]
    return pred, correct, {
        "n": len(words),
        "correct": int(sum(correct)),
        "word_accuracy": bootstrap_ci(correct, n_boot=N_BOOT, seed=SEED),
        "morpheme_prf_multiset": morpheme_prf(pred, gold),
        "stem_accuracy": m.stem_accuracy,
        "prefix_accuracy": m.prefix_accuracy,
        "suffix_accuracy": m.suffix_accuracy,
        "unsegmented_predictions": sum(p == w for p, w in zip(pred, words)),
        "words_per_second": len(words) / elapsed if elapsed else None,
        "no_split_baseline_accuracy": float(np.mean(no_split_correct)),
        "mcnemar_vs_no_split": mcnemar_exact(correct, no_split_correct),
        "per_category": categories,
        "note": "Cohen's kappa is NOT reported: computed over segmentation strings as categories, "
                "chance agreement is ~0 so kappa ~= accuracy and carries no extra information.",
    }


# --- Morfessor ------------------------------------------------------------------

def corpus_tokens():
    tokens = WORD_RE.findall(WIKI.read_text(encoding="utf-8").lower())
    with open(SMSA_TRAIN, encoding="utf-8") as f:
        for line in f:
            text = line.rsplit("\t", 1)[0]
            tokens.extend(WORD_RE.findall(text.lower()))
    parts = []
    for t in tokens:
        parts.extend(p for p in t.split("-") if len(p) >= 2)
    return parts


def train_morfessor(tokens, type_based):
    import morfessor
    random.seed(SEED)
    counts = Counter(tokens)
    model = morfessor.BaselineModel()
    modifier = (lambda x: 1) if type_based else None
    model.load_data([(c, w) for w, c in counts.items()], count_modifier=modifier)
    model.train_batch()
    return model


def morfessor_segment(model, word):
    segs = []
    for part in word.lower().split("-"):
        if part:
            segs.extend(model.viterbi_segment(part)[0])
    return segs


def boundary_eval(unique, mkk_pred):
    items = []
    for r, p in zip(unique, mkk_pred):
        g = canonical_to_surface(r["word"], r["gold_segmentation"])
        if g is not None:
            items.append((r, g, p))
    excluded = len(unique) - len(items)

    tokens = corpus_tokens()
    counts = Counter(tokens)
    gold_words = {r["word"].replace("-", "") for r in unique}
    corpus_info = {
        "sources": [str(WIKI.relative_to(ROOT)), str(SMSA_TRAIN.relative_to(ROOT)) + " (text column)"],
        "tokens": len(tokens),
        "types": len(counts),
        "gold_words_occurring_in_corpus": len(gold_words & set(counts)),
        "note": "Morfessor Baseline, default parameters, random.seed(0); test words NOT added to training.",
    }

    mkk_surface, mkk_fallback = [], 0
    for r, g, p in items:
        s = canonical_to_surface(r["word"], p)
        if s is None:
            mkk_fallback += 1
            s = [r["word"].lower().replace("-", "")]
        mkk_surface.append(s)
    gold_surface = [g for _, g, _ in items]

    systems = {"mkk": mkk_surface, "no_split": [[r["word"].lower().replace("-", "")] for r, _, _ in items]}
    for name, type_based in [("morfessor_tokens", False), ("morfessor_types", True)]:
        model = train_morfessor(tokens, type_based)
        systems[name] = [morfessor_segment(model, r["word"]) for r, _, _ in items]

    def exact(segs):
        return [boundaries(s) == boundaries(g) for s, g in zip(segs, gold_surface)]

    rng = np.random.default_rng(SEED)
    idx = rng.integers(0, len(items), size=(2000, len(items)))

    def f1_ci(segs):
        f1s = []
        for row in idx:
            f1s.append(boundary_prf([segs[i] for i in row], [gold_surface[i] for i in row])["f1"])
        return float(np.quantile(f1s, 0.025)), float(np.quantile(f1s, 0.975))

    results = {}
    for name, segs in systems.items():
        prf = boundary_prf(segs, gold_surface)
        lo, hi = f1_ci(segs)
        ex = exact(segs)
        results[name] = {**prf, "f1_ci_lower": lo, "f1_ci_upper": hi,
                         "boundary_exact_match": float(np.mean(ex)),
                         "avg_segments": float(np.mean([len(s) for s in segs]))}
    mkk_ex = exact(systems["mkk"])
    for name in ("morfessor_tokens", "morfessor_types", "no_split"):
        results[name]["mcnemar_exact_match_vs_mkk"] = mcnemar_exact(mkk_ex, exact(systems[name]))

    # Robustness: the nasal/luluh convention may favour MKK, so also report the
    # subset without meN-/peN- where the surface boundary is unambiguous.
    keep = [i for i, (r, _, _) in enumerate(items)
            if not {"meN", "peN"} & set(r["gold_segmentation"].split("~"))]
    subset = {"n": len(keep)}
    for name in ("mkk", "morfessor_tokens", "morfessor_types"):
        segs = systems[name]
        subset[name] = boundary_prf([segs[i] for i in keep], [gold_surface[i] for i in keep])
    results["subset_without_nasal_prefix"] = subset

    samples = [{"word": r["word"], "gold_surface": "|".join(g), "mkk": "|".join(systems["mkk"][i]),
                "morfessor_types": "|".join(systems["morfessor_types"][i])}
               for i, (r, g, _) in enumerate(items[:15])]
    return {
        "n_evaluated": len(items),
        "n_excluded_unmappable_gold": excluded,
        "mkk_predictions_unmappable_fallback_to_no_split": mkk_fallback,
        "convention": "meN-/peN- nasal belongs to prefix; elided k/p/t/s root keeps remainder "
                      "(menulis -> men|ulis). Reduplication items excluded.",
        "training_corpus": corpus_info,
        "systems": results,
        "samples": samples,
    }


# --- Wikipedia --------------------------------------------------------------------

AFFIXES = {"meN", "ber", "ter", "di", "peN", "per", "ke", "se", "kan", "i", "an", "lah", "kah",
           "pun", "tah", "nya", "ku", "mu", "ulg", "rp"}


def wikipedia(mkk):
    text = WIKI.read_text(encoding="utf-8")
    tokens = [t for t in WORD_RE.findall(text.lower()) if len(t) >= 2]
    unique = sorted(set(tokens))
    segmented, root_oov, word_oov = 0, 0, 0
    for w in unique:
        s = mkk.segment(w)
        if s != w:
            segmented += 1
        roots = [m for m in s.split("~") if m and m not in AFFIXES and not m.startswith("rs(")]
        root = roots[0] if roots else s
        if not (mkk.dictionary.is_kata_dasar(root) or mkk.dictionary.is_loanword(root)):
            root_oov += 1
        if not mkk.dictionary.is_kata_dasar(w.replace("-", "")):
            word_oov += 1
    return {
        "file": str(WIKI.relative_to(ROOT)),
        "lines": sum(1 for line in text.splitlines() if line.strip()),
        "tokens": len(tokens),
        "unique_words": len(unique),
        "segmented": segmented,
        "segmentation_rate": segmented / len(unique),
        "root_oov": root_oov,
        "root_oov_rate": root_oov / len(unique),
        "surface_not_in_root_list": word_oov,
        "note": "root_oov: the root left after MKK segmentation is neither in the root list nor the "
                "loanword list. Accuracy on real text is NOT measured here (needs human labels, "
                "see data/annotation/).",
    }


def main():
    mkk = ModernKataKupas()
    rows, unique = load_gold()
    pred, correct, intr = intrinsic(mkk, unique)
    out = {
        "generated": time.strftime("%Y-%m-%d %H:%M"),
        "command": "python experiments/paper_numbers.py",
        "gold": gold_stats(rows, unique),
        "intrinsic": intr,
        "boundary": boundary_eval(unique, pred),
        "wikipedia": wikipedia(mkk),
    }
    OUT_JSON.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    with open(OUT_PRED, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["word", "category", "gold_segmentation", "mkk_prediction", "correct"])
        for r, p, c in zip(unique, pred, correct):
            w.writerow([r["word"], r["category"], r["gold_segmentation"], p, c])
    print(json.dumps({k: out[k] for k in ("gold",)}, indent=1))
    i = out["intrinsic"]
    print("word acc", i["correct"], "/", i["n"], i["word_accuracy"])
    for k, v in out["boundary"]["systems"].items():
        print("boundary", k, {x: round(v[x], 4) if isinstance(v[x], float) else v[x]
                              for x in ("precision", "recall", "f1", "f1_ci_lower", "f1_ci_upper",
                                        "boundary_exact_match")})
    print("wiki", out["wikipedia"])


if __name__ == "__main__":
    main()
