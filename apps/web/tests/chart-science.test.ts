import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';
import { comparisonMode } from '../lib/science/comparison';
import { sampleProbe } from '../lib/science/field';
import type { Bundle } from '../lib/science/types';

const fixture = JSON.parse(
  readFileSync(
    new URL('./fixtures/field-reference.json', import.meta.url),
    'utf8',
  ),
);

void test('comparison requires explicit IDs for ambiguous labels and permits renamed domains', () => {
  const bundle: Bundle = structuredClone(fixture.bundles.interface);
  const reference = bundle.modes[0];
  assert.equal(comparisonMode(reference, bundle)?.id, reference.id);
  const other = structuredClone(reference);
  other.id = 'crossing-candidate';
  other.frequency_hz *= 1.02;
  bundle.modes.unshift(other);
  assert.equal(comparisonMode(reference, bundle), null);
  assert.equal(comparisonMode(reference, bundle, reference.id), reference);
  bundle.modes.reverse();
  assert.equal(comparisonMode(reference, bundle), null);
  assert.equal(comparisonMode(reference, bundle, other.id), other);
  other.provenance.solid_domain_id = 'renamed-same-solid';
  assert.equal(comparisonMode(reference, bundle, other.id), other);
  assert.equal(comparisonMode(reference, bundle, 'missing'), null);
});

void test('cached material-point probes retain Python Q derivatives, raw scaling and interface sides', () => {
  for (const sample of fixture.field_cases) {
    const bundle: Bundle = fixture.bundles[sample.bundle];
    sample.points_m.forEach((point: number[], i: number) => {
      const [x, y, z] = point,
        r = Math.hypot(x, y, z);
      const p = {
        latitude_deg: r ? (Math.atan2(z, Math.hypot(x, y)) * 180) / Math.PI : 0,
        longitude_deg: (Math.atan2(y, x) * 180) / Math.PI,
        radius_fraction: r / bundle.model.radius_m,
        ...(sample.layer_id ? { layer_id: sample.layer_id } : {}),
      };
      const values = sampleProbe(
        bundle,
        sample.terms,
        p,
        [sample.time_s, sample.time_s],
        sample.derivative,
        sample.normalized,
      );
      for (const row of values) {
        assert.equal(row[0], sample.time_s);
        row
          .slice(1)
          .forEach((v, j) =>
            assert.ok(
              Math.abs(v - sample.expected[i][j]) < 1e-11,
              `${sample.name} coordinate ${j}`,
            ),
          );
      }
    });
  }
});
