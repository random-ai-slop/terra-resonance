"""Material-sided radial sampling for the canonical piecewise-linear field.

The display may add samples but must not discard knots of an active radial
coefficient. At fixed angle, each Cartesian or spherical component of a modal
sum is linear between the union knots. Endpoint sign tests therefore find all
isolated roots of the represented field; a zero plateau remains a plateau.
No assertion about unresolved oscillations in the original continuous solution
is made by this sampling rule.
"""
from __future__ import annotations

import math
import numpy as np

from .data import validate_terms


def layer_radial_nodes(bundle, terms, radius_fraction=1.0, base_intervals=24, *, max_nodes=None):
    """Return ``[(layer_id, dimensionless_radii), ...]`` for a radial section.

    Each layer gets its own complete boundary pair. The knots are the union of
    every nonzero-amplitude term's region samples, a coarse presentation grid,
    and material/truncation boundaries. Source endpoints are excluded from the
    interior selection, so both sides retain their own exact boundary values.
    ``max_nodes`` optionally bounds the total *radial* node count; the renderer
    must still check its angular vertex product and field-cache memory before
    constructing geometry. No decimation or silent budget adaptation occurs.

    Extra midpoints are unnecessary to preserve roots of the contract's linear
    radial interpolation. Angular triangulation and visible contour accuracy
    remain separate renderer responsibilities.
    """
    validate_terms(terms, bundle)
    if isinstance(radius_fraction, bool) or not isinstance(radius_fraction, (int, float)) or not math.isfinite(radius_fraction) or not 0 < radius_fraction <= 1:
        raise ValueError('radius_fraction must be finite in (0,1]')
    if isinstance(base_intervals, bool) or not isinstance(base_intervals, (int, np.integer)) or base_intervals < 1:
        raise ValueError('base_intervals must be a positive integer')
    if max_nodes is not None and (isinstance(max_nodes, bool) or not isinstance(max_nodes, (int, np.integer)) or max_nodes < 2):
        raise ValueError('max_nodes must be null or an integer >=2')
    lookup = {mode['id']: mode for mode in bundle['modes']}
    regions = {}
    for mode_id in {term['mode_id'] for term in terms if term['amplitude'] != 0}:
        for region in lookup[mode_id]['regions']:
            regions.setdefault(region['layer_id'], []).append(region['r_m'])
    radius = bundle['model']['radius_m']
    display = np.linspace(0.0, radius_fraction, int(base_intervals) + 1)
    result = []
    count = 0
    for layer in bundle['model']['layers']:
        lower = layer['r_m'][0] / radius
        upper = min(layer['r_m'][-1] / radius, radius_fraction)
        if upper <= lower:
            continue
        nodes = np.r_[lower, display[(display > lower) & (display < upper)], upper]
        for source in regions.get(layer['id'], []):
            source = np.asarray(source, dtype=float) / radius
            interior = source[(source > lower) & (source < upper)]
            nodes = np.union1d(nodes, interior)
            if max_nodes is not None and count + len(nodes) > max_nodes:
                raise ValueError('Radial source-knot budget exceeded; reduce active modes or raise the explicit limit, not radial fidelity')
        nodes = np.unique(nodes)
        count += len(nodes)
        if max_nodes is not None and count > max_nodes:
            raise ValueError('Radial node budget exceeded before angular mesh construction')
        result.append((layer['id'], nodes))
    return result
