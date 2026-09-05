"""Spatial aliasing regressions independent of an exporter or shader."""
from copy import deepcopy
import numpy as np
import pytest

from earth_modes.data import default_scene, mass_integral, validate_bundle
from earth_modes.models import homogeneous_model
from earth_modes.solver import solve
from earth_modes.sampling import layer_radial_nodes


def sign_roots(x, y):
    roots=[]
    for i in range(len(x)-1):
        if y[i]*y[i+1]<0:
            roots.append(x[i]-y[i]*(x[i+1]-x[i])/(y[i+1]-y[i]))
        elif i>0 and y[i]==0 and y[i-1]*y[i+1]<0:
            roots.append(x[i])
    return roots


def test_real_high_overtone_preserves_all_linear_roots():
    bundle=solve(homogeneous_model(1e6,4000,8000,4000),families=['R'],gravity=0,mesh_size=160,n_max=60,frequency_max_hz=.3)
    mode=next(m for m in bundle['modes'] if m['n']==60)
    bundle['modes']=[mode]
    scene=default_scene(bundle)
    nodes=layer_radial_nodes(bundle,scene['terms'])[0][1]
    region=mode['regions'][0];source=np.asarray(region['r_m'])/bundle['model']['radius_m']
    expected=sign_roots(source,region['u'])
    actual=sign_roots(nodes,np.interp(nodes,source,region['u']))
    assert len(expected)==60
    np.testing.assert_allclose(actual,expected,atol=1e-14,rtol=1e-12)


def test_aligned_oscillations_and_budget_do_not_become_zero_region():
    bundle=solve(homogeneous_model(1e6,4000,8000,4000),families=['R'],gravity=0,n_max=0,frequency_max_hz=.02)
    mode=bundle['modes'][0];region=mode['regions'][0]
    radius=np.linspace(0,1e6,2401);u=np.sin(24*np.pi*radius/1e6)
    region.update(r_m=radius.tolist(),u=u.tolist(),v=np.zeros_like(u).tolist(),w=np.zeros_like(u).tolist())
    region.pop('potential',None)
    region['u']=(u/np.sqrt(mass_integral(bundle['model'],mode))).tolist()
    validate_bundle(bundle)
    terms=default_scene(bundle)['terms']
    nodes=layer_radial_nodes(bundle,terms)[0][1]
    values=np.interp(nodes,radius/1e6,region['u'])
    assert len(sign_roots(nodes,values))==23
    assert max(abs(values))>.99*max(abs(np.asarray(region['u'])))
    with pytest.raises(ValueError,match='budget'):
        layer_radial_nodes(bundle,terms,max_nodes=100)
    # An inactive component contributes no required sample locations.
    zero_terms=[{**terms[0],'amplitude':0.}]
    assert len(layer_radial_nodes(bundle,zero_terms)[0][1])==25
