"""
Downstream text classification (IndoNLU SmSA) with significance testing.
Revision Sep 2026 of experiments/text_classification_eval.py, which reported a
single run without any test.

    python experiments/downstream_significance.py

Differences from the old script (all conditions share them):
- identical cleaning for baseline and MKK (old baseline kept punctuation, MKK
  stripped it, which confounds the comparison); the old raw baseline is kept too
- TF-IDF token_pattern=\\S+ and lowercase=False, so single-character morphemes
  (suffix -i) are not silently dropped by scikit-learn's default \\w\\w+ pattern
- extra baseline: Sastrawi stemming
- official split: exact McNemar + paired bootstrap CI (accuracy, macro-F1)
- robustness: repeated stratified 5-fold CV (2 repeats) on train+test pooled

Output: experiments/results/downstream_significance.json
"""
import json
import sys
import time
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import RepeatedStratifiedKFold

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))

from eval_metrics import mcnemar_exact  # noqa: E402

CACHE = ROOT / "experiments" / "data" / "smsa_cache"
WORD_CACHE = CACHE / "mkk_word_segmentations.json"
OUT = ROOT / "experiments" / "results" / "downstream_significance.json"
LABELS = {"positive": 0, "neutral": 1, "negative": 2}
N_BOOT = 5000
SEED = 0


def load(path):
    texts, labels = [], []
    with open(path, encoding="utf-8") as f:
        for line in f:
            text, label = line.rstrip("\n").rsplit("\t", 1)
            texts.append(text)
            labels.append(LABELS[label])
    return texts, np.array(labels)


def clean_word(w):
    return "".join(c for c in w.lower() if c.isalnum() or c == "-")


def build_word_cache(all_texts):
    cache = {}
    if WORD_CACHE.exists():
        cache = json.loads(WORD_CACHE.read_text(encoding="utf-8"))
    vocab = {clean_word(w) for t in all_texts for w in t.split()} - {""}
    missing = sorted(vocab - set(cache))
    if missing:
        from modern_kata_kupas import ModernKataKupas
        mkk = ModernKataKupas()
        t0 = time.time()
        for i, w in enumerate(missing):
            try:
                cache[w] = mkk.segment(w)
            except Exception:
                cache[w] = w
            if i % 2000 == 0:
                print(f"  segmented {i}/{len(missing)} ({time.time() - t0:.0f}s)", flush=True)
        WORD_CACHE.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")
    return cache


def make_preprocessors(cache):
    from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
    stemmer = StemmerFactory().create_stemmer()
    stem_cache = {}

    def raw(t):  # old baseline
        return " ".join(t.lower().split())

    def clean(t):
        return " ".join(w for w in (clean_word(x) for x in t.split()) if w)

    def mkk(t):
        return " ".join(cache.get(w, w).replace("~", " ") for w in clean(t).split())

    def sastrawi(t):
        out = []
        for w in clean(t).split():
            if w not in stem_cache:
                stem_cache[w] = stemmer.stem(w) or w
            out.append(stem_cache[w])
        return " ".join(out)

    return {"baseline_raw": raw, "baseline_clean": clean, "mkk": mkk, "sastrawi_stem": sastrawi}


def fit_predict(train_x, train_y, test_x):
    vec = TfidfVectorizer(max_features=10000, ngram_range=(1, 2), token_pattern=r"\S+", lowercase=False)
    xtr = vec.fit_transform(train_x)
    clf = LogisticRegression(max_iter=1000, random_state=42)
    clf.fit(xtr, train_y)
    return clf.predict(vec.transform(test_x)), len(vec.vocabulary_)


def paired_bootstrap(y, pa, pb):
    rng = np.random.default_rng(SEED)
    n = len(y)
    acc_d, f1_d = [], []
    for _ in range(N_BOOT):
        i = rng.integers(0, n, n)
        acc_d.append(accuracy_score(y[i], pa[i]) - accuracy_score(y[i], pb[i]))
        f1_d.append(f1_score(y[i], pa[i], average="macro") - f1_score(y[i], pb[i], average="macro"))
    q = lambda a: [float(np.quantile(a, 0.025)), float(np.quantile(a, 0.975))]  # noqa: E731
    return {"accuracy_diff_ci95": q(acc_d), "f1_macro_diff_ci95": q(f1_d), "n_boot": N_BOOT}


def main():
    tr_x, tr_y = load(CACHE / "train_preprocess.tsv")
    te_x, te_y = load(CACHE / "test_preprocess.tsv")
    cache = build_word_cache(tr_x + te_x)
    prep = make_preprocessors(cache)
    processed = {k: ([f(t) for t in tr_x], [f(t) for t in te_x]) for k, f in prep.items()}

    official, preds = {}, {}
    for name, (ptr, pte) in processed.items():
        p, vocab = fit_predict(ptr, tr_y, pte)
        preds[name] = p
        official[name] = {"accuracy": accuracy_score(te_y, p), "f1_macro": f1_score(te_y, p, average="macro"),
                          "f1_weighted": f1_score(te_y, p, average="weighted"), "tfidf_features": vocab}
    comparisons = {}
    for other in ("baseline_clean", "baseline_raw", "sastrawi_stem"):
        ca = preds["mkk"] == te_y
        cb = preds[other] == te_y
        comparisons[f"mkk_vs_{other}"] = {
            "accuracy_diff": official["mkk"]["accuracy"] - official[other]["accuracy"],
            "f1_macro_diff": official["mkk"]["f1_macro"] - official[other]["f1_macro"],
            "mcnemar_exact": mcnemar_exact(list(ca), list(cb)),
            **paired_bootstrap(te_y, preds["mkk"], preds[other]),
        }

    # repeated CV on pooled data
    all_y = np.concatenate([tr_y, te_y])
    pooled = {k: np.array(v[0] + v[1], dtype=object) for k, v in processed.items()}
    rskf = RepeatedStratifiedKFold(n_splits=5, n_repeats=2, random_state=SEED)
    folds = {k: {"accuracy": [], "f1_macro": []} for k in processed}
    for tr_i, te_i in rskf.split(np.zeros(len(all_y)), all_y):
        for name, xs in pooled.items():
            p, _ = fit_predict(list(xs[tr_i]), all_y[tr_i], list(xs[te_i]))
            folds[name]["accuracy"].append(accuracy_score(all_y[te_i], p))
            folds[name]["f1_macro"].append(f1_score(all_y[te_i], p, average="macro"))
    cv = {}
    for name, m in folds.items():
        cv[name] = {k: {"mean": float(np.mean(v)), "sd": float(np.std(v, ddof=1))} for k, v in m.items()}
    for other in ("baseline_clean", "baseline_raw", "sastrawi_stem"):
        d = np.array(folds["mkk"]["f1_macro"]) - np.array(folds[other]["f1_macro"])
        cv[f"mkk_minus_{other}_f1_macro"] = {"mean": float(d.mean()), "sd": float(d.std(ddof=1)),
                                              "folds_mkk_better": int((d > 0).sum()), "n_folds": len(d)}

    out = {
        "generated": time.strftime("%Y-%m-%d %H:%M"),
        "command": "python experiments/downstream_significance.py",
        "dataset": "IndoNLU SmSA (cached train_preprocess.tsv / test_preprocess.tsv)",
        "n_train": len(tr_y), "n_test": len(te_y),
        "classifier": "TF-IDF (1-2 gram, max 10k, token_pattern \\S+) + LogisticRegression",
        "official_split": official,
        "official_comparisons": comparisons,
        "repeated_cv_5x2": cv,
    }
    OUT.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps({"official": official, "comparisons": comparisons, "cv": cv}, indent=1))


if __name__ == "__main__":
    main()
