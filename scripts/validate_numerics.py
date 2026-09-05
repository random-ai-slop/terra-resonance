#!/usr/bin/env python3
"""Recompute N1–N6 evidence and the published PREM bundle.

Run with PYTHONPATH=packages OPENBLAS_NUM_THREADS=1 .venv/bin/python scripts/validate_numerics.py.
MINEOS raw reference runs are checked in; --mineos-root rebuilds and reruns them.
"""
from __future__ import annotations
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq
from scipy.special import spherical_jn

from earth_modes.data import save_bundle, model_hash
from earth_modes.models import homogeneous_model, prem_model
from earth_modes.solver import solve

ROOT=Path(__file__).resolve().parents[1]
EVIDENCE=ROOT/'docs/validation'
MINEOS_COMMIT='26f842dbe95b0c27d5e77146d415268db1239913'


def topology(phases):
    bounds={'S':[0,1],'F':[0,1],'SFS':[0,.3,.65,1],'FS':[0,.45,1],
            'SF':[0,.55,1],'SFSFS':[0,.15,.35,.6,.8,1]}[phases]
    m=homogeneous_model(1e6,4000,8000,4000);m['id']='validation-'+phases;m['layers']=[]
    for i,p in enumerate(phases):
        m['layers'].append(dict(id=str(i),name=p,phase='solid' if p=='S' else 'fluid',
            r_m=[bounds[i]*1e6,bounds[i+1]*1e6],rho_kg_m3=[4000]*2,
            vp_m_s=[8000]*2,vs_m_s=[4000 if p=='S' else 0]*2))
    return m


def inner_toroidal_shooting(layer,l):
    """Independent traction/displacement ODE; no Ouroboros matrices or code.

    dW/dr=W/r+T/mu; dT/dr=-3T/r+[mu*(l(l+1)-2)/r²-rho*omega²]W.
    Regular centre W~r^l, free outer surface T=0. Density/modulus are linearly
    interpolated between the same supplied PREM material knots.
    """
    R=layer['r_m'][-1];r=np.array(layer['r_m'])/R
    rho=np.array(layer['rho_kg_m3']);mu=rho*np.array(layer['vs_m_s'])**2
    mr=mu[0];dr=rho[0]
    def determinant(f):
        wave=(2*np.pi*f*R)**2*dr/mr;start=1e-5
        def rhs(x,y):
            m=np.interp(x,r,mu)/mr;d=np.interp(x,r,rho)/dr
            return [y[0]/x+y[1]/m,-3*y[1]/x+((l*(l+1)-2)*m/x**2-d*wave)*y[0]]
        solution=solve_ivp(rhs,[start,1],[start,l-1],rtol=2e-9,atol=1e-10,max_step=.01)
        if not solution.success: raise RuntimeError(solution.message)
        return solution.y[1,-1]
    interval={2:(.0008,.0015),3:(.0015,.002),4:(.002,.0026)}[l]
    return brentq(determinant,*interval,xtol=1e-12)


def mineos_references(root=None):
    directory=EVIDENCE/'mineos';directory.mkdir(parents=True,exist_ok=True)
    if root:
        root=Path(root).resolve()
        commit=subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],text=True).strip()
        if commit!=MINEOS_COMMIT: raise ValueError('MINEOS checkout must match pinned '+MINEOS_COMMIT)
        executable=directory/'minos_bran.local'
        subprocess.run(['gfortran','-std=legacy','-fallow-argument-mismatch','-O2',str(root/'minos_bran.f'),'-o',str(executable)],check=True)
        for name,code in [('R',1),('T',2),('S',3),('I',4)]:
            controls=f'{ROOT}/examples/prem-isotropic-3mhz.txt\n{directory}/{name}.txt\nnone\n1.d-9 100.\n{code}\n1 4 0.1 4.0 0 4\n'
            subprocess.run([str(executable)],input=controls,text=True,capture_output=True,check=True,cwd=directory,timeout=60)
        executable.unlink()
        (directory/'none').unlink(missing_ok=True)
    result={}
    for family in ['R','S','T','I']:
        for line in (directory/(family+'.txt')).read_text().splitlines():
            match=re.match(r'^\s+(\d+)\s+([stc])\s+(\d+)\s+([\d.Ee+-]+)\s+([\d.Ee+-]+)',line)
            if match:
                n,_,l,_,f=match.groups();result[(family,int(n),int(l))]=float(f)*.001
    return result


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--mineos-root');args=parser.parse_args()
    EVIDENCE.mkdir(exist_ok=True);references=mineos_references(args.mineos_root)
    evidence={'scope':'N1–N6 frequencies, boundary physics, canonical mass and first-order Q; not source excitation or inverse kernels',
              'mineos_commit':MINEOS_COMMIT,'results':{}}
    # N1: two genuine analytic equations plus free acoustic sphere.
    m=topology('S');b=solve(m,families=['R','T'],l_min=2,l_max=2,gravity=0,mesh_size=80,n_max=0,frequency_max_hz=.02)
    roots=[brentq(lambda x:8000**2*x*spherical_jn(0,x)-4*4000**2*spherical_jn(1,x),2,3.5)*8000/(2*np.pi*1e6),
           brentq(lambda x:x*spherical_jn(2,x,derivative=True)-spherical_jn(2,x),2,3)*4000/(2*np.pi*1e6)]
    assert [(a['family'],a['n'],a['l']) for a in b['modes']]==[('R',0,0),('T',0,2)]
    evidence['results']['N1']=[dict(mode_id=a['id'],computed_hz=a['frequency_hz'],reference_hz=f,relative_error=abs(a['frequency_hz']/f-1)) for a,f in zip(b['modes'],roots)]
    fluid=solve(topology('F'),families=['R'],gravity=0,mesh_size=80,n_max=2,frequency_max_hz=.02)
    assert [(a['family'],a['n'],a['l']) for a in fluid['modes']]==[('R',0,0),('R',1,0),('R',2,0)]
    evidence['results']['N1'] += [dict(model='homogeneous fluid',mode_id=a['id'],computed_hz=a['frequency_hz'],reference_hz=f,relative_error=abs(a['frequency_hz']/f-1)) for a,f in zip(fluid['modes'],[.004,.008,.012])]
    for result in evidence['results']['N1']:
        result['tolerance']=.005
        assert result['relative_error'] < result['tolerance'],result
    print('N1 analytic roots complete',flush=True)
    # N3: every applicable family, centre and exterior phase, repeated interfaces.
    topology_results=[]
    for phases in ['S','F','SFS','FS','SF','SFSFS']:
        for gravity in [0,1,2]:
            bundle=solve(topology(phases),l_min=1,l_max=2,gravity=gravity,mesh_size=80,n_max=4,
                         frequency_min_hz=.00005,frequency_max_hz=.02,convergence_check=True)
            # A density-continuous interface can have true zero modes. Record
            # positive retained modes separately; do not claim absent n labels.
            changes=[x['provenance']['quality']['mesh_convergence']['relative_frequency_change'] for x in bundle['modes'] if x['provenance']['quality']['mesh_convergence']]
            topology_results.append(dict(phases=phases,gravity=gravity,mode_count=len(bundle['modes']),groups=bundle['provenance']['groups'],
                max_relative_frequency_change=max(changes),tested_mode_ids=[x['id'] for x in bundle['modes']]))
            assert changes and max(changes)<.005,(phases,gravity,max(changes))
    evidence['results']['N3']=topology_results
    print('N3 six topologies × three gravity treatments complete',flush=True)
    # N2/N4/N6: true default catalog; no hidden n_max cap.
    prem=prem_model();bundle=solve(prem,l_min=1,l_max=4,mesh_size=140,convergence_check=True)
    independent_inner={l:inner_toroidal_shooting(prem['layers'][0],l) for l in [2,3,4]}
    benchmark=[];norms=[]
    for mode in bundle['modes']:
        family=mode['family'];n=mode['n'];l=mode['l'];domain=mode['provenance']['solid_domain_id']
        inner=family=='T' and domain=='solid:prem-00'
        if inner and n==0 and l in independent_inner:
            ref=independent_inner[l];source='Independent traction ODE shooting; scripts/validate_numerics.py'
        elif inner and n==1 and l==1:
            ref=references.get(('I',0,1));source='MINEOS jcom4 raw index0 corresponds first nonzero l1 inner-core toroidal mode'
        else:
            ref=references.get((family,n,l)) if not inner else None
            source='MINEOS '+MINEOS_COMMIT+' raw output docs/validation/mineos/'+family+'.txt'
        if ref is not None:
            error=abs(mode['frequency_hz']/ref-1)
            assert error<.005,(mode['id'],error)
            quality=mode['provenance']['quality']
            quality['status']='benchmark_checked'
            quality['benchmark']=dict(source=source,reference_frequency_hz=ref,relative_error=error,tolerance=.005,quantity='frequency_hz',model_hash=model_hash(prem))
            quality['warnings']=[x for x in quality['warnings'] if 'not been independently' not in x]
            benchmark.append(dict(mode_id=mode['id'],**quality['benchmark']))
        total=0.
        for region in mode['regions']:
            layer=next(x for x in prem['layers'] if x['id']==region['layer_id'])
            r=np.array(region['r_m']);density=np.interp(r,layer['r_m'],layer['rho_kg_m3'])
            total+=np.trapezoid(density*r*r*sum(np.array(region[x])**2 for x in ['u','v','w']),x=r)
        norms.append(dict(mode_id=mode['id'],mass_integral=float(total)))
        convergence=mode['provenance']['quality']['mesh_convergence']
        assert convergence and convergence['relative_frequency_change']<.005,mode['id']
    evidence['results']['N2']=benchmark
    evidence['results']['N4']=[dict(mode_id=x['id'],**x['provenance']['quality']['mesh_convergence']) for x in bundle['modes']]
    evidence['results']['N6']=norms
    save_bundle(bundle,ROOT/'examples/prem-modes.json',overwrite=True)
    print('N2/N4/N6 PREM and independent references complete',flush=True)
    # N5 finite-Q, null-Q and independent central finite difference of mu.
    m=topology('S');m['reference_frequency_hz']=.01;m['layers'][0].update(q_bulk=[None]*2,q_shear=[None]*2)
    settings=dict(families=['T'],l_min=2,l_max=2,gravity=0,mesh_size=80,n_max=0,frequency_max_hz=.02)
    base=solve(m,**settings)['modes'][0]
    zero=solve(m,**settings,linear_q=True,target_frequency_hz=.001)['modes'][0]
    m['layers'][0].update(q_bulk=[1000]*2,q_shear=[300]*2)
    damped=solve(m,**settings,linear_q=True,target_frequency_hz=.001)['modes'][0]
    def perturbed(epsilon):
        q=deepcopy(m);rho=4000.;mu=rho*4000**2*(1+epsilon);ka=rho*(8000**2-4*4000**2/3)
        q['layers'][0]['vs_m_s']=[np.sqrt(mu/rho)]*2;q['layers'][0]['vp_m_s']=[np.sqrt((ka+4*mu/3)/rho)]*2
        return solve(q,**settings)['modes'][0]['frequency_hz']
    derivative=(np.log(perturbed(1e-4))-np.log(perturbed(-1e-4)))/(2e-4)
    q_from_fd=300/(2*derivative)
    assert abs(damped['q']/q_from_fd-1)<.005
    assert zero['q'] is None
    assert abs(zero['frequency_hz']/base['frequency_hz']-1)<1e-10
    evidence['results']['N5']=dict(null_q=zero['q'],null_limit_frequency_relative_error=abs(zero['frequency_hz']/base['frequency_hz']-1),
        computed_modal_q=damped['q'],finite_difference_dlnf_dlnmu=derivative,modal_q_from_finite_difference=q_from_fd,
        relative_q_error=abs(damped['q']/q_from_fd-1),attenuation=damped['provenance']['attenuation'])
    evidence['bundle_sha256']=hashlib.sha256((ROOT/'examples/prem-modes.json').read_bytes()).hexdigest()
    (EVIDENCE/'numerics.json').write_text(json.dumps(evidence,indent=2,allow_nan=False)+'\n')
    print('All N1–N6 gates passed; examples/prem-modes.json and docs/validation/numerics.json written',flush=True)


if __name__=='__main__': main()
