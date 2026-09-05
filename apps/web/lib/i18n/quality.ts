import type { Mode } from '../science/types';
import type { MessageKey } from './messages';
const labels: Record<string, MessageKey> = {
  unverified: 'Convergence unchecked',
  unconverged: 'Not yet converged',
  converged: 'Mesh converged',
  benchmark_checked: 'Frequency benchmark checked',
};
export function qualityMessage(mode: Mode): MessageKey {
  return (
    labels[mode.provenance.quality.status] ?? 'Quality evidence needs review'
  );
}
