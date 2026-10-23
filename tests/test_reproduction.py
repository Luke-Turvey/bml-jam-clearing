import json
from pathlib import Path
import numpy as np
import pytest
from bml.experiments import run, verify_reference
from bml.initial import periodic, parse_tile
from bml.model import clearing_time
from bml.plotting import plot_csv

ROOT = Path(__file__).resolve().parents[1]


def test_historical_deterministic_data():
    report = verify_reference(ROOT / 'data/clearing_times/historical', max_n=15)
    assert report['checked'] >= 2500
    assert report['mismatches'] == []
    assert report['conventions']['g_periodic_133333113.csv']['north'] > 0
    assert report['conventions']['periodic_113133313.csv']['east'] > 0


def test_repeatable_workflow(tmp_path):
    a, b = tmp_path / 'a', tmp_path / 'b'
    run(ROOT / 'figures/experiments/smoke.json', a)
    run(ROOT / 'figures/experiments/smoke.json', b)
    for p in a.glob('*.csv'):
        assert p.read_bytes() == (b / p.name).read_bytes()
    with pytest.raises(FileExistsError): run(ROOT / 'figures/experiments/smoke.json', a)
    output = tmp_path / 'plot.png'
    report = plot_csv(a / 'superlinear.csv', output)
    assert output.stat().st_size > 1000
    assert report['groups']['all']['count'] == 10


def test_power_law_fit(tmp_path):
    source = tmp_path / 'known.csv'
    source.write_text('1,3\n2,12\n4,48\n8,192\n')
    report = plot_csv(source, tmp_path / 'fit.png')
    assert report['groups']['all']['power'] == pytest.approx(2)
    assert report['groups']['all']['coefficient'] == pytest.approx(3)


def test_reference_integrity():
    import hashlib
    manifest = json.loads((ROOT / 'data/metadata/clearing_times_checksums.json').read_text())
    assert len(manifest) > 500
    for name, expected in manifest.items():
        assert hashlib.sha256((ROOT / 'data/clearing_times/historical' / name).read_bytes()).hexdigest() == expected


def test_snapshot(tmp_path):
    from bml.plotting import snapshot
    from bml.model import evolve
    output = tmp_path / 'state.png'
    snapshot('133333113', 8, 10, output)
    expected = evolve(periodic(parse_tile('133333113'), 8), 10)
    np.testing.assert_array_equal(np.load(output.with_suffix('.npy')), expected)
    assert output.stat().st_size > 1000
    assert json.loads(output.with_suffix('.json').read_text())['first_update'] == 'north'
