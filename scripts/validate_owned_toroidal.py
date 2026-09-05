#!/usr/bin/env python3
"""Recompute the full independent toroidal pilot evidence matrix.

Run: PYTHONPATH=packages OPENBLAS_NUM_THREADS=1 python scripts/validate_owned_toroidal.py
No default solver or vendor assembly is called. Checked-in MINEOS outputs remain
an independent reference, not a runtime dependency of the experimental API.
"""
from __future__ import annotations
from copy import deepcopy
import json
from pathlib import Path
import re
import time

import numpy as np
import scipy
from scipy.integrate import solve_ivp
from scipy.optimize import brentq
from scipy.special import spherical_jn

from earth_modes.data import mass_integral, model_hash
from earth_modes.experimental import solve_toroidal
from earth_modes.models import homogeneous_model, prem_model

ROOT = Path(__file__).resolve().parents[1]


def roots(function, count, start=.01, stop=40., steps=1600):
    grid = np.linspace(start,stop,steps)
    found = []
    a = grid[0]; fa = function(a)
    for b in grid[1:]:
        fb = function(b)
        if fa*fb < 0:
            found.append(brentq(function,a,b,xtol=1e-12))
            if len(found) == count:
                return found
        a,fa = b,fb
    raise AssertionError(f"Expected {count} roots, found {len(found)}")


def shell_model():
    model = homogeneous_model(1e6,4000,8000,4000)
    fluid = deepcopy(model['layers'][0]); solid = deepcopy(fluid)
    fluid.update(id='fluid',name='Fluid interior',phase='fluid',r_m=[0.,3e5],vs_m_s=[0.,0.])
    solid.update(id='shell',name='Solid shell',r_m=[3e5,1e6])
    model.update(id='pilot-shell',name='Homogeneous traction-free shell',layers=[fluid,solid])
    return model


def shell_ode(wave, degree=2, evaluation=None):
    # x=r/R, traction scaled by mu/R. Independent first-order strong form.
    def rhs(x,y):
        w,t = y
        return [w/x+t,-3*t/x+((degree*(degree+1)-2)/x**2-wave**2)*w]
    result = solve_ivp(rhs,[.3,1.],[1.,0.],rtol=2e-10,atol=2e-12,max_step=.01,dense_output=evaluation is not None)
    if not result.success:
        raise RuntimeError(result.message)
    return result.y[1,-1] if evaluation is None else result.sol(evaluation)[0]


def shape_error(model, mode, radius, reference):
    # The homogeneous cases occupy one solid region; both shapes use the same
    # resolved physical mass measure, independently of exported normalization.
    region = mode['regions'][0]
    layer = next(a for a in model['layers'] if a['id'] == region['layer_id'])
    weight = np.interp(radius,layer['r_m'],layer['rho_kg_m3'])*radius**2
    computed = np.interp(radius,region['r_m'],region['w'])
    def norm(x): return np.sqrt(np.trapezoid(weight*x*x,radius))
    computed /= norm(computed); reference = reference/norm(reference)
    if np.trapezoid(weight*computed*reference,radius) < 0:
        reference = -reference
    return float(norm(computed-reference))


def mineos_references():
    references = {}
    for family in ['T','I']:
        for line in (ROOT/'docs/validation/mineos'/f'{family}.txt').read_text().splitlines():
            match = re.match(r'^\s+(\d+)\s+([stc])\s+(\d+)\s+([\d.Ee+-]+)\s+([\d.Ee+-]+)',line)
            if match:
                n,_,l,_,frequency = match.groups()
                references[family,int(n),int(l)] = float(frequency)*.001
    return references


def inner_reference(layer, degree):
    # Strong traction ODE using rho/vs interpolation separately, independent
    # of the weak FE assembly. Each supplied profile interval is integrated
    # separately so numerical time-stepping cannot skip a material knot.
    radius = np.asarray(layer['r_m'])/layer['r_m'][-1]
    rho = np.asarray(layer['rho_kg_m3']); vs = np.asarray(layer['vs_m_s'])
    rho0 = rho[0]; mu0 = rho0*vs[0]**2
    def determinant(frequency):
        wave = (2*np.pi*frequency*layer['r_m'][-1])**2*rho0/mu0
        start = 1e-5; state = [start,degree-1.]
        def rhs(x,y):
            density = np.interp(x,radius,rho)/rho0
            speed = np.interp(x,radius,vs)
            modulus = density*rho0*speed**2/mu0
            return [y[0]/x+y[1]/modulus,-3*y[1]/x+((degree*(degree+1)-2)*modulus/x**2-density*wave)*y[0]]
        for end in radius[1:]:
            result = solve_ivp(rhs,[start,end],state,rtol=2e-10,atol=2e-12,max_step=.01)
            if not result.success: raise RuntimeError(result.message)
            state = result.y[:,-1]; start=end
        return state[1]
    brackets = {2:(.0008,.0015),3:(.0015,.002),4:(.002,.0026)}
    return brentq(determinant,*brackets[degree],xtol=1e-13)


def main():
    started = time.perf_counter()
    evidence = dict(method='Terra experimental SI quadratic toroidal FEM v1',numpy=np.__version__,scipy=scipy.__version__,
        gates=dict(relative_frequency_error=.005,sign_aligned_mass_shape_error=.01,scaled_fe_residual=1e-9,fe_mass_orthogonality=1e-8),
        scope='Named fixtures only. FE algebra diagnostics are separate from physical accuracy and exported trapezoid normalization.',cases=[],groups=[])
    sphere = homogeneous_model(1e6,4000,8000,4000)
    b = solve_toroidal(sphere,l_min=1,l_max=3,mesh_size=100,frequency_max_hz=.02)
    evidence['groups'] += [dict(case='sphere',**g) for g in b['provenance']['groups']]
    for degree in [2,3]:
        reference_roots = roots(lambda x:x*spherical_jn(degree,x,derivative=True)-spherical_jn(degree,x),4)
        for n,root in enumerate(reference_roots):
            mode = next(m for m in b['modes'] if m['l']==degree and m['n']==n)
            radius = np.linspace(0,1e6,4001)
            expected = root*4000/(2*np.pi*1e6)
            error = shape_error(sphere,mode,radius,spherical_jn(degree,root*radius/1e6))
            evidence['cases'].append(dict(case='sphere',mode_id=mode['id'],mesh_target=100,reference='spherical Bessel traction roots and j_l(k r)',
                computed_hz=mode['frequency_hz'],reference_hz=expected,relative_frequency_error=abs(mode['frequency_hz']/expected-1),
                sign_aligned_mass_shape_error=error,comparison_grid_count=len(radius),exported_mass_integral=mass_integral(sphere,mode)))
    shell = shell_model()
    bs = solve_toroidal(shell,l_min=1,l_max=2,mesh_size=100,frequency_max_hz=.02)
    evidence['groups'] += [dict(case='shell',**g) for g in bs['provenance']['groups']]
    for n,root in enumerate(roots(shell_ode,3,start=.1,stop=16,steps=100)):
        mode = next(m for m in bs['modes'] if m['l']==2 and m['n']==n)
        radius = np.linspace(3e5,1e6,4001)
        expected = root*4000/(2*np.pi*1e6)
        error = shape_error(shell,mode,radius,shell_ode(root,evaluation=radius/1e6))
        evidence['cases'].append(dict(case='shell',mode_id=mode['id'],mesh_target=100,reference='independent first-order traction/displacement ODE; free inner and outer traction',
            computed_hz=mode['frequency_hz'],reference_hz=expected,relative_frequency_error=abs(mode['frequency_hz']/expected-1),
            sign_aligned_mass_shape_error=error,comparison_grid_count=len(radius),exported_mass_integral=mass_integral(shell,mode)))
    prem = prem_model(); bp = solve_toroidal(prem,mesh_size=240,frequency_max_hz=.004)
    evidence['groups'] += [dict(case='PREM',**g) for g in bp['provenance']['groups']]
    references = mineos_references()
    for inner in [True,False]:
        for degree in range(1,5):
            n = 1 if degree == 1 else 0
            mode = next(m for m in bp['modes'] if m['l']==degree and m['n']==n and (m['regions'][0]['layer_id']=='prem-00')==inner)
            if inner and degree != 1:
                expected = inner_reference(prem['layers'][0],degree)
                source = 'Independent traction ODE with layer-local linear rho and vs'
            else:
                expected = references['I',0,1] if inner else references['T',n,degree]
                source = 'MINEOS 26f842dbe95b0c27d5e77146d415268db1239913, checked-in '+('I.txt raw n0 l1' if inner else f'T.txt raw n{n} l{degree}')
            evidence['cases'].append(dict(case='PREM',mode_id=mode['id'],mesh_target=240,reference=source,
                computed_hz=mode['frequency_hz'],reference_hz=expected,relative_frequency_error=abs(mode['frequency_hz']/expected-1),
                exported_mass_integral=mass_integral(prem,mode),model_hash=model_hash(prem)))
    evidence['PREM_mesh'] = bp['provenance']['effective_settings']
    # A purely artificial same-material boundary must preserve the solution.
    split = deepcopy(sphere); a=split['layers'][0]; c=deepcopy(a)
    a['r_m']=[0.,5e5]; c.update(id='outer',name='Artificial outer partition',r_m=[5e5,1e6]);split['layers'].append(c)
    split_bundle = solve_toroidal(split,l_min=2,l_max=2,mesh_size=100,frequency_max_hz=.01)
    expected_modes = [m for m in b['modes'] if m['l']==2 and m['frequency_hz']<=.01]
    assert len(split_bundle['modes']) == len(expected_modes)
    differences = [abs(a['frequency_hz']/c['frequency_hz']-1) for a,c in zip(split_bundle['modes'],expected_modes)]
    evidence['artificial_split'] = dict(mode_count=len(differences),max_relative_frequency_change=max(differences),
        tolerance=1e-9,shared_boundary_w_jump=max(abs(m['regions'][0]['w'][-1]-m['regions'][1]['w'][0]) for m in split_bundle['modes']))
    assert max(differences)<1e-9
    assert len(evidence['cases'])==19
    for case in evidence['cases']:
        assert case['relative_frequency_error']<=.005,case
        assert case.get('sign_aligned_mass_shape_error',0)<=.01,case
        assert abs(case['exported_mass_integral']-1)<1e-6,case
    for group in evidence['groups']:
        diagnostics=group['diagnostics']
        assert diagnostics['maximum_scaled_residual']<=1e-9
        assert diagnostics['mass_orthogonality_defect']<=1e-8
        assert diagnostics['mass_spd']
        if group['l']==1:
            assert diagnostics['rigid_rotation']['scaled_stiffness_residual']<=1e-12
            assert diagnostics['rigid_rotation']['removed_multiplicity']==1
    evidence['runtime_s']=time.perf_counter()-started
    evidence['status']='passed'
    destination=ROOT/'docs/validation/owned-toroidal.json'
    destination.write_text(json.dumps(evidence,indent=2)+'\n')
    print(json.dumps(dict(status='passed',case_count=19,max_frequency_error=max(c['relative_frequency_error'] for c in evidence['cases']),
        max_shape_error=max(c.get('sign_aligned_mass_shape_error',0) for c in evidence['cases']),runtime_s=evidence['runtime_s']),indent=2))


if __name__=='__main__': main()
