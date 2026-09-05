"""SI quadratic finite elements for elastic, isotropic toroidal modes.

The independently assembled weak form is
K(W,Z) = integral mu*((r*W'-W)*(r*Z'-Z) + (l*(l+1)-2)*W*Z) dr,
M(W,Z) = integral rho*r**2*W*Z dr.
Natural endpoints have zero shear traction; the center imposes W(0)=0.
There is no dependency on the attributed Ouroboros implementation.
"""
from __future__ import annotations

from copy import deepcopy
import math

import numpy as np
from scipy.linalg import cholesky, eigh, solve_triangular

from ..data import model_hash, validate_bundle, validate_model

METHOD = "Terra experimental SI quadratic toroidal FEM v1"


def _options(l_min, l_max, mesh_size, frequency_min_hz, frequency_max_hz, memory_mib):
    for name, value in (("l_min", l_min), ("l_max", l_max), ("mesh_size", mesh_size)):
        if type(value) is not int or not 1 <= value <= 2**53-1:
            raise ValueError(f"{name} must be a positive JSON-safe integer")
    if not 1 <= l_min <= l_max <= 64:
        raise ValueError("degree bounds must satisfy 1 <= l_min <= l_max <= 64")
    for name, value in (("frequency_min_hz", frequency_min_hz), ("frequency_max_hz", frequency_max_hz), ("memory_mib", memory_mib)):
        if isinstance(value, bool) or not isinstance(value, (float, int)) or not math.isfinite(value):
            raise ValueError(f"{name} must be finite")
    if not 0 <= frequency_min_hz < frequency_max_hz:
        raise ValueError("frequency bounds must satisfy 0 <= frequency_min_hz < frequency_max_hz")
    if memory_mib <= 0:
        raise ValueError("memory_mib must be positive")


def _plan(model, target, degree_count, budget):
    """Count mandatory knot intervals before allocating a dense matrix or mesh."""
    total = sum(a['r_m'][-1] - a['r_m'][0] for a in model['layers'] if a['phase'] == 'solid')
    domains = []
    previous_solid = False
    for layer in model['layers']:
        if layer['phase'] == 'fluid':
            previous_solid = False
            continue
        counts = [max(1, math.ceil(target * ((b-a)/total))) for a,b in zip(layer['r_m'],layer['r_m'][1:])]
        item = dict(layer=layer, counts=counts)
        if previous_solid:
            domains[-1].append(item)
        else:
            domains.append([item])
        previous_solid = True
    dimensions = [2*sum(sum(a['counts']) for a in domain)+1 for domain in domains]
    # Matrices/workspaces plus conservative accumulated Python region output.
    estimate = 128*max(dimensions,default=0)**2 + 160*degree_count*sum(n*n for n in dimensions)
    if estimate > budget*1024**2:
        raise ValueError(f"Toroidal pilot estimated memory {estimate} bytes exceeds memory_mib; mandatory profile knots cannot be dropped")
    return domains, estimate


def _assemble(domain, degree):
    """Four Gauss points integrate degree-seven SI material/basis products."""
    edges = []
    owners = []
    for item in domain:
        layer = item['layer']
        for a,b,count in zip(layer['r_m'],layer['r_m'][1:],item['counts']):
            local = np.linspace(a,b,count+1)
            edges.extend(local if not edges else local[1:])
            owners.extend([layer]*count)
    edges = np.asarray(edges)
    nodes = np.empty(2*len(edges)-1)
    nodes[::2] = edges
    nodes[1::2] = (edges[:-1]+edges[1:])/2
    if np.any(np.diff(nodes) <= 0):
        raise ValueError("Requested toroidal mesh cannot be resolved in floating-point radii")
    dimension = len(nodes)
    K = np.zeros((dimension,dimension)); M = np.zeros_like(K)
    x, weights = np.polynomial.legendre.leggauss(4)
    basis = np.column_stack((x*(x-1)/2, 1-x*x, x*(x+1)/2))
    derivative = np.column_stack((x-.5, -2*x, x+.5))
    for e,layer in enumerate(owners):
        a,b = edges[e:e+2]; half = (b-a)/2
        radius = (a+b)/2 + half*x
        rho = np.interp(radius,layer['r_m'],layer['rho_kg_m3'])
        vs = np.interp(radius,layer['r_m'],layer['vs_m_s'])
        mu = rho*vs*vs
        shear = radius[:,None]*derivative/half-basis
        stiffness = shear.T @ ((weights*half*mu)[:,None]*shear)
        stiffness += (degree*(degree+1)-2)*basis.T @ ((weights*half*mu)[:,None]*basis)
        mass = basis.T @ ((weights*half*rho*radius**2)[:,None]*basis)
        index = np.arange(2*e,2*e+3)
        K[np.ix_(index,index)] += stiffness
        M[np.ix_(index,index)] += mass
    active = np.arange(1 if nodes[0] == 0 else 0, dimension)
    return nodes, K[np.ix_(active,active)], M[np.ix_(active,active)], active


def _eigenpairs(K, M, radius, degree):
    """Remove only the known l=1 null coordinate in mass-whitened space."""
    knorm = float(np.linalg.norm(K)); mnorm = float(np.linalg.norm(M))
    symmetry = dict(stiffness=float(np.linalg.norm(K-K.T)/knorm), mass=float(np.linalg.norm(M-M.T)/mnorm))
    if max(symmetry.values()) > 1e-12:
        raise RuntimeError("Toroidal matrices lost symmetry")
    L = cholesky(M, lower=True)
    null = None
    if degree == 1:
        rigid = radius / max(radius)
        residual = float(np.linalg.norm(K@rigid)/(knorm*np.linalg.norm(rigid)))
        if residual > 1e-12:
            raise RuntimeError("Rigid toroidal rotation does not lie in the stiffness null space")
        transformed = solve_triangular(L,K,lower=True)
        transformed = solve_triangular(L,transformed.T,lower=True).T
        q = L.T@rigid; q /= np.linalg.norm(q)
        # A Householder reflection maps q to +/-e0. Remaining columns span
        # its orthogonal complement without a frequency-dependent cutoff.
        h = q.copy(); h[0] += math.copysign(1.,q[0]); h /= np.linalg.norm(h)
        complement = np.eye(len(q))[:,1:] - 2*np.outer(h,h[1:])
        reduced = complement.T@transformed@complement
        values, vectors = eigh((reduced+reduced.T)/2,driver='evd')
        vectors = solve_triangular(L.T,complement@vectors,lower=False)
        gap = float(values[0]/np.linalg.norm(transformed))
        if gap <= 64*np.finfo(float).eps*len(q):
            raise RuntimeError("Additional or numerically unresolved toroidal null space; refine or rescale the model")
        null = dict(expected_multiplicity=1, removed_multiplicity=1, scaled_stiffness_residual=residual,
                    first_positive_relative_gap=gap, shape='W proportional to r', method='mass-whitened Householder complement')
    else:
        values, vectors = eigh(K,M,driver='gvd')
    if not np.all(np.isfinite(values)) or np.any(values <= 0):
        raise RuntimeError("Toroidal positive subspace contains a nonpositive or nonfinite eigenvalue")
    residuals = np.linalg.norm(K@vectors-(M@vectors)*values,axis=0)/((knorm+values*mnorm)*np.linalg.norm(vectors,axis=0))
    orthogonality = float(np.max(np.abs(vectors.T@M@vectors-np.eye(len(values)))))
    if np.max(residuals) > 1e-9 or orthogonality > 1e-8:
        raise RuntimeError("Toroidal eigenpairs failed discrete residual or mass-orthogonality gates")
    diagnostics = dict(symmetry_relative=symmetry,mass_spd=True,
        maximum_scaled_residual=float(np.max(residuals)),mass_orthogonality_defect=orthogonality,
        residual_definition='norm(Kx-lambda Mx)/((norm(K,F)+abs(lambda)*norm(M,F))*norm(x))',
        normalization='constrained FE mass; distinct from exported trapezoid mass',rigid_rotation=null)
    return values, vectors, residuals, diagnostics


def _regions(domain, radius, vector):
    regions = []; integral = 0.
    for item in domain:
        layer = item['layer']; lo,hi = layer['r_m'][0],layer['r_m'][-1]
        selected = (radius >= lo) & (radius <= hi)
        r = radius[selected]; w = vector[selected]
        rho = np.interp(r,layer['r_m'],layer['rho_kg_m3'])
        integral += float(np.trapezoid(rho*r*r*w*w,r))
        regions.append(dict(layer_id=layer['id'],r_m=r.tolist(),u=np.zeros(len(r)).tolist(),v=np.zeros(len(r)).tolist(),w=w))
    if not math.isfinite(integral) or integral <= 0:
        raise RuntimeError("Invalid toroidal exported mass integral")
    factor = 1/math.sqrt(integral)
    # Fix one global sign for reproducible presentation; no per-layer scaling.
    largest = max((float(x) for r in regions for x in r['w']),key=abs)
    sign = 1. if largest >= 0 else -1.
    for region in regions:
        region['w'] = (region['w']*factor*sign).tolist()
    return regions, dict(source='SI generalized FE mass eigenvector',quadrature='layerwise trapezoid on exported quadratic nodes',
        pre_rescale_integral=integral,rescale_factor=factor,global_sign=sign,displacement_units='kg^(-1/2)',
        reconstruction='piecewise linear between exported nodes; FE diagnostics use quadratic basis')


def solve_toroidal(model, *, l_min=1, l_max=4, mesh_size=80, frequency_min_hz=0.0, frequency_max_hz=0.01, memory_mib=512):
    """Return an elastic experimental ModeBundle without invoking the default solver.

    All supplied radial profile knots are mandatory; ``mesh_size`` is a target
    for the combined solid domains. Density and shear speed are interpolated
    linearly within each layer. Frequencies are positive and filtered inclusively.
    The l=1 rigid rotation reserves n=0; positive l=1 branches start at n=1.
    Model Q is retained but not applied. This pilot has no self-gravity parameter
    because isotropic toroidal modes do not redistribute mass.
    """
    _options(l_min,l_max,mesh_size,frequency_min_hz,frequency_max_hz,memory_mib)
    validate_model(model)
    plans, estimate = _plan(model,mesh_size,l_max-l_min+1,memory_mib)
    modes = []; groups = []
    if not plans:
        for degree in range(l_min,l_max+1):
            groups.append(dict(family='T',l=degree,solid_domain_id=None,status='not_applicable',matrix_dimension=0,
                spectrum=dict(negative=0,near_zero=0,positive=0,threshold=0),
                spectral_completeness=dict(status='complete',reason='No solid domain supports elastic toroidal modes'),selected_count=0))
    for domain in plans:
        identity = 'solid:'+','.join(a['layer']['id'] for a in domain)
        for degree in range(l_min,l_max+1):
            radius,K,M,active = _assemble(domain,degree)
            values,vectors,residuals,diagnostics = _eigenpairs(K,M,radius[active],degree)
            selected = 0
            for index,value in enumerate(values):
                frequency = math.sqrt(float(value))/(2*math.pi)
                if not frequency_min_hz <= frequency <= frequency_max_hz:
                    continue
                n = index + (1 if degree == 1 else 0)
                vector = np.zeros(len(radius)); vector[active] = vectors[:,index]
                regions,normalization = _regions(domain,radius,vector)
                modes.append(dict(id=f'T{n}_{degree}:{identity}',family='T',n=n,l=degree,frequency_hz=frequency,q=None,
                    normalization='mass_integral_1',regions=regions,provenance=dict(solver=METHOD,experimental=True,
                        solid_domain_id=identity,source_n=n,label_convention='l1 rigid rotation reserves n0; positive branches ordered within each solid domain',
                        normalization_conversion=normalization,fe_scaled_residual=float(residuals[index]),
                        quality=dict(status='unverified',mesh_convergence=None,benchmark=None,
                            warnings=['Experimental numerical pilot; discrete algebra checks do not certify physical accuracy for this model.']))))
                selected += 1
            groups.append(dict(family='T',l=degree,solid_domain_id=identity,status='success',matrix_dimension=len(K),
                spectrum=dict(negative=0,near_zero=int(degree==1),positive=len(values),threshold=0),
                spectral_completeness=dict(status='complete',reason='Entire constrained discrete spectrum; known rigid rotation excluded, frequency window applied without renumbering'),
                selected_count=selected,selection_status='selected' if selected else 'empty_selection',
                diagnostics=diagnostics,mesh_elements=(len(radius)-1)//2,exported_radial_nodes=len(radius)))
    request = dict(l_min=l_min,l_max=l_max,mesh_size=mesh_size,frequency_min_hz=frequency_min_hz,frequency_max_hz=frequency_max_hz,memory_mib=memory_mib)
    result = dict(schema_version='1.0',model=deepcopy(model),modes=modes,provenance=dict(solver=METHOD,experimental=True,
        model_hash=model_hash(model),request=request,groups=groups,attenuation='elastic; input material Q preserved but not applied',
        material_interpolation='piecewise-linear rho and vs on mandatory SI layer knots; mu=rho*vs**2 at quadrature',
        effective_settings=dict(mesh_counts={a['layer']['id']:sum(a['counts']) for d in plans for a in d},
            mandatory_profile_knots={a['layer']['id']:a['layer']['r_m'][:] for d in plans for a in d},
            actual_mesh_size=sum(sum(a['counts']) for d in plans for a in d),estimated_working_memory_bytes=estimate),
        limitations=['Elastic isotropic toroidal modes only; not a default-backend replacement.',
                     'High discrete branches need mesh convergence; benchmark evidence covers only named fixtures.']))
    return validate_bundle(result)
