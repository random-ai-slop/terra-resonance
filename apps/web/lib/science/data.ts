import { issue } from '../i18n/core';
import canonicalize from 'canonicalize';
import { sha256 } from '@noble/hashes/sha2.js';
import { bytesToHex } from '@noble/hashes/utils.js';
import type { Bundle, Model, Scene, Project } from './types';
import { colorBound, interpolate, modeScale } from './field';
function assert(ok: unknown, msg: string | Error): asserts ok {
  if (!ok) throw msg instanceof Error ? msg : new Error(msg);
}
export function jsonTree(v: unknown, path = 'data', depth = 0): void {
  if (depth > 64) throw issue('JSON nesting exceeds 64 levels');
  if (v === null || typeof v === 'boolean') return;
  // JS has only binary64 numbers. Reject unsafe *integer lexemes* before
  // JSON.parse instead: a legal scientific float such as 1e21 is integral
  // according to Number.isInteger, but is valid RFC 8785 input.
  if (typeof v === 'number') {
    assert(Number.isFinite(v), issue('Non-finite value: {p0}', { p0: path }));
    return;
  }
  if (typeof v === 'string') {
    for (let i = 0; i < v.length; i++) {
      const c = v.charCodeAt(i);
      if (c >= 0xd800 && c <= 0xdbff) {
        const n = v.charCodeAt(++i);
        assert(
          n >= 0xdc00 && n <= 0xdfff,
          issue('Invalid Unicode: {p0}', { p0: path }),
        );
      } else
        assert(
          c < 0xdc00 || c > 0xdfff,
          issue('Invalid Unicode: {p0}', { p0: path }),
        );
    }
    return;
  }
  assert(
    typeof v === 'object' && v !== undefined,
    issue('Non-JSON value: {p0}', { p0: path }),
  );
  for (const [key, value] of Object.entries(v as object)) {
    jsonTree(key, path, depth + 1);
    jsonTree(value, path + '.' + key, depth + 1);
  }
}
const num = (
  v: unknown,
  name: string,
  min = -Infinity,
  max = Infinity,
): number => {
  assert(
    typeof v === 'number' && Number.isFinite(v) && v >= min && v <= max,
    issue('{p0} is outside the valid range', { p0: name }),
  );
  return v;
};
function text(v: unknown, name: string): asserts v is string {
  assert(
    typeof v === 'string' && v.length > 0,
    issue('{p0} must not be empty', { p0: name }),
  );
}
// Dynamic JSON is narrowed field-by-field by the validators below; no unchecked value crosses their public boundary.
// oxlint-disable-next-line typescript/no-explicit-any
function object(v: unknown, name: string): asserts v is Record<string, any> {
  assert(
    v !== null && typeof v === 'object' && !Array.isArray(v),
    issue('{p0} must be an object', { p0: name }),
  );
}
function integer(v: unknown, name: string, min = 0): number {
  const n = num(v, name, min);
  assert(
    Number.isSafeInteger(n),
    issue('{p0} must be a safe integer', { p0: name }),
  );
  return n;
}
function array(
  v: unknown,
  name: string,
  length?: number,
): asserts v is number[] {
  assert(
    Array.isArray(v) && v.length >= 2 && (!length || v.length === length),
    issue('{p0} array length does not match', { p0: name }),
  );
  for (const n of v) num(n, name);
}
function radii(v: unknown, name: string): asserts v is number[] {
  array(v, name);
  assert(
    v[0] >= 0 && v.every((a, i) => i === 0 || a > v[i - 1]),
    issue('{p0} must increase strictly', { p0: name }),
  );
}
export async function canonicalHash(v: unknown): Promise<string> {
  jsonTree(v);
  const b = new TextEncoder().encode(canonicalize(v)!);
  const h = await crypto.subtle.digest('SHA-256', b);
  return [...new Uint8Array(h)]
    .map((x) => x.toString(16).padStart(2, '0'))
    .join('');
}
export async function modelHash(m: Model): Promise<string> {
  const { provenance: _, ...content } = m;
  return canonicalHash(content);
}
export async function bundleHash(b: Bundle): Promise<string> {
  validateBundle(b);
  return canonicalHash(b);
}

/** Keep JSON.parse as the grammar parser, with a lexical preflight for facts
 * lost during parsing: duplicate object keys and integer precision. */
export function parseJson(raw: string): unknown {
  const stack: (Set<string> | null)[] = [];
  for (let i = 0; i < raw.length;) {
    const c = raw[i];
    if (c === '"') {
      const start = i++;
      let closed = false;
      while (i < raw.length) {
        if (raw[i] === '\\') {
          i += 2;
          continue;
        }
        if (raw[i++] === '"') {
          closed = true;
          break;
        }
      }
      assert(closed, issue('Unterminated JSON string'));
      const token = raw.slice(start, i);
      const decoded = JSON.parse(token);
      let after = i;
      while (/\s/.test(raw[after] ?? '') && after < raw.length) after++;
      if (raw[after] === ':') {
        const keys = stack.at(-1);
        assert(keys instanceof Set, issue('Invalid JSON object key position'));
        assert(
          !keys.has(decoded),
          issue('Duplicate JSON key: {p0}', { p0: decoded }),
        );
        keys.add(decoded);
      }
      continue;
    }
    if (c === '{' || c === '[') {
      stack.push(c === '{' ? new Set<string>() : null);
      assert(stack.length <= 64, issue('JSON nesting exceeds 64 levels'));
      i++;
      continue;
    }
    if (c === '}' || c === ']') {
      stack.pop();
      i++;
      continue;
    }
    if (c === '-' || (c >= '0' && c <= '9')) {
      const token = /^-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?/.exec(
        raw.slice(i),
      )?.[0];
      assert(token, issue('Invalid JSON number'));
      if (!/[.eE]/.test(token))
        assert(
          Number.isSafeInteger(Number(token)),
          issue(
            'Integer exceeds the safe range; encode identifiers as strings',
          ),
        );
      i += token.length;
      continue;
    }
    i++;
  }
  const parsed: unknown = JSON.parse(raw);
  jsonTree(parsed);
  return parsed;
}

function validateQuality(
  value: unknown,
  frequencyHz: number,
  expectedModelHash: string,
): void {
  object(value, 'mode.provenance.quality');
  const q = value;
  assert(
    ['unverified', 'unconverged', 'converged', 'benchmark_checked'].includes(
      q.status,
    ),
    issue('Unknown quality status'),
  );
  assert(
    Array.isArray(q.warnings) &&
      q.warnings.every((x: unknown) => typeof x === 'string'),
    issue('quality.warnings must be an array of strings'),
  );
  assert(
    'mesh_convergence' in q && 'benchmark' in q,
    issue(
      'Mesh and benchmark evidence must be declared; use null when unchecked',
    ),
  );
  const mesh = q.mesh_convergence;
  if (mesh !== null) {
    object(mesh, 'mesh_convergence');
    integer(mesh.coarse_mesh, 'coarse mesh', 1);
    integer(mesh.fine_mesh, 'fine mesh', 1);
    assert(
      mesh.fine_mesh > mesh.coarse_mesh,
      issue('The fine mesh must be larger than the coarse mesh'),
    );
    num(mesh.relative_frequency_change, 'relative frequency change', 0);
    num(mesh.tolerance, 'convergence tolerance', Number.MIN_VALUE);
  }
  const benchmark = q.benchmark;
  if (benchmark !== null) {
    object(benchmark, 'benchmark');
    for (const key of ['source', 'quantity', 'model_hash'])
      text(benchmark[key], 'benchmark.' + key);
    num(
      benchmark.reference_frequency_hz,
      'benchmark frequency',
      Number.MIN_VALUE,
    );
    num(benchmark.relative_error, 'benchmark error', 0);
    num(benchmark.tolerance, 'benchmark tolerance', Number.MIN_VALUE);
    assert(
      benchmark.quantity === 'frequency_hz',
      issue('benchmark.quantity must be frequency_hz'),
    );
    assert(
      benchmark.model_hash === expectedModelHash,
      issue('benchmark.model_hash does not match the current model'),
    );
    const measured =
      Math.abs(frequencyHz - benchmark.reference_frequency_hz) /
      benchmark.reference_frequency_hz;
    const rounding =
      64 * Number.EPSILON * Math.max(1, measured, benchmark.relative_error);
    assert(
      Number.isFinite(measured) &&
        Math.abs(measured - benchmark.relative_error) <= rounding,
      issue(
        'benchmark.relative_error is inconsistent with the current and reference frequencies',
      ),
    );
  }
  if (q.status === 'converged')
    assert(
      mesh !== null && mesh.relative_frequency_change <= mesh.tolerance,
      issue('Converged status requires passing mesh evidence'),
    );
  if (q.status === 'unconverged')
    assert(
      mesh !== null && mesh.relative_frequency_change > mesh.tolerance,
      issue('Unconverged status requires mesh evidence'),
    );
  if (q.status === 'benchmark_checked')
    assert(
      benchmark !== null && benchmark.relative_error <= benchmark.tolerance,
      issue('Benchmark-checked status requires passing benchmark evidence'),
    );
}
export function validateBundle(value: unknown): Bundle {
  jsonTree(value);
  object(value, 'bundle');
  const b = value as Bundle;
  assert(
    b?.schema_version === '1.0',
    issue('Unsupported bundle version; schema_version 1.0 is required'),
  );
  const model = b.model;
  object(model, 'model');
  text(model?.id, 'model.id');
  text(model?.name, 'model.name');
  const R = num(model.radius_m, 'model radius', Number.MIN_VALUE),
    eps = 64 * Number.EPSILON * R;
  assert(
    Array.isArray(model.layers) && model.layers.length > 0,
    issue('The model must contain material layers'),
  );
  let prev = 0,
    samples = 0;
  const layers = new Map<string, (typeof model.layers)[number]>();
  for (const l of model.layers) {
    text(l.id, 'layer.id');
    text(l.name, 'layer.name');
    assert(!layers.has(l.id), issue('Duplicate material layer ID'));
    assert(
      l.phase === 'solid' || l.phase === 'fluid',
      issue('Unknown material phase'),
    );
    radii(l.r_m, l.id + '.r_m');
    assert(
      Math.abs(l.r_m[0] - prev) <= eps,
      issue('Material layers contain a gap or overlap'),
    );
    assert(
      l.r_m.at(-1)! - l.r_m[0] > 2 * eps,
      issue('A material layer is too thin'),
    );
    prev = l.r_m.at(-1)!;
    for (const key of ['rho_kg_m3', 'vp_m_s', 'vs_m_s'] as const)
      array(l[key], key, l.r_m.length);
    for (let i = 0; i < l.r_m.length; i++) {
      assert(
        l.rho_kg_m3[i] > 0 && l.vp_m_s[i] > 0,
        issue('Density and Vp must be positive'),
      );
      assert(
        l.phase === 'fluid' ? l.vs_m_s[i] === 0 : l.vs_m_s[i] > 0,
        issue('Vs is inconsistent with the solid/fluid phase'),
      );
      assert(
        l.vp_m_s[i] ** 2 - (4 / 3) * l.vs_m_s[i] ** 2 > 0,
        issue('Bulk modulus must be positive'),
      );
    }
    for (const key of ['q_bulk', 'q_shear'] as const)
      if (key in l) {
        assert(
          Array.isArray(l[key]) && l[key]!.length === l.r_m.length,
          issue('Q sample lengths do not match'),
        );
        for (const q of l[key]!)
          assert(
            q === null || (typeof q === 'number' && q > 0),
            issue('Q must be positive or null'),
          );
        if (l.phase === 'fluid' && key === 'q_shear')
          assert(
            l[key]!.every((q) => q === null),
            issue('Fluid shear Q must be null'),
          );
      }
    layers.set(l.id, l);
    samples += l.r_m.length;
  }
  assert(
    Math.abs(prev - R) <= eps,
    issue('The model does not reach the surface'),
  );
  if (model.reference_frequency_hz !== undefined)
    num(model.reference_frequency_hz, 'reference frequency', Number.MIN_VALUE);
  if ('provenance' in model) object(model.provenance, 'model.provenance');
  assert(Array.isArray(b.modes), issue('Missing modes'));
  const ids = new Set<string>();
  const { provenance: _modelProvenance, ...modelContent } = model;
  const expectedModelHash = bytesToHex(
    sha256(new TextEncoder().encode(canonicalize(modelContent)!)),
  );
  for (const m of b.modes) {
    text(m.id, 'mode.id');
    assert(!ids.has(m.id), issue('Duplicate mode ID'));
    ids.add(m.id);
    assert(['R', 'S', 'T'].includes(m.family), issue('Unknown mode family'));
    integer(m.l, 'mode.l');
    integer(m.n, 'mode.n');
    assert(
      m.family === 'R' ? m.l === 0 : m.l > 0,
      issue('Mode family is inconsistent with l'),
    );
    num(m.frequency_hz, 'eigenfrequency', Number.MIN_VALUE);
    if (m.q !== null) num(m.q, 'modal Q', Number.MIN_VALUE);
    assert(
      m.normalization === 'mass_integral_1',
      issue('Convert to mass_integral_1 normalization first'),
    );
    assert(
      Array.isArray(m.regions) && m.regions.length > 0,
      issue('The eigenfunction is empty'),
    );
    const regids = new Set<string>();
    let norm = 0;
    for (const r of m.regions) {
      const l = layers.get(r.layer_id);
      assert(l, issue('Unknown eigenfunction material layer'));
      assert(!regids.has(r.layer_id), issue('Duplicate eigenfunction region'));
      regids.add(r.layer_id);
      radii(r.r_m, 'region.r_m');
      assert(
        Math.abs(r.r_m[0] - l.r_m[0]) <= eps &&
          Math.abs(r.r_m.at(-1)! - l.r_m.at(-1)!) <= eps,
        issue('The eigenfunction does not cover the complete material layer'),
      );
      for (const key of ['u', 'v', 'w'] as const)
        array(r[key], key, r.r_m.length);
      if (r.potential) array(r.potential, 'potential', r.r_m.length);
      if (m.family === 'T')
        assert(
          l.phase === 'solid' &&
            r.u.every((x) => x === 0) &&
            r.v.every((x) => x === 0),
          issue('T modes must be confined to solids with zero u/v'),
        );
      else
        assert(
          r.w.every((x) => x === 0),
          issue('R/S modes must have zero w'),
        );
      if (m.family === 'R')
        assert(
          r.v.every((x) => x === 0),
          issue('R modes must have zero v'),
        );
      let last = 0;
      for (let i = 0; i < r.r_m.length; i++) {
        const x = r.r_m[i],
          f =
            interpolate(l.r_m, l.rho_kg_m3, x) *
            x *
            x *
            (r.u[i] ** 2 + r.v[i] ** 2 + r.w[i] ** 2);
        if (i) norm += ((last + f) / 2) * (x - r.r_m[i - 1]);
        last = f;
      }
      samples += r.r_m.length;
    }
    assert(
      Number.isFinite(norm) &&
        Math.abs(norm - 1) <=
          Math.max(1e-8, 1e-6 * Math.max(1, Math.abs(norm))),
      issue('Mode {p0} does not have unit mass integral ({p1})', {
        p0: m.id,
        p1: norm,
      }),
    );
    const scale = modeScale(m);
    const c = m.regions.find((r) => r.r_m[0] === 0);
    if (c) {
      const e = 1e-6 * scale;
      if (m.family === 'S' && m.l === 1)
        assert(
          Math.abs(c.v[0] - Math.SQRT2 * c.u[0]) <= e,
          issue('S1 does not satisfy the regular center limit'),
        );
      else
        assert(
          Math.max(Math.abs(c.u[0]), Math.abs(c.v[0]), Math.abs(c.w[0])) <= e,
          issue('The eigenfunction is not regular at the center'),
        );
    }
    object(m.provenance, 'mode.provenance');
    validateQuality(m.provenance.quality, m.frequency_hz, expectedModelHash);
    if (m.regions.some((r) => 'potential' in r)) {
      object(m.provenance.potential, 'mode.provenance.potential');
      assert(
        ['solved', 'postprocessed'].includes(m.provenance.potential.status),
        issue('Potential values require their actual source status'),
      );
      text(m.provenance.potential.units, 'potential.units');
    }
  }
  assert(
    samples <= 2_000_000,
    issue(
      'Data sample count exceeds the browser budget; use Python for analysis',
    ),
  );
  object(b.provenance, 'bundle.provenance');
  if ('groups' in b.provenance) {
    assert(
      Array.isArray(b.provenance.groups),
      issue('groups must be an array'),
    );
    for (const g of b.provenance.groups) {
      object(g, 'group');
      assert(
        ['R', 'S', 'T'].includes(g.family) &&
          ['success', 'not_applicable'].includes(g.status),
        issue('Unknown solver group status'),
      );
      integer(g.l, 'group.l');
      integer(g.matrix_dimension, 'matrix dimension');
      object(g.spectrum, 'group.spectrum');
      for (const key of ['negative', 'near_zero', 'positive'])
        integer(g.spectrum[key], 'spectrum.' + key);
      num(g.spectrum.threshold, 'spectral threshold', 0);
      object(g.spectral_completeness, 'spectral_completeness');
      assert(
        ['complete', 'truncated'].includes(g.spectral_completeness.status) &&
          typeof g.spectral_completeness.reason === 'string',
        issue('Spectrum completeness needs a status and reason'),
      );
    }
  }
  return b;
}
function validatePoint(value: unknown, b: Bundle): void {
  object(value, 'material point');
  const p = value;
  num(p.latitude_deg, 'probe latitude', -90, 90);
  num(p.longitude_deg, 'probe longitude');
  const fraction = num(
    p.radius_fraction === undefined ? 1 : p.radius_fraction,
    'probe radius',
    0,
    1,
  );
  if ('layer_id' in p) {
    text(p.layer_id, 'Material side');
    const layer = b.model.layers.find((l) => l.id === p.layer_id);
    assert(layer, issue('Unknown probe material side'));
    const r = fraction * b.model.radius_m,
      eps = 64 * Number.EPSILON * b.model.radius_m;
    assert(
      r >= layer.r_m[0] - eps && r <= layer.r_m.at(-1)! + eps,
      issue('The probe radius is outside the selected material side'),
    );
  }
}
export function validateScene(value: unknown, b: Bundle, hash?: string): Scene {
  jsonTree(value);
  object(value, 'scene');
  const s = value as Scene;
  assert(
    ['1.0', '1.1'].includes(s.schema_version) && s.model_id === b.model.id,
    issue('Scene version or model does not match'),
  );
  assert(
    s.schema_version !== '1.0' || s.wireframe_spacing_deg == null,
    issue(
      'Scene 1.0 requires absent/null grid spacing; explicitly choose Scene 1.1',
    ),
  );
  assert(
    s.schema_version !== '1.1' || 'wireframe_spacing_deg' in s,
    issue('Scene 1.1 requires wireframe_spacing_deg'),
  );
  assert(
    s.wireframe_spacing_deg == null ||
      [5, 10, 15, 30].includes(s.wireframe_spacing_deg),
    issue('Grid spacing must be null, 5, 10, 15 or 30 degrees'),
  );
  assert(
    s.schema_version !== '1.1' || s.wireframe_spacing_deg !== undefined,
    issue('Scene 1.1 requires wireframe_spacing_deg'),
  );
  assert(
    typeof s.bundle_hash === 'string' && /^[a-f0-9]{64}$/.test(s.bundle_hash),
    issue('Missing bundle hash'),
  );
  if (hash !== undefined)
    assert(
      s.bundle_hash === hash,
      issue('The scene is bound to different numerical results'),
    );
  assert(
    Array.isArray(s.terms) && s.terms.length <= 32,
    issue('At most 32 superposition terms are supported'),
  );
  for (const t of s.terms) {
    object(t, 'term');
    const m = b.modes.find((a) => a.id === t.mode_id);
    assert(m, issue('The scene references an unknown mode'));
    assert(
      m.l <= 64,
      issue('This mode exceeds the 3D degree limit l≤64; use scientific plots'),
    );
    assert(
      Number.isSafeInteger(t.m) && Math.abs(t.m) <= m.l,
      issue('m must be an integer in [-l,l]'),
    );
    num(t.amplitude, 'coefficient');
    num(t.phase_rad, 'Phase');
  }
  num(s.time_s, 'physical time', 0);
  num(s.time_scale, 'time scale', Number.MIN_VALUE);
  num(s.deformation, 'deformation fraction', 0);
  num(s.radius_fraction, 'sampling radius', Number.MIN_VALUE, 1);
  num(s.color_limit, 'color range', Number.MIN_VALUE);
  num(s.arrow_scale, 'arrow gain', 0);
  assert(
    ['solid', 'wireframe'].includes(s.surface) &&
      ['radial', 'magnitude', 'theta', 'phi'].includes(s.color),
    issue('Unknown surface or field component'),
  );
  assert(
    ['draft', 'standard', 'high'].includes(s.quality) &&
      ['dark', 'light'].includes(s.background),
    issue('Unknown display setting'),
  );
  for (const key of [
    'geography',
    'arrows',
    'reference',
    'cutaway',
    'nodes',
  ] as const)
    assert(
      typeof s[key] === 'boolean',
      issue('Missing boolean display setting {p0}', { p0: key }),
    );
  assert(
    !s.geography || s.radius_fraction === 1,
    issue('Geography applies only at the surface'),
  );
  if (s.nodes)
    assert(
      s.color !== 'magnitude' &&
        s.terms.filter((t) => t.amplitude !== 0).length === 1,
      issue('Nodal lines require one real mode and a signed component'),
    );
  object(s.camera, 'camera');
  num(s.camera.azimuth_deg, 'camera azimuth');
  num(s.camera.elevation_deg, 'camera elevation', -90, 90);
  num(s.camera.distance, 'camera span', Number.MIN_VALUE);
  assert(
    'point' in s,
    issue('Missing point; use null when no point is selected'),
  );
  if (s.point !== null) {
    object(s.point, 'scene.point');
    assert(
      'radius_fraction' in s.point,
      issue('scene.point must explicitly provide radius_fraction'),
    );
    validatePoint(s.point, b);
  }
  object(s.trajectory, 'trajectory');
  assert(
    typeof s.trajectory.enabled === 'boolean',
    issue('Missing path settings'),
  );
  num(s.trajectory.start_s, 'path start', 0);
  num(s.trajectory.duration_s, 'path window', Number.MIN_VALUE);
  integer(s.trajectory.samples, 'Path samples', 2);
  assert(
    s.trajectory.samples <= 2048,
    issue('At most 2048 path samples are supported'),
  );
  if (s.trajectory.enabled) {
    assert(
      s.point !== null,
      issue('An enabled path requires a material point'),
    );
    const fastest = Math.max(
      0,
      ...s.terms
        .filter((t) => t.amplitude !== 0)
        .map((t) => b.modes.find((m) => m.id === t.mode_id)!.frequency_hz),
    );
    assert(
      s.trajectory.samples - 1 >= 24 * fastest * s.trajectory.duration_s,
      issue('A path needs at least 24 sample intervals per fastest period'),
    );
  }
  return s;
}
export async function defaultScene(b: Bundle): Promise<Scene> {
  validateBundle(b);
  const candidates = b.modes.filter((m) => m.l <= 64);
  assert(
    candidates.length > 0,
    issue('No displayable mode; adjust the solve range'),
  );
  const m =
    candidates.find((x) => x.family === 'S' && x.l === 2) ?? candidates[0];
  const terms = [{ mode_id: m.id, m: 0, amplitude: 1, phase_rad: 0 }];
  return {
    schema_version: '1.1',
    wireframe_spacing_deg: 15,
    model_id: b.model.id,
    bundle_hash: await canonicalHash(b),
    terms,
    time_s: 0,
    time_scale: 1 / m.frequency_hz / 8,
    deformation: 0.035,
    surface: 'solid',
    geography: false,
    color: 'radial',
    arrows: false,
    reference: true,
    cutaway: false,
    radius_fraction: 1,
    quality: 'standard',
    arrow_scale: 0.12,
    camera: { azimuth_deg: 25, elevation_deg: 18, distance: 3.2 },
    background: 'dark',
    color_limit: colorBound(b, terms),
    point: null,
    trajectory: {
      enabled: false,
      start_s: 0,
      duration_s: 1 / m.frequency_hz,
      samples: 256,
    },
    nodes: false,
  };
}
export function validateExportSpec(value: unknown): Record<string, unknown> {
  object(value, 'ExportSpec');
  jsonTree(value);
  const defaults: Record<string, unknown> = {
    format: 'png',
    width: 1200,
    height: 900,
    duration_s: 8,
    fps: null,
    transparent: false,
    annotation: true,
    omit_arrows: false,
    omit_geography: false,
    omit_analysis_overlays: false,
  };
  assert(
    Object.keys(value).every((k) => k in defaults),
    issue('ExportSpec contains unknown fields'),
  );
  const s = { ...defaults, ...value };
  assert(
    typeof s.format === 'string' &&
      ['png', 'svg', 'csv', 'frames', 'gif', 'mp4', 'glb'].includes(s.format),
    issue('Unknown export format'),
  );
  integer(s.width, 'export width', 1);
  integer(s.height, 'export height', 1);
  num(s.duration_s, 'export duration', Number.MIN_VALUE);
  if (s.fps !== null) {
    num(s.fps, 'export frame rate', Number.MIN_VALUE);
    if (s.format === 'gif')
      assert(
        [1, 2, 4, 5, 10, 20, 25, 50].includes(s.fps as number),
        issue('GIF frame rates must give exact 10 ms intervals'),
      );
  }
  for (const key of [
    'transparent',
    'annotation',
    'omit_arrows',
    'omit_geography',
    'omit_analysis_overlays',
  ])
    assert(
      typeof s[key] === 'boolean',
      issue('Invalid export boolean field {p0}', { p0: key }),
    );
  assert(
    !s.transparent || s.format === 'png' || s.format === 'svg',
    issue('Transparency is supported only for PNG/SVG'),
  );
  return s;
}
export async function parseProject(raw: string): Promise<Project> {
  assert(
    new TextEncoder().encode(raw).length <= 32 * 1024 * 1024,
    issue('Browser imports are limited to 32 MiB'),
  );
  const x = parseJson(raw);
  object(x, 'project/bundle');
  if (x.format === 'terra-project') {
    assert(x.version === '1.0', issue('Unsupported project version'));
    const b = validateBundle(x.bundle);
    validateScene(x.scene, b, await canonicalHash(b));
    if ('probe' in x) {
      object(x.probe, 'ProbeSpec');
      validatePoint(x.probe, b);
      const p = x.probe;
      const allowed = [
        'latitude_deg',
        'longitude_deg',
        'radius_fraction',
        'layer_id',
        'start_s',
        'step_s',
        'sample_count',
        'derivative',
        'normalized',
      ];
      assert(
        Object.keys(p).every((k) => allowed.includes(k)),
        issue('ProbeSpec contains unknown fields'),
      );
      num(p.start_s, 'probe start time', 0);
      num(p.step_s, 'probe step', Number.MIN_VALUE);
      integer(p.sample_count, 'probe sample count', 1);
      assert(
        [0, 1, 2].includes(p.derivative === undefined ? 0 : p.derivative),
        issue('Invalid probe derivative order'),
      );
      assert(
        typeof (p.normalized === undefined ? true : p.normalized) === 'boolean',
        issue('probe.normalized must be boolean'),
      );
      const lastTime = p.start_s + (p.sample_count - 1) * p.step_s;
      assert(Number.isFinite(lastTime), issue('Probe time range overflows'));
      const bits = new DataView(new ArrayBuffer(8));
      bits.setFloat64(0, lastTime, false);
      const exponent = (bits.getUint32(0, false) >>> 20) & 0x7ff;
      const spacing = 2 ** (Math.max(exponent - 1023, -1022) - 52);
      assert(
        p.sample_count === 1 || p.step_s >= spacing,
        issue(
          'Probe step is below floating-point resolution at this start time',
        ),
      );
    }
    const exportSpec = 'export' in x ? validateExportSpec(x.export) : undefined;
    return {
      ...x,
      ...('probe' in x
        ? {
            probe: {
              radius_fraction: 1,
              derivative: 0,
              normalized: true,
              ...x.probe,
            },
          }
        : {}),
      ...(exportSpec ? { export: exportSpec } : {}),
    } as Project;
  }
  const b = validateBundle(x);
  return {
    format: 'terra-project',
    version: '1.0',
    bundle: b,
    scene: await defaultScene(b),
  };
}
export function download(
  name: string,
  data: Blob | string,
  type = 'application/json',
) {
  const url = URL.createObjectURL(
    typeof data === 'string' ? new Blob([data], { type }) : data,
  );
  const a = document.createElement('a');
  a.href = url;
  a.download = name;
  a.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
