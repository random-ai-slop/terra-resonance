import assert from 'node:assert/strict';
import test from 'node:test';
import {
  outputRecipe,
  outputSpec,
  setAllOmissions,
} from '../lib/science/output-recipe';
import { validateExportSpec } from '../lib/science/data';
import type { ExportSpec } from '../lib/science/types';

const defaults = (value: object) => validateExportSpec(value) as ExportSpec;

void test('project-based recipes select the requested artifact and preserve defaults', () => {
  const gif = outputRecipe(defaults({ format: 'gif', fps: null }));
  assert.equal(gif.command, 'terra export terra-project.json --out earth.gif');
  assert.equal(gif.spec.fps, null); // Python GIF exporter resolves this to exactly 20 fps.
  assert.equal(
    outputRecipe(defaults({ format: 'frames' })).command,
    'terra export terra-project.json --kind frames --out frames',
  );
  const scientific = outputRecipe(
    defaults({ format: 'svg', transparent: true, annotation: false }),
    "a'b; echo unsafe",
  );
  assert.equal(
    scientific.command,
    "terra export terra-project.json --kind eigenfunctions --mode-id 'a'\\''b; echo unsafe' --out eigenfunctions.svg --transparent --no-annotation",
  );
  assert.equal(
    outputRecipe(defaults({ format: 'csv' })).command,
    'terra export terra-project.json --kind tables --out tables',
  );
  const png = outputRecipe(
    defaults({
      format: 'png',
      width: 768,
      height: 512,
      transparent: true,
      annotation: false,
    }),
  );
  assert.equal(png.spec.width, 768);
  assert.equal(png.spec.transparent, true);
  assert.equal(png.spec.annotation, false);
  assert.equal(png.command, 'terra export terra-project.json --out earth.png');
});

void test('partial omissions survive import/export and only explicit master action changes all flags', () => {
  const partial = defaults({ format: 'glb', omit_arrows: true });
  assert.deepEqual(outputRecipe(partial).spec, partial);
  assert.equal(outputSpec(partial, 'png').omit_arrows, false);
  assert.equal(partial.omit_arrows, true);
  const all = setAllOmissions(partial, true);
  assert.ok(
    all.omit_arrows && all.omit_geography && all.omit_analysis_overlays,
  );
  const none = setAllOmissions(all, false);
  assert.ok(
    !none.omit_arrows && !none.omit_geography && !none.omit_analysis_overlays,
  );
});
