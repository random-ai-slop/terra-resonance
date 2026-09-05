"""Import a Terra GLB and its manifest into an editable Blender project.

Usage:
  blender --background --python examples/blender_import.py -- mode.glb mode.blend

The input GLB contains real shape keys and weight animation. Run this script
inside Blender; standard Python cannot manufacture a Blender-native project.
"""

from pathlib import Path
import argparse
import json
import sys


def main():
    import bpy

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("glb", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--fps", type=int, default=24)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else [])
    source = args.glb.resolve()
    output = args.output.resolve()
    if not source.is_file():
        raise FileNotFoundError(source)
    if output.suffix.lower() != ".blend":
        raise ValueError("Output must end in .blend")
    if output.exists() and not args.overwrite:
        raise FileExistsError("Output exists; pass --overwrite explicitly.")
    if args.fps <= 0:
        raise ValueError("--fps must be positive")
    manifest_path = Path(str(source) + ".json")
    info = json.loads(manifest_path.read_text())
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.fps = args.fps
    bpy.ops.import_scene.gltf(filepath=str(source))
    meshes = [o for o in scene.objects if o.type == "MESH" and o.data.shape_keys is not None]
    if not meshes or not any(len(o.data.shape_keys.key_blocks) > 1 for o in meshes):
        raise RuntimeError("GLB did not import an editable morph mesh.")
    cameras = [o for o in scene.objects if o.type == "CAMERA"]
    if cameras:
        scene.camera = cameras[0]
    duration = info["playback_duration_s"]
    scene.frame_start = 1
    scene.frame_end = 1 + round(duration * args.fps)
    scene.render.resolution_x = info.get("width", 1200)
    scene.render.resolution_y = info.get("height", 900)
    scene.render.resolution_percentage = 100
    scene["terra_manifest"] = json.dumps(info, ensure_ascii=False)
    scene["physical_start_s"] = info["scene"]["time_s"]
    scene["physical_seconds_per_playback_second"] = info["scene"]["time_scale"]
    scene["scientific_note"] = (
        "Shape keys carry normalized modal illustration. Colors are fixed at initial time."
    )
    world = bpy.data.worlds.new("Terra background")
    world.use_nodes = True
    scene.world = world
    background = world.node_tree.nodes.get("Background")
    background.inputs["Color"].default_value = (
        (0.018, 0.032, 0.06, 1) if info["scene"]["background"] == "dark" else (0.8, 0.8, 0.78, 1)
    )
    background.inputs["Strength"].default_value = 0.7
    light_data = bpy.data.lights.new("Soft key", "AREA")
    light = bpy.data.objects.new("Soft key", light_data)
    scene.collection.objects.link(light)
    light.location = (3, -4, 5)
    light_data.energy = 400
    light_data.size = 5
    scene.frame_set(1)
    output.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(output))
    if not output.is_file() or output.stat().st_size == 0:
        raise RuntimeError("Blender did not save the project.")
    print(f"Saved editable scene: {output}")


if __name__ == "__main__":
    main()
