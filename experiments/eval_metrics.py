"""
Evaluation metrics for morphological segmentation (paper revision, Sep 2026).

- canonical_to_surface: map a canonical segmentation (meN~per~baik~i) onto the
  surface string (mem|per|baik|i) so rule-based output can be compared with
  surface segmenters such as Morfessor on equal terms.
- boundary_prf: micro-averaged boundary precision/recall/F1.
- morpheme_prf: multiset morpheme precision/recall/F1 over ALL words.
- mcnemar_exact / paired_bootstrap_diff: paired significance tests.

Surface convention (documented in the paper): the nasal of meN-/peN- belongs to
the prefix, and a root whose initial k/p/t/s is elided ("luluh") keeps the rest
(menulis -> men|ulis). Words containing reduplication markers (ulg, rp, rs(...))
or whose surface cannot be explained by the canonical morphemes return None and
are excluded from boundary evaluation (the excluded count is always reported).
"""
from collections import Counter
from typing import Dict, List, Optional, Sequence, Set

import numpy as np
from scipy.stats import binomtest

SEP = "~"

SURFACE_VARIANTS = {
    "meN": ["menge", "meng", "meny", "mem", "men", "me"],
    "peN": ["penge", "peng", "peny", "pem", "pen", "pe"],
    "ber": ["ber", "bel", "be"],
    "ter": ["ter", "te"],
    "per": ["per", "pel", "pe"],
}
NASAL_PREFIXES = {"meN", "peN"}
LULUH_INITIALS = set("kpts")
REDUP_MARKERS = {"ulg", "rp"}


def _has_redup_marker(morphemes: Sequence[str]) -> bool:
    return any(m in REDUP_MARKERS or m.startswith("rs(") for m in morphemes)


def canonical_to_surface(word: str, canonical: str) -> Optional[List[str]]:
    """Return surface segments whose concatenation is ``word`` (hyphens removed), or None."""
    surface = word.lower().replace("-", "")
    morphemes = [m for m in canonical.split(SEP) if m]
    if not morphemes or _has_redup_marker(morphemes):
        return None

    def solve(pos: int, i: int, prev: Optional[str]) -> Optional[List[str]]:
        if i == len(morphemes):
            return [] if pos == len(surface) else None
        m = morphemes[i]
        if m in SURFACE_VARIANTS:
            candidates = SURFACE_VARIANTS[m]
        else:
            candidates = [m.lower()]
            if prev in NASAL_PREFIXES and m[:1].lower() in LULUH_INITIALS and len(m) > 1:
                candidates.append(m[1:].lower())
        for cand in candidates:
            if cand and surface.startswith(cand, pos):
                rest = solve(pos + len(cand), i + 1, m)
                if rest is not None:
                    return [cand] + rest
        return None

    return solve(0, 0, None)


def boundaries(segments: Sequence[str]) -> Set[int]:
    """Internal boundary offsets of a segmentation (end of string excluded)."""
    out, pos = set(), 0
    for seg in segments[:-1]:
        pos += len(seg)
        out.add(pos)
    return out


def _prf(tp: int, fp: int, fn: int) -> Dict[str, float]:
    p = tp / (tp + fp) if tp + fp else 0.0
    r = tp / (tp + fn) if tp + fn else 0.0
    f = 2 * p * r / (p + r) if p + r else 0.0
    return {"precision": p, "recall": r, "f1": f, "tp": tp, "fp": fp, "fn": fn}


def boundary_prf(pred: Sequence[Sequence[str]], gold: Sequence[Sequence[str]]) -> Dict[str, float]:
    """Micro-averaged boundary P/R/F1 over paired surface segmentations."""
    tp = fp = fn = 0
    for p, g in zip(pred, gold):
        bp, bg = boundaries(p), boundaries(g)
        tp += len(bp & bg)
        fp += len(bp - bg)
        fn += len(bg - bp)
    return _prf(tp, fp, fn)


def morpheme_prf(pred: Sequence[str], gold: Sequence[str]) -> Dict[str, float]:
    """Multiset morpheme P/R/F1 over canonical segmentations; every word counts."""
    tp = fp = fn = 0
    for p, g in zip(pred, gold):
        cp = Counter(m for m in p.split(SEP) if m)
        cg = Counter(m for m in g.split(SEP) if m)
        common = sum((cp & cg).values())
        tp += common
        fp += sum(cp.values()) - common
        fn += sum(cg.values()) - common
    return _prf(tp, fp, fn)


def mcnemar_exact(a_correct: Sequence[bool], b_correct: Sequence[bool]) -> Dict[str, float]:
    """Exact (binomial) McNemar test on paired correctness vectors."""
    b = sum(1 for x, y in zip(a_correct, b_correct) if x and not y)
    c = sum(1 for x, y in zip(a_correct, b_correct) if y and not x)
    p = 1.0 if b + c == 0 else binomtest(b, b + c, 0.5).pvalue
    return {"b": b, "c": c, "p_value": float(p)}


def paired_bootstrap_diff(a: Sequence[float], b: Sequence[float], n_boot: int = 10000,
                          seed: int = 0, level: float = 0.95) -> Dict[str, float]:
    """Bootstrap CI of mean(a) - mean(b) resampling items jointly."""
    a_arr, b_arr = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(a_arr), size=(n_boot, len(a_arr)))
    diffs = a_arr[idx].mean(axis=1) - b_arr[idx].mean(axis=1)
    alpha = (1 - level) / 2
    return {
        "diff": float(a_arr.mean() - b_arr.mean()),
        "ci_lower": float(np.quantile(diffs, alpha)),
        "ci_upper": float(np.quantile(diffs, 1 - alpha)),
        "n_boot": n_boot,
    }


def bootstrap_ci(values: Sequence[float], n_boot: int = 10000, seed: int = 0,
                 level: float = 0.95) -> Dict[str, float]:
    """Percentile bootstrap CI of the mean."""
    arr = np.asarray(values, dtype=float)
    rng = np.random.default_rng(seed)
    means = arr[rng.integers(0, len(arr), size=(n_boot, len(arr)))].mean(axis=1)
    alpha = (1 - level) / 2
    return {"mean": float(arr.mean()), "ci_lower": float(np.quantile(means, alpha)),
            "ci_upper": float(np.quantile(means, 1 - alpha)), "n_boot": n_boot}
