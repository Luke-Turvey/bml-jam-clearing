"""Describe completed survey measurements without inferring asymptotic classes."""
import csv
from collections import Counter
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import numpy as np

from run_survey import ROOT, SIZES, TILES


def fit(n, t):
    x, y = np.log2(n), np.log2(t)
    power, intercept = np.linalg.lstsq(np.column_stack((x, np.ones(len(x)))), y, rcond=None)[0]
    residual = y-power*x-intercept
    return {'observations': len(n), 'minimum_n': int(n[0]), 'maximum_n': int(n[-1]),
            'power': float(power), 'intercept': float(intercept), 'log_base': 2,
            'coefficient': float(2**intercept),
            'log_rmse': float(np.sqrt(np.mean(residual**2)))}


def rational(value):
    return {'numerator': value.numerator, 'denominator': value.denominator}


def exact_affine_periodic(n, t, plan):
    """Select an exact training model, then check fixed coefficients on held-out sizes."""
    training = (n >= plan['training']['minimum_n']) & (n <= plan['training']['maximum_n'])
    validation = (n >= plan['validation']['minimum_n']) & (n <= plan['validation']['maximum_n'])
    train_n, train_t = n[training], t[training]
    valid_n, valid_t = n[validation], t[validation]
    spacing, anchor = plan['n_spacing'], plan['sample_anchor']
    train_q = (train_n-anchor)//spacing
    valid_q = (valid_n-anchor)//spacing
    if (len(train_n) != plan['training']['observations'] or
            len(valid_n) != plan['validation']['observations'] or
            np.any((n-anchor) % spacing) or not np.all(np.diff(train_q) == 1) or
            not np.all(np.diff(valid_q) == 1)):
        raise ValueError('saved sizes do not match the affine-periodic analysis design')
    tested = []
    for period in plan['candidate_periods_in_sample_index']:
        train_counts = Counter(int(q % period) for q in train_q)
        valid_counts = Counter(int(q % period) for q in valid_q)
        if (min(train_counts.values()) < plan['minimum_training_observations_per_residue'] or
                min(valid_counts.values()) < plan['minimum_validation_observations_per_residue'] or
                len(train_counts) != period or len(valid_counts) != period):
            raise ValueError(f'period {period} lacks the required observed cycles')
        differences = train_t[period:]-train_t[:-period]
        same_drift = bool(len(differences) and np.all(differences == differences[0]))
        tested.append({'period_in_sample_index': period, 'exact_training_drift': same_drift})
        if not same_drift:
            continue
        slope = Fraction(int(differences[0]), spacing*period)
        offsets = []
        for residue in range(period):
            index = int(np.flatnonzero(train_q % period == residue)[0])
            offsets.append(Fraction(int(train_t[index]))-slope*int(train_n[index]))

        def prediction(size):
            return slope*int(size)+offsets[((int(size)-anchor)//spacing) % period]

        if not all(prediction(size) == int(time) for size, time in zip(train_n, train_t)):
            raise AssertionError('constant training drift did not reconstruct its residue offsets')
        mismatches = [{'n': int(size), 'observed': int(time),
                       'predicted': rational(prediction(size)),
                       'residual': rational(Fraction(int(time))-prediction(size))}
                      for size, time in zip(valid_n, valid_t)
                      if prediction(size) != int(time)]
        validated = not mismatches
        exact_suffix = None
        if validated:
            mismatch_indices = [index for index, (size, time) in enumerate(zip(n, t))
                                if prediction(size) != int(time)]
            first = mismatch_indices[-1]+1 if mismatch_indices else 0
            exact_suffix = {'minimum_n': int(n[first]), 'maximum_n': int(n[-1]),
                            'observations': len(n)-first,
                            'coefficients_refitted': False}
        candidate = {
            'period_in_sample_index': period, 'n_period': spacing*period,
            'sample_anchor': anchor, 'q_definition': plan['sample_index'],
            'slope': rational(slope), 'offsets': [rational(value) for value in offsets],
            'training': {'minimum_n': int(train_n[0]), 'maximum_n': int(train_n[-1]),
                         'observations': len(train_n), 'exact': True,
                         'minimum_observations_per_residue': min(train_counts.values())},
            'validation': {'minimum_n': int(valid_n[0]), 'maximum_n': int(valid_n[-1]),
                           'observations': len(valid_n), 'exact': validated,
                           'minimum_observations_per_residue': min(valid_counts.values()),
                           'mismatch_count': len(mismatches), 'mismatches': mismatches},
            'validated': validated, 'observed_exact_suffix': exact_suffix,
        }
        return candidate, tested
    return None, tested


def check_periodic_records(records, measurements, plan):
    """Check model selection via first differences and coefficients by integer arithmetic."""
    counts = Counter()
    checks = []
    for record in records:
        rows = measurements[record['tile']]
        training_rows = [(n, t) for n, t in rows
                         if plan['training']['minimum_n'] <= n <= plan['training']['maximum_n']]
        increments = [right[1]-left[1] for left, right in zip(training_rows, training_rows[1:])]
        qualifying_periods = [p for p in plan['candidate_periods_in_sample_index']
                              if all(increments[i] == increments[i+p]
                                     for i in range(len(increments)-p))]
        independent_period = min(qualifying_periods, default=None)
        model = record['affine_periodic_candidate']
        if model is None:
            if independent_period is not None:
                raise AssertionError(f'{record["tile"]}: independent periodic differences found a model')
            counts['no_exact_training_model'] += 1
            checks.append({'tile': record['tile'], 'smallest_exact_training_period': None,
                           'training_first_differences_checked': len(increments),
                           'training_observations_checked': 0, 'validation_observations_checked': 0})
            continue
        period = model['period_in_sample_index']
        if period != independent_period:
            raise AssertionError(f'{record["tile"]}: independent minimum period differs')
        slope = model['slope']
        if (slope['numerator']*plan['n_spacing']*period !=
                sum(increments[:period])*slope['denominator']):
            raise AssertionError('stored slope differs from independent sum of first differences')
        training_checks, validation_checks, validation_mismatches = 0, 0, []
        all_mismatch_indices = []
        for index, (n, time) in enumerate(rows):
            q = (n-plan['sample_anchor'])//plan['n_spacing']
            offset = model['offsets'][q % period]
            numerator = slope['numerator']*n*offset['denominator'] + offset['numerator']*slope['denominator']
            observed = time*slope['denominator']*offset['denominator']
            if numerator != observed:
                all_mismatch_indices.append(index)
            if plan['training']['minimum_n'] <= n <= plan['training']['maximum_n']:
                training_checks += 1
                if numerator != observed:
                    raise AssertionError(f'{record["tile"]}: reconstructed training model failed')
            elif plan['validation']['minimum_n'] <= n <= plan['validation']['maximum_n']:
                validation_checks += 1
                if numerator != observed:
                    validation_mismatches.append(n)
        if (training_checks != plan['training']['observations'] or
                validation_checks != plan['validation']['observations']):
            raise AssertionError('independent check did not cover the planned observation counts')
        if bool(validation_mismatches) == model['validated']:
            raise AssertionError('reported held-out result differs from independent exact arithmetic')
        if validation_mismatches != [item['n'] for item in model['validation']['mismatches']]:
            raise AssertionError('reported validation mismatch locations differ')
        if model['validated']:
            category = 'validated_affine' if period == 1 else 'validated_affine_periodic'
            first = all_mismatch_indices[-1]+1 if all_mismatch_indices else 0
            suffix = model['observed_exact_suffix']
            if (suffix['minimum_n'] != rows[first][0] or
                    suffix['maximum_n'] != rows[-1][0] or
                    suffix['observations'] != len(rows)-first or suffix['coefficients_refitted']):
                raise AssertionError('reported exact suffix differs from independent checks')
        else:
            category = 'failed_validation'
        counts[category] += 1
        checks.append({'tile': record['tile'], 'period_in_sample_index': period,
                       'smallest_exact_training_period': independent_period,
                       'training_first_differences_checked': len(increments),
                       'training_observations_checked': training_checks,
                       'validation_observations_checked': validation_checks,
                       'validation_mismatches': validation_mismatches})
    result = {key: counts[key] for key in ['validated_affine', 'validated_affine_periodic',
                                          'failed_validation', 'no_exact_training_model']}
    return result, {'method': 'independent first-difference periodicity followed by integer cross multiplication of rational coefficients',
                    'counts': result, 'cases': checks,
                    'tiles_checked_for_minimum_training_period': len(checks),
                    'training_first_differences_checked': sum(c['training_first_differences_checked'] for c in checks),
                    'training_observations_checked': sum(c['training_observations_checked'] for c in checks),
                    'validation_observations_checked': sum(c['validation_observations_checked'] for c in checks)}


def printed_catalogue(directory):
    """Read the immutable comparison mapping, independent of manuscript edits."""
    path = directory/'printed_catalogue.json'
    record = json.loads(path.read_text())
    if set(record['entries']) != set(TILES):
        raise ValueError('the printed comparison catalogue must contain all 512 tiles')
    return record, hashlib.sha256(path.read_bytes()).hexdigest()


def analyse():
    directory = ROOT/'data/clearing_times/survey_north_first'
    plan_path = Path(__file__).parent/'analysis-plan.json'
    plan = json.loads(plan_path.read_text())
    periodic_plan_path = Path(__file__).parent/'affine-periodic-plan.json'
    periodic_plan = json.loads(periodic_plan_path.read_text())
    metadata = json.loads((directory/'metadata.json').read_text())
    if metadata['status'] != 'complete':
        raise ValueError('survey is not complete')
    records = []
    measurements = {}
    comparison, comparison_sha256 = printed_catalogue(directory)
    historical = comparison['entries']
    for tile in TILES:
        path = directory/f'{tile}.csv'
        content = path.read_bytes()
        if hashlib.sha256(content).hexdigest() != metadata['csv_sha256'][path.name]:
            raise ValueError(f'measurement hash mismatch: {path}')
        with path.open() as stream:
            rows = [(int(r['n']), int(r['clearing_time'])) for r in csv.DictReader(stream)]
        if [n for n,t in rows] != SIZES:
            raise ValueError(f'incomplete or reordered sizes: {path}')
        n,t = np.array(rows, dtype=np.int64).T
        measurements[tile] = rows
        tail_n, tail_t = n[n>=333], t[n>=333]
        differences = np.diff(tail_t)
        is_affine = bool(np.all(differences == differences[0]))
        affine = None
        if is_affine:
            slope = Fraction(int(differences[0]), 3)
            intercept = Fraction(int(tail_t[0]))-slope*int(tail_n[0])
            affine = {'slope': rational(slope), 'intercept': rational(intercept),
                      'minimum_n': 333, 'maximum_n': 498, 'observations': 56}
        fits = {str(c): fit(n[n>=c],t[n>=c]) for c in plan['minimum_size_cutoffs']}
        candidate, tested_periods = exact_affine_periodic(n, t, periodic_plan)
        if candidate and candidate['validated']:
            descriptor = ('validated finite affine formula' if candidate['period_in_sample_index'] == 1
                          else 'validated finite affine-plus-periodic formula')
        else:
            descriptor = 'finite-range power fit; no validated exact periodic model'
        record = {'tile': tile, 'observations': len(rows), 'minimum_n': 3, 'maximum_n': 498,
                  'tail_descriptor': 'observed affine tail' if is_affine else 'observed non-affine tail',
                  'asymptotic_status': 'not inferred from finite survey', 'affine_tail': affine, 'fits': fits,
                  'finite_model_descriptor': descriptor,
                  'affine_periodic_candidate': candidate,
                  'affine_periodic_search': tested_periods,
                  'printed_catalogue': historical.get(tile)}
        records.append(record)
    affine_count = sum(r['affine_tail'] is not None for r in records)
    periodic_counts, periodic_checks = check_periodic_records(records, measurements, periodic_plan)
    period_counts = Counter(r['affine_periodic_candidate']['period_in_sample_index'] for r in records
                            if r['affine_periodic_candidate'] and r['affine_periodic_candidate']['validated'])
    near_one_unmatched = [r['tile'] for r in records
                          if r['fits']['100']['power'] < 1.05 and
                          not (r['affine_periodic_candidate'] and r['affine_periodic_candidate']['validated'])]
    protocol = dict(periodic_plan)
    protocol.update(periodic_counts)
    protocol['counts'] = periodic_counts
    protocol['validated_period_counts'] = {str(p): count for p, count in sorted(period_counts.items())}
    protocol['plan_sha256'] = hashlib.sha256(periodic_plan_path.read_bytes()).hexdigest()
    protocol['descriptive_power_threshold_check'] = {
        'threshold': 1.05, 'comparison': 'power < threshold at minimum-size cutoff 100',
        'unmatched_count': len(near_one_unmatched), 'unmatched_tiles': near_one_unmatched,
        'used_to_select_period_limit': False,
    }
    summary = {
        'tiles': len(records), 'observations': sum(r['observations'] for r in records),
        'sizes_per_tile': len(SIZES), 'minimum_n': 3, 'maximum_n': 498,
        'observed_affine_tail': affine_count,
        'observed_non_affine_tail': len(records)-affine_count,
        'asymptotically_classified_by_survey': 0,
        'first_update': 'north', 'tile_anchor': 'bottom-left',
        'analysis_plan_sha256': hashlib.sha256(plan_path.read_bytes()).hexdigest(),
        'analysis_source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'printed_catalogue_input_sha256': comparison_sha256,
        'printed_catalogue_original_source': comparison['source'],
        'numpy': np.__version__,
        'fits': {'model': 'log2(T)=power*log2(n)+intercept', 'method': 'ordinary least squares',
                 'weighting': 'equal weight per sampled size', 'cutoffs': plan['minimum_size_cutoffs']},
        'affine_tail_criterion': plan['affine_tail'],
        'affine_periodic_analysis': protocol,
        'records': records,
    }
    (directory/'analysis.json').write_text(json.dumps(summary,indent=2)+'\n')
    compact_summary = {k: v for k, v in summary.items() if k != 'records'}
    compact_summary['selected_cases'] = [r for r in records if r['tile'] in {
        '111111111', '333333333', '113133313', '133333113', '133131313', '333131313'}]
    (directory/'summary.json').write_text(json.dumps(compact_summary,indent=2)+'\n')
    periodic_checks['plan_sha256'] = protocol['plan_sha256']
    periodic_checks['analysis_source_sha256'] = summary['analysis_source_sha256']
    periodic_checks['schema_version'] = 1
    periodic_checks['raw_csv_integrity'] = {
        'files_checked': len(records), 'measurements_checked': summary['observations'],
        'method': 'SHA-256 against the completed simulation metadata before analysis',
        'metadata_sha256': hashlib.sha256((directory/'metadata.json').read_bytes()).hexdigest(),
        'raw_measurements_modified': False,
    }
    (directory/'independent-validation.json').write_text(json.dumps(periodic_checks,indent=2)+'\n')
    with (directory/'catalogue.csv').open('w',newline='') as stream:
        fields = ['tile','tail_descriptor','asymptotic_status','power_all','power_n_ge_100',
                  'power_n_ge_250','power_n_ge_350','affine_slope','affine_intercept',
                  'finite_model_descriptor','power_coefficient_n_ge_100','validated_period',
                  'periodic_slope','periodic_offsets_q_mod_p','exact_formula_minimum_n']
        writer=csv.DictWriter(stream,fieldnames=fields)
        writer.writeheader()
        for r in records:
            candidate = r['affine_periodic_candidate']
            writer.writerow({'tile':r['tile'],'tail_descriptor':r['tail_descriptor'],
                'asymptotic_status':'not inferred from finite survey','power_all':r['fits']['3']['power'],
                'power_n_ge_100':r['fits']['100']['power'],
                'power_n_ge_250':r['fits']['250']['power'],
                'power_n_ge_350':r['fits']['350']['power'],
                'affine_slope':str(Fraction(**r['affine_tail']['slope'])) if r['affine_tail'] else '',
                'affine_intercept':str(Fraction(**r['affine_tail']['intercept'])) if r['affine_tail'] else '',
                'finite_model_descriptor':r['finite_model_descriptor'],
                'power_coefficient_n_ge_100':r['fits']['100']['coefficient'],
                'validated_period':candidate['period_in_sample_index'] if candidate and candidate['validated'] else '',
                'periodic_slope':str(Fraction(**candidate['slope'])) if candidate else '',
                'periodic_offsets_q_mod_p':';'.join(str(Fraction(**b)) for b in candidate['offsets']) if candidate else '',
                'exact_formula_minimum_n':candidate['observed_exact_suffix']['minimum_n']
                    if candidate and candidate['validated'] else ''})
    write_tex(summary)
    print(json.dumps({k:v for k,v in summary.items() if k != 'records'},indent=2))


def write_tex(summary):
    from render_survey import write_tex as write_catalogue_tex
    write_catalogue_tex(summary, ROOT/'latex/sections/survey.tex')


if __name__ == '__main__':
    analyse()
