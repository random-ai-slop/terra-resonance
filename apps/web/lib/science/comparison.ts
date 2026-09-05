import type { Bundle, Mode } from './types';

function domain(mode: Mode): string | null {
  return (
    mode.provenance.solid_domain_id ??
    (mode.family === 'T'
      ? 'solid:' + mode.regions.map((r) => r.layer_id).join(',')
      : null)
  );
}

/** Identity is only a suggestion. Never resolve an ambiguous list by its order. */
export function comparisonMode(
  reference: Mode,
  candidate: Bundle,
  explicitId?: string,
): Mode | null {
  if (explicitId !== undefined)
    return candidate.modes.find((m) => m.id === explicitId) ?? null;
  const matches = candidate.modes.filter(
    (m) =>
      m.family === reference.family &&
      m.l === reference.l &&
      m.n === reference.n &&
      domain(m) === domain(reference),
  );
  return matches.length === 1 ? matches[0] : null;
}
