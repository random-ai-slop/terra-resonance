import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';
import * as THREE from 'three';
import {
  buildPatches,
  nodeCoordinateDefined,
  nodePoints,
  radialSamples,
  validateRenderBudget,
  zeroComponent,
  type Patch,
} from '../lib/science/geometry';
import type { Bundle, Scene } from '../lib/science/types';

const fixture = JSON.parse(
  readFileSync(
    new URL('./fixtures/field-reference.json', import.meta.url),
    'utf8',
  ),
);

test('true radial sections retain closely spaced high-overtone zeros and both interface sides', () => {
  const bundle: Bundle = structuredClone(fixture.bundles.analytic),
    scene: Scene = structuredClone(fixture.default_scenes.analytic);
  const radial = bundle.modes.find((m) => m.id === 'radial')!;
  radial.n = 18;
  radial.regions[0].r_m = [0, 0.913, 0.914, 0.915, 2];
  radial.regions[0].u = [0, 1, -1, 1, 0];
  radial.regions[0].v = radial.regions[0].w = [0, 0, 0, 0, 0];
  scene.terms = [{ mode_id: 'radial', m: 0, amplitude: 1, phase_rad: 0 }];
  scene.cutaway = true;
  const samples = radialSamples(bundle, scene, bundle.model.layers[0], 32);
  for (const r of radial.regions[0].r_m) assert.ok(samples.includes(r));
  const patches = buildPatches(bundle, scene);
  assert.equal(patches.filter((p) => p.kind === 'section').length, 2);
  const section = patches.find((p) => p.kind === 'section')!;
  const nodes = nodePoints(section, section.bases[0], 'radial');
  const radii: number[] = [];
  for (let i = 0; i < nodes.length; i += 3)
    radii.push(Math.hypot(nodes[i], nodes[i + 1], nodes[i + 2]));
  assert.ok(radii.some((r) => Math.abs(r - 0.9135) < 1e-5));
  assert.ok(radii.some((r) => Math.abs(r - 0.9145) < 1e-5));
  patches.forEach((p) => p.geometry.dispose());
  const layered: Bundle = fixture.bundles.interface,
    view: Scene = structuredClone(fixture.default_scenes.interface);
  view.cutaway = true;
  const sides = buildPatches(layered, view).filter((p) => p.kind === 'section');
  assert.equal(new Set(sides.map((p) => p.layerId)).size, 2);
  sides.forEach((p) => p.geometry.dispose());
});

test('node contours do not promote coordinate singularities or zero regions to roots', () => {
  const base = new Float64Array([0, 0, 1, 1, 0, 0, 0, 1, 0]);
  const geometry = new THREE.BufferGeometry().setAttribute(
    'position',
    new THREE.Float32BufferAttribute(base, 3),
  );
  geometry.setIndex([0, 1, 2]);
  const patch: Patch = {
    base,
    geometry,
    work: new Float64Array(9),
    bases: [],
    kind: 'surface',
  };
  const vector = new Float64Array([0, 0, 1, 1, 0, 1, 0, 1, -1]);
  assert.equal(nodeCoordinateDefined(base, 0, 'theta'), false);
  assert.equal(nodeCoordinateDefined([0, 0, 0], 0, 'radial'), false);
  assert.equal(nodePoints(patch, vector, 'theta').length, 0);
  assert.equal(zeroComponent(patch, new Float64Array(9), 'radial'), true);
  assert.equal(nodePoints(patch, new Float64Array(9), 'radial').length, 0);
  geometry.dispose();
});

test('all overlays count before fields are allocated and large source grids are refused', () => {
  const bundle: Bundle = structuredClone(fixture.bundles.analytic),
    scene: Scene = structuredClone(fixture.default_scenes.analytic);
  const plain = validateRenderBudget(bundle, scene);
  scene.geography = true;
  scene.arrows = true;
  scene.nodes = true;
  const overlay = validateRenderBudget(bundle, scene);
  assert.ok(overlay.cachePoints > plain.cachePoints);
  assert.ok(overlay.cacheBytes > plain.cacheBytes);
  bundle.modes.find((m) => m.id === scene.terms[0].mode_id)!.l = 64;
  scene.quality = 'high';
  scene.nodes = false;
  scene.geography = false;
  scene.arrows = false;
  validateRenderBudget(bundle, scene);
  scene.nodes = true;
  assert.throws(() => validateRenderBudget(bundle, scene), /budget/);
  scene.nodes = false;
  scene.cutaway = true;
  const selected = bundle.modes.find((m) => m.id === scene.terms[0].mode_id)!;
  selected.regions[0].r_m = Array.from(
    { length: 1000 },
    (_, i) => (2 * i) / 999,
  );
  assert.throws(() => validateRenderBudget(bundle, scene), /budget/);
});

test('weak radial components keep their roots while exact toroidal projection noise remains zero', () => {
  const base = new Float64Array([1, 0, 0, 0, 1, 0, -1, 0, 0]);
  const geometry = new THREE.BufferGeometry().setAttribute(
    'position',
    new THREE.Float32BufferAttribute(base, 3),
  );
  geometry.setIndex([0, 1, 2]);
  const patch: Patch = {
    base,
    geometry,
    work: new Float64Array(9),
    bases: [],
    kind: 'surface',
  };
  // Order-one azimuthal vector with radial values [+1e-13, -1e-13, +1e-13].
  const mixed = new Float64Array([1e-13, 1, 0, -1, -1e-13, 0, -1e-13, -1, 0]);
  assert.equal(zeroComponent(patch, mixed, 'radial'), false);
  assert.equal(nodePoints(patch, mixed, 'radial').length, 6);
  // Common scaling also must not erase roots through sign-product underflow.
  const tiny = Float64Array.from(mixed, (x) => x * 1e-190);
  assert.equal(zeroComponent(patch, tiny, 'radial'), false);
  assert.equal(nodePoints(patch, tiny, 'radial').length, 6);
  const bundle: Bundle = fixture.bundles.analytic,
    scene: Scene = structuredClone(fixture.default_scenes.analytic);
  scene.terms = [{ mode_id: 'toroidal', m: 1, amplitude: 1, phase_rad: 0 }];
  const toroidal = buildPatches(bundle, scene)[0];
  assert.equal(zeroComponent(toroidal, toroidal.bases[0], 'radial'), true);
  assert.equal(nodePoints(toroidal, toroidal.bases[0], 'radial').length, 0);
  toroidal.geometry.dispose();
  geometry.dispose();
});
