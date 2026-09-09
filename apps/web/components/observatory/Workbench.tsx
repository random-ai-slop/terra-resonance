'use client';
import {
  issue,
  formatError,
  formatMessage,
  ContextualError,
  message,
  type TextToken,
} from '@/lib/i18n/core';
import { qualityMessage } from '@/lib/i18n/quality';
import { useLocale } from '@/lib/i18n/provider';
import { useEffect, useRef, useState } from 'react';
import {
  Activity,
  ArrowDownToLine,
  FolderOpen,
  Maximize2,
  Pause,
  Play,
  Plus,
  RotateCcw,
  X,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import Viewport, { type ViewHandle } from './Viewport';
import Charts from './Charts';
import { useObservatoryTools } from './useObservatoryTools';
import {
  outputSpec,
  outputRecipe,
  setAllOmissions,
} from '@/lib/science/output-recipe';
import { Choice, NumberField, Range, Toggle } from './Controls';
import type {
  Bundle,
  Scene,
  Term,
  Project,
  ProbeSpec,
  ExportSpec,
} from '@/lib/science/types';
import { modeLabel } from '@/lib/science/types';
import {
  defaultScene,
  download,
  parseProject,
  validateBundle,
  validateScene,
} from '@/lib/science/data';
import { colorBound } from '@/lib/science/field';
import { validateRenderBudget } from '@/lib/science/geometry';
import palettes from '@/public/data/palettes.json';
import { assetUrl } from '@/lib/science/asset-url';
import {
  type Lessons,
  lessonMetadata,
  recognizedLesson,
  localizeLesson,
} from '@/lib/i18n/lessons';
export default function Workbench() {
  const { t: tr, locale, setLocale } = useLocale();
  const [lessons, setLessons] = useState<Lessons | null>(null);
  const [savedProbe, setSavedProbe] = useState<ProbeSpec | null>(null),
    [projectRevision, setProjectRevision] = useState(0),
    [exportSettings, setExportSettings] = useState<ExportSpec>({
      format: 'png',
      width: 1200,
      height: 900,
      duration_s: 8,
      fps: 24,
      transparent: false,
      annotation: true,
      omit_arrows: false,
      omit_geography: false,
      omit_analysis_overlays: false,
    });
  const [bundle, setBundle] = useState<Bundle | null>(null),
    [scene, setScene] = useState<Scene | null>(null),
    [comparison, setComparison] = useState<Bundle | null>(null),
    [playing, setPlaying] = useState(false),
    [time, setTime] = useState(0),
    [error, setError] = useState<unknown>(null),
    [viewStatus, setViewStatus] = useState<TextToken[]>([]),
    [present, setPresent] = useState(false),
    [preset, setPreset] = useState(2),
    [exportOpen, setExportOpen] = useState(false),
    [busy, setBusy] = useState(false),
    [annotation, setAnnotation] = useState(true),
    [transparent, setTransparent] = useState(false);
  const [projectExtras, setProjectExtras] = useState<Record<string, unknown>>(
    {},
  );
  const view = useRef<ViewHandle | null>(null),
    exportPanel = useRef<HTMLElement>(null),
    file = useRef<HTMLInputElement>(null),
    compareFile = useRef<HTMLInputElement>(null);
  useEffect(() => {
    let cancelled = false;
    Promise.all(
      ['/data/prem-modes.json', '/data/lessons.json'].map(async (url) => {
        const response = await fetch(assetUrl(url));
        if (!response.ok)
          throw issue('Could not load the default scientific data');
        return response.json();
      }),
    )
      .then(async ([b, c]) => {
        const catalog = c as Lessons;
        const valid = validateBundle(b);
        const fallback = await defaultScene(valid);
        const lesson = catalog.lessons[2];
        if (!lesson || catalog.bundle_hash !== fallback.bundle_hash)
          throw issue('The default lesson does not match the mode bundle');
        const initialScene = {
          ...lesson.scene,
          deformation: 0.15,
          arrows: false,
          reference: false,
          geography: true,
          nodes: false,
          cutaway: false,
          radius_fraction: 1,
          point: null,
          trajectory: { ...lesson.scene.trajectory, enabled: false },
        } satisfies Scene;
        const p = await parseProject(
          JSON.stringify({
            format: 'terra-project',
            version: '1.0',
            bundle: valid,
            scene: initialScene,
            probe: lesson.probe,
            export: lesson.export,
            teaching: lessonMetadata(lesson),
          }),
        );
        if (cancelled) return;
        validateRenderBudget(p.bundle, p.scene);
        setLessons(catalog);
        setBundle(p.bundle);
        setScene(p.scene);
        setTime(p.scene.time_s);
        setSavedProbe(p.probe ?? null);
        if (p.export) {
          setExportSettings(p.export);
          setAnnotation(p.export.annotation);
          setTransparent(p.export.transparent);
        }
        setProjectExtras({ teaching: lessonMetadata(lesson) });
        setPreset(2);
      })
      .catch((e) => {
        if (!cancelled) setError(e);
      });
    return () => {
      cancelled = true;
    };
  }, []);
  useEffect(() => {
    if (exportOpen)
      exportPanel.current?.scrollIntoView({ behavior: 'auto', block: 'start' });
  }, [exportOpen]);
  function loadProject(p: Project) {
    validateRenderBudget(p.bundle, p.scene);
    if (p.probe && p.probe.sample_count > 10000)
      throw issue(
        'The website can plot at most 10,000 probe samples. Use the CLI for this project.',
      );
    if (!p.bundle.modes.some((m) => m.l <= 64))
      throw issue('The bundle contains no displayable modes');
    const {
      bundle: _b,
      scene: _s,
      probe: _p,
      export: _e,
      format: _f,
      version: _v,
      ...extras
    } = p;
    setProjectExtras(extras);
    setPreset(-1);
    setPlaying(false);
    setBundle(p.bundle);
    setScene(p.scene);
    setTime(p.scene.time_s);
    setSavedProbe(p.probe ?? null);
    setProjectRevision((v) => v + 1);
    if (p.export) {
      setExportSettings(p.export);
      setAnnotation(p.export.annotation);
      setTransparent(p.export.transparent);
    }
  }
  useObservatoryTools({
    bundle,
    scene,
    time: () => view.current?.time() ?? time,
    configure: (s) => {
      if (bundle) validateRenderBudget(bundle, s);
      setPlaying(false);
      setScene(s);
      setTime(s.time_s);
      setError('');
    },
    load: loadProject,
  });
  async function load(f: File | undefined, compare = false) {
    if (!f) return;
    try {
      if (f.size > 32 * 1024 * 1024)
        throw issue('Browser imports are limited to 32 MiB');
      const p = await parseProject(await f.text());
      if (compare) {
        setComparison(p.bundle);
      } else {
        loadProject(p);
      }
      setError('');
    } catch (e) {
      setError(
        new ContextualError(
          message(
            'Could not import the project. The current project was preserved.',
          ),
          e,
        ),
      );
    }
  }
  function patch(changes: Partial<Scene>) {
    if (!scene || !bundle) return;
    try {
      const next = {
        ...scene,
        time_s: view.current?.time() ?? scene.time_s,
        ...changes,
      };
      validateScene(next, bundle);
      validateRenderBudget(bundle, next);
      setScene(next);
      setError('');
    } catch (e) {
      setError(e);
    }
  }
  function terms(next: Term[]) {
    if (!bundle || !scene) return;
    patch({
      terms: next,
      color_limit: colorBound(bundle, next),
      nodes: scene.nodes && next.filter((t) => t.amplitude !== 0).length === 1,
    });
  }
  function snapshot() {
    return { ...scene!, time_s: view.current?.time() ?? time };
  }
  function json(name: string, v: unknown) {
    download(name, JSON.stringify(v, null, 2));
  }
  function chosenSpec(format = exportSettings.format) {
    return outputSpec(exportSettings, format, annotation, transparent);
  }
  function saveProject() {
    try {
      const spec = chosenSpec();
      json('terra-project.json', {
        ...projectExtras,
        format: 'terra-project',
        version: '1.0',
        bundle,
        scene: snapshot(),
        ...(savedProbe ? { probe: savedProbe } : {}),
        export: spec,
      });
      setError('');
    } catch (e) {
      setError(e);
    }
  }
  async function perform(fn: () => Promise<void>) {
    setBusy(true);
    try {
      await fn();
      setError('');
    } catch (e) {
      setError(e);
    } finally {
      setBusy(false);
    }
  }
  async function applyPreset(index: number) {
    if (!bundle || !scene) return;
    try {
      const catalog =
        lessons ??
        ((await fetch(assetUrl('data/lessons.json')).then((r) => {
          if (!r.ok) throw issue('The lesson catalog is not available yet');
          return r.json();
        })) as Lessons);
      setLessons(catalog);
      if (catalog.bundle_hash !== scene.bundle_hash)
        throw issue(
          'These lessons use the bundled PREM data. Load the default model before selecting a lesson; the current project was preserved.',
        );
      const lesson = catalog.lessons[index];
      if (!lesson) throw issue('Lesson not found');
      validateScene(lesson.scene, bundle, scene.bundle_hash);
      loadProject({
        format: 'terra-project',
        version: '1.0',
        bundle,
        scene: structuredClone(lesson.scene),
        ...(lesson.probe ? { probe: lesson.probe } : {}),
        ...(lesson.export ? { export: lesson.export } : {}),
      });
      setProjectExtras({ teaching: lessonMetadata(lesson) });
      setPreset(index);
      setError('');
    } catch (e) {
      setError(e);
    }
  }
  if (!bundle || !scene)
    return (
      <main className="loading">
        <Activity size={40} />
        <h1>Terra Resonance</h1>
        <p>
          {formatError(locale, error) ||
            tr('Loading PREM modes and scientific data…')}
        </p>
      </main>
    );
  const primary =
      bundle.modes.find((m) => m.id === scene.terms[0]?.mode_id) ??
      bundle.modes.find((m) => m.l <= 64)!,
    period = 1 / primary.frequency_hz,
    active = scene.terms.filter((t) => t.amplitude !== 0).length;
  let recipe: ReturnType<typeof outputRecipe> | null = null;
  let recipeError: unknown = null;
  try {
    recipe = outputRecipe(chosenSpec(), primary.id);
  } catch (e) {
    recipeError = e;
  }
  const solveRequest = bundle.provenance.request;
  const hasSolveRequest =
    solveRequest !== null &&
    typeof solveRequest === 'object' &&
    !Array.isArray(solveRequest);
  const recognized = recognizedLesson(
    scene.bundle_hash,
    projectExtras.teaching,
    lessons,
  );
  const activeLesson = recognized ? localizeLesson(recognized, locale) : null;
  const importedTeaching =
    !recognized &&
    projectExtras.teaching &&
    typeof projectExtras.teaching === 'object'
      ? (projectExtras.teaching as Record<string, unknown>)
      : null;
  const omittedLabels = [
    exportSettings.omit_arrows ? tr('arrows') : '',
    exportSettings.omit_geography ? tr('geographic lines') : '',
    exportSettings.omit_analysis_overlays ? tr('analysis overlays') : '',
  ].filter(Boolean);

  const gradient = (
    scene.color === 'magnitude' ? palettes.magnitude : palettes.signed
  )
    .filter((_, i) => i % 16 === 0 || i === 255)
    .map((rgb) => `rgb(${rgb.map((c) => Math.round(c * 255)).join(',')})`)
    .join(',');
  return (
    <main className={`observatory ${present ? 'present' : ''}`}>
      <header className="topbar">
        <div className="brand">
          <span className="brand-mark">
            <Activity size={23} />
          </span>
          <div>
            <strong>Terra Resonance</strong>
            <span>{tr('Earth normal-mode observatory')}</span>
          </div>
        </div>
        <div className="header-actions">
          <label className="language-choice">
            <span>{tr('Language')}</span>
            <select
              aria-label={tr('Language')}
              value={locale}
              onChange={(e) => setLocale(e.target.value as 'en' | 'zh-CN')}
            >
              <option value="en">English</option>
              <option value="zh-CN">中文</option>
            </select>
          </label>
          <Button variant="ghost" onClick={() => compareFile.current?.click()}>
            {' '}
            {tr('Compare data')}{' '}
          </Button>
          <Button variant="outline" onClick={() => file.current?.click()}>
            <FolderOpen /> {tr('Import project')}{' '}
          </Button>
          <Button variant="outline" onClick={saveProject}>
            {' '}
            {tr('Save project')}{' '}
          </Button>
          <Button onClick={() => setExportOpen((v) => !v)}>
            <ArrowDownToLine /> {tr('Export')}{' '}
          </Button>
        </div>
        <input
          hidden
          ref={file}
          type="file"
          accept=".json"
          onChange={(e) => {
            void load(e.target.files?.[0]);
            e.target.value = '';
          }}
        />
        <input
          hidden
          ref={compareFile}
          type="file"
          accept=".json"
          onChange={(e) => {
            void load(e.target.files?.[0], true);
            e.target.value = '';
          }}
        />
      </header>
      {!!error && (
        <div className="error-banner" role="alert">
          <span>{formatError(locale, error)}</span>
          <Button
            variant="ghost"
            size="icon"
            aria-label={tr('Dismiss error')}
            onClick={() => setError('')}
          >
            <X />
          </Button>
        </div>
      )}
      <div className="work-area">
        <aside className="catalog panel">
          <div className="panel-heading">
            <h2>{tr('Compose an oscillation')}</h2>
          </div>
          <div className="model-card">
            <span className="status-dot" />{' '}
            {tr('Spherical · non-rotating · isotropic')}
            <strong>{bundle.model.name}</strong>
            <span>
              {(bundle.model.radius_m / 1000).toFixed(0)} km ·{' '}
              {tr('{layers} material layers · {modes} modes', {
                layers: bundle.model.layers.length,
                modes: bundle.modes.length,
              })}
            </span>
          </div>
          <div className="section-title">
            <h3>{tr('Mode superposition')}</h3>
            <Button
              size="icon-sm"
              variant="ghost"
              aria-label={tr('Add a mode')}
              disabled={scene.terms.length >= 32}
              onClick={() =>
                terms([
                  ...scene.terms,
                  { mode_id: primary.id, m: 0, amplitude: 0.5, phase_rad: 0 },
                ])
              }
            >
              <Plus />
            </Button>
          </div>
          {scene.terms.map((t, i) => {
            const m = bundle.modes.find((m) => m.id === t.mode_id)!;
            return (
              <div className="term-card" key={i}>
                <div className="term-heading">
                  <span>
                    {tr('Term')} {String(i + 1).padStart(2, '0')}
                  </span>
                  {scene.terms.length > 1 && (
                    <Button
                      size="icon-xs"
                      variant="ghost"
                      aria-label={tr('Remove term {p0}', { p0: i + 1 })}
                      onClick={() =>
                        terms(scene.terms.filter((_, j) => j !== i))
                      }
                    >
                      <X />
                    </Button>
                  )}
                </div>
                <Choice
                  label={tr('Mode n / family / l')}
                  value={m.id}
                  options={bundle.modes.map((m) => ({
                    value: m.id,
                    label: `${modeLabel(m)} · ${(m.frequency_hz * 1000).toFixed(3)} mHz${m.family === 'T' ? ' · ' + (m.regions.some((r) => r.r_m.at(-1) === bundle.model.radius_m) ? tr('surface solid domain') : tr('internal solid domain')) : ''}`,
                  }))}
                  onChange={(id) => {
                    const mode = bundle.modes.find((m) => m.id === id)!;
                    terms(
                      scene.terms.map((x, j) =>
                        i === j
                          ? {
                              ...x,
                              mode_id: id,
                              m: Math.max(-mode.l, Math.min(mode.l, x.m)),
                            }
                          : x,
                      ),
                    );
                  }}
                />
                <div className="term-metrics">
                  <span>{(1 / m.frequency_hz / 60).toFixed(2)} min</span>
                  <span>
                    {m.q ? `Q ${m.q.toFixed(0)}` : tr('No decay envelope')}
                  </span>
                </div>
                {m.l === 0 ? (
                  <p className="hint">
                    {tr(
                      'Azimuthal order m = 0 · spherically symmetric radial mode',
                    )}
                  </p>
                ) : (
                  <Range
                    label={tr('Azimuthal order m')}
                    value={t.m}
                    min={-m.l}
                    max={m.l}
                    onChange={(v) =>
                      terms(
                        scene.terms.map((x, j) =>
                          i === j ? { ...x, m: v } : x,
                        ),
                      )
                    }
                  />
                )}
                <Range
                  label={tr('Illustration coefficient')}
                  value={t.amplitude}
                  min={-2}
                  max={2}
                  step={0.05}
                  onChange={(v) =>
                    terms(
                      scene.terms.map((x, j) =>
                        i === j ? { ...x, amplitude: v } : x,
                      ),
                    )
                  }
                />
                <Range
                  label={tr('Phase')}
                  value={(t.phase_rad * 180) / Math.PI}
                  min={-180}
                  max={180}
                  unit="°"
                  onChange={(v) =>
                    terms(
                      scene.terms.map((x, j) =>
                        i === j ? { ...x, phase_rad: (v * Math.PI) / 180 } : x,
                      ),
                    )
                  }
                />
              </div>
            );
          })}
          <details className="explain" open>
            <summary>{tr('Start with a question')}</summary>
            <div className="preset-list">
              {(lessons?.lessons ?? []).map((lesson, i) => (
                <button
                  key={localizeLesson(lesson, locale).title}
                  aria-pressed={preset === i}
                  onClick={() => void applyPreset(i)}
                >
                  <span>0{i + 1}</span>
                  {localizeLesson(lesson, locale).title}
                </button>
              ))}
            </div>
          </details>
          <details className="explain">
            <summary>{tr('Numerical source and recomputation')}</summary>
            <p>
              {' '}
              {tr(
                'Frequencies and shapes come from the same calculation. Quality:',
              )}
              {tr(qualityMessage(primary))}{' '}
              {tr(
                '. Changing material properties or gravity requires a new offline solve.',
              )}{' '}
            </p>
            <Button
              variant="outline"
              onClick={() => json('model.json', bundle.model)}
            >
              {' '}
              {tr('Download current model')}{' '}
            </Button>
            <Button
              variant="ghost"
              onClick={() =>
                perform(async () => {
                  const r = await fetch(assetUrl('data/prem-modes.json'));
                  const p = await parseProject(await r.text());
                  loadProject(p);
                })
              }
            >
              {' '}
              {tr('Load default PREM')}{' '}
            </Button>
            {hasSolveRequest ? (
              <>
                <Button
                  variant="outline"
                  onClick={() => json('solve.json', solveRequest)}
                >
                  {' '}
                  {tr('Download solve configuration')}{' '}
                </Button>
                <pre>
                  terra solve model.json --config solve.json --out modes.json
                </pre>
                <p className="hint">
                  {' '}
                  {tr(
                    "Download both the model and its original configuration. Frequency range, mesh, gravity and Q settings come from this bundle's solve record.",
                  )}{' '}
                </p>
              </>
            ) : (
              <p className="hint">
                {' '}
                {tr(
                  "This bundle has no replayable solve request. Define a configuration from the model's source; display settings cannot determine it.",
                )}{' '}
              </p>
            )}
            <details>
              <summary>{tr('Full calculation record')}</summary>
              <pre>{JSON.stringify(bundle.provenance, null, 2)}</pre>
            </details>
          </details>
        </aside>
        <section
          className={`stage ${scene.background === 'light' ? 'light-stage' : ''}`}
        >
          <div className="stage-heading">
            <div>
              <h1>
                {active > 1 ? tr('Modes in superposition') : modeLabel(primary)}{' '}
                <span>
                  {active > 1
                    ? tr('{p0} active terms', { p0: active })
                    : primary.family === 'R'
                      ? tr('Spherical breathing')
                      : primary.family === 'T'
                        ? tr('Toroidal oscillation')
                        : tr('Spheroidal oscillation')}
                </span>
              </h1>
            </div>
            <Button
              variant="ghost"
              size="icon"
              aria-label={
                present ? tr('Exit presentation') : tr('Enter presentation')
              }
              onClick={() => setPresent((v) => !v)}
            >
              <Maximize2 />
            </Button>
          </div>
          <Viewport
            bundle={bundle}
            scene={scene}
            playing={playing}
            onTime={setTime}
            onCamera={(camera) => patch({ camera })}
            onPoint={(point) => patch({ point })}
            onError={setError}
            onStatus={setViewStatus}
            onReject={(previous, error, previousBundle) => {
              setBundle(previousBundle);
              setPlaying(false);
              setScene(previous);
              setTime(previous.time_s);
              setError(error);
            }}
            handle={view}
          />
          {viewStatus.length > 0 && (
            <output className="view-status">
              {viewStatus
                .map((note) => formatMessage(locale, note))
                .join(' · ')}
            </output>
          )}
          <div className="view-corner">
            <span>{tr('z north · x 0°E')}</span>
            <span>{tr('Drag to rotate · double-click to track a point')}</span>
          </div>
          <div className="color-legend">
            <span>
              {
                {
                  radial: tr('Radial displacement uᵣ'),
                  magnitude: tr('Displacement magnitude |u|'),
                  theta: tr('Colatitudinal component uθ'),
                  phi: tr('Longitudinal component uφ'),
                }[scene.color]
              }
            </span>
            <div style={{ background: `linear-gradient(90deg,${gradient})` }} />
            <div>
              <span>
                {scene.color === 'magnitude'
                  ? '0'
                  : `−${scene.color_limit.toFixed(2)}`}
              </span>
              <span>{tr('Dimensionless')}</span>
              <span>+{scene.color_limit.toFixed(2)}</span>
            </div>
          </div>
          <div className="playback">
            <Button
              className="play-button"
              aria-label={playing ? tr('Pause') : tr('Play')}
              onClick={() => {
                if (playing) {
                  const t = view.current?.time() ?? time;
                  patch({ time_s: t });
                  setTime(t);
                }
                setPlaying((v) => !v);
              }}
            >
              {playing ? <Pause /> : <Play />}
            </Button>
            <div className="clock">
              <strong>
                {(time / 60).toFixed(2)} <small>min</small>
              </strong>
              <span>
                {tr('Physical time · ×{scale}', {
                  scale: scene.time_scale.toFixed(1),
                })}
              </span>
            </div>
            <div className="seek">
              <Range
                label={tr('Seek within two reference periods')}
                value={((time % (period * 2)) / (period * 2)) * 100}
                min={0}
                max={100}
                step={0.1}
                onChange={(v) => {
                  setPlaying(false);
                  const t = (v / 100) * period * 2;
                  patch({ time_s: t });
                  setTime(t);
                }}
              />
            </div>
            <Button
              variant="ghost"
              size="icon"
              aria-label={tr('Return to zero time')}
              onClick={() => {
                setPlaying(false);
                patch({ time_s: 0 });
                setTime(0);
              }}
            >
              <RotateCcw />
            </Button>
          </div>
          <div className="observation-note">
            <strong>
              {activeLesson?.title ??
                (typeof importedTeaching?.title === 'string'
                  ? importedTeaching.title
                  : tr('Free exploration'))}
            </strong>
            <p>
              {activeLesson
                ? activeLesson.conclusion
                : tr(
                    'This view uses an imported scientific project. Saving preserves its modes, settings and provenance. Double-click the sphere to track a material point.',
                  )}
            </p>
            {activeLesson && (
              <details className="lesson-steps">
                <summary>
                  {tr('Observation steps and a testable conclusion')}
                </summary>
                <ol>
                  {activeLesson.steps.map((step) => (
                    <li key={step}>{step}</li>
                  ))}
                </ol>
                <p>{activeLesson.conclusion}</p>
                <p>
                  {tr('Note:')}
                  {activeLesson.caution}
                </p>
              </details>
            )}
            {importedTeaching && (
              <details className="lesson-steps">
                <summary>{tr('Imported teaching notes')}</summary>
                <pre>{JSON.stringify(importedTeaching, null, 2)}</pre>
              </details>
            )}
          </div>
        </section>
        <aside className="inspector panel">
          <div className="panel-heading">
            <h2>{tr('Reveal the structure')}</h2>
          </div>
          <Choice
            label={tr('Surface representation')}
            value={scene.surface}
            options={[
              { value: 'solid', label: tr('Filled surface') },
              { value: 'wireframe', label: tr('Surface grid') },
            ]}
            onChange={(v) => patch({ surface: v as Scene['surface'] })}
          />
          {scene.surface === 'wireframe' && (
            <>
              <Choice
                label={tr('Surface grid spacing')}
                value={String(scene.wireframe_spacing_deg ?? 'legacy')}
                options={[
                  { value: 'legacy', label: tr('Legacy triangle wires') },
                  ...[30, 15, 10, 5].map((n) => ({
                    value: String(n),
                    label: `${n}°`,
                  })),
                ]}
                onChange={(v) =>
                  patch({
                    schema_version: '1.1',
                    wireframe_spacing_deg:
                      v === 'legacy' ? null : (Number(v) as 5 | 10 | 15 | 30),
                  })
                }
              />
              <p className="hint">
                {tr(
                  'This is a material latitude/longitude display grid, independent of the solver mesh.',
                )}
              </p>
            </>
          )}
          <Choice
            label={tr('Color quantity')}
            value={scene.color}
            options={[
              { value: 'radial', label: tr('Radial · uᵣ') },
              { value: 'magnitude', label: tr('Magnitude · |u|') },
              { value: 'theta', label: tr('Colatitudinal · uθ') },
              { value: 'phi', label: tr('Longitudinal · uφ') },
            ]}
            onChange={(v) =>
              patch({
                color: v as Scene['color'],
                nodes: v === 'magnitude' ? false : scene.nodes,
              })
            }
          />
          <Range
            label={tr('Deformation gain')}
            value={scene.deformation}
            min={0}
            max={0.2}
            step={0.005}
            unit=" R"
            onChange={(v) => patch({ deformation: v })}
          />
          <p className="hint">
            {' '}
            {tr(
              'Each mode uses a fixed radial normalization. Gain controls visible deformation, not earthquake displacement.',
            )}{' '}
          </p>
          <Toggle
            label={tr('Displacement arrows')}
            checked={scene.arrows}
            onChange={(v) => patch({ arrows: v })}
          />
          {scene.arrows && (
            <Range
              label={tr('Arrow length')}
              value={scene.arrow_scale}
              min={0.02}
              max={0.4}
              step={0.01}
              onChange={(v) => patch({ arrow_scale: v })}
            />
          )}
          <Toggle
            label={tr('Undeformed reference sphere')}
            checked={scene.reference}
            onChange={(v) => patch({ reference: v })}
          />
          <Toggle
            label={tr('Geographic outlines')}
            checked={scene.geography}
            disabled={scene.radius_fraction !== 1}
            onChange={(v) => patch({ geography: v })}
          />
          <Toggle
            label={tr('Spatial nodal lines')}
            checked={scene.nodes}
            disabled={active !== 1 || scene.color === 'magnitude'}
            onChange={(v) => patch({ nodes: v })}
          />
          <Toggle
            label={tr('Cut away the interior')}
            checked={scene.cutaway}
            onChange={(v) => patch({ cutaway: v })}
          />
          <Range
            label={tr('Visible radius')}
            value={scene.radius_fraction}
            min={0.05}
            max={1}
            step={0.01}
            unit=" R"
            onChange={(v) =>
              patch({
                radius_fraction: v,
                geography: v === 1 && scene.geography,
              })
            }
          />
          <details className="explain" open>
            <summary>{tr('Tracked material point')}</summary>
            <Toggle
              label={tr('Show tracked point')}
              checked={!!scene.point}
              onChange={(v) =>
                patch({
                  point: v
                    ? {
                        latitude_deg: 28,
                        longitude_deg: 34,
                        radius_fraction: scene.radius_fraction,
                      }
                    : null,
                  trajectory: { ...scene.trajectory, enabled: false },
                })
              }
            />
            {scene.point && (
              <>
                <div className="coordinate-fields">
                  <NumberField
                    label={tr('Latitude / °')}
                    value={scene.point.latitude_deg}
                    min={-90}
                    max={90}
                    step={1}
                    onChange={(v) =>
                      patch({ point: { ...scene.point!, latitude_deg: v } })
                    }
                  />
                  <NumberField
                    label={tr('Longitude / °')}
                    value={scene.point.longitude_deg}
                    min={-180}
                    max={180}
                    step={1}
                    onChange={(v) =>
                      patch({ point: { ...scene.point!, longitude_deg: v } })
                    }
                  />
                  <NumberField
                    label={tr('Radius / R')}
                    value={scene.point.radius_fraction}
                    min={0}
                    max={1}
                    step={0.01}
                    onChange={(v) =>
                      patch({
                        point: {
                          latitude_deg: scene.point!.latitude_deg,
                          longitude_deg: scene.point!.longitude_deg,
                          radius_fraction: v,
                        },
                      })
                    }
                  />
                </div>
                <Choice
                  label={tr('Material side')}
                  value={scene.point.layer_id ?? 'auto'}
                  options={[
                    {
                      value: 'auto',
                      label: tr('Automatic · outer side at interfaces'),
                    },
                    ...bundle.model.layers
                      .filter((layer) => {
                        const r =
                          scene.point!.radius_fraction * bundle.model.radius_m;
                        const eps = 64 * Number.EPSILON * bundle.model.radius_m;
                        return (
                          r >= layer.r_m[0] - eps &&
                          r <= layer.r_m.at(-1)! + eps
                        );
                      })
                      .map((layer) => ({
                        value: layer.id,
                        label: `${layer.name} · ${layer.phase === 'fluid' ? tr('fluid') : tr('solid')}`,
                      })),
                  ]}
                  onChange={(v) => {
                    const { layer_id: _side, ...point } = scene.point!;
                    patch({
                      point: v === 'auto' ? point : { ...point, layer_id: v },
                    });
                  }}
                />
                <Toggle
                  label={tr('Analytical motion path')}
                  checked={scene.trajectory.enabled}
                  onChange={(v) =>
                    patch({
                      trajectory: {
                        ...scene.trajectory,
                        enabled: v,
                        start_s: time,
                        duration_s: period,
                        samples: Math.max(
                          192,
                          Math.ceil(
                            period *
                              Math.max(
                                ...scene.terms.map(
                                  (t) =>
                                    bundle.modes.find(
                                      (m) => m.id === t.mode_id,
                                    )!.frequency_hz,
                                ),
                              ) *
                              24,
                          ) + 1,
                        ),
                      },
                    })
                  }
                />
                {scene.trajectory.enabled && (
                  <>
                    <NumberField
                      label={tr('Path window / s')}
                      value={scene.trajectory.duration_s}
                      min={1}
                      max={1e7}
                      onChange={(v) =>
                        patch({
                          trajectory: { ...scene.trajectory, duration_s: v },
                        })
                      }
                    />
                    <NumberField
                      label={tr('Path samples')}
                      value={scene.trajectory.samples}
                      min={24}
                      max={2048}
                      onChange={(v) =>
                        patch({
                          trajectory: { ...scene.trajectory, samples: v },
                        })
                      }
                    />
                  </>
                )}
              </>
            )}
          </details>
          <details className="explain">
            <summary>{tr('Display and time settings')}</summary>
            <NumberField
              label={tr('Physical seconds / playback second')}
              value={scene.time_scale}
              min={0.001}
              max={1e6}
              onChange={(v) => patch({ time_scale: v })}
            />
            <NumberField
              label={tr('Fixed color limit')}
              value={scene.color_limit}
              min={1e-12}
              step={0.1}
              onChange={(v) => patch({ color_limit: v })}
            />
            <Button
              variant="ghost"
              size="sm"
              onClick={() =>
                patch({ color_limit: colorBound(bundle, scene.terms) })
              }
            >
              {' '}
              {tr('Restore recommended range')}{' '}
            </Button>
            <Choice
              label={tr('Field sampling')}
              value={scene.quality}
              options={[
                { value: 'draft', label: tr('Draft') },
                { value: 'standard', label: tr('Standard') },
                { value: 'high', label: tr('High') },
              ]}
              onChange={(v) => patch({ quality: v as Scene['quality'] })}
            />
            <Choice
              label={tr('Canvas background')}
              value={scene.background}
              options={[
                { value: 'dark', label: tr('Ink blue') },
                { value: 'light', label: tr('Cool white') },
              ]}
              onChange={(v) => patch({ background: v as Scene['background'] })}
            />
            <Button
              variant="outline"
              onClick={() =>
                patch({
                  camera: {
                    azimuth_deg: -55,
                    elevation_deg: 22,
                    distance: 3.2,
                  },
                })
              }
            >
              {' '}
              {tr('Reset camera')}{' '}
            </Button>
          </details>
          <div className="integrity">
            <span className="status-dot" /> {tr('Data binding')}
            <code>{scene.bundle_hash.slice(0, 16)}…</code>
            <span>
              {tr('First mode:')}
              {tr(qualityMessage(primary))}
            </span>
          </div>
        </aside>
      </div>
      <Charts
        onError={setError}
        bundle={bundle}
        scene={scene}
        time={time}
        comparison={comparison}
        key={projectRevision}
        initialProbe={savedProbe}
        onProbeChange={setSavedProbe}
      />
      {exportOpen && (
        <section className="export-panel" ref={exportPanel}>
          <div className="section-title">
            <div>
              <span className="eyebrow">
                {tr('Reproducible figures and scenes')}
              </span>
              <h2>{tr('Take this observation with you')}</h2>
            </div>
            <Button
              variant="ghost"
              size="icon"
              aria-label={tr('Close export')}
              onClick={() => setExportOpen(false)}
            >
              <X />
            </Button>
          </div>
          <div className="export-settings">
            <Choice
              label={tr('Production recipe')}
              value={exportSettings.format}
              options={[
                { value: 'png', label: tr('Publication figure · PNG') },
                { value: 'gif', label: tr('Classroom animation · GIF') },
                { value: 'mp4', label: tr('Presentation video · MP4') },
                { value: 'glb', label: tr('3D project · GLB') },
                { value: 'frames', label: tr('Lossless frame sequence') },
                { value: 'svg', label: tr('Scientific figure · SVG') },
                { value: 'csv', label: tr('Numerical tables · CSV') },
              ]}
              onChange={(v) => {
                setExportSettings({
                  ...exportSettings,
                  format: v as ExportSpec['format'],
                  fps: v === 'gif' ? 20 : 24,
                  width: v === 'mp4' ? 1920 : 1200,
                  height: v === 'mp4' ? 1080 : 900,
                });
              }}
            />
            <NumberField
              label={tr('Width / px')}
              value={exportSettings.width}
              min={64}
              max={4096}
              onChange={(v) =>
                setExportSettings({ ...exportSettings, width: Math.round(v) })
              }
            />
            <NumberField
              label={tr('Height / px')}
              value={exportSettings.height}
              min={64}
              max={4096}
              onChange={(v) =>
                setExportSettings({ ...exportSettings, height: Math.round(v) })
              }
            />
            <NumberField
              label={tr('Playback duration / s')}
              value={exportSettings.duration_s}
              min={0.1}
              max={600}
              step={0.1}
              onChange={(v) =>
                setExportSettings({ ...exportSettings, duration_s: v })
              }
            />
            <NumberField
              label={tr('Frame rate / fps')}
              value={
                exportSettings.fps ??
                (exportSettings.format === 'gif' ? 20 : 24)
              }
              min={1}
              max={120}
              onChange={(v) =>
                setExportSettings({ ...exportSettings, fps: Math.round(v) })
              }
            />
          </div>
          <div className="export-grid">
            <div>
              <Toggle
                label={tr('Figure annotations')}
                checked={annotation}
                onChange={setAnnotation}
              />
              <Toggle
                label={tr('Transparent PNG background')}
                checked={transparent}
                onChange={setTransparent}
              />
              <Button
                disabled={busy}
                onClick={() =>
                  perform(() =>
                    view.current!.png(
                      annotation,
                      transparent,
                      chosenSpec('png'),
                    ),
                  )
                }
              >
                {' '}
                {tr('Download PNG and record (ZIP)')}{' '}
              </Button>
              <p className="hint">
                {' '}
                {tr(
                  'Uses the dimensions above. The ZIP contains a PNG and its provenance JSON. Use SVG for scientific curves.',
                )}{' '}
              </p>
            </div>
            <div>
              <Toggle
                label={tr('Omit unsupported GLB overlays')}
                checked={
                  exportSettings.omit_arrows &&
                  exportSettings.omit_geography &&
                  exportSettings.omit_analysis_overlays
                }
                onChange={(value) =>
                  setExportSettings(setAllOmissions(exportSettings, value))
                }
              />
              <p className="hint">
                {tr(
                  '{duration} seconds of editable animation. Colors remain fixed at the starting time. Current omissions: {omissions}. The master switch changes all three only when toggled.',
                  {
                    duration: exportSettings.duration_s,
                    omissions: omittedLabels.length
                      ? omittedLabels.join(', ')
                      : tr('none'),
                  },
                )}
              </p>
              <Button
                disabled={busy}
                variant="outline"
                onClick={() =>
                  perform(() => view.current!.glb(false, chosenSpec('glb')))
                }
              >
                {' '}
                {tr('Download GLB and record (ZIP)')}{' '}
              </Button>
            </div>
            <div>
              <p>{tr('Run this production recipe offline')}</p>
              <Button
                variant="outline"
                onClick={saveProject}
                disabled={!recipe}
              >
                {' '}
                {tr('Download complete production project')}{' '}
              </Button>
              {recipe ? (
                <>
                  <pre>{recipe.command}</pre>
                  <p className="hint">
                    {tr(recipe.description)}{' '}
                    {tr(
                      'Place the downloaded terra-project.json in the directory where you run this command.',
                    )}{' '}
                  </p>
                </>
              ) : (
                <p className="hint" role="alert">
                  {' '}
                  {tr('Invalid production configuration:')}
                  {formatError(locale, recipeError)}
                </p>
              )}
            </div>
          </div>
        </section>
      )}
      <footer className="footer">
        <span>
          {tr(
            'Terra Resonance · linear normal modes with explicit assumptions.',
          )}
        </span>
        <span>
          {tr(
            'Scientific inputs and display settings are saved separately · GPL-3.0-or-later',
          )}
        </span>
      </footer>
    </main>
  );
}
