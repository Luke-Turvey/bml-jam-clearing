"""Check exact periodic-model selection against controlled sequences."""

import importlib.util
import json
from pathlib import Path

import numpy as np
import pytest


SURVEY_DIRECTORY = Path(__file__).resolve().parents[1]/'miscellaneous/survey'


@pytest.fixture
def survey_analysis(monkeypatch):
    monkeypatch.syspath_prepend(str(SURVEY_DIRECTORY))
    spec = importlib.util.spec_from_file_location('survey_analysis_under_test',
                                               SURVEY_DIRECTORY/'analyse_survey.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def periodic_plan():
    return json.loads((SURVEY_DIRECTORY/'affine-periodic-plan.json').read_text())


def phased_sequence():
    sizes = np.arange(3, 499, 3, dtype=np.int64)
    q = sizes//3
    offsets = np.array([3, -2, 5], dtype=np.int64)
    return sizes, 7*q+offsets[(q+1) % 3]


def test_rational_slope_and_nonzero_periodic_phase(survey_analysis, periodic_plan):
    sizes, times = phased_sequence()
    model, _ = survey_analysis.exact_affine_periodic(sizes, times, periodic_plan)
    assert model['validated']
    assert model['period_in_sample_index'] == 3
    assert model['slope'] == {'numerator': 7, 'denominator': 3}
    assert model['offsets'] == [{'numerator': value, 'denominator': 1}
                                for value in [-2, 5, 3]]
    assert model['observed_exact_suffix']['observations'] == 166
    rows = [(int(n), int(t)) for n, t in zip(sizes, times)]
    counts, checks = survey_analysis.check_periodic_records(
        [{'tile': 'synthetic', 'affine_periodic_candidate': model}],
        {'synthetic': rows}, periodic_plan)
    assert counts['validated_affine_periodic'] == 1
    assert checks['validation_observations_checked'] == 56


def test_changed_validation_value_rejects_fixed_training_model(survey_analysis, periodic_plan):
    sizes, times = phased_sequence()
    times[sizes == 432] += 1
    model, _ = survey_analysis.exact_affine_periodic(sizes, times, periodic_plan)
    assert model['period_in_sample_index'] == 3
    assert not model['validated']
    assert model['observed_exact_suffix'] is None
    assert [row['n'] for row in model['validation']['mismatches']] == [432]
    rows = [(int(n), int(t)) for n, t in zip(sizes, times)]
    counts, _ = survey_analysis.check_periodic_records(
        [{'tile': 'synthetic', 'affine_periodic_candidate': model}],
        {'synthetic': rows}, periodic_plan)
    assert counts['failed_validation'] == 1


def test_quadratic_sequence_has_no_tested_exact_period(survey_analysis, periodic_plan):
    sizes = np.arange(3, 499, 3, dtype=np.int64)
    model, search = survey_analysis.exact_affine_periodic(sizes, sizes*sizes, periodic_plan)
    assert model is None
    assert len(search) == 12
    assert all(not row['exact_training_drift'] for row in search)
