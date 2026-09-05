import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';
import React from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import * as THREE from 'three';
import { messages, type MessageKey } from '../lib/i18n/messages';
import {
  resolveLocale,
  translate,
  issue,
  formatError,
  message,
  ContextualError,
} from '../lib/i18n/core';
import {
  lessonMetadata,
  recognizedLesson,
  localizeLesson,
  type Lessons,
} from '../lib/i18n/lessons';
import ScientificPlot from '../components/observatory/ScientificPlot';
import { validateScene, bundleHash } from '../lib/science/data';
import { surfaceGrid, gridParameters } from '../lib/science/surface-grid';
import { buildPatches } from '../lib/science/geometry';
import { buildGLBScene, glbExporter } from '../lib/science/browser-export';
import type { Bundle, Scene } from '../lib/science/types';
const fixture = JSON.parse(
  readFileSync(
    new URL('./fixtures/field-reference.json', import.meta.url),
    'utf8',
  ),
);
const bundle: Bundle = fixture.bundles.analytic;
const fresh = (): Scene => structuredClone(fixture.default_scenes.analytic);

test('locale fallback and all translated parameters preserve deferred diagnostic identity', () => {
  assert.equal(resolveLocale(null, null), 'en');
  assert.equal(resolveLocale('en', 'zh-CN'), 'en');
  assert.equal(resolveLocale('fr', 'zh-CN'), 'zh-CN');
  for (const [key, value] of Object.entries(messages)) {
    const names = (s: string) =>
      [...s.matchAll(/\{(\w+)\}/g)].map((x) => x[1]).sort();
    assert.deepEqual(names(value), names(key), key);
    const params = Object.fromEntries(names(key).map((x) => [x, 7]));
    assert.ok(translate('zh-CN', key as MessageKey, params));
  }
  const error = new ContextualError(
    message('Could not load the default scientific data'),
    issue('Grid spacing must be null, 5, 10, 15 or 30 degrees'),
  );
  assert.equal(error.message, formatError('en', error));
  assert.match(formatError('zh-CN', error), /网格/);
  assert.equal(error.message, formatError('en', error));
});

test('only complete canonical teaching metadata is localized', () => {
  const catalog: Lessons = JSON.parse(
    readFileSync(
      new URL('../public/data/lessons.json', import.meta.url),
      'utf8',
    ),
  );
  const lesson = catalog.lessons[2],
    teaching = lessonMetadata(lesson);
  assert.equal(
    recognizedLesson(catalog.bundle_hash, teaching, catalog),
    lesson,
  );
  assert.notEqual(localizeLesson(lesson, 'zh-CN').title, lesson.title);
  assert.equal(recognizedLesson('another hash', teaching, catalog), null);
  assert.equal(
    recognizedLesson(
      catalog.bundle_hash,
      { ...teaching, caution: 'My scientific caution' },
      catalog,
    ),
    null,
  );
  assert.equal(
    recognizedLesson(
      catalog.bundle_hash,
      { ...teaching, custom: true },
      catalog,
    ),
    null,
  );
});

test('localized scientific plots keep numeric paths and English export annotations', () => {
  const props = {
    series: [
      {
        name: '用户模态',
        color: '#336677',
        points: [
          [0, 2],
          [1, -3],
          [2, 4],
        ],
      },
    ],
    xlabel: message('Physical time / min'),
    ylabel: message('Normalized displacement'),
  };
  const en = renderToStaticMarkup(
    React.createElement(ScientificPlot, { ...props, locale: 'en' }),
  );
  const zh = renderToStaticMarkup(
    React.createElement(ScientificPlot, { ...props, locale: 'zh-CN' }),
  );
  assert.deepEqual(zh.match(/d="[ML][^"]+"/g), en.match(/d="[ML][^"]+"/g));
  assert.match(zh, /归一化位移/);
  assert.match(zh, /data-export-text="Normalized displacement"/);
  assert.match(zh, /data-export-text="用户模态"/);
});

test('Scene 1.0 remains legacy; density edits never mutate the scientific bundle', async () => {
  const scene = fresh(),
    before = await bundleHash(bundle);
  scene.schema_version = '1.0';
  delete scene.wireframe_spacing_deg;
  assert.equal(validateScene(scene, bundle).schema_version, '1.0');
  assert.equal('wireframe_spacing_deg' in scene, false);
  scene.wireframe_spacing_deg = 15;
  assert.throws(() => validateScene(scene, bundle), /Scene 1.0/);
  scene.schema_version = '1.1';
  for (const spacing of [null, 5, 10, 15, 30] as const) {
    scene.wireframe_spacing_deg = spacing;
    validateScene(scene, bundle);
  }
  delete scene.wireframe_spacing_deg;
  assert.throws(() => validateScene(scene, bundle), /requires wireframe/);
  assert.equal(await bundleHash(bundle), before);
});

test('grid density has exact curve counts, material clipping and independent science sampling', () => {
  const scene = fresh();
  scene.surface = 'wireframe';
  scene.quality = 'draft';
  for (const [spacing, count, edges, cutEdges] of [
    [5, 4651, 4544, 3440],
    [15, 1507, 1472, 1136],
    [30, 721, 704, 560],
  ]) {
    scene.wireframe_spacing_deg = spacing as 5 | 15 | 30;
    scene.cutaway = false;
    const full = surfaceGrid(bundle, scene);
    assert.equal(full.points.length / 3, count);
    assert.equal(full.indices.length / 2, edges);
    scene.cutaway = true;
    const cut = surfaceGrid(bundle, scene);
    assert.deepEqual(cut.points, full.points);
    assert.equal(cut.indices.length / 2, cutEdges);
    for (let i = 0; i < cut.indices.length; i += 2) {
      const a = cut.indices[i] * 3,
        b = cut.indices[i + 1] * 3;
      assert.ok(
        !(
          cut.points[a] + cut.points[b] > 0 &&
          cut.points[a + 1] + cut.points[b + 1] < 0
        ),
      );
    }
  }
  const scientific = buildPatches(bundle, scene);
  scene.wireframe_spacing_deg = 5;
  const dense = buildPatches(bundle, scene);
  assert.deepEqual(scientific[0].base, dense[0].base);
  assert.ok(scientific.at(-1)!.base.length < dense.at(-1)!.base.length);
  [...scientific, ...dense].forEach((p) => p.geometry.dispose());
  scene.surface = 'solid';
  assert.equal(gridParameters(bundle, scene).pointCount, 0);
});

test('parametric GLB has lines, filled sections and complete animation tracks', async () => {
  class BlobReader {
    result: ArrayBuffer | null = null;
    onloadend: (() => void) | null = null;
    readAsArrayBuffer(blob: Blob) {
      void blob.arrayBuffer().then((b) => {
        this.result = b;
        this.onloadend?.();
      });
    }
  }
  Object.defineProperty(globalThis, 'FileReader', {
    value: BlobReader,
    configurable: true,
  });
  const scene = fresh();
  scene.surface = 'wireframe';
  scene.wireframe_spacing_deg = 30;
  scene.cutaway = true;
  scene.quality = 'draft';
  const patches = buildPatches(bundle, scene);
  const { root, clip } = buildGLBScene(patches, bundle, scene, 0.17, true);
  const meshes = root.children.filter(
    (o) => o instanceof THREE.Mesh,
  ) as THREE.Mesh[];
  assert.equal(meshes.filter((m) => m.userData.kind === 'surface').length, 0);
  assert.equal(meshes.filter((m) => m.userData.kind === 'grid').length, 1);
  assert.ok(
    meshes
      .filter((m) => m.userData.kind === 'section')
      .every((m) => !(m.material as THREE.MeshBasicMaterial).wireframe),
  );
  assert.equal(clip.tracks.length, meshes.length);
  const buffer = (await glbExporter().parseAsync(root, {
    binary: true,
    animations: [clip],
  })) as ArrayBuffer;
  const length = new DataView(buffer).getUint32(12, true),
    json = JSON.parse(
      new TextDecoder().decode(new Uint8Array(buffer, 20, length)),
    );
  const primitives = json.meshes.flatMap(
    (m: { primitives: unknown[] }) => m.primitives,
  );
  const lines = primitives.filter(
    (p: { mode: number; targets?: unknown[] }) => p.mode === 1 && p.targets,
  );
  assert.equal(lines.length, 1);
  assert.equal(json.accessors[lines[0].indices].count, 1120);
  assert.ok(
    primitives.some(
      (p: { mode?: number }) => p.mode === 4 || p.mode === undefined,
    ),
  );
  patches.forEach((p) => p.geometry.dispose());
  meshes.forEach((m) => m.geometry.dispose());
});
