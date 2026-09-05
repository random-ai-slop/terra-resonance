'use client';
import { useLocale } from '@/lib/i18n/provider';
import { useEffect, useLayoutEffect, useMemo, useRef, useState } from 'react';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import {
  Table,
  TableHeader,
  TableBody,
  TableHead,
  TableRow,
  TableCell,
} from '@/components/ui/table';
import type { Bundle, Scene, ProbeSpec } from '@/lib/science/types';
import { modeLabel } from '@/lib/science/types';
import { sampleProbe, modeScale } from '@/lib/science/field';
import { canonicalHash } from '@/lib/science/data';
import { downloadArtifact } from '@/lib/science/download-artifact';
import { Choice, NumberField, Toggle } from './Controls';
import { frequencySeries } from '@/lib/science/chart-data';
import { comparisonMode as resolveComparison } from '@/lib/science/comparison';
import ScientificPlot, { type Series } from './ScientificPlot';
import { issue, message } from '@/lib/i18n/core';
import { englishSvg } from '@/lib/science/chart-export';
const colors = ['#4ca3b0', '#d8a259', '#aa9dd1'];
function Plot(
  props: Omit<React.ComponentProps<typeof ScientificPlot>, 'locale'>,
) {
  const { locale } = useLocale();
  return <ScientificPlot {...props} locale={locale} />;
}
export default function Charts({
  bundle,
  scene,
  time,
  comparison,
  initialProbe,
  onProbeChange,
  onError,
}: {
  bundle: Bundle;
  scene: Scene;
  time: number;
  comparison: Bundle | null;
  initialProbe: ProbeSpec | null;
  onProbeChange: (spec: ProbeSpec | null) => void;
  onError: (error: unknown) => void;
}) {
  const { t: tr } = useLocale();
  const mode =
      bundle.modes.find((m) => m.id === scene.terms[0]?.mode_id) ??
      bundle.modes[0],
    [tab, setTab] = useState(initialProbe ? 'probe' : 'eigen'),
    [probeStart, setProbeStart] = useState(
      initialProbe?.start_s ?? scene.time_s,
    ),
    [probeCount, setProbeCount] = useState(
      initialProbe?.sample_count ??
        Math.max(
          240,
          Math.ceil(
            7200 *
              Math.max(
                0,
                ...scene.terms
                  .filter((t) => t.amplitude !== 0)
                  .map(
                    (t) =>
                      bundle.modes.find((m) => m.id === t.mode_id)!
                        .frequency_hz,
                  ),
              ) *
              24,
          ),
        ),
    ),
    [raw, setRaw] = useState(initialProbe ? !initialProbe.normalized : false),
    [derivative, setDerivative] = useState(
      String(initialProbe?.derivative ?? 0),
    ),
    [duration, setDuration] = useState(
      initialProbe ? initialProbe.step_s * initialProbe.sample_count : 7200,
    );
  const [independentPoint] = useState(
    initialProbe
      ? {
          latitude_deg: initialProbe.latitude_deg,
          longitude_deg: initialProbe.longitude_deg,
          radius_fraction: initialProbe.radius_fraction,
          ...(initialProbe.layer_id ? { layer_id: initialProbe.layer_id } : {}),
        }
      : null,
  );
  const [probeLinked, setProbeLinked] = useState(
    !initialProbe ||
      (!!scene.point &&
        initialProbe.latitude_deg === scene.point.latitude_deg &&
        initialProbe.longitude_deg === scene.point.longitude_deg &&
        initialProbe.radius_fraction === scene.point.radius_fraction &&
        initialProbe.layer_id === scene.point.layer_id),
  );
  const probePoint = probeLinked ? scene.point : independentPoint;
  const [probeStep, setProbeStep] = useState(
    initialProbe?.step_s ?? duration / probeCount,
  );
  const container = useRef<HTMLDivElement>(null);
  const probeChanged = useRef(onProbeChange);
  useLayoutEffect(() => {
    probeChanged.current = onProbeChange;
  }, [onProbeChange]);
  const probe = useMemo(() => {
    if (!probePoint) return [];
    if (probeCount > 10000) return [];
    return sampleProbe(
      bundle,
      scene.terms,
      probePoint,
      Array.from({ length: probeCount }, (_, i) => probeStart + i * probeStep),
      Number(derivative),
      !raw,
    );
  }, [
    bundle,
    scene.terms,
    probePoint,
    probeStart,
    probeCount,
    probeStep,
    derivative,
    raw,
  ]);
  useEffect(() => {
    probeChanged.current(
      probePoint && probe.length
        ? {
            ...probePoint,
            start_s: probeStart,
            step_s: probeStep,
            sample_count: probe.length,
            derivative: Number(derivative) as 0 | 1 | 2,
            normalized: !raw,
          }
        : null,
    );
  }, [
    probePoint,
    probeStart,
    probeStep,
    duration,
    probe.length,
    derivative,
    raw,
  ]);
  const eigen: Series[] = mode.regions.flatMap((r) =>
    ['u', 'v', 'w'].map((key, i) => ({
      name: key.toUpperCase(),
      color: colors[i],
      points: r.r_m.map((radius, j) => [
        radius / bundle.model.radius_m,
        r[key as 'u'][j] / (raw ? 1 : modeScale(mode)),
      ]),
    })),
  );
  const roots = ['u', 'v', 'w'].map((key) => ({
    key,
    values: mode.regions.flatMap((r) => {
      const v = r[key as 'u'];
      if (v.every((x) => Math.abs(x) <= modeScale(mode) * 1e-12)) return [];
      const found: number[] = [];
      for (let j = 1; j < v.length; j++) {
        if (v[j] * v[j - 1] < 0)
          found.push(
            (r.r_m[j - 1] +
              ((r.r_m[j] - r.r_m[j - 1]) * v[j - 1]) / (v[j - 1] - v[j])) /
              bundle.model.radius_m,
          );
        else if (j < v.length - 1 && v[j] === 0)
          found.push(r.r_m[j] / bundle.model.radius_m);
      }
      return found;
    }),
  }));
  const potential: Series[] = mode.regions
    .filter((r) => r.potential)
    .map((r) => ({
      name: 'δΦ',
      color: colors[2],
      points: r.r_m.map((v, i) => [v / bundle.model.radius_m, r.potential![i]]),
    }));
  const model: Series[] = bundle.model.layers.flatMap((l) =>
    ['rho_kg_m3', 'vp_m_s', 'vs_m_s'].map((key, i) => ({
      name: ['ρ / 10³ kg m⁻³', 'Vp / km s⁻¹', 'Vs / km s⁻¹'][i],
      color: colors[i],
      points: l.r_m.map((r, j) => [
        r / bundle.model.radius_m,
        l[key as 'rho_kg_m3'][j] / 1000,
      ]),
    })),
  );
  async function runExport(action: () => Promise<void>) {
    try {
      await action();
      onError(null);
    } catch (error) {
      onError(error);
    }
  }
  async function saveSvg() {
    const selectedId = container.current
      ?.querySelector('[role="tab"][aria-selected="true"]')
      ?.getAttribute('aria-controls');
    const svg = selectedId
      ? document
          .getElementById(selectedId)
          ?.querySelector<SVGElement>('.plot-wrap svg')
      : null;
    if (!svg) throw issue('No data to plot.');
    if (svg) {
      const source = englishSvg(svg);
      await downloadArtifact(`terra-${tab}.svg`, source, {
        annotation_language: 'en',
        scene,
        bundle_hash: scene.bundle_hash,
        kind: tab,
        mode_id: mode.id,
        normalized: !raw,
        derivative: Number(derivative),
        ...(probePoint
          ? {
              probe: {
                ...probePoint,
                start_s: probeStart,
                step_s: probeStep,
                sample_count: probeCount,
                derivative: Number(derivative),
                normalized: !raw,
              },
            }
          : {}),
        ...(tab === 'compare' && comparison && comparisonMode
          ? {
              comparison_bundle: comparison,
              comparison: {
                reference_mode_id: mode.id,
                candidate_mode_id: comparisonMode.id,
                reference_bundle_hash: scene.bundle_hash,
                candidate_bundle_hash: await canonicalHash(comparison),
                selection:
                  explicitComparisonId === undefined
                    ? 'unique_identity_suggestion'
                    : 'explicit_id',
                normalized: !raw,
                interpretation:
                  'Separate-model comparison; matching labels are not physical mode tracking.',
              },
            }
          : {}),
        provenance: bundle.provenance,
      });
    }
  }
  async function csv() {
    if (!probe.length) return;
    await downloadArtifact(
      'terra-probe.csv',
      'time_s,x,y,z\n' + probe.map((row) => row.join(',')).join('\n'),
      {
        bundle_hash: scene.bundle_hash,
        scene,
        probe: {
          ...probePoint,
          start_s: probeStart,
          sample_count: probe.length,
          step_s: probeStep,
          derivative: Number(derivative),
          normalized: !raw,
        },
        units: raw ? `kg^-1/2 s^-${derivative}` : `s^-${derivative}`,
      },
    );
  }
  const [comparisonSelection, setComparisonSelection] = useState<{
    bundle: Bundle;
    referenceId: string;
    candidateId: string;
  } | null>(null);
  const explicitComparisonId =
    comparisonSelection?.bundle === comparison &&
    comparisonSelection?.referenceId === mode.id
      ? comparisonSelection.candidateId
      : undefined;
  const comparisonMode = comparison
    ? resolveComparison(mode, comparison, explicitComparisonId)
    : null;
  return (
    <section className="science-panel" ref={container}>
      <div className="science-heading">
        <span className="eyebrow">{tr('Scientific quantities')}</span>
        <Button
          size="sm"
          variant="ghost"
          onClick={() => void runExport(saveSvg)}
        >
          {' '}
          {tr('Download current SVG')}{' '}
        </Button>
      </div>
      <p className="hint">
        {tr('The ZIP includes data or a figure with its provenance record.')}
      </p>
      <Tabs value={tab} onValueChange={setTab}>
        <TabsList>
          <TabsTrigger value="eigen">{tr('Eigenfunctions')}</TabsTrigger>
          <TabsTrigger value="model">{tr('Interior model')}</TabsTrigger>
          <TabsTrigger value="spectrum">{tr('Frequency catalog')}</TabsTrigger>
          <TabsTrigger value="probe">{tr('Point time series')}</TabsTrigger>
          <TabsTrigger value="compare">{tr('Model comparison')}</TabsTrigger>
        </TabsList>
        <TabsContent value="eigen">
          <div className="chart-caption">
            <span>
              {modeLabel(mode)}{' '}
              {tr(
                '· Interpolate each material layer separately and retain both interface limits',
              )}
            </span>
            <Toggle
              label={tr('Canonical mass normalization')}
              checked={raw}
              onChange={setRaw}
            />
          </div>
          <Plot
            series={eigen}
            xlabel={message('Radius r / R')}
            ylabel={
              raw ? 'U, V, W / kg⁻¹ᐟ²' : message('U, V, W / fixed radial norm')
            }
          />
          <details className="radial-roots">
            <summary>
              {tr('Radial zero crossings within each material layer')}
            </summary>
            {roots.map(({ key, values }) => (
              <p key={key}>
                {key.toUpperCase()}：
                {values.length
                  ? values.map((v) => v.toFixed(4)).join(', ')
                  : tr('No discrete roots, or an identically zero component')}
              </p>
            ))}
          </details>
          {potential.length > 0 && (
            <details>
              <summary>{tr('Gravity potential perturbation δΦ')}</summary>
              <Plot
                series={potential}
                xlabel={message('Radius r / R')}
                ylabel={
                  mode.provenance.potential?.units
                    ? `δΦ / ${mode.provenance.potential.units}`
                    : message('Gravity potential perturbation δΦ')
                }
              />
            </details>
          )}
          <p className="hint">
            {' '}
            {tr(
              'Read zero crossings from the curves. An identically zero component has no discrete nodes. Display scaling does not change the eigenfunction.',
            )}{' '}
          </p>
        </TabsContent>
        <TabsContent value="model">
          <Plot
            series={model}
            xlabel={message('Radius r / R')}
            ylabel={message('Material profiles')}
          />
          <div className="layer-list">
            {bundle.model.layers.map((l) => (
              <span key={l.id}>
                {l.name} · {l.phase === 'fluid' ? tr('Fluid') : tr('solid')} ·{' '}
                {(l.r_m[0] / 1000).toFixed(0)}–
                {(l.r_m.at(-1)! / 1000).toFixed(0)} km
              </span>
            ))}
          </div>
        </TabsContent>
        <TabsContent value="spectrum">
          <Plot
            series={frequencySeries(bundle)}
            xlabel={message('Spherical-harmonic degree l')}
            ylabel={message('Frequency / mHz')}
          />
          <div className="table-scroll">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>{tr('Mode identity')}</TableHead>
                  <TableHead>{tr('Frequency / mHz')}</TableHead>
                  <TableHead>{tr('Period / min')}</TableHead>
                  <TableHead>Q</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {bundle.modes.map((m) => (
                  <TableRow key={m.id}>
                    <TableCell>{m.id}</TableCell>
                    <TableCell>{(m.frequency_hz * 1000).toFixed(6)}</TableCell>
                    <TableCell>
                      {(1 / m.frequency_hz / 60).toFixed(3)}
                    </TableCell>
                    <TableCell>{m.q?.toFixed(1) ?? '∞'}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </TabsContent>
        <TabsContent value="probe">
          {probePoint ? (
            <>
              {independentPoint && (
                <Toggle
                  label={tr('Follow the tracked 3D point')}
                  checked={probeLinked}
                  onChange={setProbeLinked}
                  disabled={!scene.point && !probeLinked}
                />
              )}
              <div className="chart-options">
                <NumberField
                  label={tr('Start / s')}
                  value={probeStart}
                  min={0}
                  onChange={setProbeStart}
                />
                <NumberField
                  label={tr('Sample count')}
                  value={probeCount}
                  min={2}
                  max={10000}
                  onChange={(v) => {
                    setProbeCount(Math.round(v));
                    setProbeStep(duration / Math.round(v));
                  }}
                />

                <Choice
                  label={tr('Time derivative')}
                  value={derivative}
                  onChange={setDerivative}
                  options={[
                    { value: '0', label: tr('Displacement') },
                    { value: '1', label: tr('First derivative') },
                    { value: '2', label: tr('Second derivative') },
                  ]}
                />
                <NumberField
                  label={tr('Window / s')}
                  value={duration}
                  min={1}
                  max={1e7}
                  onChange={(v) => {
                    setDuration(v);
                    setProbeStep(v / probeCount);
                  }}
                />
                <Toggle
                  label={tr('Canonical field')}
                  checked={raw}
                  onChange={setRaw}
                />
                <Button variant="outline" onClick={() => void runExport(csv)}>
                  CSV
                </Button>
              </div>
              {probeCount / duration <
                24 *
                  Math.max(
                    0,
                    ...scene.terms
                      .filter((t) => t.amplitude !== 0)
                      .map(
                        (t) =>
                          bundle.modes.find((m) => m.id === t.mode_id)!
                            .frequency_hz,
                      ),
                  ) && (
                <p className="hint">
                  {' '}
                  {tr(
                    'Fewer than 24 samples per fastest period. Increase the sample count to resolve the curve. Sampling below Nyquist cannot support frequency analysis.',
                  )}{' '}
                </p>
              )}
              <Plot
                series={['x', 'y', 'z'].map((name, i) => ({
                  name,
                  color: colors[i],
                  points: probe.map((p) => [p[0] / 60, p[i + 1]]),
                }))}
                cursor={time / 60}
                xlabel={message('Physical time / min')}
                ylabel={
                  derivative === '0'
                    ? raw
                      ? 'Displacement / kg⁻¹ᐟ²'
                      : message('Normalized displacement')
                    : `${raw ? 'kg⁻¹ᐟ² · ' : ''}s^−${derivative}`
                }
              />
              <p className="hint">
                ({probePoint.latitude_deg.toFixed(1)}° N,{' '}
                {probePoint.longitude_deg.toFixed(1)}° E), r/R=
                {probePoint.radius_fraction.toFixed(3)}
                {tr(
                  '. x points to longitude 0°, y to 90°E, and z north. This is a time series for specified modal coefficients, not a source-calibrated seismogram.',
                )}{' '}
              </p>
            </>
          ) : (
            <p className="empty-chart">
              {' '}
              {tr(
                'Double-click the sphere or enable a tracked point in the inspector. Its location, path and time series stay linked.',
              )}{' '}
            </p>
          )}
        </TabsContent>
        <TabsContent value="compare">
          {comparison && (
            <>
              <Choice
                label={tr('Comparison mode ID')}
                value={comparisonMode?.id ?? ''}
                options={[
                  { value: '', label: tr('Select a candidate mode') },
                  ...comparison.modes.map((m) => ({
                    value: m.id,
                    label: `${m.id} · ${(m.frequency_hz * 1000).toPrecision(6)} mHz`,
                  })),
                ]}
                onChange={(candidateId) =>
                  setComparisonSelection({
                    bundle: comparison,
                    referenceId: mode.id,
                    candidateId,
                  })
                }
              />
              <p className="hint">
                {' '}
                {tr(
                  'A shared label is a pairing suggestion, not physical mode tracking across models. Select an explicit ID when candidate names differ.',
                )}{' '}
              </p>
            </>
          )}

          {comparison && comparisonMode ? (
            <>
              <p className="chart-caption">
                {bundle.model.name} → {comparison.model.name} · {mode.id} →{' '}
                {comparisonMode.id}
                <br />
                Δf ={' '}
                {(
                  (comparisonMode.frequency_hz - mode.frequency_hz) *
                  1e6
                ).toFixed(4)}{' '}
                µHz（
                {(
                  (comparisonMode.frequency_hz / mode.frequency_hz - 1) *
                  100
                ).toFixed(4)}
                %）
              </p>
              <Plot
                series={[
                  ...eigen,
                  ...comparisonMode.regions.flatMap((r) =>
                    ['u', 'v', 'w'].map((key, i) => ({
                      name: message('Compare {p0}', { p0: key.toUpperCase() }),
                      color: ['#85c6cb', '#edcda1', '#d4c8ed'][i],
                      points: r.r_m.map((radius, j) => [
                        radius / comparison.model.radius_m,
                        r[key as 'u'][j] /
                          (raw ? 1 : modeScale(comparisonMode)),
                      ]),
                    })),
                  ),
                ]}
                xlabel={message("Each model's radius r / R")}
                ylabel={message(
                  'Eigenfunctions · comparison is not spatial superposition',
                )}
              />
            </>
          ) : (
            <p className="empty-chart">
              {comparison
                ? tr(
                    'No unique candidate shares this identity. Select an explicit ID to compare.',
                  )
                : tr(
                    'Import a second result with Compare data. The models remain separate; compare their frequencies and radial structure using explicit mode identities.',
                  )}
            </p>
          )}
        </TabsContent>
      </Tabs>
    </section>
  );
}
