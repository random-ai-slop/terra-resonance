import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';
import * as THREE from 'three';
import {
  animationSampling,
  buildGLBScene,
  glbExporter,
} from '../lib/science/browser-export';
import { evaluate, spatial } from '../lib/science/field';
import type { Bundle, Scene } from '../lib/science/types';
import type { Patch } from '../lib/science/geometry';
import { validateExportSpec } from '../lib/science/data';
import type { ExportSpec } from '../lib/science/types';

const fixture = JSON.parse(
  readFileSync(
    new URL('./fixtures/field-reference.json', import.meta.url),
    'utf8',
  ),
);
const bundle: Bundle = fixture.bundles.analytic;
function setup() {
  const scene: Scene = structuredClone(fixture.default_scenes.analytic);
  scene.terms = [
    { mode_id: 'radial', m: 0, amplitude: -0.8, phase_rad: 0.37 },
    { mode_id: 'dipole', m: 1, amplitude: 0.4, phase_rad: -0.81 },
  ];
  scene.time_scale = 4;
  scene.surface = 'wireframe';
  scene.wireframe_spacing_deg = null;
  const base = new Float64Array([2, 0, 0, 0, 2, 0, 0, 0, 2, -2, 0, 0]);
  const geometry = new THREE.BufferGeometry().setAttribute(
    'position',
    new THREE.Float32BufferAttribute(base, 3),
  );
  geometry.setIndex([0, 1, 2, 0, 2, 3]);
  const patch: Patch = {
    geometry,
    base,
    kind: 'surface',
    work: new Float64Array(base.length),
    bases: scene.terms.map((t) =>
      spatial(
        bundle,
        bundle.modes.find((m) => m.id === t.mode_id)!,
        t.m,
        base,
      ),
    ),
  };
  return { scene, patch };
}

test('GLB sample bound includes Q and off-key displacement reconstructed independently', () => {
  const { scene, patch } = setup(),
    start = 0.29;
  const sampling = animationSampling([patch], bundle, scene, start);
  assert.ok(sampling.guaranteed_error_m <= sampling.tolerance_m);
  const { root, clip } = buildGLBScene([patch], bundle, scene, start, false);
  const mesh = root.children.find((o) => o instanceof THREE.Mesh) as THREE.Mesh;
  const track = clip.tracks[0];
  for (const playback of [0.1317, 2.713, 7.927]) {
    let k = 0;
    while (k < track.times.length - 2 && track.times[k + 1] < playback) k++;
    const alpha =
      (playback - track.times[k]) / (track.times[k + 1] - track.times[k]);
    const width = scene.terms.length * 2;
    const expected = evaluate(
      bundle,
      scene.terms,
      patch.base,
      start + playback * scene.time_scale,
    );
    for (let i = 0; i < patch.base.length; i++) {
      let displacement = 0;
      for (let j = 0; j < width; j++) {
        const weight =
          (1 - alpha) * track.values[k * width + j] +
          alpha * track.values[(k + 1) * width + j];
        displacement +=
          weight *
          (mesh.geometry.morphAttributes.position![j] as THREE.BufferAttribute)
            .array[i] *
          bundle.model.radius_m;
      }
      assert.ok(
        Math.abs(
          displacement -
            expected[i] * scene.deformation * bundle.model.radius_m,
        ) <= sampling.tolerance_m,
      );
    }
  }
  assert.equal(
    mesh.geometry.index!.count,
    10,
    'two triangles have five distinct wire edges',
  );
  assert.ok(
    root.children.some((o) => o instanceof THREE.LineSegments),
    'reference retained',
  );
  assert.ok(
    root.children.some((o) => o instanceof THREE.OrthographicCamera),
    'camera retained',
  );
});

test('GLB binary camera spans, topology, weights and accessor bounds survive serialization', async () => {
  // The exporter only needs FileReader for the binary Blob it creates, not a DOM.
  class BlobReader {
    result: ArrayBuffer | null = null;
    onloadend: (() => void) | null = null;
    readAsArrayBuffer(blob: Blob) {
      void blob.arrayBuffer().then((buffer) => {
        this.result = buffer;
        this.onloadend?.();
      });
    }
  }
  Object.defineProperty(globalThis, 'FileReader', {
    value: BlobReader,
    configurable: true,
  });
  const { scene, patch } = setup(),
    { root, clip } = buildGLBScene([patch], bundle, scene, 0.29, false);
  const buffer = (await glbExporter().parseAsync(root, {
    binary: true,
    animations: [clip],
  })) as ArrayBuffer;
  const header = new DataView(buffer);
  assert.equal(header.getUint32(0, true), 0x46546c67);
  assert.equal(header.getUint32(8, true), buffer.byteLength);
  const length = header.getUint32(12, true),
    json = JSON.parse(
      new TextDecoder().decode(new Uint8Array(buffer, 20, length)),
    );
  assert.equal(
    json.cameras[0].orthographic.ymag,
    (scene.camera.distance * bundle.model.radius_m) / 2,
  );
  assert.equal(
    json.cameras[0].orthographic.xmag,
    (scene.camera.distance * bundle.model.radius_m * 4) / 3 / 2,
  );
  const primitive = json.meshes[0].primitives[0];
  assert.equal(primitive.mode, 1, 'GL_LINES requires pair indices');
  assert.equal(json.accessors[primitive.indices].count, 10);
  assert.equal(primitive.targets.length, scene.terms.length * 2);
  for (const accessor of json.accessors) {
    const view = json.bufferViews[accessor.bufferView];
    const width = { SCALAR: 1, VEC2: 2, VEC3: 3, VEC4: 4, MAT4: 16 }[
      accessor.type as string
    ]!;
    const bytes = { 5121: 1, 5123: 2, 5125: 4, 5126: 4 }[
      accessor.componentType as number
    ]!;
    assert.ok(width && bytes);
    assert.ok(
      (accessor.byteOffset ?? 0) +
        (accessor.count - 1) * (view.byteStride ?? width * bytes) +
        width * bytes <=
        view.byteLength,
    );
    assert.ok(
      (view.byteOffset ?? 0) + view.byteLength <= json.buffers[0].byteLength,
    );
  }
});

test('static zero-term GLB and explicit overlay omission are safe', () => {
  const { scene, patch } = setup();
  scene.point = { latitude_deg: 0, longitude_deg: 0, radius_fraction: 1 };
  assert.throws(
    () => buildGLBScene([patch], bundle, scene, 0, false),
    /explicit omission/,
  );
  scene.terms = [];
  patch.bases = [];
  const { root, clip, manifest } = buildGLBScene(
    [patch],
    bundle,
    scene,
    0,
    true,
  );
  assert.equal(clip.tracks.length, 0);
  assert.deepEqual(manifest.appearance_omissions, ['analysis_overlays']);
  const mesh = root.children.find((o) => o instanceof THREE.Mesh) as THREE.Mesh;
  assert.ok(
    [...mesh.geometry.getAttribute('color').array].every(Number.isFinite),
  );
  const spec = validateExportSpec({
    format: 'glb',
    duration_s: 3.5,
    width: 1920,
    height: 1080,
    omit_analysis_overlays: true,
  }) as unknown as ExportSpec;
  const changed = buildGLBScene([patch], bundle, scene, 0, false, spec);
  assert.equal(changed.clip.duration, 3.5);
  assert.equal(changed.manifest.aspect, 16 / 9);
  assert.equal(changed.manifest.export.width, 1920);
  assert.throws(
    () =>
      buildGLBScene([patch], bundle, scene, 0, true, {
        ...spec,
        format: 'gif',
      }),
    /format=glb/,
  );
});
