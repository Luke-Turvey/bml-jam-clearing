"""Checks for saved manuscript assets and a simulation-free paper build."""
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

import pytest

from bml.publication import save_paper_figures

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def rendered_figures(tmp_path):
    source = tmp_path / 'outputs'
    source.mkdir()
    reports = []
    for number in range(1, 14):
        directory = source / f'figure{number:02d}'
        directory.mkdir()
        (directory / f'figure{number:02d}.pdf').write_bytes(
            f'%PDF-1.4\nfigure {number}\n'.encode())
        reports.append({'figure': number, 'first_update': 'north'})
    (source / 'index.json').write_text(json.dumps(reports))
    (source / 'figure_statistics.tex').write_text(r'\newcommand{\FigureSixMaxN}{999}')
    return source


def test_saved_figures_change_only_when_explicitly_replaced(rendered_figures, tmp_path):
    saved = tmp_path / 'paper'
    manifest = save_paper_figures(rendered_figures, saved)
    assert len(manifest['figures']) == 13
    original = (saved / 'figures/figure01.pdf').read_bytes()
    source_pdf = rendered_figures / 'figure01/figure01.pdf'
    source_pdf.write_bytes(b'%PDF-1.4\nupdated figure\n')
    assert (saved / 'figures/figure01.pdf').read_bytes() == original
    save_paper_figures(rendered_figures, saved)
    assert (saved / 'figures/figure01.pdf').read_bytes() == source_pdf.read_bytes()


def test_incomplete_build_preserves_saved_set(rendered_figures, tmp_path):
    saved = tmp_path / 'paper'
    save_paper_figures(rendered_figures, saved)
    original = {p.relative_to(saved): p.read_bytes() for p in saved.rglob('*') if p.is_file()}
    (rendered_figures / 'figure01/figure01.pdf').write_bytes(b'%PDF-1.4\nnew\n')
    (rendered_figures / 'figure13/figure13.pdf').unlink()
    with pytest.raises(FileNotFoundError):
        save_paper_figures(rendered_figures, saved)
    assert {p.relative_to(saved): p.read_bytes() for p in saved.rglob('*') if p.is_file()} == original


def test_saved_paper_assets_match_manifest():
    saved = ROOT / 'latex'
    manifest = json.loads((ROOT / 'data/metadata/paper-figures.json').read_text())
    assert [r['number'] for r in manifest['figures']] == list(range(1, 14))
    for entry in manifest['figures']:
        assert entry['computation']['first_update'] == 'north'
        assert entry['computation']['figure'] == entry['number']
        assert (saved / entry['file']).read_bytes().startswith(b'%PDF-')
    for entry in [*manifest['figures'], manifest['statistics']]:
        contents = (saved / entry['file']).read_bytes()
        assert hashlib.sha256(contents).hexdigest() == entry['sha256']


@pytest.mark.skipif(shutil.which('pdflatex') is None, reason='pdflatex is not installed')
def test_paper_compiles_outside_repository(tmp_path):
    latex = tmp_path / 'latex'
    shutil.copytree(ROOT / 'latex', latex,
                    ignore=lambda _, names: [name for name in names
                                           if name == 'build' or Path(name).suffix not in
                                           {'', '.tex', '.sty', '.bib', '.bbl', '.pdf'}
                                           or name == 'main.pdf'])
    assert not (latex / 'Makefile').exists()
    assert (latex / 'main.bbl').is_file()
    command = ['pdflatex', '-interaction=nonstopmode', '-halt-on-error',
               '-no-shell-escape', '-recorder', 'main.tex']
    for _ in range(3):
        result = subprocess.run(command, cwd=latex, capture_output=True, text=True, timeout=180)
        assert result.returncode == 0, result.stdout + result.stderr
    log = (latex / 'main.log').read_text()
    assert 'undefined references' not in log
    assert 'Citation ' not in log
    inputs = [line for line in (latex / 'main.fls').read_text().splitlines()
              if line.startswith('INPUT ')]
    assert not any(str(ROOT) in line for line in inputs)
    assert (latex / 'main.pdf').read_bytes().startswith(b'%PDF-')
