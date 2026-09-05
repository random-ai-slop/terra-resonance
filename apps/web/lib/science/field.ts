import { issue } from '../i18n/core';
import type { Bundle, Mode, Term } from './types';
const PI = Math.PI;
export function harmonic(
  l: number,
  m: number,
  theta: number,
  phi: number,
): [number, number, number] {
  if (
    !Number.isInteger(l) ||
    l < 0 ||
    l > 64 ||
    !Number.isInteger(m) ||
    Math.abs(m) > l
  )
    throw issue('Spherical harmonics require integer 0≤l≤64 and |m|≤l');
  if (
    !Number.isFinite(theta) ||
    theta < 0 ||
    theta > PI ||
    !Number.isFinite(phi)
  )
    throw issue('Invalid spherical-harmonic angles');
  const k = Math.abs(m),
    x = Math.cos(theta),
    sin = Math.sin(theta);
  let log = 0;
  for (let j = l - k + 1; j <= l + k; j++) log += Math.log(j);
  const norm =
    Math.sqrt((2 * l + 1) / (4 * PI)) *
    Math.exp(-log / 2) *
    (k ? Math.SQRT2 : 1);
  const trig = m < 0 ? Math.sin(k * phi) : Math.cos(k * phi);
  const dtrig = m < 0 ? k * Math.cos(k * phi) : -k * Math.sin(k * phi);
  // Differentiate the recurrence itself: subtracting nearly equal Legendre
  // values and then dividing by sin(theta) loses precision near the poles.
  let p = 1,
    dp = 0;
  for (let j = 1; j <= k; j++) {
    const factor = -(2 * j - 1);
    dp = factor * (x * p + sin * dp);
    p *= factor * sin;
  }
  if (l > k) {
    let previous = p,
      previousDerivative = dp;
    dp = (2 * k + 1) * (-sin * p + x * dp);
    p = x * (2 * k + 1) * p;
    for (let n = k + 2; n <= l; n++) {
      const next = ((2 * n - 1) * x * p - (n + k - 1) * previous) / (n - k);
      const derivative =
        ((2 * n - 1) * (-sin * p + x * dp) - (n + k - 1) * previousDerivative) /
        (n - k);
      previous = p;
      previousDerivative = dp;
      p = next;
      dp = derivative;
    }
  }
  const azimuth =
    Math.abs(sin) < 1e-10 ? (k === 1 ? dp * (x >= 0 ? 1 : -1) : 0) : p / sin;
  return [norm * p * trig, norm * dp * trig, norm * azimuth * dtrig];
}
export function modeScale(mode: Mode): number {
  let s = 0;
  for (const r of mode.regions)
    for (let i = 0; i < r.r_m.length; i++)
      s = Math.max(s, Math.hypot(r.u[i], r.v[i], r.w[i]));
  if (!Number.isFinite(s) || s <= 0)
    throw issue('A mode requires finite nonzero displacement coefficients');
  return s;
}
export function interpolate(x: number[], y: number[], q: number): number {
  if (q <= x[0]) return y[0];
  if (q >= x[x.length - 1]) return y[y.length - 1];
  let lo = 0,
    hi = x.length - 1;
  while (hi - lo > 1) {
    const mid = (lo + hi) >> 1;
    if (x[mid] > q) hi = mid;
    else lo = mid;
  }
  return y[lo] + ((y[hi] - y[lo]) * (q - x[lo])) / (x[hi] - x[lo]);
}
export function spatial(
  bundle: Bundle,
  mode: Mode,
  m: number,
  points: ArrayLike<number>,
  normalized = true,
  layerId?: string,
): Float64Array {
  if (points.length % 3 !== 0)
    throw issue('Spatial points must have three coordinates');
  if (!Number.isInteger(m) || Math.abs(m) > mode.l || mode.l > 64)
    throw issue('Mode degree exceeds field evaluation limits');
  if (
    layerId !== undefined &&
    !bundle.model.layers.some((l) => l.id === layerId)
  )
    throw issue('Unknown material side {p0}', { p0: layerId });
  const result = new Float64Array(points.length),
    scale = normalized ? modeScale(mode) : 1;
  const R = bundle.model.radius_m,
    eps = 64 * Number.EPSILON * R,
    k = Math.sqrt(mode.l * (mode.l + 1));
  for (let i = 0; i < points.length; i += 3) {
    const px = points[i],
      py = points[i + 1],
      pz = points[i + 2];
    if (![px, py, pz].every(Number.isFinite))
      throw issue('Spatial coordinates must be finite');
    let r = Math.hypot(px, py, pz);
    if (r > R + eps) continue;
    for (const layer of bundle.model.layers)
      for (const boundary of [layer.r_m[0], layer.r_m.at(-1)!])
        if (Math.abs(r - boundary) <= eps) r = boundary;
    const layer = layerId
      ? bundle.model.layers.find((a) => a.id === layerId)
      : [...bundle.model.layers]
          .reverse()
          .find((a) => r >= a.r_m[0] && r <= a.r_m.at(-1)!);
    if (!layer || r < layer.r_m[0] || r > layer.r_m.at(-1)!) continue;
    const reg = mode.regions.find((a) => a.layer_id === layer.id);
    if (!reg) continue;
    const u = interpolate(reg.r_m, reg.u, r) / scale,
      v = interpolate(reg.r_m, reg.v, r) / scale,
      w = interpolate(reg.r_m, reg.w, r) / scale;
    if (r === 0) {
      if (mode.family === 'S' && mode.l === 1) {
        const axis = m === 0 ? 2 : m === 1 ? 0 : 1;
        result[i + axis] = Math.sqrt(3 / (4 * PI)) * u * (m === 0 ? 1 : -1);
      }
      continue;
    }
    const theta = Math.atan2(Math.hypot(px, py), pz),
      phi = Math.atan2(py, px);
    const st = Math.sin(theta),
      ct = Math.cos(theta),
      cp = Math.cos(phi),
      sp = Math.sin(phi);
    const [y, dt, dp] = harmonic(mode.l, m, theta, phi);
    const radial = u * y,
      t = k ? (v * dt - w * dp) / k : 0,
      p = k ? (v * dp + w * dt) / k : 0;
    result[i] = radial * st * cp + t * ct * cp - p * sp;
    result[i + 1] = radial * st * sp + t * ct * sp + p * cp;
    result[i + 2] = radial * ct - t * st;
  }
  return result;
}
export function temporal(
  mode: Mode,
  term: Term,
  t: number,
  derivative = 0,
): number {
  if (!Number.isFinite(t) || t < 0 || ![0, 1, 2].includes(derivative))
    throw issue('Time must be nonnegative and derivative order must be 0/1/2');
  const w = 2 * PI * mode.frequency_hz,
    g = mode.q ? (PI * mode.frequency_hz) / mode.q : 0,
    p = w * t + term.phase_rad,
    c = Math.cos(p),
    s = Math.sin(p);
  return (
    term.amplitude *
    Math.exp(-g * t) *
    (derivative === 0
      ? c
      : derivative === 1
        ? -g * c - w * s
        : (g * g - w * w) * c + 2 * g * w * s)
  );
}
export function evaluate(
  bundle: Bundle,
  terms: Term[],
  points: ArrayLike<number>,
  t: number,
  derivative = 0,
  normalized = true,
  layerId?: string,
): Float64Array {
  const out = new Float64Array(points.length);
  for (const term of terms) {
    const mode = bundle.modes.find((m) => m.id === term.mode_id);
    if (!mode) throw issue('Unknown mode {p0}', { p0: term.mode_id });
    const basis = spatial(bundle, mode, term.m, points, normalized, layerId),
      a = temporal(mode, term, t, derivative);
    for (let i = 0; i < out.length; i++) out[i] += a * basis[i];
  }
  return out;
}
export function colorBound(bundle: Bundle, terms: Term[]): number {
  return Math.max(
    1e-12,
    terms.reduce(
      (s, t) =>
        s +
        Math.abs(t.amplitude) *
          Math.sqrt(
            (3 * (2 * bundle.modes.find((m) => m.id === t.mode_id)!.l + 1)) /
              (4 * PI),
          ),
      0,
    ),
  );
}

/** One material point, many physical times; spatial bases are time-independent. */
export function sampleProbe(
  bundle: Bundle,
  terms: Term[],
  point: import('./types').MaterialPoint,
  times: ArrayLike<number>,
  derivative = 0,
  normalized = true,
): number[][] {
  if (![0, 1, 2].includes(derivative))
    throw issue('Derivative order must be 0/1/2');
  const r = point.radius_fraction * bundle.model.radius_m,
    theta = ((90 - point.latitude_deg) * PI) / 180,
    phi = (point.longitude_deg * PI) / 180,
    xyz = [
      r * Math.sin(theta) * Math.cos(phi),
      r * Math.sin(theta) * Math.sin(phi),
      r * Math.cos(theta),
    ];
  const bases = terms
    .filter((t) => t.amplitude !== 0)
    .map((term) => {
      const mode = bundle.modes.find((m) => m.id === term.mode_id);
      if (!mode) throw issue('Unknown mode {p0}', { p0: term.mode_id });
      return {
        term,
        mode,
        vector: spatial(bundle, mode, term.m, xyz, normalized, point.layer_id),
      };
    });
  return Array.from(times, (time) => {
    if (!Number.isFinite(time) || time < 0)
      throw issue('Time must be finite and nonnegative');
    const row = [time, 0, 0, 0];
    for (const { term, mode, vector } of bases) {
      const factor = temporal(mode, term, time, derivative);
      for (let i = 0; i < 3; i++) row[i + 1] += factor * vector[i];
    }
    return row;
  });
}
