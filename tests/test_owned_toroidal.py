"""Physical and public-contract checks for the independent toroidal pilot."""
from copy import deepcopy

import numpy as np
import pytest
from scipy.optimize import brentq
from scipy.special import spherical_jn

from earth_modes.data import mass_integral
from earth_modes.experimental import solve_toroidal
from earth_modes.experimental import toroidal
from earth_modes.models import homogeneous_model


def sphere():
    return homogeneous_model(1e6,4000,8000,4000)


def test_analytic_frequency_shape_and_rigid_rotation():
    model=sphere()
    bundle=solve_toroidal(model,l_min=1,l_max=2,mesh_size=60,frequency_max_hz=.01)
    mode=next(m for m in bundle['modes'] if m['l']==2 and m['n']==0)
    root=brentq(lambda x:x*spherical_jn(2,x,derivative=True)-spherical_jn(2,x),2,3)
    assert abs(mode['frequency_hz']/(root*4000/(2*np.pi*1e6))-1)<.005
    region=mode['regions'][0];r=np.asarray(region['r_m']);w=np.asarray(region['w']);reference=spherical_jn(2,root*r/1e6)
    weight=4000*r*r
    reference/=np.sqrt(np.trapezoid(weight*reference**2,r))
    if np.trapezoid(weight*w*reference,r)<0: reference=-reference
    assert np.sqrt(np.trapezoid(weight*(w-reference)**2,r))<.01
    assert abs(mass_integral(model,mode)-1)<1e-12
    assert region['w'][0]==0
    assert min(m['n'] for m in bundle['modes'] if m['l']==1)==1
    for group in bundle['provenance']['groups']:
        diagnostics=group['diagnostics']
        assert diagnostics['maximum_scaled_residual']<1e-9
        assert diagnostics['mass_orthogonality_defect']<1e-8
        if group['l']==1:
            assert diagnostics['rigid_rotation']['scaled_stiffness_residual']<1e-12


def test_filter_preserves_ids_and_exact_inclusive_boundary():
    model=sphere()
    broad=solve_toroidal(model,l_min=2,l_max=2,mesh_size=30,frequency_max_hz=.02)
    selected=broad['modes'][2]
    narrow=solve_toroidal(model,l_min=2,l_max=2,mesh_size=30,frequency_min_hz=selected['frequency_hz'],frequency_max_hz=selected['frequency_hz']*1.00001)
    assert [m['id'] for m in narrow['modes']]==[selected['id']]
    empty=solve_toroidal(model,l_min=2,l_max=2,mesh_size=30,frequency_max_hz=1e-10)
    assert empty['modes']==[]
    assert empty['provenance']['groups'][0]['selection_status']=='empty_selection'
    fluid=solve_toroidal(homogeneous_model(vs_m_s=0),l_min=1,l_max=2)
    assert fluid['modes']==[]
    assert all(g['status']=='not_applicable' for g in fluid['provenance']['groups'])


def test_profile_knots_q_and_multiple_solid_domains_preserved():
    model=sphere();a=model['layers'][0]
    a.update(r_m=[0.,123456.,2e5],rho_kg_m3=[4000.,4100.,4200.],vp_m_s=[8000.]*3,vs_m_s=[4000.,4100.,4000.],q_shear=[300.]*3,q_bulk=[None]*3)
    fluid=deepcopy(a);fluid.update(id='fluid',phase='fluid',r_m=[2e5,5e5],rho_kg_m3=[4000.]*2,vp_m_s=[8000.]*2,vs_m_s=[0.]*2,q_shear=[None]*2,q_bulk=[None]*2)
    shell=deepcopy(fluid);shell.update(id='shell',phase='solid',r_m=[5e5,654321.,1e6],rho_kg_m3=[4000.]*3,vp_m_s=[8000.]*3,vs_m_s=[4000.]*3,q_shear=[200.]*3,q_bulk=[None]*3)
    model['layers']=[a,fluid,shell];original=deepcopy(model)
    bundle=solve_toroidal(model,l_min=2,l_max=2,mesh_size=40,frequency_max_hz=.02)
    assert bundle['model']==model==original
    assert {m['provenance']['solid_domain_id'] for m in bundle['modes']}=={'solid:sphere','solid:shell'}
    for mode in bundle['modes']:
        assert mode['q'] is None
        assert 'potential' not in mode['provenance']
        assert len(mode['regions'])==1
        region=mode['regions'][0]
        layer=next(a for a in model['layers'] if a['id']==region['layer_id'])
        assert set(layer['r_m'])<=set(region['r_m'])
        assert set(region['u']+region['v'])=={0.}


def test_mandatory_knots_trigger_preflight_before_assembly(monkeypatch):
    model=sphere();layer=model['layers'][0]
    layer.update(r_m=np.linspace(0,1e6,501).tolist(),rho_kg_m3=[4000.]*501,vp_m_s=[8000.]*501,vs_m_s=[4000.]*501)
    def forbidden(*args): raise AssertionError('Dense assembly must not run over budget')
    monkeypatch.setattr(toroidal,'_assemble',forbidden)
    with pytest.raises(ValueError,match='mandatory profile knots'):
        solve_toroidal(model,mesh_size=1,memory_mib=1)


@pytest.mark.parametrize('options',[{'l_min':0},{'l_max':65},{'l_min':2,'l_max':1},{'mesh_size':True},
    {'mesh_size':1.5},{'frequency_min_hz':-1},{'frequency_min_hz':.01,'frequency_max_hz':.01},
    {'frequency_max_hz':float('inf')},{'memory_mib':0}])
def test_invalid_request_fails(options):
    with pytest.raises(ValueError): solve_toroidal(sphere(),**options)
