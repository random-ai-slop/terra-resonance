import type { Bundle } from './types';
export type Series = { name: string; color: string; points: number[][] };
/** Disconnected solid domains have independent toroidal dispersion branches. */
export function frequencySeries(bundle: Bundle): Series[] {
  const domains = [
    ...new Set(
      bundle.modes
        .filter((m) => m.family === 'T')
        .map((m) => m.provenance.solid_domain_id),
    ),
  ];
  const groups = new Map<string, Series>();
  for (const mode of bundle.modes) {
    const domain = mode.provenance.solid_domain_id ?? null,
      key = JSON.stringify([mode.family, mode.n, domain]);
    let group = groups.get(key);
    if (!group) {
      group = {
        name: `${mode.n}${mode.family}${mode.family === 'T' ? `·domain ${domains.indexOf(domain) + 1}` : ''}`,
        color: { R: '#4ca3b0', S: '#d8a259', T: '#aa9dd1' }[mode.family],
        points: [],
      };
      groups.set(key, group);
    }
    group.points.push([mode.l, mode.frequency_hz * 1000]);
  }
  return [...groups.values()].map((g) => ({
    ...g,
    points: g.points.sort((a, b) => a[0] - b[0]),
  }));
}

/** Preserve adjacent tick distinctions for a short interval far from zero. */
export function tickLabel(value: number, step: number): string {
  const magnitude = Math.floor(
    Math.log10(Math.max(Math.abs(value), Number.MIN_VALUE)),
  );
  const resolution = Math.floor(
    Math.log10(Math.max(Math.abs(step), Number.MIN_VALUE)),
  );
  return value.toPrecision(
    Math.max(3, Math.min(15, magnitude - resolution + 2)),
  );
}
