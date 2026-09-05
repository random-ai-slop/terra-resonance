"""Numerical regression gates: boundary physics, normalization and real spectra."""
from copy import deepcopy
import math

import numpy as np
import pytest
from scipy.optimize import brentq
from scipy.special import spherical_jn

from earth_modes.data import validate_bundle
from earth_modes.models import homogeneous_model, prem_model
from earth_modes.solver import solve, SolverError


def topology(phases):
    bounds={'S':[0,1],'F':[0,1],'SFS':[0,.3,.65,1],'FS':[0,.45,1],
            'SF':[0,.55,1],'SFSFS':[0,.15,.35,.6,.8,1]}[phases]
    model=homogeneous_model(1e6,4000,8000,4000)
    model['id']='topology-'+phases;model['layers']=[]
    for i,phase in enumerate(phases):
        model['layers'].append(dict(id=str(i),name=phase,phase='solid' if phase=='S' else 'fluid',
            r_m=[bounds[i]*1e6,bounds[i+1]*1e6],rho_kg_m3=[4000]*2,
            vp_m_s=[8000]*2,vs_m_s=[4000 if phase=='S' else 0]*2))
    return model


def test_analytic_roots_and_scaling():
    model=topology('S')
    result=solve(model,families=['R','T'],l_min=2,l_max=2,gravity=0,mesh_size=60,n_max=0,frequency_max_hz=.02)
    radial=brentq(lambda x:8000**2*x*spherical_jn(0,x)-4*4000**2*spherical_jn(1,x),2,3.5)*8000/(2*np.pi*1e6)
    toroidal=brentq(lambda x:x*spherical_jn(2,x,derivative=True)-spherical_jn(2,x),2,3)*4000/(2*np.pi*1e6)
    assert np.allclose([m['frequency_hz'] for m in result['modes']],[radial,toroidal],rtol=.005)
    scaled=deepcopy(model);scaled['radius_m']*=2;scaled['layers'][0]['r_m']=[0,2e6]
    again=solve(scaled,families=['R','T'],l_min=2,l_max=2,gravity=0,mesh_size=60,n_max=0,frequency_max_hz=.02)
    assert np.allclose([m['frequency_hz']*2 for m in again['modes']],[m['frequency_hz'] for m in result['modes']],rtol=1e-8)


@pytest.mark.parametrize('phases',['S','F','SFS','FS','SF','SFSFS'])
@pytest.mark.parametrize('gravity',[0,1,2])
def test_topologies(phases,gravity):
    bundle=solve(topology(phases),l_min=1,l_max=2,gravity=gravity,mesh_size=36,n_max=4,frequency_max_hz=.02)
    validate_bundle(bundle)
    assert all(m['frequency_hz']>0 for m in bundle['modes'])
    assert {'R','S'}.issubset({m['family'] for m in bundle['modes']})
    if phases=='F':
        assert all(g['status']=='not_applicable' for g in bundle['provenance']['groups'] if g['family']=='T')
    for mode in bundle['modes']:
        if mode['family']=='T':
            assert all(topology(phases)['layers'][int(r['layer_id'])]['phase']=='solid' for r in mode['regions'])
        for region in mode['regions']:
            if region['r_m'][0]==0:
                if mode['family']=='S' and mode['l']==1:
                    assert region['v'][0]==pytest.approx(math.sqrt(2)*region['u'][0])
                else: assert region['u'][0]==region['v'][0]==region['w'][0]==0


def test_free_fluid_surface_is_not_a_rigid_wall():
    b=solve(topology('F'),families=['R'],gravity=0,mesh_size=40,n_max=2,frequency_max_hz=.02)
    assert np.allclose([m['frequency_hz'] for m in b['modes']],[.004,.008,.012],rtol=.001)


def test_q_limit_and_uniform_toroidal_quality():
    m=topology('S');m['reference_frequency_hz']=.01
    m['layers'][0].update(q_bulk=[None,None],q_shear=[None,None])
    kw=dict(families=['T'],l_min=2,l_max=2,gravity=0,mesh_size=60,n_max=0,frequency_max_hz=.02)
    reference=solve(m,**kw)
    infinite=solve(m,**kw,linear_q=True,target_frequency_hz=.001)
    assert infinite['modes'][0]['q'] is None
    assert infinite['modes'][0]['frequency_hz']==pytest.approx(reference['modes'][0]['frequency_hz'],rel=1e-10)
    m['layers'][0].update(q_bulk=[1000,1000],q_shear=[300,300])
    finite=solve(m,**kw,linear_q=True,target_frequency_hz=.001)
    assert finite['modes'][0]['q']==pytest.approx(300,rel=.005)
    assert finite['provenance']['effective_model']['model']['layers'][0]['vs_m_s'][0]<4000
    assert finite['model']['layers'][0]['vs_m_s'][0]==4000


def test_layer_split_is_not_a_new_toroidal_domain():
    one=topology('S');two=deepcopy(one)
    a=deepcopy(one['layers'][0]);a['r_m']=[0,5e5]
    b=deepcopy(a);b['id']='1';b['r_m']=[5e5,1e6];two['layers']=[a,b]
    kw=dict(families=['T'],l_min=2,l_max=2,gravity=0,mesh_size=40,n_max=1,frequency_max_hz=.02)
    original=solve(one,**kw);split=solve(two,**kw)
    assert np.allclose([m['frequency_hz'] for m in original['modes']],[m['frequency_hz'] for m in split['modes']],rtol=1e-9)
    assert len(split['modes'][0]['regions'])==2


def test_request_and_budget_fail_before_solve():
    with pytest.raises(ValueError,match='target_frequency'): solve(topology('S'),linear_q=True)
    with pytest.raises(SolverError,match='memory'): solve(prem_model(),mesh_size=10000)
    with pytest.raises(ValueError,match='Unknown'): solve(topology('S'),imaginary_option=1)


def test_one_metre_surface_layer_does_not_hide_low_spectrum():
    thin=topology('SF')
    thin['layers'][0]['r_m'][-1]=999999
    thin['layers'][1]['r_m'][0]=999999
    result=solve(thin,families=['R'],mesh_size=40,gravity=2,n_max=0,frequency_max_hz=.02)
    reference=solve(topology('S'),families=['R'],mesh_size=40,gravity=2,n_max=0,frequency_max_hz=.02)
    assert len(result['modes'])==1
    assert result['modes'][0]['frequency_hz']==pytest.approx(reference['modes'][0]['frequency_hz'],rel=.001)
    assert 'shifted-inverse' in result['provenance']['groups'][0]['eigensolver']


def test_radial_and_spheroidal_q_against_material_finite_difference():
    model=topology('S');model['reference_frequency_hz']=.01
    model['layers'][0].update(q_bulk=[1000]*2,q_shear=[300]*2)
    settings=dict(families=['R','S'],l_min=2,l_max=2,gravity=2,mesh_size=60,n_max=0,frequency_max_hz=.02)
    modes=solve(model,**settings,linear_q=True,target_frequency_hz=.01)['modes']
    inverse_q=np.zeros(len(modes))
    for component,material_q in [('bulk',1000),('shear',300)]:
        frequencies=[]
        for epsilon in [-1e-4,1e-4]:
            perturbed=deepcopy(model)
            mu=4000*4000**2*(1+epsilon if component=='shear' else 1)
            bulk=4000*(8000**2-4*4000**2/3)*(1+epsilon if component=='bulk' else 1)
            perturbed['layers'][0]['vp_m_s']=[np.sqrt((bulk+4*mu/3)/4000)]*2
            perturbed['layers'][0]['vs_m_s']=[np.sqrt(mu/4000)]*2
            frequencies.append([m['frequency_hz'] for m in solve(perturbed,**settings)['modes']])
        inverse_q+=(np.log(frequencies[1])-np.log(frequencies[0]))/1e-4/material_q
    assert np.allclose([m['q'] for m in modes],1/inverse_q,rtol=.005)


@pytest.mark.parametrize('gravity', [1, 2])
@pytest.mark.parametrize('vs', [0, 4000])
def test_material_density_jump_matches_thin_transition(gravity, vs):
    """A fluid rho' density sheet must survive merging same-phase domains.

    Solid forms eliminate rho' by integration by parts: the same test guards
    against mistakenly applying the fluid correction twice in solids.
    """
    def model(width):
        result=homogeneous_model(1e6,8000,8000,vs)
        def layer(name,a,b,rhoa,rhob):
            return dict(id=name,name=name,phase='solid' if vs else 'fluid',
                        r_m=[a,b],rho_kg_m3=[rhoa,rhob],vp_m_s=[8000]*2,vs_m_s=[vs]*2)
        lo,hi=5e5-width/2,5e5+width/2
        result['layers']=[layer('inner',0,lo,8000,8000)]
        if width:result['layers'].append(layer('transition',lo,hi,8000,4000))
        result['layers'].append(layer('outer',hi,1e6,4000,4000))
        return result
    options=dict(families=['R','S'],l_min=2,l_max=2,gravity=gravity,n_max=0,frequency_max_hz=.02)
    sharp=solve(model(0),mesh_size=240,**options)['modes']
    smooth=solve(model(100),mesh_size=240,**options)['modes']
    assert [m['id'] for m in sharp]==[m['id'] for m in smooth]==['R0_0','S0_2']
    error=np.abs(np.array([m['frequency_hz'] for m in sharp])/[m['frequency_hz'] for m in smooth]-1)
    assert np.all(error < .0015 if vs == 0 else error < 1e-5)
    if vs == 0:
        coarse=solve(model(0),mesh_size=120,**options)['modes']
        coarse_s_error=abs(coarse[1]['frequency_hz']/smooth[1]['frequency_hz']-1)
        assert error[1] < .6*coarse_s_error


def test_gravity_float_fails_at_request_boundary():
    with pytest.raises(ValueError,match='gravity'):
        solve(topology('S'),gravity=1.0)
