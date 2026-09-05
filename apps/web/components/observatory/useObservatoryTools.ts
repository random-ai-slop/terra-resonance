'use client';
import { useEffect, useLayoutEffect, useRef } from 'react';
import { flushSync } from 'react-dom';
import type { Bundle, Project, Scene } from '@/lib/science/types';
import { parseProject, validateScene } from '@/lib/science/data';
type Tool = {
  name: string;
  title: string;
  description: string;
  inputSchema: object;
  annotations: { readOnlyHint: boolean; untrustedContentHint: boolean };
  execute: (input: unknown) => unknown;
};
type Context = {
  registerTool: (
    tool: Tool,
    options: { signal: AbortSignal },
  ) => void | Promise<void>;
};
type Actions = {
  bundle: Bundle | null;
  scene: Scene | null;
  time: () => number;
  configure: (s: Scene) => void;
  load: (p: Project) => void;
};
/** Optional browser automation uses exactly the same validated project state. */
export function useObservatoryTools(actions: Actions) {
  const latest = useRef(actions);
  useLayoutEffect(() => {
    latest.current = actions;
  }, [actions]);
  useEffect(() => {
    const context = (document as Document & { modelContext?: Context })
      .modelContext;
    if (!context?.registerTool) return;
    const lifecycle = new AbortController();
    function state() {
      const a = latest.current;
      if (!a.bundle || !a.scene) throw Error('Default data is not ready');
      return { ...a, bundle: a.bundle, scene: a.scene };
    }
    const toolList: Tool[] = [
      {
        name: 'read_observatory',
        title: 'Read the normal-mode workbench',
        description:
          'Read the current model, available mode identities and frequencies, and complete scientific SceneSpec at the actual playback time.',
        inputSchema: {
          type: 'object',
          properties: {},
          additionalProperties: false,
        },
        annotations: { readOnlyHint: true, untrustedContentHint: true },
        execute(input) {
          if (!input || typeof input !== 'object' || Object.keys(input).length)
            throw Error('Expected an empty object');
          const a = state();
          return {
            model: { id: a.bundle.model.id, name: a.bundle.model.name },
            modes: a.bundle.modes.map((m) => ({
              id: m.id,
              family: m.family,
              n: m.n,
              l: m.l,
              frequency_hz: m.frequency_hz,
              quality: m.provenance.quality?.status,
            })),
            scene: { ...a.scene, time_s: a.time() },
          };
        },
      },
      {
        name: 'configure_scene',
        title: 'Configure and pause the visible scene',
        description:
          'Apply a complete SceneSpec bound to the current mode bundle, and pause at its physical time. This changes the visible workbench only; it does not recompute eigenmodes or save files.',
        inputSchema: {
          type: 'object',
          properties: { scene: { type: 'object' } },
          required: ['scene'],
          additionalProperties: false,
        },
        annotations: { readOnlyHint: false, untrustedContentHint: false },
        execute(input) {
          const a = state();
          if (
            !input ||
            typeof input !== 'object' ||
            !('scene' in input) ||
            Object.keys(input).length !== 1
          )
            throw Error('Expected only a scene object');
          const s = validateScene(input.scene, a.bundle, a.scene.bundle_hash);
          flushSync(() => a.configure(s));
          return {
            status: 'configured',
            time_s: s.time_s,
            terms: s.terms.length,
            bundle_hash: s.bundle_hash,
          };
        },
      },
      {
        name: 'load_mode_project',
        title: 'Load a scientific project',
        description:
          'Validate and load self-contained Terra project JSON or a ModeBundle into the visible workbench. Invalid input preserves the current project. No upload or server computation occurs.',
        inputSchema: {
          type: 'object',
          properties: { json: { type: 'string' } },
          required: ['json'],
          additionalProperties: false,
        },
        annotations: { readOnlyHint: false, untrustedContentHint: true },
        async execute(input) {
          if (
            !input ||
            typeof input !== 'object' ||
            !('json' in input) ||
            typeof input.json !== 'string' ||
            Object.keys(input).length !== 1
          )
            throw Error('Expected only a JSON string');
          const p = await parseProject(input.json);
          if (!p.bundle.modes.some((m) => m.l <= 64))
            throw Error('No displayable mode exists in the bundle');
          flushSync(() => latest.current.load(p));
          return {
            status: 'loaded',
            model_id: p.bundle.model.id,
            mode_count: p.bundle.modes.length,
            bundle_hash: p.scene.bundle_hash,
          };
        },
      },
    ];
    for (const tool of toolList) {
      try {
        void Promise.resolve(
          context.registerTool(tool, { signal: lifecycle.signal }),
        ).catch((e) => console.warn('Optional WebMCP registration failed', e));
      } catch (e) {
        console.warn('Optional WebMCP registration failed', e);
      }
    }
    return () => lifecycle.abort();
  }, []);
}
