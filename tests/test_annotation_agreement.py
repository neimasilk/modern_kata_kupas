"""Tests for experiments/annotation_agreement.py (inter-annotator agreement)."""
import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "experiments")))

from annotation_agreement import agreement, boundary_slots, cohen_kappa_binary  # noqa: E402


def test_boundary_slots():
    # menulis -> men|ulis : 6 inter-character slots, boundary after position 3
    assert boundary_slots("menulis", "meN~tulis") == [0, 0, 1, 0, 0, 0]
    assert boundary_slots("buku-buku", "buku~ulg") is None


def test_cohen_kappa_binary_perfect_and_chance():
    assert cohen_kappa_binary([1, 0, 1, 0], [1, 0, 1, 0]) == pytest.approx(1.0)
    # identical marginals, no agreement beyond chance
    assert cohen_kappa_binary([1, 1, 0, 0], [1, 0, 1, 0]) == pytest.approx(0.0)


def test_cohen_kappa_binary_constant_raters():
    assert cohen_kappa_binary([0, 0, 0], [0, 0, 0]) == 1.0


def test_agreement_report():
    a = {"menulis": "meN~tulis", "makanan": "makan~an", "buku-buku": "buku~ulg"}
    b = {"menulis": "meN~tulis", "makanan": "makanan", "buku-buku": "buku~ulg"}
    rep = agreement(a, b)
    assert rep["n_words"] == 3
    assert rep["exact_agreement"] == pytest.approx(2 / 3)
    assert rep["boundary_kappa_words"] == 2          # buku-buku excluded (reduplication)
    assert rep["disagreements"] == [{"word": "makanan", "a": "makan~an", "b": "makanan"}]


def test_agreement_ignores_blank_annotations():
    rep = agreement({"x": "", "makanan": "makan~an"}, {"x": "x", "makanan": "makan~an"})
    assert rep["n_words"] == 1
