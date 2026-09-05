import { issue } from '../i18n/core';
import type { Bundle, Scene } from './types';
export function gridParameters(bundle: Bundle, scene: Scene) {
  const degree = Math.max(
    0,
    ...scene.terms.map((t) => bundle.modes.find((m) => m.id === t.mode_id)!.l),
  );
  const intervals = Math.max(
    { draft: 32, standard: 48, high: 96 }[scene.quality],
    4 * (degree + 1),
  );
  const spacing =
    scene.surface === 'wireframe'
      ? (scene.wireframe_spacing_deg ?? null)
      : null;
  const pointCount = spacing
    ? (180 / spacing - 1) * (2 * intervals + 1) +
      (360 / spacing) * (intervals + 1)
    : 0;
  return {
    degree,
    intervals,
    spacing,
    pointCount,
    sparse: spacing !== null && spacing * degree >= 90,
  };
}
/** Indexed material-coordinate curves. Field sampling and visible spacing are independent. */
export function surfaceGrid(bundle: Bundle, scene: Scene) {
  const { intervals: n, spacing, pointCount } = gridParameters(bundle, scene);
  const points: number[] = [],
    indices: number[] = [];
  if (!spacing) return { points, indices };
  const radius = scene.radius_fraction * bundle.model.radius_m;
  function curve(count: number, angles: (i: number) => [number, number]) {
    const start = points.length / 3;
    for (let i = 0; i <= count; i++) {
      const [theta, phi] = angles(i);
      const p = [
        radius * Math.sin(theta) * Math.cos(phi),
        radius * Math.sin(theta) * Math.sin(phi),
        radius * Math.cos(theta),
      ];
      points.push(
        ...p.map((x) => (Math.abs(x) < 8 * Number.EPSILON * radius ? 0 : x)),
      );
      if (i) {
        const a = start + i - 1,
          b = start + i;
        const x = (points[3 * a] + points[3 * b]) / 2,
          y = (points[3 * a + 1] + points[3 * b + 1]) / 2;
        if (!scene.cutaway || !(x > 0 && y < 0)) indices.push(a, b);
      }
    }
  }
  for (let j = 1; j < 180 / spacing; j++)
    curve(2 * n, (i) => [(j * spacing * Math.PI) / 180, (i * Math.PI) / n]);
  for (let k = 0; k < 360 / spacing; k++)
    curve(n, (i) => [(i * Math.PI) / n, (k * spacing * Math.PI) / 180]);
  if (points.length / 3 !== pointCount)
    throw issue('Surface grid allocation mismatch');
  return { points, indices };
}
