"""Tests for experiments/eval_metrics.py and the metric fixes in experiments/evaluate.py."""
import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "experiments")))

from eval_metrics import (  # noqa: E402
    boundaries,
    boundary_prf,
    canonical_to_surface,
    mcnemar_exact,
    morpheme_prf,
    paired_bootstrap_diff,
)


# --- canonical -> surface mapping -------------------------------------------

@pytest.mark.parametrize("word,canonical,expected", [
    ("makanan", "makan~an", ["makan", "an"]),
    ("bukuku", "buku~ku", ["buku", "ku"]),
    ("menulis", "meN~tulis", ["men", "ulis"]),          # t luluh
    ("membaca", "meN~baca", ["mem", "baca"]),
    ("mengajar", "meN~ajar", ["meng", "ajar"]),
    ("menyapu", "meN~sapu", ["meny", "apu"]),            # s luluh
    ("mengkompilasi", "meN~kompilasi", ["meng", "kompilasi"]),  # loanword, no luluh
    ("memperbaiki", "meN~per~baik~i", ["mem", "per", "baik", "i"]),
    ("pemukulan", "peN~pukul~an", ["pem", "ukul", "an"]),
    ("belajar", "ber~ajar", ["bel", "ajar"]),
    ("bekerja", "ber~kerja", ["be", "kerja"]),
    ("kebersihan", "ke~bersih~an", ["ke", "bersih", "an"]),
    ("diupload", "di~upload", ["di", "upload"]),
    ("menulis", "menulis", ["menulis"]),                 # unsegmented
])
def test_canonical_to_surface(word, canonical, expected):
    assert canonical_to_surface(word, canonical) == expected


def test_canonical_to_surface_hyphen_is_ignored():
    # hyphenated loanword affixation: boundaries are computed on the hyphen-less string
    assert canonical_to_surface("di-upload", "di~upload") == ["di", "upload"]


@pytest.mark.parametrize("word,canonical", [
    ("buku-buku", "buku~ulg"),           # reduplication marker -> not mappable
    ("lelaki", "laki~rp"),
    ("pembelajaran", "peN~ajar~an"),     # hidden ber- : surface cannot be explained
    ("menulis", "meN~baca"),             # wrong root
])
def test_canonical_to_surface_unmappable(word, canonical):
    assert canonical_to_surface(word, canonical) is None


# --- boundary metrics ---------------------------------------------------------

def test_boundaries_positions():
    assert boundaries(["mem", "per", "baik", "i"]) == {3, 6, 10}
    assert boundaries(["menulis"]) == set()


def test_boundary_prf_micro():
    gold = [["mem", "per", "baik", "i"], ["makan", "an"]]
    pred = [["memper", "bai", "ki"], ["makan", "an"]]
    # word1 gold {3,6,10}, pred {6,9} -> tp1 fp1 fn2 ; word2 tp1
    res = boundary_prf(pred, gold)
    assert res["tp"] == 2 and res["fp"] == 1 and res["fn"] == 2
    assert res["precision"] == pytest.approx(2 / 3)
    assert res["recall"] == pytest.approx(2 / 4)
    assert res["f1"] == pytest.approx(2 * (2 / 3) * 0.5 / (2 / 3 + 0.5))


def test_boundary_prf_no_predicted_boundaries():
    res = boundary_prf([["makanan"]], [["makan", "an"]])
    assert res["precision"] == 0.0 and res["recall"] == 0.0 and res["f1"] == 0.0


# --- morpheme P/R/F1 (multiset, all words) --------------------------------------

def test_morpheme_prf_counts_unsegmented_words_as_misses():
    # an unsegmented prediction must still count toward FN (old evaluate.py skipped it)
    res = morpheme_prf(["makanan"], ["makan~an"])
    assert res["tp"] == 0 and res["fp"] == 1 and res["fn"] == 2


def test_morpheme_prf_is_multiset():
    res = morpheme_prf(["jalan~ulg~jalan"], ["jalan~ulg~jalan"])
    assert res["tp"] == 3 and res["fp"] == 0 and res["fn"] == 0


# --- significance ---------------------------------------------------------------

def test_mcnemar_exact_symmetric_and_bounds():
    a = [True] * 10 + [False] * 10
    b = [False] * 10 + [True] * 10
    res = mcnemar_exact(a, b)
    assert res["b"] == 10 and res["c"] == 10
    assert res["p_value"] == pytest.approx(1.0)


def test_mcnemar_exact_detects_difference():
    a = [True] * 30
    b = [False] * 30
    assert mcnemar_exact(a, b)["p_value"] < 1e-6


def test_mcnemar_exact_no_discordant():
    res = mcnemar_exact([True, False], [True, False])
    assert res["p_value"] == 1.0


def test_paired_bootstrap_diff_zero_when_identical():
    a = [1, 0, 1, 1, 0]
    res = paired_bootstrap_diff(a, a, n_boot=200, seed=0)
    assert res["diff"] == 0.0 and res["ci_lower"] == 0.0 and res["ci_upper"] == 0.0


# --- evaluate.py regression tests ------------------------------------------------

class _FixedSystem:
    def __init__(self, mapping):
        self.mapping = mapping

    def segment(self, word):
        return self.mapping.get(word, word)


def _evaluate(mapping, gold_rows):
    from evaluate import MorphologicalEvaluator
    ev = MorphologicalEvaluator(_FixedSystem(mapping))
    return ev.evaluate_dataset(gold_rows, show_progress=False)


def test_evaluate_prefix_accuracy_counts_unsegmented_words():
    gold = [
        {"word": "menulis", "gold_segmentation": "meN~tulis", "category": "x"},
        {"word": "membaca", "gold_segmentation": "meN~baca", "category": "x"},
    ]
    # second word left unsegmented -> its prefix is wrong; old code skipped it and reported 1.0
    m = _evaluate({"menulis": "meN~tulis"}, gold)
    assert m.prefix_accuracy == pytest.approx(0.5)


def test_evaluate_suffix_accuracy_only_over_words_with_gold_suffix_or_pred_suffix():
    gold = [
        {"word": "makanan", "gold_segmentation": "makan~an", "category": "x"},
        {"word": "tulisan", "gold_segmentation": "tulis~an", "category": "x"},
    ]
    m = _evaluate({"makanan": "makan~an", "tulisan": "tulis~kan"}, gold)
    assert m.suffix_accuracy == pytest.approx(0.5)


def test_evaluate_morpheme_metrics_include_unsegmented_words():
    gold = [{"word": "makanan", "gold_segmentation": "makan~an", "category": "x"}]
    m = _evaluate({}, gold)
    assert m.morpheme_recall == 0.0
    assert m.false_negatives == 2


def test_evaluate_parse_segmentation_splits_on_separator():
    from evaluate import MorphologicalEvaluator
    ev = MorphologicalEvaluator(_FixedSystem({}))
    # old code returned ["meN~tulis"] because seg == seg.strip('~') for normal input
    assert ev.parse_segmentation("meN~tulis") == ["meN", "tulis"]
    assert ev.parse_segmentation("menulis") == ["menulis"]
