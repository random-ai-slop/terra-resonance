import { issue, message } from '../i18n/core';
import * as THREE from 'three';
import { gridParameters, surfaceGrid } from './surface-grid';
import type { Bundle, Scene, Layer } from './types';
import { spatial } from './field';
import coastline from '../../public/data/coastlines.json';
export type Patch = {
  geometry: THREE.BufferGeometry;
  base: Float64Array;
  work: Float64Array;
  bases: Float64Array[];
  layerId?: string;
  kind: 'surface' | 'section' | 'grid';
};
export function component(
  v: ArrayLike<number>,
  i: number,
  p: ArrayLike<number>,
  color: Scene['color'],
): number {
  const x = p[i],
    y = p[i + 1],
    z = p[i + 2],
    r = Math.hypot(x, y, z);
  if (color === 'magnitude') return Math.hypot(v[i], v[i + 1], v[i + 2]);
  if (r === 0) return 0;
  const phi = Math.hypot(x, y) < 1e-14 ? 0 : Math.atan2(y, x),
    theta = Math.atan2(Math.hypot(x, y), z),
    st = Math.sin(theta),
    ct = Math.cos(theta),
    cp = Math.cos(phi),
    sp = Math.sin(phi);
  return color === 'radial'
    ? (v[i] * x + v[i + 1] * y + v[i + 2] * z) / r
    : color === 'theta'
      ? v[i] * ct * cp + v[i + 1] * ct * sp - v[i + 2] * st
      : -v[i] * sp + v[i + 1] * cp;
}
export const cut = (x: number, y: number) => x > 1e-10 && y < -1e-10;
/** Preserve every radial knot of the piecewise-linear scientific field.
 * A fixed-angle component cannot acquire an unseen root between these knots. */
export function radialSamples(
  bundle: Bundle,
  s: Scene,
  layer: Layer,
  base: number,
): number[] {
  const low = layer.r_m[0],
    high = Math.min(
      layer.r_m.at(-1)!,
      s.radius_fraction * bundle.model.radius_m,
    );
  if (high <= low) return [];
  const intervals = Math.max(
    4,
    Math.ceil(((base / 2) * (high - low)) / bundle.model.radius_m),
  );
  const knots = new Set<number>(
    Array.from(
      { length: intervals + 1 },
      (_, i) => low + ((high - low) * i) / intervals,
    ),
  );
  for (const term of s.terms) {
    const region = bundle.modes
      .find((m) => m.id === term.mode_id)!
      .regions.find((r) => r.layer_id === layer.id);
    if (region)
      for (const r of region.r_m) if (r >= low && r <= high) knots.add(r);
  }
  knots.add(low);
  knots.add(high);
  return [...knots].sort((a, b) => a - b);
}
export function buildPatches(bundle: Bundle, s: Scene): Patch[] {
  validateRenderBudget(bundle, s);
  const degree = Math.max(
      0,
      ...s.terms.map((t) => bundle.modes.find((m) => m.id === t.mode_id)!.l),
    ),
    base = { draft: 32, standard: 48, high: 96 }[s.quality],
    lat = Math.max(base, 4 * (degree + 1)),
    lon = 2 * lat,
    R = bundle.model.radius_m,
    rr = s.radius_fraction * R;
  const layerSamples = new Map(
    bundle.model.layers.map((layer) => [
      layer.id,
      s.cutaway ? radialSamples(bundle, s, layer, base) : [],
    ]),
  );
  const count =
    (lat + 1) * (lon + 1) +
    2 *
      (lat + 1) *
      [...layerSamples.values()].reduce((total, rs) => total + rs.length, 0);
  if (count > 250000 || count * s.terms.length * 24 > 128 * 1024 ** 2)
    throw issue(
      'The 3D cache budget is exceeded. Reduce field sampling or the number of terms',
    );
  const patches: Patch[] = [];
  function add(
    points: number[],
    indices: number[],
    kind: Patch['kind'],
    layerId?: string,
  ) {
    const physical = new Float64Array(points);
    let bases: Float64Array[];
    try {
      bases = s.terms.map((t) =>
        spatial(
          bundle,
          bundle.modes.find((m) => m.id === t.mode_id)!,
          t.m,
          physical,
          true,
          layerId,
        ),
      );
    } catch (error) {
      for (const patch of patches) patch.geometry.dispose();
      throw error;
    }
    const g = new THREE.BufferGeometry();
    g.setAttribute(
      'position',
      new THREE.Float32BufferAttribute(
        points.map((v) => v / R),
        3,
      ),
    );
    g.setAttribute(
      'color',
      new THREE.Float32BufferAttribute(new Float32Array(points.length), 3),
    );
    g.setIndex(indices);
    if (kind !== 'grid') g.computeVertexNormals();
    patches.push({
      geometry: g,
      base: physical,
      work: new Float64Array(physical.length),
      bases,
      kind,
      layerId,
    });
  }
  const p: number[] = [],
    idx: number[] = [];
  for (let j = 0; j <= lat; j++)
    for (let k = 0; k <= lon; k++) {
      const th = (Math.PI * j) / lat,
        ph = (2 * Math.PI * k) / lon;
      p.push(
        rr * Math.sin(th) * Math.cos(ph),
        rr * Math.sin(th) * Math.sin(ph),
        rr * Math.cos(th),
      );
    }
  for (let j = 0; j < lat; j++)
    for (let k = 0; k < lon; k++) {
      const a = j * (lon + 1) + k,
        b = a + 1,
        c = a + lon + 1,
        d = c + 1;
      if (
        s.cutaway &&
        cut(
          (p[a * 3] + p[d * 3]) / 2 / R,
          (p[a * 3 + 1] + p[d * 3 + 1]) / 2 / R,
        )
      )
        continue;
      if (j > 0) idx.push(a, c, b);
      if (j < lat - 1) idx.push(b, c, d);
    }
  add(p, idx, 'surface');
  if (s.cutaway)
    for (const layer of bundle.model.layers) {
      const low = layer.r_m[0],
        high = Math.min(layer.r_m.at(-1)!, rr);
      if (high <= low) continue;
      const radii = layerSamples.get(layer.id)!;
      const nr = radii.length - 1;
      for (const ph of [-Math.PI / 2, 0]) {
        const ps: number[] = [],
          is: number[] = [];
        for (let a = 0; a <= nr; a++) {
          const r = radii[a];
          for (let j = 0; j <= lat; j++) {
            const th = (Math.PI * j) / lat;
            ps.push(
              r * Math.sin(th) * Math.cos(ph),
              r * Math.sin(th) * Math.sin(ph),
              r * Math.cos(th),
            );
          }
        }
        for (let a = 0; a < nr; a++)
          for (let j = 0; j < lat; j++) {
            const x = a * (lat + 1) + j,
              y = x + lat + 1;
            is.push(x, y, x + 1, x + 1, y, y + 1);
          }
        add(ps, is, 'section', layer.id);
      }
    }
  const grid = surfaceGrid(bundle, s);
  if (grid.points.length) add(grid.points, grid.indices, 'grid');
  return patches;
}
export function nodePoints(
  patch: Patch,
  field: Float64Array,
  color: Scene['color'],
): Float64Array {
  const index = patch.geometry.index!,
    values = Array.from({ length: patch.base.length / 3 }, (_, i) =>
      component(field, i * 3, patch.base, color),
    );
  if (zeroComponent(patch, field, color)) return new Float64Array();
  const max = values.reduce(
    (a, b, i) =>
      nodeCoordinateDefined(patch.base, i * 3, color)
        ? Math.max(a, Math.abs(b))
        : a,
    0,
  );
  const eps = max * 1e-9,
    out: number[] = [];
  for (let i = 0; i < index.count; i += 3) {
    const ids = [index.getX(i), index.getX(i + 1), index.getX(i + 2)],
      hits: number[][] = [];
    // At centre no spherical component is defined; theta/phi at a pole are
    // only a coordinate convention. Do not turn these conventions into nodes.
    if (ids.some((id) => !nodeCoordinateDefined(patch.base, id * 3, color)))
      continue;
    if (ids.every((id) => Math.abs(values[id]) <= eps)) continue;
    for (let j = 0; j < 3; j++) {
      const a = ids[j],
        b = ids[(j + 1) % 3],
        va = values[a],
        vb = values[b];
      let t: number | undefined;
      if (Math.abs(va) <= eps) t = 0;
      else if ((va < 0 && vb > 0) || (va > 0 && vb < 0)) t = va / (va - vb);
      if (t === undefined) continue;
      const hit = [0, 1, 2].map(
        (k) =>
          patch.base[a * 3 + k] +
          t! * (patch.base[b * 3 + k] - patch.base[a * 3 + k]),
      );
      if (!hits.some((h) => Math.hypot(...h.map((v, k) => v - hit[k])) < 1e-8))
        hits.push(hit);
    }
    if (hits.length === 2) out.push(...hits[0], ...hits[1]);
  }
  return new Float64Array(out);
}

export function nodeCoordinateDefined(
  points: ArrayLike<number>,
  i: number,
  color: Scene['color'],
) {
  const r = Math.hypot(points[i], points[i + 1], points[i + 2]);
  return (
    r > 0 &&
    ((color !== 'theta' && color !== 'phi') ||
      Math.hypot(points[i], points[i + 1]) > 64 * Number.EPSILON * r)
  );
}

export function zeroComponent(
  patch: Patch,
  field: Float64Array,
  color: Scene['color'],
) {
  let maximum = 0,
    vectorScale = 0;
  for (let i = 0; i < field.length; i += 3)
    if (nodeCoordinateDefined(patch.base, i, color)) {
      maximum = Math.max(
        maximum,
        Math.abs(component(field, i, patch.base, color)),
      );
      vectorScale = Math.max(
        vectorScale,
        Math.hypot(field[i], field[i + 1], field[i + 2]),
      );
    }
  return maximum <= 64 * Number.EPSILON * vectorScale;
}

export function geographyPoints(bundle: Bundle, scene: Scene): Float64Array {
  const out: number[] = [],
    R = bundle.model.radius_m;
  for (const line of coastline.lines)
    for (let i = 1; i < line.length; i++) {
      const pair = [line[i - 1], line[i]].map(([longitude, latitude]) => {
        const phi = (longitude * Math.PI) / 180,
          theta = ((90 - latitude) * Math.PI) / 180;
        return [
          R * Math.sin(theta) * Math.cos(phi),
          R * Math.sin(theta) * Math.sin(phi),
          R * Math.cos(theta),
        ];
      });
      if (scene.cutaway && pair.some((p) => cut(p[0] / R, p[1] / R))) continue;
      out.push(...pair[0], ...pair[1]);
    }
  return new Float64Array(out);
}

/** Cheap conservative preflight: no spherical harmonics or field caches allocated. */
export function validateRenderBudget(bundle: Bundle, scene: Scene) {
  const degree = Math.max(
    0,
    ...scene.terms.map((t) => {
      const mode = bundle.modes.find((m) => m.id === t.mode_id);
      if (!mode) throw issue('Unknown mode in renderer');
      return mode.l;
    }),
  );
  if (degree > 64 || scene.terms.length > 32)
    throw issue('Renderer supports degree <=64 and <=32 terms');
  const base = { draft: 32, standard: 48, high: 96 }[scene.quality];
  const lat = Math.max(base, 4 * (degree + 1)),
    lon = 2 * lat;
  let points = (lat + 1) * (lon + 1),
    triangles = 2 * lon * (lat - 1);
  if (scene.cutaway)
    for (const layer of bundle.model.layers) {
      const rows = radialSamples(bundle, scene, layer, base).length;
      points += 2 * rows * (lat + 1);
      triangles += 4 * Math.max(0, rows - 1) * lat;
    }
  const geography = scene.geography
    ? geographyPoints(bundle, scene).length / 3
    : 0;
  const arrows = scene.arrows ? 264 : 0;
  const nodes = scene.nodes ? triangles * 2 : 0;
  const cachePoints =
    points +
    gridParameters(bundle, scene).pointCount +
    geography +
    arrows +
    nodes +
    (scene.point ? 1 : 0);
  // Arrow head/shaft and reference vertices count toward display allocation too.
  const decorative =
    (scene.reference ? 36 * 18 * 12 : 0) +
    arrows * 32 +
    (scene.point ? 117 : 0) +
    (scene.trajectory.enabled ? scene.trajectory.samples : 0);
  const totalPoints = cachePoints + decorative,
    cacheBytes = cachePoints * scene.terms.length * 24;
  if (totalPoints > 250000 || cacheBytes > 128 * 1024 ** 2)
    throw issue(
      'Display budget exceeded: about {p0} vertices and {p1} MiB of field cache{p2}. Reduce field sampling, terms or overlays',
      {
        p0: totalPoints.toLocaleString(),
        p1: (cacheBytes / 1024 ** 2).toFixed(1),
        p2: scene.nodes ? message(' (conservative nodal-line bound)') : '',
      },
    );
  return {
    totalPoints,
    cacheBytes,
    cachePoints,
    nodeUpperBound: nodes,
    gridPointCount: gridParameters(bundle, scene).pointCount,
  };
}
