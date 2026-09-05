#!/usr/bin/env python3
"""R1 density-sheet evidence: sharp interfaces versus thin continuous profiles."""
from pathlib import Path
import json
import numpy as np
from earth_modes.models import homogeneous_model
from earth_modes.solver import solve


def material(width,vs):
    model=homogeneous_model(1e6,8000,8000,vs)
    def layer(name,a,b,rhoa,rhob):
        return dict(id=name,name=name,phase='solid' if vs else 'fluid',r_m=[a,b],
                    rho_kg_m3=[rhoa,rhob],vp_m_s=[8000]*2,vs_m_s=[vs]*2)
    lo,hi=5e5-width/2,5e5+width/2
    model['layers']=[layer('inner',0,lo,8000,8000)]
    if width:model['layers'].append(layer('transition',lo,hi,8000,4000))
    model['layers'].append(layer('outer',hi,1e6,4000,4000))
    return model


def main():
    rows=[]
    for vs in (0,4000):
        for gravity in (1,2):
            runs=[]
            options=dict(families=['R','S'],l_min=2,l_max=2,gravity=gravity,n_max=0,frequency_max_hz=.02)
            for width,mesh in [(0,120),(0,240),(100,240)]:
                modes=solve(material(width,vs),mesh_size=mesh,**options)['modes']
                assert [m['id'] for m in modes]==['R0_0','S0_2']
                runs.append(dict(width_m=width,mesh_size=mesh,frequencies_hz={m['id']:m['frequency_hz'] for m in modes}))
            errors={key:abs(runs[1]['frequencies_hz'][key]/value-1) for key,value in runs[2]['frequencies_hz'].items()}
            tolerance=.0015 if vs==0 else 1e-5
            assert max(errors.values())<tolerance
            if vs==0:
                assert errors['S0_2']<.6*abs(runs[0]['frequencies_hz']['S0_2']/runs[2]['frequencies_hz']['S0_2']-1)
            rows.append(dict(phase='solid' if vs else 'fluid',gravity=gravity,model=material(0,vs),request=options,
                             runs=runs,sharp_to_thin_relative_error=errors,tolerance=tolerance))
    out=Path(__file__).resolve().parents[1]/'docs/validation/density-interfaces.json'
    out.write_text(json.dumps(dict(kind='thin-transition consistency, not independent solver benchmark',results=rows),indent=2,allow_nan=False)+'\n')
    print(f'{len(rows)} density-interface gates passed; {out}')


if __name__=='__main__':main()
