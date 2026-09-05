import { issue } from '../i18n/core';
import * as THREE from 'three';
import { GLTFExporter } from 'three/addons/exporters/GLTFExporter.js';
import type { Bundle, Scene, ExportSpec } from './types';
import type { Patch } from './geometry';
import { gridParameters } from './surface-grid';
import { component } from './geometry';
import { colorBound, modeScale, temporal } from './field';
import { validateExportSpec } from './data';
import { downloadArtifact } from './download-artifact';
import palettes from '../../public/data/palettes.json';

function metadata(
  bundle: Bundle,
  scene: Scene,
  time: number,
  patches: Patch[],
) {
  return {
    format: 'terra-export',
    version: '1.0',
    scene: { ...scene, time_s: time },
    bundle_hash: scene.bundle_hash,
    provenance: bundle.provenance,
    renderer: `Three.js ${THREE.REVISION}`,
    annotation_language: 'en',
    section_surface: 'filled scientific triangles (including legacy Scene 1.0)',
    grid: {
      ...gridParameters(bundle, scene),
      segmentCount: patches
        .filter((p) => p.kind === 'grid')
        .reduce((n, p) => n + (p.geometry.index?.count ?? 0) / 2, 0),
    },
    coordinates: 'right-handed x=0E, y=90E, z=north',
    illustration_units: 'dimensionless; not source-calibrated displacement',
    modes: scene.terms.map((term) => {
      const mode = bundle.modes.find((m) => m.id === term.mode_id)!;
      return {
        ...term,
        frequency_hz: mode.frequency_hz,
        q: mode.q,
        illustration_divisor: modeScale(mode),
        canonical_units: 'kg^(-1/2)',
        quality: mode.provenance.quality,
      };
    }),
  };
}

function rgb(value: number, scene: Scene) {
  const t =
    scene.color === 'magnitude'
      ? value / scene.color_limit
      : (value / scene.color_limit + 1) / 2;
  return (scene.color === 'magnitude' ? palettes.magnitude : palettes.signed)[
    Math.floor(Math.max(0, Math.min(1, t)) * 255)
  ];
}

/** Save the actual displayed frame with a fixed scientific color scale. */
export async function exportPNG(
  renderer: THREE.WebGLRenderer,
  world: THREE.Scene,
  camera: THREE.Camera,
  bundle: Bundle,
  scene: Scene,
  time: number,
  annotation: boolean,
  transparent: boolean,
  spec?: ExportSpec,
) {
  const resolved = validateExportSpec(
    spec ?? { format: 'png', annotation, transparent },
  ) as unknown as ExportSpec;
  if (resolved.format !== 'png') throw issue('PNG export requires format=png');
  if (resolved.width > 4096 || resolved.height > 4096)
    throw issue('PNG dimensions exceed the browser 4096 px limit');
  const previousSize = renderer.getSize(new THREE.Vector2()),
    pixelRatio = renderer.getPixelRatio();
  const ortho = camera instanceof THREE.OrthographicCamera ? camera : null;
  const previousExtents = ortho
    ? {
        left: ortho.left,
        right: ortho.right,
        top: ortho.top,
        bottom: ortho.bottom,
      }
    : null;
  const alpha = renderer.getClearAlpha();
  try {
    if (spec) {
      if (!ortho)
        throw issue('PNG scene export requires an orthographic camera');
      renderer.setPixelRatio(1);
      renderer.setSize(resolved.width, resolved.height, false);
      const halfHeight = (ortho.top - ortho.bottom) / 2;
      ortho.left = (-halfHeight * resolved.width) / resolved.height;
      ortho.right = -ortho.left;
      ortho.updateProjectionMatrix();
      annotation = resolved.annotation;
      transparent = resolved.transparent;
    }
    if (transparent) renderer.setClearAlpha(0);
    renderer.render(world, camera);
    const source = renderer.domElement,
      canvas = document.createElement('canvas');
    canvas.width = source.width;
    canvas.height = source.height;
    if (canvas.width > 4096 || canvas.height > 4096)
      throw issue('PNG dimensions exceed the browser 4096 px limit');
    const ctx = canvas.getContext('2d');
    if (!ctx) throw issue('PNG canvas is unavailable');
    ctx.drawImage(source, 0, 0);
    let clipped = 0,
      sampled = 0;
    const factors = scene.terms.map((t) =>
      temporal(
        bundle.modes.find((m) => m.id === t.mode_id)!,
        t,
        time,
      ),
    );
    const patches: Patch[] = [];
    world.traverse((object) => {
      const patch = object.userData.patch as Patch | undefined;
      if (!patch) return;
      patches.push(patch);
      if (patch.kind === 'grid') return;
      const vector = new Float64Array(3);
      for (let i = 0; i < patch.base.length; i += 3) {
        vector.fill(0);
        for (let j = 0; j < factors.length; j++)
          for (let k = 0; k < 3; k++)
            vector[k] += factors[j] * patch.bases[j][i + k];
        const value = component(
          vector,
          0,
          patch.base.subarray(i, i + 3),
          scene.color,
        );
        if (Math.abs(value) > scene.color_limit) clipped++;
        sampled++;
      }
    });
    if (annotation) {
      const size = Math.max(12, Math.min(23, canvas.width / 64));
      const lines = [
        bundle.model.name +
          ' · ' +
          scene.terms.map((t) => `${t.mode_id} (m=${t.m})`).join(' + '),
        `Physical t=${time.toFixed(2)} s · playback ${scene.time_scale.toPrecision(4)} s/s · gain ${scene.deformation} R`,
        `${scene.color} · normalized illustration (dimensionless) · ${clipped}/${sampled} samples clipped`,
        'Quality: ' +
          scene.terms
            .map(
              (t) =>
                `${t.mode_id}: ${bundle.modes.find((m) => m.id === t.mode_id)!.provenance.quality.status}`,
            )
            .join('; '),
      ];
      const panel = Math.ceil(size * 8.4),
        margin = Math.max(12, size);
      ctx.fillStyle =
        scene.background === 'dark'
          ? 'rgba(11,22,33,.90)'
          : 'rgba(247,249,250,.94)';
      ctx.fillRect(0, canvas.height - panel, canvas.width, panel);
      ctx.fillStyle = scene.background === 'dark' ? '#eef4f5' : '#162d3b';
      ctx.font = `${size}px sans-serif`;
      lines.forEach((line, i) =>
        ctx.fillText(
          line,
          margin,
          canvas.height - panel + size * (1.5 + i * 1.25),
          canvas.width - 2 * margin,
        ),
      );
      const x = margin,
        y = canvas.height - size * 2.2,
        width = canvas.width - 2 * margin,
        height = size * 0.7;
      const palette =
        scene.color === 'magnitude' ? palettes.magnitude : palettes.signed;
      palette.forEach((color, i) => {
        ctx.fillStyle = `rgb(${color.map((c) => Math.round(c * 255)).join(',')})`;
        ctx.fillRect(x + (width * i) / 256, y, width / 256 + 1, height);
      });
      ctx.fillStyle = scene.background === 'dark' ? '#eef4f5' : '#162d3b';
      ctx.fillText(
        scene.color === 'magnitude' ? '0' : (-scene.color_limit).toPrecision(4),
        x,
        canvas.height - size * 0.35,
      );
      ctx.textAlign = 'right';
      ctx.fillText(
        scene.color_limit.toPrecision(4),
        x + width,
        canvas.height - size * 0.35,
      );
      ctx.textAlign = 'left';
    }
    const blob = await new Promise<Blob>((resolve, reject) =>
      canvas.toBlob(
        (b) => (b ? resolve(b) : reject(issue('PNG encoding failed'))),
        'image/png',
      ),
    );
    await downloadArtifact('terra-view.png', blob, {
      ...metadata(bundle, scene, time, patches),
      width: canvas.width,
      height: canvas.height,
      annotation,
      transparent,
      clipping: { clipped, sampled },
      appearance_omissions: [],
      export: {
        ...resolved,
        width: canvas.width,
        height: canvas.height,
        annotation,
        transparent,
      },
    });
  } finally {
    if (spec) {
      renderer.setPixelRatio(pixelRatio);
      renderer.setSize(previousSize.x, previousSize.y, false);
    }
    if (ortho && previousExtents) {
      Object.assign(ortho, previousExtents);
      ortho.updateProjectionMatrix();
    }
    renderer.setClearAlpha(alpha);
    renderer.render(world, camera);
  }
}

export type Sampling = {
  steps: number;
  duration_s: number;
  measured_error_m: number;
  guaranteed_error_m: number;
  tolerance_m: number;
};

/** A C2 interpolation bound covers every non-key time; actual off-key checks are independent. */
export function animationSampling(
  patches: Patch[],
  bundle: Bundle,
  scene: Scene,
  time: number,
  duration = 8,
): Sampling {
  const active = scene.terms
    .map((term, j) => ({
      term,
      j,
      mode: bundle.modes.find((m) => m.id === term.mode_id)!,
    }))
    .filter((x) => x.term.amplitude !== 0);
  const maxFrequency = Math.max(0, ...active.map((x) => x.mode.frequency_hz));
  const maxima = scene.terms.map((_, j) => {
    let maximum = 0;
    for (const patch of patches)
      for (let i = 0; i < patch.base.length; i += 3)
        maximum = Math.max(
          maximum,
          Math.hypot(
            patch.bases[j][i],
            patch.bases[j][i + 1],
            patch.bases[j][i + 2],
          ),
        );
    return maximum;
  });
  const scale = scene.deformation * bundle.model.radius_m;
  const tolerance = 0.01 * scale * colorBound(bundle, scene.terms);
  let steps = Math.max(
    2,
    Math.ceil(duration * scene.time_scale * maxFrequency * 24),
  );
  for (;;) {
    if ((steps + 1) * Math.max(1, scene.terms.length * 2) > 1_000_000)
      throw issue(
        'GLB scalar key budget exceeded; reduce playback speed or term count',
      );
    const dt = (duration * scene.time_scale) / steps;
    const guaranteed =
      ((scale * dt * dt) / 8) *
      active.reduce((sum, { term, mode, j }) => {
        const gamma =
            mode.q === null ? 0 : (Math.PI * mode.frequency_hz) / mode.q,
          omega = 2 * Math.PI * mode.frequency_hz;
        return (
          sum +
          maxima[j] *
            Math.abs(term.amplitude) *
            (gamma * gamma + omega * omega) *
            Math.exp(-gamma * time)
        );
      }, 0);
    let measured = 0;
    for (let k = 0; k < steps; k++)
      for (const fraction of [0.211324865405187, 0.5, 0.788675134594813]) {
        let bound = 0;
        for (const { term, mode, j } of active) {
          const left = temporal(mode, term, time + k * dt),
            right = temporal(mode, term, time + (k + 1) * dt);
          const actual = temporal(mode, term, time + (k + fraction) * dt);
          bound +=
            maxima[j] *
            Math.abs(actual - ((1 - fraction) * left + fraction * right));
        }
        measured = Math.max(measured, bound * scale);
      }
    if (!Number.isFinite(guaranteed) || !Number.isFinite(measured))
      throw issue('Nonfinite GLB interpolation estimate');
    if (guaranteed <= tolerance && measured <= tolerance)
      return {
        steps,
        duration_s: duration,
        measured_error_m: measured,
        guaranteed_error_m: guaranteed,
        tolerance_m: tolerance,
      };
    steps *= 2;
  }
}

function edgeIndex(index: THREE.BufferAttribute) {
  const edges = new Set<string>(),
    out: number[] = [];
  for (let i = 0; i < index.count; i += 3) {
    const ids = [index.getX(i), index.getX(i + 1), index.getX(i + 2)];
    for (let j = 0; j < 3; j++) {
      const a = Math.min(ids[j], ids[(j + 1) % 3]),
        b = Math.max(ids[j], ids[(j + 1) % 3]),
        key = `${a}:${b}`;
      if (!edges.has(key)) {
        edges.add(key);
        out.push(a, b);
      }
    }
  }
  return out;
}

/** Construct a glTF-ready scene. Exporter never receives shader-only deformation. */
export function buildGLBScene(
  patches: Patch[],
  bundle: Bundle,
  scene: Scene,
  time: number,
  omit: boolean,
  spec?: ExportSpec,
) {
  const resolved = validateExportSpec(
    spec ?? { format: 'glb' },
  ) as unknown as ExportSpec;
  if (resolved.format !== 'glb') throw issue('GLB export requires format=glb');
  if (resolved.width > 4096 || resolved.height > 4096)
    throw issue(
      'GLB camera aspect dimensions exceed the browser 4096 px limit',
    );
  if (
    (scene.arrows && !(omit || resolved.omit_arrows)) ||
    (scene.geography && !(omit || resolved.omit_geography)) ||
    ((scene.nodes || scene.point || scene.trajectory.enabled) &&
      !(omit || resolved.omit_analysis_overlays))
  )
    throw issue(
      'GLB requires explicit omission of enabled arrows, geography and analysis overlays',
    );
  const count = patches.reduce((n, patch) => n + patch.base.length / 3, 0),
    targets = scene.terms.length * 2;
  const cacheBytes = count * scene.terms.length * 24;
  if (
    count > 250000 ||
    cacheBytes > 128 * 1024 ** 2 ||
    count * targets > 8_000_000 ||
    72 * count * targets + cacheBytes > 512 * 1024 ** 2
  )
    throw issue('GLB geometry memory budget exceeded');
  const sampling = animationSampling(
      patches,
      bundle,
      scene,
      time,
      resolved.duration_s,
    ),
    root = new THREE.Group(),
    tracks: THREE.KeyframeTrack[] = [];
  root.rotation.x = -Math.PI / 2;
  root.scale.setScalar(bundle.model.radius_m);
  const factors = scene.terms.map((term) =>
    temporal(
      bundle.modes.find((m) => m.id === term.mode_id)!,
      term,
      time,
    ),
  );
  const visiblePatches = patches.filter(
    (p) =>
      !(
        p.kind === 'surface' &&
        scene.surface === 'wireframe' &&
        scene.wireframe_spacing_deg != null
      ),
  );
  if (
    (sampling.steps + 1) * Math.max(1, targets) * visiblePatches.length >
    1_000_000
  )
    throw issue('GLB scalar key budget exceeded across animated primitives');
  for (const [index, patch] of visiblePatches.entries()) {
    const g = patch.geometry.clone();
    g.setAttribute(
      'position',
      new THREE.BufferAttribute(
        Float32Array.from(patch.base, (x) => x / bundle.model.radius_m),
        3,
      ),
    );
    // Normals from the last displayed frame would contradict the base mesh.
    if (patch.kind !== 'grid') g.computeVertexNormals();
    const colors = new Float32Array(patch.base.length),
      vector = new Float64Array(patch.base.length);
    for (let j = 0; j < factors.length; j++)
      for (let i = 0; i < vector.length; i++)
        vector[i] += factors[j] * patch.bases[j][i];
    const color = new THREE.Color();
    for (let i = 0; i < vector.length; i += 3) {
      const v = rgb(component(vector, i, patch.base, scene.color), scene);
      color.setRGB(v[0], v[1], v[2], THREE.SRGBColorSpace);
      colors.set([color.r, color.g, color.b], i);
    }
    g.setAttribute('color', new THREE.BufferAttribute(colors, 3));
    g.morphTargetsRelative = true;
    g.morphAttributes.position = [];
    for (const basis of patch.bases)
      for (const sign of [1, -1])
        g.morphAttributes.position.push(
          new THREE.BufferAttribute(
            Float32Array.from(basis, (x) => x * scene.deformation * sign),
            3,
          ),
        );
    const wireframe =
      patch.kind === 'grid' ||
      (scene.surface === 'wireframe' && patch.kind === 'surface');
    // GLTFExporter uses LINES for wireframe materials but does not expand triangle indices.
    if (wireframe && patch.kind !== 'grid' && g.index)
      g.setIndex(edgeIndex(g.index));
    const mesh = new THREE.Mesh(
      g,
      new THREE.MeshBasicMaterial({
        vertexColors: true,
        side: THREE.DoubleSide,
        wireframe,
      }),
    );
    mesh.name = `terra_patch_${index}`;
    mesh.userData = { kind: patch.kind, layer_id: patch.layerId ?? null };
    mesh.updateMorphTargets();
    root.add(mesh);
    if (targets) {
      mesh.morphTargetInfluences = factors.flatMap((a) => [
        Math.max(0, a),
        Math.max(0, -a),
      ]);
      const times: number[] = [],
        weights: number[] = [];
      for (let k = 0; k <= sampling.steps; k++) {
        const playback = (sampling.duration_s * k) / sampling.steps;
        times.push(playback);
        for (const term of scene.terms) {
          const a = temporal(
            bundle.modes.find((m) => m.id === term.mode_id)!,
            term,
            time + playback * scene.time_scale,
          );
          weights.push(Math.max(0, a), Math.max(0, -a));
        }
      }
      tracks.push(
        new THREE.NumberKeyframeTrack(
          `${mesh.name}.morphTargetInfluences`,
          times,
          weights,
        ),
      );
    }
  }
  if (scene.reference) {
    const sphere = new THREE.SphereGeometry(scene.radius_fraction, 36, 18);
    sphere.rotateX(Math.PI / 2);
    root.add(
      new THREE.LineSegments(
        new THREE.WireframeGeometry(sphere),
        new THREE.LineBasicMaterial({
          color: 0x73828a,
          transparent: true,
          opacity: 0.1,
        }),
      ),
    );
    sphere.dispose();
  }
  const span = scene.camera.distance,
    aspect = resolved.width / resolved.height;
  const camera = new THREE.OrthographicCamera(
    (-span * aspect) / 2,
    (span * aspect) / 2,
    span / 2,
    -span / 2,
    0.01,
    100,
  );
  const az = (scene.camera.azimuth_deg * Math.PI) / 180,
    el = (scene.camera.elevation_deg * Math.PI) / 180;
  camera.position.set(
    5 * Math.cos(el) * Math.cos(az),
    5 * Math.cos(el) * Math.sin(az),
    5 * Math.sin(el),
  );
  camera.up.set(0, 0, 1);
  camera.lookAt(0, 0, 0);
  camera.name = 'Terra orthographic camera';
  // Camera extents are expressed in physical metres by glTF; node transforms scale positions only.
  camera.left *= bundle.model.radius_m;
  camera.right *= bundle.model.radius_m;
  camera.top *= bundle.model.radius_m;
  camera.bottom *= bundle.model.radius_m;
  camera.near *= bundle.model.radius_m;
  camera.far *= bundle.model.radius_m;
  camera.updateProjectionMatrix();
  root.add(camera);
  const omissions = [
    scene.arrows && 'arrows',
    scene.geography && 'geography',
    (scene.point || scene.nodes || scene.trajectory.enabled) &&
      'analysis_overlays',
  ].filter(Boolean);
  root.userData = {
    ...metadata(bundle, scene, time, patches),
    units: 'metres',
    gltf_axes: 'y-up; root maps scientific z-up',
    aspect,
    export: {
      ...resolved,
      omit_arrows: omit || resolved.omit_arrows,
      omit_geography: omit || resolved.omit_geography,
      omit_analysis_overlays: omit || resolved.omit_analysis_overlays,
    },
    ...sampling,
    resources: {
      counted_patch_points: count,
      visible_animated_points: visiblePatches.reduce(
        (n, p) => n + p.base.length / 3,
        0,
      ),
      field_cache_bytes: cacheBytes,
      conservative_morph_vertices: count * targets,
      conservative_geometry_bytes: 72 * count * targets + cacheBytes,
      weight_tracks: tracks.length,
      scalar_weights: tracks.reduce((n, track) => n + track.values.length, 0),
    },
    appearance_omissions: omissions,
    scientific_color: 'frozen at export start',
    material: 'unlit fixed vertex colors',
    annotation: 'metadata only',
    interpolation_validation:
      'C2 global interpolation bound plus midpoint and two non-key samples in every key interval; bounds include Q decay',
  };
  root.updateMatrixWorld(true);
  return {
    root,
    clip: new THREE.AnimationClip(
      'Normal-mode displacement',
      sampling.duration_s,
      tracks,
    ),
    manifest: root.userData,
  };
}

export async function exportGLB(
  patches: Patch[],
  bundle: Bundle,
  scene: Scene,
  time: number,
  omit: boolean,
  spec?: ExportSpec,
) {
  const { root, clip, manifest } = buildGLBScene(
    patches,
    bundle,
    scene,
    time,
    omit,
    spec,
  );
  try {
    const result = await glbExporter().parseAsync(root, {
      binary: true,
      animations: clip.tracks.length ? [clip] : [],
    });
    await downloadArtifact(
      'terra-mode.glb',
      new Blob([result as ArrayBuffer], { type: 'model/gltf-binary' }),
      manifest,
    );
  } finally {
    root.traverse((object) => {
      const mesh = object as THREE.Mesh;
      mesh.geometry?.dispose();
      if (mesh.material)
        for (const material of Array.isArray(mesh.material)
          ? mesh.material
          : [mesh.material])
          material.dispose();
    });
  }
}

/** Three r185 serializes ortho magnitudes as full spans; glTF requires half-spans. */
export function glbExporter() {
  return new GLTFExporter().register((writer) => ({
    writeNode(object, node) {
      if (!(object instanceof THREE.OrthographicCamera)) return;
      const json = (
        writer as unknown as {
          json: { cameras: { orthographic: { xmag: number; ymag: number } }[] };
        }
      ).json;
      const camera = json.cameras[node.camera as number].orthographic;
      camera.xmag = (object.right - object.left) / (2 * object.zoom);
      camera.ymag = (object.top - object.bottom) / (2 * object.zoom);
    },
  }));
}
