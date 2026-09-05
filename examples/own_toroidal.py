"""Source recipe for the experimental numerical pilot (not an installed file).

Install terra-resonance, then run this copied recipe from any directory:
    python own_toroidal.py --out toroidal-pilot
It writes a canonical bundle, a reproducible project and one annotated PNG.
"""
import argparse
import math
from pathlib import Path

from earth_modes import default_scene, homogeneous_model, make_project, save_bundle, save_project
from earth_modes.experimental import solve_toroidal
from earth_modes.export import export_image


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path,default=Path('toroidal-pilot'))
    args=parser.parse_args()
    bundle=solve_toroidal(homogeneous_model(1e6,4000,8000,4000),l_min=2,l_max=2,mesh_size=100,frequency_max_hz=.002)
    scene=default_scene(bundle)
    scene['terms'][0]['m']=1
    scene['color']='phi'
    # Analytic T(l=2,m=1) phi envelope in the normalized angular basis.
    scene['color_limit']=1.05*math.sqrt(15/(4*math.pi))/math.sqrt(6)
    scene['arrows']=True
    project=make_project(bundle,scene)
    args.out.mkdir(parents=True,exist_ok=True)
    save_bundle(bundle,args.out/'modes.json')
    save_project(project,args.out/'project.terra.json')
    export_image(bundle,scene,args.out/'toroidal.png',width=800,height=600)
    print(f"Wrote {len(bundle['modes'])} experimental modes and a reproducible scene to {args.out}")


if __name__=='__main__': main()
