"""Save a fixed set of figure PDFs and numerical captions for the manuscript."""
import hashlib
import json
import tempfile
from pathlib import Path


def save_paper_figures(source, output, *, manifest_path=None):
    """Copy a complete numbered-figure build into a publication snapshot.

    Read and validate every input before replacing saved assets. The snapshot
    contains independent copies; rendering new figures does not modify it.
    PDFs go in the paper's figures directory and caption values beside main.tex.
    """
    source, output = Path(source), Path(output)
    reports = json.loads((source / 'index.json').read_text())
    if len(reports) != 13 or {r['figure'] for r in reports} != set(range(1, 14)):
        raise ValueError('a paper snapshot requires all thirteen numbered figures')
    by_number = {r['figure']: r for r in reports}
    if any(r.get('first_update') != 'north' for r in reports):
        raise ValueError('paper figure reports must specify North-first updates')
    assets, figures = {}, []
    for number in range(1, 14):
        name = f'figure{number:02d}.pdf'
        contents = (source / f'figure{number:02d}' / name).read_bytes()
        if not contents.startswith(b'%PDF-'):
            raise ValueError(f'{name} is not a PDF')
        assets['figures/' + name] = contents
        figures.append({'number': number, 'file': 'figures/' + name,
                        'sha256': hashlib.sha256(contents).hexdigest(),
                        'computation': by_number[number]})
    statistics = (source / 'figure_statistics.tex').read_bytes()
    if not statistics.strip():
        raise ValueError('the numerical caption file is empty')
    assets['figure_statistics.tex'] = statistics
    manifest = {'figures': figures, 'statistics': {
        'file': 'figure_statistics.tex', 'sha256': hashlib.sha256(statistics).hexdigest()
    }}
    manifest_bytes = (json.dumps(manifest, indent=2) + '\n').encode()
    manifest_path = Path(manifest_path) if manifest_path is not None else output / 'manifest.json'
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.paper-figures-', dir=output.parent) as staging:
        staging = Path(staging)
        for name, contents in assets.items():
            (staging / name).parent.mkdir(parents=True, exist_ok=True)
            (staging / name).write_bytes(contents)
        output.mkdir(exist_ok=True)
        for name in assets:
            (output / name).parent.mkdir(parents=True, exist_ok=True)
            (staging / name).replace(output / name)
        staged_manifest = staging / 'manifest.json'
        staged_manifest.write_bytes(manifest_bytes)
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        staged_manifest.replace(manifest_path)
    return manifest
