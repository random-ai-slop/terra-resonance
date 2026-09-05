"""Spherical elastic normal modes using the attributed Ouroboros Galerkin core.

All public values are SI. The numerical mesh and material discontinuities are
separate; the adapter records raw spectral extraction and one whole-mode mass
normalization. No renderer or file-system service is needed to solve a model.
"""
from __future__ import annotations

from copy import deepcopy
import math
import time

import numpy as np
from scipy.linalg import eigh, cholesky, solve as linear_solve, solve_triangular
from scipy.interpolate import interp1d

from .data import validate_model, validate_bundle
from .vendor.Ouroboros.modes import setup, lib, FEM, compute_modes as core

UPSTREAM_COMMIT = 'fa63363040a28c08d9fe2bd7d05dcc823d90dd1e'
PATCHES = ['private-namespace', 'numpy-modern', 'sorted-jacobi-quadrature',
           'material-mesh', 'whole-mode-discrete-normalization', 'physical-spectrum-extraction', 'shifted-inverse-low-spectrum-refinement',
           'indexed-mixed-reduction', 'regular-centre-congruence', 'fluid-free-surface',
           'multi-interface-offset', 'fluid-material-density-sheet', 'rigid-translation-stiffness-projection', 'linear-density-gravity', 'poisson-potential', 'linear-q-strain-energy']
DEFAULTS = dict(families=['R', 'S', 'T'], l_min=0, l_max=4,
                frequency_min_hz=.00005, frequency_max_hz=.003, mesh_size=100,
                gravity=2, n_max=None, linear_q=False, target_frequency_hz=None,
                convergence_check=False, memory_mib=512)


class SolverError(RuntimeError):
    """A numerical request failed; diagnostics describe the failed group."""
    def __init__(self, message, **diagnostics):
        super().__init__(message)
        self.diagnostics = diagnostics


def _hash(model):
    from .data import model_hash
    return model_hash(model)


def _request(arguments):
    extra=set(arguments)-set(DEFAULTS)
    if extra:
        raise ValueError('Unknown solve options: '+', '.join(sorted(extra)))
    p={**deepcopy(DEFAULTS), **arguments}
    p['families']=list(p['families'])
    if not p['families'] or len(set(p['families']))!=len(p['families']) or any(x not in 'RST' or len(x)!=1 for x in p['families']):
        raise ValueError('families must contain distinct R, S or T entries')
    for k in ['l_min','l_max','mesh_size']:
        if type(p[k]) is not int or p[k] < (4 if k=='mesh_size' else 0):
            raise ValueError(k+' must be a nonnegative integer (mesh_size >= 4)')
    if p['l_max']<p['l_min']:
        raise ValueError('l_max must be >= l_min')
    if type(p['gravity']) is not int or p['gravity'] not in [0,1,2]:
        raise ValueError('gravity must be 0, 1 or 2')
    for k in ['frequency_min_hz','frequency_max_hz','memory_mib']:
        if isinstance(p[k],bool) or not isinstance(p[k],(int,float)) or not np.isfinite(p[k]) or p[k]<=0:
            raise ValueError(k+' must be finite and positive')
    if p['frequency_max_hz']<=p['frequency_min_hz']:
        raise ValueError('frequency interval must have increasing bounds')
    if p['n_max'] is not None and (type(p['n_max']) is not int or p['n_max']<0):
        raise ValueError('n_max must be null or a nonnegative integer')
    for k in ['linear_q','convergence_check']:
        if type(p[k]) is not bool: raise ValueError(k+' must be boolean')
    if p['linear_q']:
        target=p['target_frequency_hz']
        if isinstance(target,bool) or not isinstance(target,(int,float)) or not np.isfinite(target) or target<=0:
            raise ValueError('linear_q requires explicit positive target_frequency_hz')
    elif p['target_frequency_hz'] is not None:
        raise ValueError('target_frequency_hz requires linear_q=True')
    return p


def _allocation(model, target):
    layers=model['layers']
    weights=np.array([(a['r_m'][-1]-a['r_m'][0])/np.mean(a['vp_m_s']) for a in layers])
    extra=max(0,target-4*len(layers))
    fractional=extra*weights/weights.sum()
    counts=4+np.floor(fractional).astype(int)
    order=np.argsort(-(fractional-np.floor(fractional)),kind='stable')
    counts[order[:extra-int(np.floor(fractional).sum())]]+=1
    return counts


def _prepare(model, counts, family, gravity):
    """Build real element data without averaging across material interfaces."""
    edges=[]; mus=[]; kappas=[]; rhos=[]; rhops=[]; domains=[]
    raw_r=[]; raw_rho=[]; start=0
    for layer,count in zip(model['layers'],counts):
        r=np.asarray(layer['r_m'])/1e6
        rho=np.asarray(layer['rho_kg_m3'])/1e3
        vp=np.asarray(layer['vp_m_s'])/1e3; vs=np.asarray(layer['vs_m_s'])/1e3
        mu=rho*vs**2; ka=rho*(vp**2-4*vs**2/3)
        # Every material boundary is an element edge. Piecewise-linear profiles
        # are sampled separately on their own side, including density jumps.
        e=np.linspace(r[0],r[-1],int(count)+1)
        nodal=[np.interp(e,r,x) for x in [rho,mu,ka]]
        rhos.extend((nodal[0][:-1]+nodal[0][1:])/2)
        mus.extend((nodal[1][:-1]+nodal[1][1:])/2)
        kappas.extend((nodal[2][:-1]+nodal[2][1:])/2)
        rhops.extend(np.diff(nodal[0])/np.diff(e))
        edges.extend(e if not edges else e[1:])
        raw_r.extend(r); raw_rho.extend(rho)
        if not domains or domains[-1]['phase']!=layer['phase']:
            domains.append(dict(phase=layer['phase'],start=start,end=start+int(count),layers=[layer['id']],r0=float(r[0]),r1=float(r[-1])))
        else:
            domains[-1]['end']=start+int(count); domains[-1]['layers'].append(layer['id']); domains[-1]['r1']=float(r[-1])
        start+=int(count)
    e=np.asarray(edges); va=e[:-1]; vb=np.diff(e)
    x,J,rx,invV,Dr=setup.StartUp(2,va,vb)
    mu=np.asarray(mus); ka=np.asarray(kappas)
    fem=setup.model_para(mu,ka,np.asarray(rhos),x,ka-2*mu/3,1/(ka+4*mu/3),J,rx)
    pV=pDr=px=vV=vDr=vx=PV=PDr=Px=None
    if family!='T':
        pV,pDr,px=setup.StartUp4pressure(3,va,vb); fem.add_xp(px)
    if family=='S':
        vV,vDr,vx=setup.StartUp4V(1,va,vb); fem.add_xV(vx)
    if family!='T' and gravity==2:
        PV,PDr,Px=setup.StartUp4Perturbation(2,va,vb); fem.add_xP(Px)
    if family!='T' and gravity:
        fem.add_rho_p(np.asarray(rhops))
    count_thick=[d['start'] for d in domains]+[domains[-1]['end']]
    brk_radius=[domains[0]['r0']]+[d['r1'] for d in domains]
    # Gravity integrates the original profile, retaining both sides of jumps.
    rr=np.asarray(raw_r); dd=np.asarray(raw_rho)
    brk_num=[]
    for d in domains:
        candidates=np.where(np.isclose(rr,d['r0'],rtol=0,atol=1e-12))[0]
        brk_num.append(int(candidates[-1]) if d['r0'] else 0)
    brk_num.append(len(rr))
    return dict(fem=fem,x=x,invV=invV,Dr=Dr,pV=pV,pDr=pDr,vV=vV,vDr=vDr,vx=vx,PV=PV,PDr=PDr,
                domains=domains,count_thick=count_thick,brk_radius=brk_radius,brk_num=brk_num,
                rho=dd,radius=rr,counts=counts)


def _assemble(prep,family,l,gravity):
    domains=prep['domains']; types=[int(d['phase']=='solid') for d in domains]
    switch=family+'_'+['noGP','G','GP'][gravity]
    return core.build_matrices_radial_or_spheroidal(
        -1 if family=='R' else l, prep['fem'],prep['count_thick'],
        prep['invV'],prep['pV'],prep['vV'],prep['PV'],2,3,1,2 if gravity==2 else None,
        prep['Dr'],prep['pDr'],prep['vDr'],prep['PDr'],prep['rho'],prep['radius'],
        types,prep['brk_radius'],prep['brk_num'],len(domains),switch)


def _raw_regions(prep,family,l,vec,block_len,A0_inv,E,domain_index=None):
    domains=prep['domains']; x=prep['x']; k=math.sqrt(l*(l+1))
    if family=='T':
        d=domains[domain_index]
        r=lib.sqzx(x[:,d['start']:d['end']],d['end']-d['start'],2)*1e6
        return [(d,r,np.zeros(len(r)),np.zeros(len(r)),np.asarray(vec))]
    coeff=E@vec
    result=[]; offset=0
    for d,bl in zip(domains,block_len):
        n=d['end']-d['start']; r=lib.sqzx(x[:,d['start']:d['end']],n,2)*1e6
        u=np.asarray(coeff[offset:offset+bl[0]]); v=np.zeros(len(r))
        if family=='S':
            source=coeff[offset+bl[0]:offset+bl[0]+bl[1]]
            if d['phase']=='fluid':
                rv=lib.sqzx(prep['vx'][:,d['start']:d['end']],n,1)*1e6
                v=interp1d(rv,source,kind='cubic')(r)
            else: v=np.asarray(source)
        result.append((d,r,u,v,np.zeros(len(r))))
        offset+=sum(bl)
    return result


def _canonical(model,raw,family,l):
    regions=[]; integral=0.0; corrections=[]
    for d,r,u,v,w in raw:
        for layer in model['layers']:
            if layer['id'] not in d['layers']: continue
            lo,hi=layer['r_m'][0],layer['r_m'][-1]
            rr=np.unique(np.r_[lo,r[(r>lo)&(r<hi)],hi])
            parts=[np.interp(rr,r,a) for a in [u,v,w]]
            if lo==0 and family=='T' and parts[2][0]!=0:
                corrections.append(dict(kind='toroidal_centre_regularity',before=float(parts[2][0]),after=0.))
                parts[2][0]=0.
            rho=np.interp(rr,layer['r_m'],layer['rho_kg_m3'])
            integral+=float(np.trapezoid(rho*rr**2*sum(a*a for a in parts),x=rr))
            regions.append(dict(layer_id=layer['id'],r_m=rr.tolist(),u=parts[0],v=parts[1],w=parts[2]))
    if not np.isfinite(integral) or integral<=0:
        raise SolverError('Eigenfunction has invalid mass integral',family=family,l=l)
    factor=1/math.sqrt(integral)
    for region in regions:
        for key in ['u','v','w']: region[key]=(region[key]*factor).tolist()
    return regions,dict(source='Ouroboros unscaled generalized mass eigenvector; tangential unit-vector basis',
        quadrature='layerwise trapezoid on exported region grid',pre_rescale_integral=integral,rescale_factor=factor,
        displacement_units='kg^(-1/2)',internal_radius_to_m=1e6,internal_density_to_kg_m3=1e3,
        internal_generalized_mass_to_kg=1e15,centre_method='regular U=V=0 except S l1 even-U extrapolation and V=sqrt(2)U',corrections=corrections)


def _potential(model, mode, gravity):
    """Poisson potential of the displacement, integrated by parts per layer.

    This includes boundary density sheets without differentiating density jumps.
    Dimensionless radius ratios avoid overflow for high angular degrees.
    """
    if mode['family']=='T':
        return  # Toroidal mass redistribution is identically zero.
    by_id={a['id']:a for a in model['layers']}
    radius=np.concatenate([a['r_m'] for a in mode['regions']])
    density=np.concatenate([np.interp(a['r_m'],by_id[a['layer_id']]['r_m'],by_id[a['layer_id']]['rho_kg_m3']) for a in mode['regions']])
    u=np.concatenate([a['u'] for a in mode['regions']]); v=np.concatenate([a['v'] for a in mode['regions']])
    l=mode['l']; k=math.sqrt(l*(l+1)); phi=np.zeros(len(radius))
    inner=density*(l*u+k*v); outer=density*(-(l+1)*u+k*v)
    for i,r in enumerate(radius):
        a=0 if r==0 else np.trapezoid(inner[:i+1]*(radius[:i+1]/r)**(l+1),x=radius[:i+1])
        ratio=np.divide(r,radius[i:],out=np.zeros(len(radius)-i),where=radius[i:]!=0)
        if l==0: ratio[:]=1
        b=np.trapezoid(outer[i:]*ratio**l,x=radius[i:])
        phi[i]=-4*np.pi*6.6723e-11/(2*l+1)*(a+b)
    offset=0
    for region in mode['regions']:
        count=len(region['r_m']); region['potential']=phi[offset:offset+count].tolist(); offset+=count
    mode['provenance']['potential']=dict(status='postprocessed',units='m kg^(-1/2) s^(-2)',gravity=gravity,
        method='Poisson integral of canonical displacement; layer boundaries retained',
        role='consistent self-gravity diagnostic' if gravity==2 else 'diagnostic only; not included in the selected eigenvalue problem')


def _inverse_q(layer,key):
    if key not in layer:
        raise ValueError('linear_q requires '+key+' in material '+layer['id']+'; use null for infinite Q')
    return np.array([0. if q is None else 1./q for q in layer[key]])


def _dispersed_model(reference,target):
    reference_frequency=reference.get('reference_frequency_hz')
    if reference_frequency is None or reference_frequency<=0:
        raise ValueError('linear_q requires model.reference_frequency_hz')
    effective=deepcopy(reference)
    log_ratio=math.log(target/reference_frequency)
    for layer in effective['layers']:
        rho=np.asarray(layer['rho_kg_m3'],dtype=float); mu=rho*np.asarray(layer['vs_m_s'])**2
        kappa=rho*np.asarray(layer['vp_m_s'])**2-4*mu/3
        kappa*=1+2/math.pi*log_ratio*_inverse_q(layer,'q_bulk')
        if layer['phase']=='solid': mu*=1+2/math.pi*log_ratio*_inverse_q(layer,'q_shear')
        if np.any(kappa<=0) or (layer['phase']=='solid' and np.any(mu<=0)):
            raise ValueError('linear-Q shift produces nonpositive stiffness; approximation invalid')
        layer['vp_m_s']=np.sqrt((kappa+4*mu/3)/rho).tolist()
        layer['vs_m_s']=np.sqrt(mu/rho).tolist()
    effective['reference_frequency_hz']=target
    return validate_model(effective)


def _attenuate(reference,effective,mode,target):
    """First-order Q from bulk and deviatoric strain energy (D&T 9.13–14).

    A canonical mass integral of one makes omega² the modal inertia denominator.
    The eigenfunction is elastic at target; the final logarithmic correction is
    first order and must not be described as a nonlinear viscoelastic solve.
    """
    by_id={a['id']:a for a in effective['layers']}
    loss=0.; energy_bulk=0.; energy_shear=0.; l=mode['l']; k=math.sqrt(l*(l+1))
    for reg in mode['regions']:
        layer=by_id[reg['layer_id']]; r=np.asarray(reg['r_m'])
        u=np.asarray(reg['u']); v=np.asarray(reg['v']); w=np.asarray(reg['w'])
        rho=np.interp(r,layer['r_m'],layer['rho_kg_m3'])
        mu=rho*np.interp(r,layer['r_m'],layer['vs_m_s'])**2
        kappa=rho*np.interp(r,layer['r_m'],layer['vp_m_s'])**2-4*mu/3
        if mode['family']=='T':
            shear=(r*np.gradient(w,r,edge_order=2)-w)**2+(l*(l+1)-2)*w*w
            bulk=np.zeros_like(r)
        else:
            du=np.gradient(u,r,edge_order=2); dv=np.gradient(v,r,edge_order=2)
            bulk=(r*du+2*u-k*v)**2
            shear=(2*r*du-2*u+k*v)**2/3+(r*dv-v+k*u)**2+(l*(l+1)-2)*v*v
        qb=np.interp(r,layer['r_m'],_inverse_q(layer,'q_bulk'))
        qs=np.interp(r,layer['r_m'],_inverse_q(layer,'q_shear')) if layer['phase']=='solid' else np.zeros_like(r)
        energy_bulk+=float(np.trapezoid(kappa*bulk,x=r))
        energy_shear+=float(np.trapezoid(mu*shear,x=r))
        loss+=float(np.trapezoid(kappa*bulk*qb+mu*shear*qs,x=r))
    elastic=mode['frequency_hz']; inverse_q=loss/(2*math.pi*elastic)**2
    if not np.isfinite(inverse_q) or inverse_q<0: raise SolverError('Invalid strain-energy modal Q',mode_id=mode['id'])
    mode['q']=None if inverse_q==0 else 1/inverse_q
    corrected=elastic*(1+inverse_q/math.pi*math.log(elastic/target))
    if corrected<=0: raise SolverError('Linear-Q modal correction is nonpositive',mode_id=mode['id'])
    mode['frequency_hz']=corrected
    mode['provenance']['attenuation']=dict(method='first-order constant-Q logarithmic dispersion and strain-energy loss',
        elastic_frequency_hz=elastic,corrected_frequency_hz=corrected,target_frequency_hz=target,
        reference_frequency_hz=reference['reference_frequency_hz'],inverse_modal_q=inverse_q,
        bulk_strain_energy=energy_bulk,shear_strain_energy=energy_shear,
        eigenfunction='elastic approximation at effective target-frequency model',experimental=True)
    mode['provenance']['quality']['warnings'].append('Experimental first-order Q; no exact viscoelastic eigenfunction.')


def _eigenpairs(A,B,request):
    """Refine low eigenpairs through a shifted inverse for thin-layer contrast.

    Direct symmetric eigensolvers have absolute error governed by the largest
    stiffness eigenvalue. The inverse problem resolves a requested low-frequency
    window without silently treating those physical modes as numerical zeros.
    High-frequency eigenpairs remain the direct full-spectrum solution.
    """
    values,vectors=eigh(A,B,check_finite=True)
    roundoff=np.max(abs(values))*np.finfo(float).eps*len(values)*8
    floor=(2*np.pi*request['frequency_min_hz'])**2
    if roundoff < floor*.1: return values,vectors,'direct symmetric generalized eigensolve'
    shift=-floor
    factor=cholesky(B,lower=True)
    shifted=A-shift*B
    scale=1/np.sqrt(np.maximum(abs(np.diag(shifted)),np.finfo(float).tiny))
    rhs=scale[:,None]*factor
    inverse=rhs.T@linear_solve(scale[:,None]*shifted*scale[None,:],rhs,assume_a='sym')
    reciprocal,basis=eigh((inverse+inverse.T)/2)
    refined=np.full_like(reciprocal,np.inf)
    np.divide(1.,reciprocal,out=refined,where=reciprocal!=0)
    refined+=shift
    bound=max((2*np.pi*request['frequency_max_hz'])**2*4,roundoff*10)
    old=np.flatnonzero(abs(values)<bound)
    new=np.flatnonzero(abs(refined)<bound)
    new=new[np.argsort(refined[new])]
    if len(old)!=len(new):
        raise SolverError('Ill-conditioned spectrum could not be classified reliably',direct_window_count=len(old),inverse_window_count=len(new),window_omega_squared=bound)
    values[old]=refined[new]
    vectors[:,old]=solve_triangular(factor.T,basis[:,new],lower=False)
    return values,vectors,'direct full spectrum with shifted-inverse refinement of low-frequency window'


def _spectrum(eigenvalues,excluded,family,l,domain_id,request):
    vals=np.asarray(eigenvalues)
    threshold=max(min(float(np.max(np.abs(vals)))*np.finfo(float).eps*max(len(vals),1)*8, (2*np.pi*request['frequency_min_hz'])**2*1e-3),1e-16)
    group=dict(family=family,l=l,solid_domain_id=domain_id,status='success',matrix_dimension=len(vals),
        spectrum=dict(negative=int(np.sum(vals < -threshold)),near_zero=int(np.sum(abs(vals)<=threshold)),
                      positive=int(np.sum(vals>threshold)),threshold=threshold),
        excluded_subspace_count=excluded,exclusion_basis='Ouroboros mixed fluid tangential essential-space dimension' if excluded else 'none',
        spectral_completeness=dict(status='truncated' if request['n_max'] is not None else 'complete',reason='explicit n_max' if request['n_max'] is not None else 'full computed finite-element eigenspectrum'))
    physical=vals[excluded:]
    if np.any(physical < -threshold):
        raise SolverError('Significant negative omega² in retained physical spectrum',group=group,min_omega_squared=float(np.min(physical)))
    return group,threshold


def _elastic(model,request):
    counts=_allocation(model,request['mesh_size']); groups=[]; modes=[]
    # Conservative unreduced mixed matrix dimension, before allocating dense FE blocks.
    dimension=int(max(sum((8 if a['phase']=='fluid' else 6)*int(n)+4 for a,n in zip(model['layers'],counts)),1))
    memory=12*8*dimension*dimension
    if memory>request['memory_mib']*1024**2:
        raise SolverError('Estimated solver memory exceeds memory_mib; lower mesh_size or raise budget',estimated_bytes=memory,matrix_dimension=dimension)
    started=time.perf_counter()
    for family in request['families']:
        prep=_prepare(model,counts,family,request['gravity'])
        degrees=[0] if family=='R' else range(max(1,request['l_min']),request['l_max']+1)
        for l in degrees:
            if family=='T':
                prep['fem'].set_k(math.sqrt(l*(l+1)))
                solid=[i for i,d in enumerate(prep['domains']) if d['phase']=='solid']
                if not solid:
                    groups.append(dict(family='T',l=l,solid_domain_id=None,status='not_applicable',matrix_dimension=0,
                        spectrum=dict(negative=0,near_zero=0,positive=0,threshold=0),excluded_subspace_count=0,
                        exclusion_basis='no solid domain',spectral_completeness=dict(status='complete',reason='fluid has no elastic toroidal modes')))
                jobs=[]
                for i in solid:
                    domain=prep['domains'][i]
                    local=lib.modelDiv(prep['fem'],np.arange(domain['start'],domain['end']))
                    A,B=FEM.toroidal(local,prep['invV'],2,prep['Dr'])
                    centre=domain['start']==0
                    eig,vec,method=_eigenpairs(A[1:,1:] if centre else A,B[1:,1:] if centre else B,request)
                    if centre: vec=np.vstack((np.zeros(vec.shape[1]),vec))
                    jobs.append((i,eig,vec,None,None,method,0))
            else:
                A,B,A0,E,Bfull,types,bl=_assemble(prep,family,l,request['gravity'])
                if family=='S' and l==1 and request['gravity'] in [0,2]:
                    # Free isolated spheres admit exact rigid translation. The
                    # piecewise FE gravity quadrature weakly breaks that symmetry;
                    # remove only its rank-one stiffness coupling, keeping inertia.
                    full=np.concatenate([np.r_[np.ones(block[0]),np.full(block[1],math.sqrt(2))] for block in bl])
                    translation=full[np.delete(np.arange(len(full)),[0,bl[0][0]])]
                    bt=B@translation; at=A@translation; norm=float(translation@bt)
                    A=A-np.outer(at,bt)/norm-np.outer(bt,at)/norm+np.outer(bt,bt)*float(translation@at)/(norm*norm)
                    A=(A+A.T)/2
                eig,vec,eigen_method=_eigenpairs(A,B,request)
                excluded=sum(d['end']-d['start'] for d in prep['domains'] if d['phase']=='fluid') if family=='S' else 0
                if family=='S' and prep['domains'][0]['phase']=='fluid': excluded=max(0,excluded-1)
                jobs=[(None,eig,vec,bl,A0,E,excluded)]
            for domain_index,eig,vec,bl,A0,E,excluded in jobs:
                domain_id=None if domain_index is None else 'solid:'+','.join(prep['domains'][domain_index]['layers'])
                group,threshold=_spectrum(eig,excluded,family,l,domain_id,request)
                group['eigensolver']=eigen_method if family!='T' else E
                groups.append(group)
                for raw_index in range(excluded,len(eig)):
                    n=raw_index-excluded
                    if request['n_max'] is not None and n>request['n_max']: break
                    if eig[raw_index]<=threshold: continue
                    f=math.sqrt(float(eig[raw_index]))/(2*math.pi)
                    if not request['linear_q'] and not request['frequency_min_hz']<=f<=request['frequency_max_hz']: continue
                    raw=_raw_regions(prep,family,l,vec[:,raw_index],bl,A0,E,domain_index)
                    regions,norm=_canonical(model,raw,family,l)
                    identity=f'{family}{n}_{l}'+(':'+domain_id if domain_id else '')
                    modes.append(dict(id=identity,family=family,n=n,l=l,frequency_hz=f,q=None,regions=regions,
                        normalization='mass_integral_1',provenance=dict(solver='Ouroboros v6.0',upstream_commit=UPSTREAM_COMMIT,
                        solid_domain_id=domain_id,raw_eigenpair_index=raw_index,source_n=n,label_convention='radial index after essential-space removal, retaining zero-mode index',
                        normalization_conversion=norm,potential=dict(status='absent',reason='not evaluated'),
                        quality=dict(status='unverified',mesh_convergence=None,benchmark=None,warnings=['Finite-element result has not been independently benchmarked.']))))
    return dict(schema_version='1.0',model=deepcopy(model),modes=modes,provenance=dict(
        solver='Ouroboros mixed Galerkin v6.0',upstream_commit=UPSTREAM_COMMIT,patches=PATCHES,model_hash=_hash(model),
        request=deepcopy(request),gravity=request['gravity'],groups=groups,
        effective_settings=dict(mesh_counts={a['id']:int(n) for a,n in zip(model['layers'],counts)},actual_mesh_size=int(sum(counts)),
            matrix_dimension_estimate=dimension,estimated_working_memory_bytes=memory),runtime_s=time.perf_counter()-started,
        effective_model=dict(reference='bundle.model')))


def solve(model, families=('R','S','T'), l_min=0,l_max=4,frequency_min_hz=.00005,
          frequency_max_hz=.003,mesh_size=100,gravity=2,**options):
    """Compute physical R/S/T eigenpairs; a failed requested group raises SolverError.

    Mesh refinement is opt-in. Input dictionaries are never modified. Frequencies
    filter the full discrete spectrum unless an explicit ``n_max`` truncates it.
    """
    request=_request(dict(families=families,l_min=l_min,l_max=l_max,
        frequency_min_hz=frequency_min_hz,frequency_max_hz=frequency_max_hz,mesh_size=mesh_size,gravity=gravity,**options))
    reference=deepcopy(validate_model(model))
    effective=_dispersed_model(reference,request['target_frequency_hz']) if request['linear_q'] else reference
    try:
        result=_elastic(effective,request)
    except np.linalg.LinAlgError as error:
        raise SolverError('Matrix factorization failed: '+str(error),request=request,model_hash=_hash(reference)) from error
    if request['linear_q']:
        for mode in result['modes']: _attenuate(reference,effective,mode,request['target_frequency_hz'])
    if request['convergence_check']:
        fine_request={**request,'mesh_size':max(2*mesh_size,mesh_size+len(effective['layers'])*4),'convergence_check':False}
        fine=_elastic(effective,fine_request)
        if request['linear_q']:
            for mode in fine['modes']: _attenuate(reference,effective,mode,request['target_frequency_hz'])
        candidates={m['id']:m for m in fine['modes']}
        for mode in result['modes']:
            other=candidates.get(mode['id'])
            if other is None:
                mode['provenance']['quality']['warnings'].append('Corresponding mode absent from refined frequency window.')
                continue
            change=abs(mode['frequency_hz']-other['frequency_hz'])/other['frequency_hz']
            mode['provenance']['quality'].update(status='converged' if change<=.005 else 'unconverged',
                mesh_convergence=dict(coarse_mesh=result['provenance']['effective_settings']['actual_mesh_size'],
                    fine_mesh=fine['provenance']['effective_settings']['actual_mesh_size'],relative_frequency_change=change,tolerance=.005))
    if request['linear_q']:
        result['modes']=[m for m in result['modes'] if request['frequency_min_hz']<=m['frequency_hz']<=request['frequency_max_hz']]
    for mode in result['modes']:
        _potential(effective,mode,request['gravity'])
    if request['linear_q']:
        result['model']=reference
        result['provenance']['model_hash']=_hash(reference)
        result['provenance']['effective_model']=dict(model=effective,model_hash=_hash(effective),
            method='stiffness*(1+2/(pi*Q)*log(target/reference))')
    return validate_bundle(result)
