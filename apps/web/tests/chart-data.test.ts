import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';
import { frequencySeries } from '../lib/science/chart-data';
import type { Bundle } from '../lib/science/types';
test('PREM inner-core and mantle fundamentals never share a dispersion polyline', () => {
  const b = JSON.parse(
    readFileSync(
      new URL('../public/data/prem-modes.json', import.meta.url),
      'utf8',
    ),
  ) as Bundle;
  const branches = frequencySeries(b).filter((s) => s.name.startsWith('0T'));
  assert.equal(branches.length, 2);
  for (const branch of branches)
    assert.deepEqual(
      branch.points.map((p) => p[0]),
      [2, 3, 4],
    );
  // Independent frequency families: inner-core >1 mHz, mantle <1 mHz.
  assert.ok(branches.some((s) => s.points.every((p) => p[1] > 1)));
  assert.ok(branches.some((s) => s.points.every((p) => p[1] < 1)));
});
