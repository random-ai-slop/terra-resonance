import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';
import { fileURLToPath } from 'node:url';
import {
  canonicalHash,
  defaultScene,
  modelHash,
  parseJson,
  parseProject,
  validateBundle,
  validateExportSpec,
  validateScene,
} from '../lib/science/data';
import { evaluate, harmonic } from '../lib/science/field';
import type { Bundle, Scene } from '../lib/science/types';

const fixture = JSON.parse(
  readFileSync(
    fileURLToPath(
      new URL('./fixtures/field-reference.json', import.meta.url),
    ),
    'utf8',
  ),
);

test('frequency evidence is consistent with its actual model and frequency', async () => {
  const bundle = structuredClone(Object.values(fixture.bundles)[0]) as Bundle;
  const mode = bundle.modes[0];
  const benchmark = {
    source: 'Analytic field fixture, not an Earth benchmark', quantity: 'frequency_hz',
    model_hash: await modelHash(bundle.model), reference_frequency_hz: mode.frequency_hz,
    relative_error: 0, tolerance: .005,
  };
  mode.provenance.quality = { status: 'benchmark_checked', mesh_convergence: null, benchmark, warnings: [] };
  assert.equal(validateBundle(bundle), bundle);
  for (const [key, value] of [
    ['model_hash', '0'.repeat(64)], ['quantity', 'unrelated'],
    ['reference_frequency_hz', 2 * mode.frequency_hz], ['relative_error', .1],
  ] as const) {
    const bad = structuredClone(bundle);
    Object.assign(bad.modes[0].provenance.quality.benchmark!, { [key]: value });
    assert.throws(() => validateBundle(bad), /benchmark/);
  }
  benchmark.relative_error = Number.EPSILON;
  validateBundle(bundle);
  const prem = JSON.parse(readFileSync(new URL('../public/data/prem-modes.json', import.meta.url), 'utf8'));
  validateBundle(prem);
});

test('JSON integer-valued decimal lexemes are accepted without changing JCS identity', async () => {
  const bundle = structuredClone(Object.values(fixture.bundles)[0]) as Bundle;
  const raw = JSON.stringify(bundle).replace(/"(n|l)":(\d+)/g, '"$1":$2.0');
  const decimal = validateBundle(parseJson(raw));
  assert.equal(await canonicalHash(decimal), await canonicalHash(bundle));
  const scene = await defaultScene(decimal);
  validateScene(scene, decimal, await canonicalHash(decimal));
  assert.ok(evaluate(decimal, scene.terms, [0, 0, 0], 0).every(Number.isFinite));
  for (const invalid of [true, .5, 1e21]) {
    const bad = structuredClone(bundle);
    Object.assign(bad.modes[0], {n: invalid});
    assert.throws(() => validateBundle(bad));
  }
});
function close(
  actual: ArrayLike<number>,
  expected: number[],
  name: string,
  tolerance = 1e-11,
) {
  assert.equal(actual.length, expected.length, name + ' length');
  for (let i = 0; i < expected.length; i++)
    assert.ok(
      Number.isFinite(actual[i]) &&
        Math.abs(actual[i] - expected[i]) <= tolerance,
      `${name}[${i}] ${actual[i]} != ${expected[i]}`,
    );
}

test('shared Python fields: Cartesian centre, poles, material sides and Q derivatives', () => {
  for (const sample of fixture.field_cases) {
    const b = validateBundle(fixture.bundles[sample.bundle]);
    const actual = evaluate(
      b,
      sample.terms,
      sample.points_m.flat(),
      sample.time_s,
      sample.derivative,
      sample.normalized,
      sample.layer_id ?? undefined,
    );
    close(actual, sample.expected.flat(), sample.name);
  }
  for (const sample of fixture.harmonic_cases) {
    const actual = sample.theta.map((theta: number, i: number) =>
      harmonic(sample.l, sample.m, theta, sample.phi[i]),
    );
    for (let component = 0; component < 3; component++)
      close(
        actual.map((v: number[]) => v[component]),
        sample.expected[component],
        `Y${sample.l},${sample.m} component ${component}`,
      );
  }
});

test('independent dipole identity remains stable very close to a pole', () => {
  const a = Math.sqrt(3 / (4 * Math.PI));
  for (const theta of [0, 1e-12, 1e-9, 1e-7, Math.PI - 1e-9, Math.PI]) {
    const phi = 0.713;
    close(
      harmonic(1, 1, theta, phi),
      [
        -a * Math.sin(theta) * Math.cos(phi),
        -a * Math.cos(theta) * Math.cos(phi),
        a * Math.sin(phi),
      ],
      'analytic Y11',
      1e-14,
    );
  }
});

test('JCS artifact identity, valid scientific floats and lexical rejection', async () => {
  for (const sample of fixture.hash_cases) {
    assert.equal(await canonicalHash(sample.value), sample.sha256);
    assert.equal(
      await canonicalHash(parseJson(JSON.stringify(sample.value))),
      sample.sha256,
    );
  }
  for (const [name, b] of Object.entries(fixture.bundles)) {
    assert.equal(await canonicalHash(b), fixture.bundle_hashes[name]);
    assert.equal(
      await modelHash((b as Bundle).model),
      fixture.model_hashes[name],
    );
  }
  for (const raw of fixture.invalid_json_cases)
    assert.throws(() => parseJson(raw));
  assert.throws(() => parseJson('{"a":1,"a":2}'), /Duplicate/);
  assert.throws(() => parseJson('{"a":{"b":1,"b":2}}'), /Duplicate/);
  assert.equal(
    (parseJson('{"scientific":1e21}') as { scientific: number }).scientific,
    1e21,
  );
});

test('default SceneSpec, project import and bad-state rejection match Python', async () => {
  for (const [name, value] of Object.entries(fixture.bundles)) {
    const bundle = validateBundle(value),
      scene = await defaultScene(bundle);
    assert.deepEqual(scene, fixture.default_scenes[name]);
    validateScene(scene, bundle, fixture.bundle_hashes[name]);
    const project = {
      format: 'terra-project',
      version: '1.0',
      bundle,
      scene,
      export: { format: 'gif' },
    };
    assert.deepEqual(await parseProject(JSON.stringify(project)), {
      ...project,
      export: validateExportSpec(project.export),
    });
    const bad = structuredClone(project);
    bad.bundle.provenance.changed = true;
    await assert.rejects(() => parseProject(JSON.stringify(bad)), /different numerical/);
  }
  const b = fixture.bundles.analytic as Bundle,
    original = fixture.default_scenes.analytic as Scene;
  const invalids = [
    (s: Scene) => {
      s.geography = true;
      s.radius_fraction = 0.5;
    },
    (s: Scene) => {
      s.trajectory.enabled = true;
    },
    (s: Scene) => {
      s.point = { latitude_deg: 0, longitude_deg: 0, radius_fraction: 1 };
      s.trajectory.enabled = true;
      s.trajectory.samples = 8;
    },
    (s: Scene) => {
      s.nodes = true;
      s.color = 'magnitude';
    },
  ];
  for (const mutate of invalids) {
    const s = structuredClone(original);
    mutate(s);
    assert.throws(() => validateScene(s, b, fixture.bundle_hashes.analytic));
  }
  const large = structuredClone(original);
  large.deformation = 0.8;
  large.arrow_scale = 3;
  large.camera.distance = 0.8;
  large.camera.elevation_deg = 90;
  validateScene(large, b, fixture.bundle_hashes.analytic); // UI slider range is not wire validity.
  const falseQuality = structuredClone(b);
  falseQuality.modes[0].provenance.quality.status = 'converged';
  assert.throws(() => validateBundle(falseQuality), /evidence/);
  assert.throws(
    () => validateExportSpec({ format: 'mp4', transparent: true }),
    /Transparency/,
  );
  assert.throws(() => validateExportSpec({ format: 'gif', fps: 24 }), /GIF/);
});

test('independent ProbeSpec defaults, export defaults and strict scene points survive import', async () => {
  const bundle = validateBundle(fixture.bundles.analytic);
  const scene = await defaultScene(bundle);
  const project = {
    format: 'terra-project',
    version: '1.0',
    bundle,
    scene,
    metadata: { author: 'saved metadata', nested: { notes: ['retained'] } },
    probe: {
      latitude_deg: 35,
      longitude_deg: 105,
      start_s: 1.3,
      step_s: 0.3,
      sample_count: 1,
    },
    export: { format: 'png' },
  };
  const original = JSON.stringify(project);
  const parsed = await parseProject(original);
  assert.equal(parsed.scene.point, null);
  assert.deepEqual(parsed.probe, {
    ...project.probe,
    radius_fraction: 1,
    derivative: 0,
    normalized: true,
  });
  assert.deepEqual(parsed.export, validateExportSpec(project.export));
  assert.deepEqual(
    (parsed as unknown as typeof project).metadata,
    project.metadata,
  );
  assert.equal(JSON.stringify(project), original);
  for (const key of ['normalized', 'derivative', 'radius_fraction']) {
    const bad = { ...project, probe: { ...project.probe, [key]: null } };
    await assert.rejects(() => parseProject(JSON.stringify(bad)));
  }
  const invalidPoint = {
    ...project,
    scene: { ...scene, point: { latitude_deg: 0, longitude_deg: 0 } },
  };
  await assert.rejects(
    () => parseProject(JSON.stringify(invalidPoint)),
    /radius_fraction/,
  );
  const tooFine = {
    ...project,
    probe: { ...project.probe, start_s: 1e12, step_s: 1e-5, sample_count: 2 },
  };
  await assert.rejects(
    () => parseProject(JSON.stringify(tooFine)),
    /floating-point resolution/,
  );
  await parseProject(
    JSON.stringify({ ...tooFine, probe: { ...tooFine.probe, step_s: 0.001 } }),
  );
  await parseProject(
    JSON.stringify({
      ...tooFine,
      probe: { ...tooFine.probe, sample_count: 1 },
    }),
  );
});
