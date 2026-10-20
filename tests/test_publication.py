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
    original = (saved / 'figure01.pdf').read_bytes()
    source_pdf = rendered_figures / 'figure01/figure01.pdf'
    source_pdf.write_bytes(b'%PDF-1.4\nupdated figure\n')
    assert (saved / 'figure01.pdf').read_bytes() == original
    save_paper_figures(rendered_figures, saved)
    assert (saved / 'figure01.pdf').read_bytes() == source_pdf.read_bytes()


def test_incomplete_build_preserves_saved_set(rendered_figures, tmp_path):
    saved = tmp_path / 'paper'
    save_paper_figures(rendered_figures, saved)
    original = {p.name: p.read_bytes() for p in saved.iterdir()}
    (rendered_figures / 'figure01/figure01.pdf').write_bytes(b'%PDF-1.4\nnew\n')
    (rendered_figures / 'figure13/figure13.pdf').unlink()
    with pytest.raises(FileNotFoundError):
        save_paper_figures(rendered_figures, saved)
    assert {p.name: p.read_bytes() for p in saved.iterdir()} == original


def test_saved_paper_assets_match_manifest():
    saved = ROOT / 'figures/paper'
    manifest = json.loads((saved / 'manifest.json').read_text())
    assert [r['number'] for r in manifest['figures']] == list(range(1, 14))
    for entry in manifest['figures']:
        assert entry['computation']['first_update'] == 'north'
        assert entry['computation']['figure'] == entry['number']
        assert (saved / entry['file']).read_bytes().startswith(b'%PDF-')
    for entry in [*manifest['figures'], manifest['statistics']]:
        contents = (saved / entry['file']).read_bytes()
        assert hashlib.sha256(contents).hexdigest() == entry['sha256']


def test_default_build_needs_only_saved_assets_and_latex(tmp_path):
    latex = tmp_path / 'latex'
    latex.mkdir()
    shutil.copyfile(ROOT / 'latex/Makefile', latex / 'Makefile')
    saved = tmp_path / 'figures/paper'
    shutil.copytree(ROOT / 'figures/paper', saved)
    original = {p.name: p.read_bytes() for p in saved.iterdir()}
    engine = latex / 'test-latexmk'
    engine.write_text('#!/bin/sh\nprintf "%s\\n" "$@" > latex-arguments.txt\n')
    engine.chmod(0o755)
    command = ['make', '-C', str(latex), 'PYTHON=false', f'LATEXMK={engine}']
    result = subprocess.run(command, capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    assert (latex / 'latex-arguments.txt').read_text().splitlines() == [
        '-pdf', '-interaction=nonstopmode', '-halt-on-error', '-outdir=build', 'main.tex']
    assert {p.name: p.read_bytes() for p in saved.iterdir()} == original
    (saved / 'figure13.pdf').unlink()
    result = subprocess.run(command, capture_output=True, text=True)
    assert result.returncode != 0
    assert 'Missing saved paper asset:' in result.stdout
    assert 'figure13.pdf' in result.stdout
