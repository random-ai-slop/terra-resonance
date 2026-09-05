#!/usr/bin/env python3
"""Independent scientific audit of an explicitly accepted agreement integration.

Run only after the coordinator supplies integration I:
  PYTHONPATH=packages OPENBLAS_NUM_THREADS=1 python scripts/validate_agreement.py \
    --integration FULL_COMMIT --artifacts artifacts/agreement-science/RUN_NAME

Twelve real solves, 44 cross-method rows, 44 refinement rows, and independent
manufactured checks. Full inputs/reports stay in ignored artifacts; the compact
public evidence preserves hashes, requests, actual meshes, metrics and failures.
This script does not rerun or reinterpret the existing nineteen reference cases.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import subprocess
import time
import traceback

import numpy as np
import scipy

from earth_modes.data import bundle_hash, canonical_hash, mass_integral, model_hash, validate_bundle
from earth_modes.models import homogeneous_model, prem_model
from earth_modes.solver import solve
from earth_modes.experimental import solve_toroidal

ROOT = Path(__file__).resolve().parents[1]
EPS = np.finfo(float).eps
LABELS = ((1, 1), (0, 2), (1, 2), (2, 2), (3, 2), (0, 3), (0, 4))
PREM_LABELS = ((1, 1), (0, 2), (0, 3), (0, 4))


def require(condition, message):
    """Audit gates remain active even when Python is launched with -O."""
    if not condition:
        raise AssertionError(message)


def close(actual, expected, *, atol=1e-12, rtol=1e-12, label='value'):
    require(math.isfinite(actual) and math.isclose(actual, expected, abs_tol=atol, rel_tol=rtol),
            f'{label}: actual={actual!r}, independent expected={expected!r}')


def encode(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode('utf-8')


def write_json(path, value):
    data = encode(value)
    path.write_bytes(data)
    return dict(path=str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path),
                bytes=len(data), sha256=hashlib.sha256(data).hexdigest(), canonical_hash=canonical_hash(value))


def shell_model():
    model = homogeneous_model(1e6, 4000, 8000, 4000)
    fluid = deepcopy(model['layers'][0]); solid = deepcopy(fluid)
    fluid.update(id='fluid', name='Fluid interior', phase='fluid', r_m=[0., 3e5], vs_m_s=[0., 0.])
    solid.update(id='shell', name='Solid shell', r_m=[3e5, 1e6])
    model.update(id='pilot-shell', name='Homogeneous traction-free shell', layers=[fluid, solid])
    return model


def explicit_ids(model, labels):
    """Expected physical domains come from model topology, never returned modes."""
    domains = []
    previous_solid = False
    for layer in model['layers']:
        if layer['phase'] == 'fluid':
            previous_solid = False
        else:
            if not previous_solid:
                domains.append([])
            domains[-1].append(layer['id'])
            previous_solid = True
    return [f'T{n}_{degree}:solid:{",".join(domain)}' for domain in domains for n, degree in labels]


def oracle(model, a, b):
    """Independent analytic polynomial integration, not Gaussian quadrature.

    Work in interval-local t in [0,1]. Interpolate endpoint values using the
    original regional arrays, multiply polynomials in extended precision, and
    integrate each coefficient analytically. No agreement implementation helper
    or FE basis is called. Material sides and tolerated clamped tails are kept.
    """
    ld = np.longdouble
    partitions = []
    aa = []; bb = []; ab = []

    def integral(weight, left, right):
        coefficients = np.convolve(weight, np.convolve(left, right))
        return np.sum(coefficients / np.arange(1, len(coefficients)+1, dtype=ld), dtype=ld)

    for layer in model['layers']:
        ar = next((r for r in a['regions'] if r['layer_id'] == layer['id']), None)
        if ar is None:
            continue
        br = next(r for r in b['regions'] if r['layer_id'] == layer['id'])
        lo, hi = layer['r_m'][0], layer['r_m'][-1]
        nodes = sorted(set([lo, hi] + [r for grid in (layer['r_m'], ar['r_m'], br['r_m'])
                                             for r in grid if lo < r < hi]))
        av = np.interp(nodes, ar['r_m'], ar['w']).astype(ld)
        bv = np.interp(nodes, br['r_m'], br['w']).astype(ld)
        density = np.interp(nodes, layer['r_m'], layer['rho_kg_m3']).astype(ld)
        for i, (left, right) in enumerate(zip(nodes, nodes[1:])):
            r0 = ld(left); h = ld(right) - r0
            weight = h*np.convolve([density[i], density[i+1]-density[i]], [r0*r0, 2*r0*h, h*h])
            ap = np.array([av[i], av[i+1]-av[i]], dtype=ld)
            bp = np.array([bv[i], bv[i+1]-bv[i]], dtype=ld)
            aa.append(integral(weight, ap, ap)); bb.append(integral(weight, bp, bp)); ab.append(integral(weight, ap, bp))
            partitions.append((weight, ap, bp))
    A = np.sum(aa, dtype=ld); B = np.sum(bb, dtype=ld); C = np.sum(ab, dtype=ld)
    require(A > 0 and B > 0, 'Independent oracle requires positive norms')
    c = C / np.sqrt(A*B)
    indeterminate = abs(c) <= 64*EPS
    sign = 1 if indeterminate or c >= 0 else -1
    residuals = []
    for weight, ap, bp in partitions:
        residual = ap / np.sqrt(A) - sign*bp / np.sqrt(B)
        residuals.append(integral(weight, residual, residual))
    d2 = np.sum(residuals, dtype=ld)
    require(d2 >= 0, f'Independent polynomial residual became negative: {d2}')
    return dict(reference_continuous_norm=float(A), candidate_continuous_norm=float(B),
                signed_overlap=float(c), overlap=float(abs(c)), alignment_sign=sign,
                alignment_indeterminate=bool(indeterminate), shape_distance=float(np.sqrt(d2)))


class Audit:
    def __init__(self, api, artifacts, evidence):
        self.api = api
        self.artifacts = artifacts
        self.evidence = evidence

    def report(self, name, a, b, ids=None, kind='manufactured', gate=False):
        ids = ids or [[a['modes'][0]['id'], b['modes'][0]['id']]]
        before = [bundle_hash(a), bundle_hash(b)]
        report = self.api.toroidal_agreement(a, b, ids)
        require(self.api.validate_agreement(report) is report, f'{name}: validator must return original mapping')
        require([bundle_hash(a), bundle_hash(b)] == before, f'{name}: input mutation')
        require(report['pairs'] == ids, f'{name}: pair order changed')
        require(len(report['rows']) == len(ids), f'{name}: missing or extra rows')
        require(report['model_hash'] == model_hash(a['model']) == model_hash(b['model']), f'{name}: wrong model hash')
        for role, source, expected in zip(('reference', 'candidate'), (a, b), before):
            require(report['sources'][role]['bundle_hash'] == expected, f'{name}: source hash')
            require(report['sources'][role]['bundle'] == source, f'{name}: source content altered')
        row_evidence = []
        lookups = [{m['id']: m for m in bundle['modes']} for bundle in (a, b)]
        for index, (pair, row) in enumerate(zip(ids, report['rows'])):
            ma, mb = [lookup[identity] for lookup, identity in zip(lookups, pair)]
            expected = oracle(a['model'], ma, mb)
            for key in ('reference_continuous_norm', 'candidate_continuous_norm', 'signed_overlap', 'overlap', 'shape_distance'):
                close(row[key], expected[key], label=f'{name}/{index}/{key}')
            require(row['alignment_sign'] == expected['alignment_sign'], f'{name}: oracle alignment sign')
            require(row['alignment_indeterminate'] == expected['alignment_indeterminate'], f'{name}: oracle alignment flag')
            require(row['pair_index'] == index, f'{name}: wrong index')
            require(row['delta_frequency_hz'] == mb['frequency_hz'] - ma['frequency_hz'], f'{name}: subtraction order')
            require(row['relative_frequency_change'] == (mb['frequency_hz']-ma['frequency_hz'])/ma['frequency_hz'], f'{name}: relative difference')
            require(row['radial_label_mismatch'] == (ma['n'] != mb['n']), f'{name}: n mismatch')
            layer_ids = [layer['id'] for layer in a['model']['layers'] if any(r['layer_id'] == layer['id'] for r in ma['regions'])]
            require(row['layer_ids'] == layer_ids, f'{name}: support order')
            for role, bundle, mode in zip(('reference', 'candidate'), (a, b), (ma, mb)):
                counts = bundle['provenance'].get('effective_settings', {}).get('mesh_counts', {})
                require(row[f'{role}_mesh_elements'] == {layer: counts.get(layer) for layer in layer_ids}, f'{name}: guessed/wrong mesh counts')
                require(row[f'{role}_radial_samples'] == {r['layer_id']: len(r['r_m']) for r in mode['regions']}, f'{name}: wrong sample counts')
            if gate:
                require(abs(row['relative_frequency_change']) <= 1e-4, f'{name}/{pair}: frequency regression gate')
                require(row['shape_distance'] <= .003, f'{name}/{pair}: shape regression gate')
            row_evidence.append(dict(row=row, independent_polynomial=expected))
        artifact = write_json(self.artifacts / f'{name}.json', report)
        loaded = self.api.load_agreement(self.artifacts / f'{name}.json')
        require(canonical_hash(loaded) == canonical_hash(report), f'{name}: reload changed report')
        self.evidence['reports'].append(dict(name=name, kind=kind, model_hash=report['model_hash'],
            reference_bundle_hash=before[0], candidate_bundle_hash=before[1], artifact=artifact, rows=row_evidence))
        return report

    def reject(self, name, operation):
        try:
            operation()
        except ValueError as error:
            self.evidence['counterexamples'].append(dict(name=name, outcome='rejected', error_type=type(error).__name__, message=str(error)))
        else:
            raise AssertionError(f'{name}: expected ValueError, operation was accepted')

    def check(self, name, **details):
        self.evidence['counterexamples'].append(dict(name=name, outcome='checked', **details))


def fixture(model, regions, *, n=0, frequency=.001, domain='manufactured-domain'):
    mode = dict(id=f'T{n}_2', family='T', n=n, l=2, frequency_hz=frequency, q=None,
        normalization='mass_integral_1', regions=[], provenance=dict(solver='Manufactured audit field; not a computed eigenmode',
        solid_domain_id=domain, quality=dict(status='unverified', mesh_convergence=None, benchmark=None, warnings=['Manufactured independent metric fixture.'])))
    for layer_id, radius, values in regions:
        mode['regions'].append(dict(layer_id=layer_id, r_m=list(radius), u=[0.]*len(radius), v=[0.]*len(radius), w=list(values)))
    bundle = dict(schema_version='1.0', model=deepcopy(model), modes=[mode], provenance=dict(audit_fixture=True))
    normalize(bundle)
    return validate_bundle(bundle)


def normalize(bundle):
    mode = bundle['modes'][0]
    factor = 1/math.sqrt(mass_integral(bundle['model'], mode))
    for region in mode['regions']:
        region['w'] = [v*factor for v in region['w']]
    return bundle


def manufactured(audit):
    api = audit.api
    model = homogeneous_model(1., 1., 4., 1.)
    a = fixture(model, [('sphere', [0., 1.], [0., 1.])])
    b = fixture(model, [('sphere', [0., .5, 1.], [0., .5, 1.])])
    same = audit.report('same-linear-different-discrete-norm', a, b)
    close(same['rows'][0]['shape_distance'], 0., atol=1e-14)
    require(not math.isclose(same['rows'][0]['reference_continuous_norm'], same['rows'][0]['candidate_continuous_norm']), 'Fixture must have unequal continuous norms')
    negative = deepcopy(b)
    negative['modes'][0]['regions'][0]['w'] = [-v for v in negative['modes'][0]['regions'][0]['w']]
    flip = audit.report('global-sign', a, negative)
    require(flip['rows'][0]['alignment_sign'] == -1, 'Global sign was not removed')
    close(flip['rows'][0]['shape_distance'], 0., atol=1e-14)
    audit.check('valid-canonical-grid-and-global-sign-invariance')

    density_model = deepcopy(model)
    density_model['layers'][0].update(r_m=[0., 1/3, 1.], rho_kg_m3=[1., 9., 1.], vp_m_s=[4.]*3, vs_m_s=[1.]*3)
    da = fixture(density_model, [('sphere', [0., 1.], [0., 1.])])
    db = fixture(density_model, [('sphere', [0., .5, 1.], [0., .25, 1.])])
    density = audit.report('density-knot-versus-field-knots', da, db)
    AA = Fraction(727, 1215); BB = Fraction(64007, 155520); AB = Fraction(75931, 155520)
    expected = math.sqrt(2-2*float(AB)/math.sqrt(float(AA*BB)))
    close(density['rows'][0]['shape_distance'], expected)
    knots = api.agreement_curves(density, 0)[0]['r_m']
    require(knots == [0., 1/3, .5, 1.], 'Density-only knot omitted from curve partition')
    audit.check('independent-rational-density-knot', AA=str(AA), BB=str(BB), AB=str(AB), expected_distance=expected)

    layered = deepcopy(model)
    inner = deepcopy(layered['layers'][0]); outer = deepcopy(inner)
    inner.update(id='inner', r_m=[0., .5], rho_kg_m3=[91/11]*2)
    outer.update(id='outer', r_m=[.5, 1.])
    layered['layers'] = [inner, outer]
    la = fixture(layered, [('inner', [0., .25, .5], [0., 1., 0.]), ('outer', [.5, .75, 1.], [0., 1., 0.])])
    lb = fixture(layered, [('inner', [0., .25, .5], [0., 1., 0.]), ('outer', [.5, .75, 1.], [0., -1., 0.])])
    opposite = audit.report('density-interface-one-global-sign', la, lb)
    row = opposite['rows'][0]
    close(row['signed_overlap'], 0., atol=64*EPS)
    close(row['shape_distance'], math.sqrt(2))
    require(row['alignment_indeterminate'] and row['alignment_sign'] == 1, 'Orthogonal alignment must be fixed+1 and indeterminate')
    curves = api.agreement_curves(opposite, 0)
    require(len(curves) == 2 and curves[0]['r_m'][-1] == curves[1]['r_m'][0] == .5, 'Material sides lost')
    for curve in curves:
        require(np.allclose(np.asarray(curve['residual_w']), np.asarray(curve['reference_w'])-np.asarray(curve['candidate_w']), rtol=0, atol=0), 'Residual orientation or independent layer alignment')
    audit.check('independent-rational-interface', inner_mass_factor='11/960', outer_mass_factor='91/960', inner_outer_density_ratio='91/11')

    partial = fixture(layered, [('outer', [.5, .75, 1.], [0., 1., 0.])])
    audit.reject('same-incomplete-connected-support', lambda: api.toroidal_agreement(partial, partial, [['T0_2', 'T0_2']]))
    separated = deepcopy(model)
    si = deepcopy(inner); fluid = deepcopy(inner); so = deepcopy(outer)
    si.update(r_m=[0., .3], rho_kg_m3=[1., 1.]); fluid.update(id='fluid', phase='fluid', r_m=[.3, .6], rho_kg_m3=[1., 1.], vs_m_s=[0., 0.]); so.update(r_m=[.6, 1.])
    separated['layers'] = [si, fluid, so]
    ia = fixture(separated, [('inner', [0., .3], [0., 1.])], domain='forged-equal-domain')
    ob = fixture(separated, [('outer', [.6, 1.], [1., 2.])], domain='forged-equal-domain')
    audit.reject('forged-domain-label', lambda: api.toroidal_agreement(ia, ob, [['T0_2', 'T0_2']]))

    mismatch = deepcopy(b); mismatch['modes'][0].update(id='T1_2', n=1)
    labels = audit.report('explicit-different-n', a, mismatch)
    require(labels['rows'][0]['radial_label_mismatch'], 'Different n silently relabelled')
    tiny = fixture(model, [('sphere', [0., .5, 1.], [0., .5+1e-9, 1.])])
    small = audit.report('tiny-direct-residual', b, tiny)
    require(1e-12 < small['rows'][0]['shape_distance'] < 1e-8, 'Tiny real residual erased or exaggerated')
    frequency = deepcopy(b); frequency['modes'][0]['frequency_hz'] += 4e-15
    delta = audit.report('tiny-frequency-delta', b, frequency)
    require(delta['rows'][0]['delta_frequency_hz'] != 0, 'Representable frequency delta erased')
    audit.check('small-shape-and-frequency', shape_distance=small['rows'][0]['shape_distance'], delta_hz=delta['rows'][0]['delta_frequency_hz'])

    # Shell endpoints permit both outward and inward offsets, including at the
    # inner endpoint; a sphere cannot have a negative radius.
    unit_shell = deepcopy(separated)
    unit_shell['layers'] = [dict(fluid, id='fluid', r_m=[0., .6]), so]
    reference = fixture(unit_shell, [('outer', [.6, .8, 1.], [1., 1.5, 2.])])
    for name, radii in [('inward', [.6+16*EPS, .8, 1.-16*EPS]), ('outward', [.6-16*EPS, .8, 1.+16*EPS])]:
        candidate = fixture(unit_shell, [('outer', radii, [1., 1.5, 2.])])
        result = audit.report(f'endpoint-{name}', reference, candidate)
        shape = api.agreement_curves(result, 0)[0]
        require(shape['r_m'][0] == .6 and shape['r_m'][-1] == 1., 'Integration must use model boundaries')
        expected = np.interp(shape['r_m'], radii, candidate['modes'][0]['regions'][0]['w']) / math.sqrt(result['rows'][0]['candidate_continuous_norm']) * result['rows'][0]['alignment_sign']
        require(np.allclose(shape['candidate_w'], expected, rtol=1e-12, atol=1e-14), 'Endpoint relocated instead of original interpolation')
    outside = deepcopy(reference); outside['modes'][0]['regions'][0]['r_m'][0] += 128*EPS
    audit.reject('outside-endpoint-tolerance', lambda: api.toroidal_agreement(reference, outside, [['T0_2', 'T0_2']]))
    renamed = deepcopy(a); renamed['model']['name'] += ' renamed'
    audit.reject('different-canonical-model', lambda: api.toroidal_agreement(a, renamed, [['T0_2', 'T0_2']]))
    zero = deepcopy(a); zero['modes'][0]['regions'][0]['w'] = [0., 0.]
    audit.reject('zero-norm', lambda: api.toroidal_agreement(a, zero, [['T0_2', 'T0_2']]))
    invalid = deepcopy(a); invalid['modes'][0]['regions'][0]['w'][1] = float('nan')
    audit.reject('nonfinite-field', lambda: api.toroidal_agreement(a, invalid, [['T0_2', 'T0_2']]))

    for name, effective in [('reference', {'reference': 'bundle.model'}),
                            ('embedded', {'model': deepcopy(model), 'model_hash': model_hash(model)})]:
        declared = deepcopy(b); declared['provenance']['effective_model'] = effective
        audit.report(f'elastic-effective-{name}', a, declared)
    for name, change in [('linear-q', {'request': {'linear_q': True}}),
                         ('malformed-linear-q', {'request': {'linear_q': 'false'}}),
                         ('stale-effective-hash', {'effective_model': {'reference': 'bundle.model', 'model_hash': '0'*64}}),
                         ('unknown-effective-reference', {'effective_model': {'reference': 'elsewhere'}}),
                         ('hash-only-effective', {'effective_model': {'model_hash': model_hash(model)}})]:
        bad = deepcopy(b); bad['provenance'].update(change)
        audit.reject(name, lambda bad=bad: api.toroidal_agreement(a, bad, [['T0_2', 'T0_2']]))
    effective_changed = deepcopy(model); effective_changed['layers'][0]['rho_kg_m3'] = [2., 2.]
    bad = deepcopy(b); bad['provenance']['effective_model'] = {'model': effective_changed, 'model_hash': model_hash(effective_changed)}
    audit.reject('declared-effective-model-conflict', lambda: api.toroidal_agreement(a, bad, [['T0_2', 'T0_2']]))
    for name, field, value in [('negative-distance', 'shape_distance', -1e-15),
                               ('overlap-outside-range', 'overlap', 1+1e-13),
                               ('bool-number', 'shape_distance', False),
                               ('wrong-norm', 'reference_continuous_norm', 2.)]:
        tampered = deepcopy(same); tampered['rows'][0][field] = value
        audit.reject(name, lambda tampered=tampered: api.validate_agreement(tampered))
    erased = deepcopy(delta); erased['rows'][0]['delta_frequency_hz'] = 0.
    audit.reject('erased-small-frequency', lambda: api.validate_agreement(erased))
    mutated = deepcopy(same); mutated['sources']['reference']['bundle']['provenance']['extra'] = 'tampered'
    audit.reject('source-hash-tamper', lambda: api.validate_agreement(mutated))


def physical_matrix(audit):
    solve_count = 0; cross_rows = 0; refinement_rows = 0
    for name, model, meshes, labels in [('sphere', homogeneous_model(1e6, 4000, 8000, 4000), (40, 80), LABELS),
                                       ('shell', shell_model(), (40, 80), LABELS),
                                       ('prem', prem_model(), (140, 280), PREM_LABELS)]:
        identities = explicit_ids(model, labels)
        require(len(identities) == (8 if name == 'prem' else 7), f'{name}: expected identity matrix changed')
        pairs = [[identity, identity] for identity in identities]
        saved = {}
        for mesh in meshes:
            for method in ('default', 'owned'):
                request = dict(l_min=1, l_max=4, frequency_min_hz=1e-8, frequency_max_hz=.012, mesh_size=mesh)
                if method == 'default':
                    request.update(families=['T'], n_max=3, gravity=0)
                    bundle = solve(model, **request)
                else:
                    bundle = solve_toroidal(model, **request)
                solve_count += 1
                lookup = {m['id']: m for m in bundle['modes']}
                for identity in identities:
                    require(identity in lookup, f'{name}/{method}/{mesh}: required branch absent: {identity}')
                saved[method, mesh] = bundle
                counts = bundle['provenance']['effective_settings']['mesh_counts']
                domains = {}
                for identity in identities:
                    mode = lookup[identity]
                    domain = identity.split(':', 1)[1]
                    domains[domain] = dict(elements=sum(counts[r['layer_id']] for r in mode['regions']),
                        per_layer_elements={r['layer_id']: counts[r['layer_id']] for r in mode['regions']},
                        regional_radial_samples={r['layer_id']: len(r['r_m']) for r in mode['regions']})
                audit.evidence['solves'].append(dict(case=name, method=method, mesh_target=mesh, request=request,
                    model_hash=model_hash(model), bundle_hash=bundle_hash(bundle), mode_count=len(bundle['modes']),
                    expected_mode_ids=identities, domains=domains,
                    artifact=write_json(audit.artifacts/f'{name}-{method}-{mesh}-bundle.json', bundle)))
            audit.report(f'{name}-cross-{mesh}', saved['default', mesh], saved['owned', mesh], pairs, kind='cross_method', gate=True)
            cross_rows += len(pairs)
        for method in ('default', 'owned'):
            audit.report(f'{name}-{method}-refinement', saved[method, meshes[0]], saved[method, meshes[1]], pairs, kind='refinement', gate=True)
            refinement_rows += len(pairs)
    require((solve_count, cross_rows, refinement_rows) == (12, 44, 44), 'Incomplete physical matrix')
    audit.evidence['matrix_counts'] = dict(solves=solve_count, cross_method_rows=cross_rows, refinement_rows=refinement_rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--integration', required=True, help='Coordinator-accepted full integration commit; must equal current HEAD')
    parser.add_argument('--artifacts', type=Path, required=True, help='New audit output directory, never overwritten')
    args = parser.parse_args()
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    require(len(args.integration) == 40 and args.integration == head, 'Await accepted integration I; --integration must equal full current HEAD')
    require(os.environ.get('OPENBLAS_NUM_THREADS') == '1', 'Run this audit with OPENBLAS_NUM_THREADS=1')
    dirty_runtime = subprocess.run(['git', 'diff', '--quiet', 'HEAD', '--', 'packages/earth_modes'], cwd=ROOT).returncode
    require(dirty_runtime == 0, 'Runtime sources differ from accepted integration I')
    # Import the new public API only after the accepted integration guard.
    import earth_modes
    from earth_modes import agreement
    expected_package = (ROOT/'packages/earth_modes').resolve()
    imported_package = Path(earth_modes.__file__).resolve()
    require(imported_package == expected_package/'__init__.py', 'earth_modes import is not bound to accepted primary source')
    require(Path(agreement.__file__).resolve() == expected_package/'agreement.py', 'agreement import is not bound to accepted primary source')
    runtime_identity = dict(imported_package=str(imported_package), imported_agreement=str(Path(agreement.__file__).resolve()),
        files={str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in (
            expected_package/'__init__.py', expected_package/'agreement.py', expected_package/'data.py',
            expected_package/'models.py', expected_package/'solver.py', expected_package/'experimental/toroidal.py',
            expected_package/'assets/schema/agreement.schema.json')})

    artifacts = args.artifacts.resolve()
    artifacts.mkdir(parents=True, exist_ok=False)
    started = time.perf_counter()
    evidence = dict(schema_version='1.0', status='running', integration_commit=head,
        recorded_utc=datetime.now(timezone.utc).isoformat(), runtime_identity=runtime_identity, script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        environment=dict(python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__, platform=platform.platform(), openblas_threads=1),
        scope='Independent audit of canonical elastic T agreement; no new continuum accuracy or solver promotion claim.',
        oracle='Layer-local polynomial antiderivatives in longdouble, independently of the production Gaussian rule.',
        gates=dict(named_relative_frequency_change=1e-4, named_shape_distance=.003, expected_solves=12, expected_cross_rows=44, expected_refinement_rows=44),
        retained_reference=dict(path='docs/validation/owned-toroidal.json', sha256=hashlib.sha256((ROOT/'docs/validation/owned-toroidal.json').read_bytes()).hexdigest(),
            case_count=19, rerun=False, scope='Original independent references and original shape measure retained without reinterpretation.'),
        solves=[], reports=[], counterexamples=[])
    audit = Audit(agreement, artifacts, evidence)
    try:
        manufactured(audit)
        physical_matrix(audit)
        evidence['status'] = 'passed'
    except Exception as error:
        evidence['status'] = 'failed'
        evidence['failure'] = dict(type=type(error).__name__, message=str(error), traceback=traceback.format_exc())
        raise
    finally:
        evidence['runtime_s'] = time.perf_counter()-started
        write_json(artifacts/'audit-summary.json', evidence)
        (ROOT/'docs/validation/agreement.json').write_bytes(encode(evidence))
        print(json.dumps(dict(status=evidence['status'], integration_commit=head,
            counts=evidence.get('matrix_counts'), counterexamples=len(evidence['counterexamples']), artifacts=str(artifacts)), indent=2))


if __name__ == '__main__':
    main()
