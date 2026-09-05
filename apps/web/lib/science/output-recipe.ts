import type { MessageKey } from '../i18n/messages';
import type { ExportSpec } from './types';
import { validateExportSpec } from './data';

const omissions = [
  'omit_arrows',
  'omit_geography',
  'omit_analysis_overlays',
] as const;

/** Resolve only the chosen output's presentation options, preserving the stored draft. */
export function outputSpec(
  draft: ExportSpec,
  format = draft.format,
  annotation = draft.annotation,
  transparent = draft.transparent,
): ExportSpec {
  const value = {
    ...draft,
    format,
    annotation,
    transparent: ['png', 'svg'].includes(format) && transparent,
  };
  if (format !== 'glb') for (const key of omissions) value[key] = false;
  return validateExportSpec(value) as ExportSpec;
}

/** The master switch is an explicit user action, never a lossy import transform. */
export function setAllOmissions(
  draft: ExportSpec,
  enabled: boolean,
): ExportSpec {
  return {
    ...draft,
    omit_arrows: enabled,
    omit_geography: enabled,
    omit_analysis_overlays: enabled,
  };
}

function shellQuote(value: string): string {
  return "'" + value.replaceAll("'", "'\\''") + "'";
}

/** Commands consume the downloaded project so dimensions, timing and flags cannot drift. */
export function outputRecipe(spec: ExportSpec, modeId?: string) {
  const resolved = outputSpec(spec);
  let command = 'terra export terra-project.json';
  let description: MessageKey =
    'Uses the complete scene and production settings saved in the project.';
  if (resolved.format === 'frames') {
    command += ' --kind frames --out frames';
  } else if (resolved.format === 'svg') {
    command += ' --kind eigenfunctions';
    if (modeId) command += ' --mode-id ' + shellQuote(modeId);
    command += ' --out eigenfunctions.svg';
    if (resolved.transparent) command += ' --transparent';
    if (!resolved.annotation) command += ' --no-annotation';
    description =
      "Native eigenfunction SVG for the first scene mode. Other scientific curves use the chart panel's SVG export.";
  } else if (resolved.format === 'csv') {
    command += ' --kind tables --out tables';
    description =
      'Exports frequency, eigenfunction and material CSV with the complete Model JSON. Use probe CSV for point time series.';
  } else {
    command += ' --out earth.' + resolved.format;
  }
  return { spec: resolved, command, description };
}
