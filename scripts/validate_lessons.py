#!/usr/bin/env python3
"""Verify six persisted teaching projects and their sampled visual envelopes."""
from pathlib import Path
import json
import numpy as np
from earth_modes.data import load_bundle,load_project,bundle_hash
from earth_modes.export_common import ExportLimits
from earth_modes.export_render import geometry,scalar
from earth_modes.export_overlays import build_overlays

ROOT=Path(__file__).resolve().parents[1]


def main():
    directory=ROOT/'examples/lessons'
    catalog=json.loads((directory/'catalog.json').read_text())
    canonical=load_bundle(ROOT/'examples/prem-modes.json')
    assert catalog['bundle_hash']==bundle_hash(canonical)
    assert len(catalog['lessons'])==6
    rows=[]
    for entry in catalog['lessons']:
        project=load_project(directory/(entry['id']+'.terra.json'))
        assert 1<=len(entry['steps'])<=3 and entry['conclusion'] and entry['caution']
        assert len(project['bundle']['modes'])==47
        assert bundle_hash(project['bundle'])==catalog['bundle_hash']
        for key in ('scene','probe','export'):assert project[key]==entry[key]
        scene=project['scene'];probe=project['probe']
        for key in ('latitude_deg','longitude_deg','radius_fraction','layer_id'):
            assert scene['point'].get(key)==probe.get(key)
        period=scene['trajectory']['duration_s']
        assert np.isclose(probe['step_s']*(probe['sample_count']-1),period)
        geo=geometry(canonical,scene,ExportLimits())
        basis=np.asarray([scalar(geo.points[:geo.mesh_count],b[:geo.mesh_count],scene['color']) for b in geo.bases])
        times=np.linspace(0,period,65)
        values=geo.coefficients(times)@basis
        max_sample=float(abs(values).max())
        assert max_sample<=scene['color_limit']
        overlay=build_overlays(canonical,scene,geo,ExportLimits())
        inner_segments=0
        if scene['nodes']:
            norms=np.linalg.norm(overlay.node_points,axis=2)
            inner_segments=int(np.count_nonzero(np.all((norms>1e-8)&(norms<.99),axis=1)))
            assert inner_segments>0
        image=json.loads((directory/(entry['id']+'.png.json')).read_text())
        assert image['scene']==scene and image['bundle_hash']==catalog['bundle_hash']
        assert image['clipping_samples']==0
        rows.append(dict(id=entry['id'],steps=len(entry['steps']),fixed_color_limit=scene['color_limit'],
                         sampled_component_peak=max_sample,sampled_times=65,clipped_samples=0,
                         node_segments=len(overlay.node_points),internal_node_segments=inner_segments,
                         point_samples=probe['sample_count'],physical_window_s=period))
    evidence=dict(bundle_hash=catalog['bundle_hash'],scope='project identity, lesson sampling, fixed color envelopes and real section-node geometry',lessons=rows)
    (ROOT/'docs/validation/lessons.json').write_text(json.dumps(evidence,indent=2,allow_nan=False)+'\n')
    print(json.dumps(rows,indent=2))


if __name__=='__main__':main()
