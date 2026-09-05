export type Layer = {
  id: string;
  name: string;
  phase: 'solid' | 'fluid';
  r_m: number[];
  rho_kg_m3: number[];
  vp_m_s: number[];
  vs_m_s: number[];
  q_bulk?: (number | null)[];
  q_shear?: (number | null)[];
};
export type Model = {
  id: string;
  name: string;
  radius_m: number;
  layers: Layer[];
  reference_frequency_hz?: number;
  provenance?: Record<string, unknown>;
};
export type Region = {
  layer_id: string;
  r_m: number[];
  u: number[];
  v: number[];
  w: number[];
  potential?: number[];
};
export type Mode = {
  id: string;
  family: 'R' | 'S' | 'T';
  n: number;
  l: number;
  frequency_hz: number;
  q: number | null;
  regions: Region[];
  normalization: string;
  provenance: ModeProvenance;
};
export type Bundle = {
  schema_version: '1.0';
  model: Model;
  modes: Mode[];
  provenance: Record<string, unknown>;
};

export type Quality = Record<string, unknown> & {
  status: 'unverified' | 'unconverged' | 'converged' | 'benchmark_checked';
  mesh_convergence:
    | (Record<string, unknown> & {
        coarse_mesh: number;
        fine_mesh: number;
        relative_frequency_change: number;
        tolerance: number;
      })
    | null;
  benchmark:
    | (Record<string, unknown> & {
        source: string;
        reference_frequency_hz: number;
        relative_error: number;
        tolerance: number;
        quantity: string;
        model_hash: string;
      })
    | null;
  warnings: string[];
};
export type PotentialInfo = Record<string, unknown> & {
  status: 'absent' | 'solved' | 'postprocessed';
  units?: string;
  gravity?: 0 | 1 | 2;
};
export type ModeProvenance = Record<string, unknown> & {
  quality: Quality;
  potential?: PotentialInfo;
  solid_domain_id?: string | null;
};
export type Term = {
  mode_id: string;
  m: number;
  amplitude: number;
  phase_rad: number;
};
export type Scene = {
  schema_version: '1.0' | '1.1';
  wireframe_spacing_deg?: 5 | 10 | 15 | 30 | null;
  model_id: string;
  bundle_hash: string;
  terms: Term[];
  time_s: number;
  time_scale: number;
  deformation: number;
  surface: 'solid' | 'wireframe';
  geography: boolean;
  color: 'radial' | 'magnitude' | 'theta' | 'phi';
  arrows: boolean;
  reference: boolean;
  cutaway: boolean;
  radius_fraction: number;
  quality: 'draft' | 'standard' | 'high';
  arrow_scale: number;
  camera: { azimuth_deg: number; elevation_deg: number; distance: number };
  background: 'dark' | 'light';
  color_limit: number;
  point: MaterialPoint | null;
  trajectory: {
    enabled: boolean;
    start_s: number;
    duration_s: number;
    samples: number;
  };
  nodes: boolean;
};
export type Project = {
  format: 'terra-project';
  version: '1.0';
  bundle: Bundle;
  scene: Scene;
  probe?: ProbeSpec;
  export?: ExportSpec;
};
export const modeLabel = (m: Mode) => `${m.n}${m.family}${m.l}`;

export type MaterialPoint = {
  latitude_deg: number;
  longitude_deg: number;
  radius_fraction: number;
  layer_id?: string;
};

export type ProbeSpec = MaterialPoint & {
  start_s: number;
  step_s: number;
  sample_count: number;
  derivative: 0 | 1 | 2;
  normalized: boolean;
};
export type ExportSpec = {
  format: 'png' | 'svg' | 'csv' | 'frames' | 'gif' | 'mp4' | 'glb';
  width: number;
  height: number;
  duration_s: number;
  fps: number | null;
  transparent: boolean;
  annotation: boolean;
  omit_arrows: boolean;
  omit_geography: boolean;
  omit_analysis_overlays: boolean;
};
