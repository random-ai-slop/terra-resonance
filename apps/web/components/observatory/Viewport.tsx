'use client';
import { issue, message, type TextToken } from '@/lib/i18n/core';
import { useEffect, useLayoutEffect, useImperativeHandle, useRef } from 'react';
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { exportPNG, exportGLB } from '@/lib/science/browser-export';
import type {
  Bundle,
  Scene,
  MaterialPoint,
  ExportSpec,
} from '@/lib/science/types';
import { spatial, temporal, evaluate } from '@/lib/science/field';
import {
  buildPatches,
  component,
  cut,
  nodePoints,
  zeroComponent,
  geographyPoints,
  validateRenderBudget,
  type Patch,
} from '@/lib/science/geometry';

import palettes from '@/public/data/palettes.json';
import { gridParameters } from '@/lib/science/surface-grid';
import { useLocale } from '@/lib/i18n/provider';
export type ViewHandle = {
  png: (
    annotation: boolean,
    transparent: boolean,
    spec?: ExportSpec,
  ) => Promise<void>;
  glb: (omit: boolean, spec?: ExportSpec) => Promise<void>;
  time: () => number;
};
type Props = {
  bundle: Bundle;
  scene: Scene;
  playing: boolean;
  onTime: (t: number) => void;
  onCamera: (camera: Scene['camera']) => void;
  onPoint: (p: MaterialPoint) => void;
  onError: (error: unknown) => void;
  onStatus?: (s: TextToken[]) => void;
  onReject?: (previous: Scene, error: unknown, previousBundle: Bundle) => void;
  handle: React.Ref<ViewHandle>;
};
type LineField = {
  line: THREE.LineSegments;
  points: Float64Array;
  bases: Float64Array[];
  lift: number;
  work: Float64Array;
};
const linearPalettes = {
  signed: palettes.signed.map((rgb) =>
    new THREE.Color().setRGB(
      ...(rgb as [number, number, number]),
      THREE.SRGBColorSpace,
    ),
  ),
  magnitude: palettes.magnitude.map((rgb) =>
    new THREE.Color().setRGB(
      ...(rgb as [number, number, number]),
      THREE.SRGBColorSpace,
    ),
  ),
};
function disposeGroup(group: THREE.Group) {
  group.traverse((o) => {
    const mesh = o as THREE.Mesh;
    mesh.geometry?.dispose();
    if (mesh.material)
      for (const material of Array.isArray(mesh.material)
        ? mesh.material
        : [mesh.material])
        material.dispose();
  });
  group.clear();
}
class World {
  renderer: THREE.WebGLRenderer;
  world = new THREE.Scene();
  camera = new THREE.OrthographicCamera(-2, 2, 2, -2, 0.01, 100);
  controls: OrbitControls;
  root = new THREE.Group();
  patches: Patch[] = [];
  meshes: THREE.Mesh[] = [];
  lines: LineField[] = [];
  arrows: THREE.ArrowHelper[] = [];
  arrowPoints = new Float64Array();
  arrowBases: Float64Array[] = [];
  arrowWork = new Float64Array();
  marker: THREE.Mesh | null = null;
  trace: THREE.Line | null = null;
  s: Scene;
  b: Bundle;
  key = '';
  time = 0;
  width = 1;
  height = 1;
  nodeMessage: TextToken[] = [];
  clipping: TextToken[] = [];
  samplingMessage: TextToken[] = [];
  lastStatus = '';
  reportStatus: (s: TextToken[]) => void;
  constructor(
    el: HTMLElement,
    b: Bundle,
    s: Scene,
    onCamera: Props['onCamera'],
    onPoint: Props['onPoint'],
    onStatus: (s: TextToken[]) => void,
  ) {
    validateRenderBudget(b, s);
    this.reportStatus = onStatus;
    this.b = b;
    this.s = s;
    this.time = s.time_s;
    this.renderer = new THREE.WebGLRenderer({
      antialias: true,
      alpha: true,
      preserveDrawingBuffer: true,
    });
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.renderer.outputColorSpace = THREE.SRGBColorSpace;
    el.appendChild(this.renderer.domElement);
    this.camera.up.set(0, 0, 1);
    this.controls = new OrbitControls(this.camera, this.renderer.domElement);
    this.controls.enablePan = false;
    this.controls.minZoom = 0.5;
    this.controls.maxZoom = 2.5;
    this.world.add(this.root);
    this.world.add(new THREE.AmbientLight(0xffffff, 1));
    const light = new THREE.DirectionalLight(0xffffff, 1.15);
    light.position.set(3, -4, 6);
    this.world.add(light);
    this.controls.addEventListener('end', () => {
      const p = this.camera.position;
      onCamera({
        azimuth_deg: (Math.atan2(p.y, p.x) * 180) / Math.PI,
        elevation_deg: (Math.asin(p.z / p.length()) * 180) / Math.PI,
        distance: this.s.camera.distance / this.camera.zoom,
      });
    });
    let down = [0, 0];
    this.renderer.domElement.addEventListener('pointerdown', (e) => {
      down = [e.clientX, e.clientY];
    });
    this.renderer.domElement.addEventListener('dblclick', (e) => {
      if (Math.hypot(e.clientX - down[0], e.clientY - down[1]) > 8) return;
      const rect = this.renderer.domElement.getBoundingClientRect(),
        ray = new THREE.Raycaster();
      ray.setFromCamera(
        new THREE.Vector2(
          ((e.clientX - rect.left) / rect.width) * 2 - 1,
          1 - ((e.clientY - rect.top) / rect.height) * 2,
        ),
        this.camera,
      );
      const hit = ray.intersectObjects(this.meshes)[0];
      if (!hit?.face) return;
      const patch = hit.object.userData.patch as Patch;
      const pos = patch.geometry.getAttribute('position'),
        f = hit.face;
      const bary = THREE.Triangle.getBarycoord(
        hit.point,
        new THREE.Vector3().fromBufferAttribute(pos, f.a),
        new THREE.Vector3().fromBufferAttribute(pos, f.b),
        new THREE.Vector3().fromBufferAttribute(pos, f.c),
        new THREE.Vector3(),
      );
      if (!bary) return;
      const v = new THREE.Vector3();
      [f.a, f.b, f.c].forEach((id, i) =>
        v.addScaledVector(
          new THREE.Vector3(
            patch.base[id * 3],
            patch.base[id * 3 + 1],
            patch.base[id * 3 + 2],
          ),
          bary.getComponent(i),
        ),
      );
      let r = v.length();
      if (r === 0) {
        onPoint({
          latitude_deg: 0,
          longitude_deg: 0,
          radius_fraction: 0,
          ...(patch.layerId ? { layer_id: patch.layerId } : {}),
        });
        return;
      }
      if (patch.kind === 'surface') {
        v.normalize().multiplyScalar(
          this.s.radius_fraction * this.b.model.radius_m,
        );
        r = v.length();
      }
      onPoint({
        latitude_deg: (Math.asin(v.z / r) * 180) / Math.PI,
        longitude_deg: (Math.atan2(v.y, v.x) * 180) / Math.PI,
        radius_fraction: r / this.b.model.radius_m,
        ...(patch.layerId ? { layer_id: patch.layerId } : {}),
      });
    });
    try {
      this.configure(s);
    } catch (error) {
      this.dispose();
      throw error;
    }
  }
  clear() {
    this.root.traverse((o) => {
      const m = o as THREE.Mesh;
      m.geometry?.dispose();
      if (m.material)
        for (const mat of Array.isArray(m.material) ? m.material : [m.material])
          mat.dispose();
    });
    this.root.clear();
    this.patches = [];
    this.meshes = [];
    this.lines = [];
    this.arrows = [];
    this.marker = null;
    this.trace = null;
  }
  resize(w: number, h: number) {
    this.width = Math.max(1, w);
    this.height = Math.max(1, h);
    this.renderer.setSize(this.width, this.height);
    this.setCamera(this.s.camera);
  }
  setCamera(c: Scene['camera']) {
    const a = (c.azimuth_deg * Math.PI) / 180,
      e = (c.elevation_deg * Math.PI) / 180;
    this.camera.position.set(
      5 * Math.cos(e) * Math.cos(a),
      5 * Math.cos(e) * Math.sin(a),
      5 * Math.sin(e),
    );
    this.camera.zoom = 1;
    const h = c.distance / 2;
    this.camera.left = (-h * this.width) / this.height;
    this.camera.right = (h * this.width) / this.height;
    this.camera.top = h;
    this.camera.bottom = -h;
    this.camera.lookAt(0, 0, 0);
    this.camera.updateProjectionMatrix();
    this.controls.update();
  }
  configure(s: Scene, bundle = this.b) {
    validateRenderBudget(bundle, s);
    const previous = {
      root: this.root,
      patches: this.patches,
      meshes: this.meshes,
      lines: this.lines,
      arrows: this.arrows,
      arrowPoints: this.arrowPoints,
      arrowBases: this.arrowBases,
      arrowWork: this.arrowWork,
      marker: this.marker,
      trace: this.trace,
      s: this.s,
      key: this.key,
      time: this.time,
      nodeMessage: this.nodeMessage,
      b: this.b,
    };
    try {
      this.b = bundle;
      this.configureNext(s);
      if (previous.root !== this.root) {
        this.world.remove(previous.root);
        this.world.add(this.root);
      }
      this.setCamera(s.camera);
      this.renderAt(s.time_s);
      if (previous.root !== this.root) disposeGroup(previous.root);
    } catch (error) {
      if (previous.root !== this.root) {
        this.world.remove(this.root);
        disposeGroup(this.root);
        this.world.add(previous.root);
      }
      Object.assign(this, previous);
      this.setCamera(previous.s.camera);
      this.renderAt(previous.time);
      throw error;
    }
  }
  configureNext(s: Scene) {
    this.s = s;
    const key = JSON.stringify({
      bundleHash: s.bundle_hash,
      terms: s.terms.map((t) => [t.mode_id, t.m]),
      surface: s.surface,
      gridSpacing: s.wireframe_spacing_deg ?? null,
      radius: s.radius_fraction,
      quality: s.quality,
      cutaway: s.cutaway,
      reference: s.reference,
      arrows: s.arrows,
      geography: s.geography,
      background: s.background,
      nodes: s.nodes,
      nodeComponent: s.nodes ? s.color : null,
      nodeActive: s.nodes ? s.terms.findIndex((t) => t.amplitude !== 0) : null,
      point: s.point,
      trajectory: s.trajectory,
      trajectoryTerms: s.trajectory.enabled ? s.terms : null,
      trajectoryGain: s.trajectory.enabled ? s.deformation : null,
    });
    if (this.key !== key) {
      this.key = key;
      this.root = new THREE.Group();
      this.patches = [];
      this.meshes = [];
      this.lines = [];
      this.arrows = [];
      this.arrowPoints = new Float64Array();
      this.arrowBases = [];
      this.arrowWork = new Float64Array();
      this.marker = null;
      this.trace = null;
      this.nodeMessage = [];
      this.patches = buildPatches(this.b, s);
      for (const patch of this.patches) {
        if (patch.kind === 'grid') {
          const grid = new THREE.LineSegments(
            patch.geometry,
            new THREE.LineBasicMaterial({ vertexColors: true }),
          );
          grid.userData.patch = patch;
          this.root.add(grid);
          continue;
        }
        const material = new THREE.MeshStandardMaterial({
          vertexColors: true,
          side: THREE.DoubleSide,
          roughness: 0.8,
          metalness: 0,
          wireframe: s.surface === 'wireframe' && patch.kind === 'surface',
        });
        const mesh = new THREE.Mesh(patch.geometry, material);
        mesh.userData.patch = patch;
        mesh.visible = !(
          patch.kind === 'surface' &&
          s.surface === 'wireframe' &&
          s.wireframe_spacing_deg != null
        );
        this.root.add(mesh);
        this.meshes.push(mesh);
      }
      if (s.reference) {
        const g = new THREE.SphereGeometry(s.radius_fraction, 36, 18);
        g.rotateX(Math.PI / 2);
        const ref = new THREE.LineSegments(
          new THREE.WireframeGeometry(g),
          new THREE.LineBasicMaterial({
            color: s.background === 'dark' ? 0x73828a : 0x7b878e,
            transparent: true,
            opacity: 0.1,
          }),
        );
        g.dispose();
        this.root.add(ref);
      }
      const mkline = (
        points: Float64Array,
        color: number,
        layerId?: string,
        lift = 1,
      ) => {
        if (!points.length) return;
        const g = new THREE.BufferGeometry().setAttribute(
          'position',
          new THREE.Float32BufferAttribute(new Float32Array(points.length), 3),
        );
        const line = new THREE.LineSegments(
          g,
          new THREE.LineBasicMaterial({
            color,
            transparent: true,
            opacity: 0.8,
          }),
        );
        this.root.add(line);
        this.lines.push({
          line,
          points,
          lift,
          work: new Float64Array(points.length),
          bases: s.terms.map((t) =>
            spatial(
              this.b,
              this.b.modes.find((m) => m.id === t.mode_id)!,
              t.m,
              points,
              true,
              layerId,
            ),
          ),
        });
      };
      if (s.geography) {
        mkline(
          geographyPoints(this.b, s),
          s.background === 'dark' ? 0x1b353d : 0x142d35,
          undefined,
          1.001,
        );
      }
      if (s.nodes) {
        const term = s.terms.findIndex((t) => t.amplitude !== 0);
        const zeroRegions = new Set<string | undefined>();
        for (const patch of this.patches.filter((p) => p.kind !== 'grid'))
          if (zeroComponent(patch, patch.bases[term], s.color))
            zeroRegions.add(patch.layerId);
        this.nodeMessage = zeroRegions.size
          ? [
              message(
                'The component is identically zero; nodal contours do not apply: {regions}',
                {
                  regions: [...zeroRegions].reduce<TextToken | string>(
                    (joined, region, index) => {
                      const label = region ?? message('current shell');
                      return index
                        ? message('{left}, {right}', {
                            left: joined,
                            right: label,
                          })
                        : label;
                    },
                    '',
                  ),
                },
              ),
            ]
          : [];
        if (s.color === 'theta' || s.color === 'phi')
          this.nodeMessage.push(
            message(
              'Spherical components at the poles are coordinate conventions, not classified physical nodes.',
            ),
          );
        for (const patch of this.patches.filter((p) => p.kind !== 'grid'))
          mkline(
            nodePoints(patch, patch.bases[term], s.color),
            0x193e49, // Zero-valued surfaces are pale in both palettes.
            patch.layerId,
          );
      }
      if (s.arrows) {
        const points: number[] = [];
        for (let j = 1; j < 12; j++)
          for (let k = 0; k < 24; k++) {
            const th = (j * Math.PI) / 12,
              ph = (k * 2 * Math.PI) / 24,
              r = s.radius_fraction * this.b.model.radius_m,
              x = r * Math.sin(th) * Math.cos(ph),
              y = r * Math.sin(th) * Math.sin(ph);
            if (s.cutaway && cut(x / r, y / r)) continue;
            points.push(x, y, r * Math.cos(th));
            const a = new THREE.ArrowHelper(
              new THREE.Vector3(1, 0, 0),
              new THREE.Vector3(),
              0.1,
              s.background === 'dark' ? 0xe4edf0 : 0x152f3b,
              0.025,
              0.011,
            );
            this.arrows.push(a);
            this.root.add(a);
          }
        this.arrowPoints = new Float64Array(points);
        this.arrowWork = new Float64Array(points.length);
        this.arrowBases = s.terms.map((t) =>
          spatial(
            this.b,
            this.b.modes.find((m) => m.id === t.mode_id)!,
            t.m,
            this.arrowPoints,
          ),
        );
      }
      if (s.point) {
        this.marker = new THREE.Mesh(
          new THREE.SphereGeometry(0.012, 12, 8),
          new THREE.MeshBasicMaterial({ color: 0xffffff }),
        );
        this.root.add(this.marker);
        if (s.trajectory.enabled) {
          const p = this.pointPosition(),
            out: number[] = [];
          const n = s.trajectory.samples;
          const fmax = Math.max(
            ...s.terms
              .filter((t) => t.amplitude !== 0)
              .map(
                (t) =>
                  this.b.modes.find((m) => m.id === t.mode_id)!.frequency_hz,
              ),
          );
          if (n - 1 < 24 * fmax * s.trajectory.duration_s)
            throw issue(
              'The path needs at least 24 samples per fastest period',
            );
          for (let i = 0; i < n; i++) {
            const t =
                s.trajectory.start_s + (i / (n - 1)) * s.trajectory.duration_s,
              u = evaluate(this.b, s.terms, p, t, 0, true, s.point.layer_id);
            out.push(
              ...p.map(
                (x, k) => x / this.b.model.radius_m + s.deformation * u[k],
              ),
            );
          }
          this.trace = new THREE.Line(
            new THREE.BufferGeometry().setAttribute(
              'position',
              new THREE.Float32BufferAttribute(out, 3),
            ),
            new THREE.LineBasicMaterial({
              color: s.background === 'dark' ? 0xe9eef1 : 0x253d49,
              transparent: true,
              opacity: 0.8,
            }),
          );
          this.root.add(this.trace);
        }
      }
    }
  }
  pointPosition(): number[] {
    const p = this.s.point!,
      th = ((90 - p.latitude_deg) * Math.PI) / 180,
      ph = (p.longitude_deg * Math.PI) / 180,
      r = p.radius_fraction * this.b.model.radius_m;
    return [
      r * Math.sin(th) * Math.cos(ph),
      r * Math.sin(th) * Math.sin(ph),
      r * Math.cos(th),
    ];
  }
  sum(bases: Float64Array[], factors: number[], u: Float64Array): Float64Array {
    u.fill(0);
    for (let j = 0; j < bases.length; j++)
      for (let i = 0; i < u.length; i++) u[i] += factors[j] * bases[j][i];
    return u;
  }
  renderAt(t: number) {
    this.time = t;
    const s = this.s,
      R = this.b.model.radius_m,
      factors = s.terms.map((term) =>
        temporal(
          this.b.modes.find((m) => m.id === term.mode_id)!,
          term,
          t,
        ),
      );
    let clipped = 0,
      samples = 0;
    for (const patch of this.patches) {
      const u = this.sum(patch.bases, factors, patch.work),
        pos = patch.geometry.getAttribute('position') as THREE.BufferAttribute,
        colors = patch.geometry.getAttribute('color') as THREE.BufferAttribute;
      for (let i = 0; i < u.length; i += 3) {
        pos.setXYZ(
          i / 3,
          patch.base[i] / R + s.deformation * u[i],
          patch.base[i + 1] / R + s.deformation * u[i + 1],
          patch.base[i + 2] / R + s.deformation * u[i + 2],
        );
        const c = component(u, i, patch.base, s.color),
          v =
            s.color === 'magnitude'
              ? c / s.color_limit
              : (c / s.color_limit + 1) / 2,
          col =
            linearPalettes[s.color === 'magnitude' ? 'magnitude' : 'signed'][
              Math.floor(Math.max(0, Math.min(1, v)) * 255)
            ];
        colors.setXYZ(i / 3, col.r, col.g, col.b);
        if (patch.kind !== 'grid') {
          if (Math.abs(c) > s.color_limit) clipped++;
          samples++;
        }
      }
      pos.needsUpdate = true;
      colors.needsUpdate = true;
      if (patch.kind !== 'grid') patch.geometry.computeVertexNormals();
    }
    for (const item of this.lines) {
      const u = this.sum(item.bases, factors, item.work),
        p = item.line.geometry.getAttribute(
          'position',
        ) as THREE.BufferAttribute;
      for (let i = 0; i < u.length; i += 3)
        p.setXYZ(
          i / 3,
          (item.points[i] / R) * item.lift + s.deformation * u[i],
          (item.points[i + 1] / R) * item.lift + s.deformation * u[i + 1],
          (item.points[i + 2] / R) * item.lift + s.deformation * u[i + 2],
        );
      p.needsUpdate = true;
    }
    if (s.arrows) {
      const u = this.sum(this.arrowBases, factors, this.arrowWork);
      this.arrows.forEach((a, j) => {
        const i = j * 3,
          v = new THREE.Vector3(u[i], u[i + 1], u[i + 2]),
          len = v.length() * s.arrow_scale;
        a.visible = len > 1e-7;
        a.position.set(
          this.arrowPoints[i] / R + s.deformation * u[i],
          this.arrowPoints[i + 1] / R + s.deformation * u[i + 1],
          this.arrowPoints[i + 2] / R + s.deformation * u[i + 2],
        );
        if (a.visible) {
          a.setDirection(v.normalize());
          a.setLength(
            len,
            Math.min(0.025, len * 0.35),
            Math.min(0.011, len * 0.16),
          );
        }
      });
    }
    if (s.point && this.marker) {
      const p = this.pointPosition(),
        u = evaluate(this.b, s.terms, p, t, 0, true, s.point.layer_id);
      this.marker.position.set(
        p[0] / R + s.deformation * u[0],
        p[1] / R + s.deformation * u[1],
        p[2] / R + s.deformation * u[2],
      );
    }
    this.renderer.setClearColor(
      s.background === 'dark' ? 0x0b1621 : 0xf7f9fa,
      1,
    );
    this.renderer.render(this.world, this.camera);
    this.clipping = clipped
      ? [
          message(
            'Color clipping: {p0}/{p1} scientific display samples exceed the fixed range',
            { p0: clipped, p1: samples },
          ),
        ]
      : [];
    this.publishStatus();
  }
  publishStatus() {
    const notes = [
      ...this.nodeMessage,
      ...this.clipping,
      ...this.samplingMessage,
    ];
    if (gridParameters(this.b, this.s).sparse)
      notes.push(
        message(
          'Sparse grid: high-degree features may lie between lines. Use a filled surface or smaller spacing.',
        ),
      );
    const key = JSON.stringify(notes);
    if (key !== this.lastStatus) {
      this.lastStatus = key;
      this.reportStatus(notes);
    }
  }
  sampling(dt: number) {
    const fastest = Math.max(
      0,
      ...this.s.terms
        .filter((t) => t.amplitude !== 0)
        .map((t) => this.b.modes.find((m) => m.id === t.mode_id)!.frequency_hz),
    );
    const framesPerCycle =
      dt > 0 && fastest > 0 ? 1 / (dt * fastest * this.s.time_scale) : Infinity;
    this.samplingMessage =
      framesPerCycle < 12
        ? [
            message(
              'Playback undersampling: about {frames} frames per fastest period. Reduce the time scale.',
              { frames: framesPerCycle.toFixed(1) },
            ),
          ]
        : [];
    if (framesPerCycle < 2)
      this.samplingMessage.push(
        message('The playback rate is below the Nyquist limit.'),
      );
    this.publishStatus();
  }
  async png(annotation: boolean, transparent: boolean, spec?: ExportSpec) {
    this.renderAt(this.time);
    await exportPNG(
      this.renderer,
      this.world,
      this.camera,
      this.b,
      this.s,
      this.time,
      annotation,
      transparent,
      spec,
    );
  }
  async glb(omit: boolean, spec?: ExportSpec) {
    await exportGLB(this.patches, this.b, this.s, this.time, omit, spec);
  }
  dispose() {
    this.clear();
    this.controls.dispose();
    this.renderer.dispose();
    this.renderer.domElement.remove();
  }
}
export default function Viewport({
  bundle,
  scene,
  playing,
  onTime,
  onCamera,
  onPoint,
  onError,
  onStatus,
  onReject,
  handle,
}: Props) {
  const { t: tr } = useLocale();
  const el = useRef<HTMLDivElement>(null),
    engine = useRef<World | null>(null),
    initial = useRef({ bundle, scene }),
    callbacks = useRef({
      onTime,
      onCamera,
      onPoint,
      onError,
      onStatus,
      onReject,
    });
  useLayoutEffect(() => {
    callbacks.current = {
      onTime,
      onCamera,
      onPoint,
      onError,
      onStatus,
      onReject,
    };
  }, [onTime, onCamera, onPoint, onError, onStatus, onReject]);
  useImperativeHandle(
    handle,
    () => ({
      async png(annotation, transparent, spec) {
        if (!engine.current) throw issue('The 3D view is not ready yet');
        await engine.current.png(annotation, transparent, spec);
      },
      async glb(omit, spec) {
        if (!engine.current) throw issue('The 3D view is not ready yet');
        await engine.current.glb(omit, spec);
      },
      time() {
        return engine.current?.time ?? initial.current.scene.time_s;
      },
    }),
    [],
  );
  useEffect(() => {
    if (!el.current) return;
    let world: World | undefined;
    try {
      world = new World(
        el.current,
        initial.current.bundle,
        initial.current.scene,
        (c) => callbacks.current.onCamera(c),
        (p) => callbacks.current.onPoint(p),
        (s) => callbacks.current.onStatus?.(s),
      );
      engine.current = world;
      const resize = new ResizeObserver((es) => {
        world!.resize(es[0].contentRect.width, es[0].contentRect.height);
        world!.renderAt(world!.time);
      });
      resize.observe(el.current);
      return () => {
        resize.disconnect();
        world?.dispose();
        engine.current = null;
      };
    } catch (e) {
      world?.dispose();
      callbacks.current.onError(e);
    }
  }, []);
  useEffect(() => {
    try {
      engine.current?.configure(scene, bundle);
    } catch (e) {
      callbacks.current.onError(e);
      if (engine.current)
        callbacks.current.onReject?.(
          { ...engine.current.s, time_s: engine.current.time },
          e,
          engine.current.b,
        );
    }
  }, [bundle, scene]);
  useEffect(() => {
    let id = 0,
      last: number | null = null,
      report = 0;
    function frame(now: number) {
      const w = engine.current;
      if (w && playing) {
        const dt = last === null ? 0 : Math.max(0, now - last) / 1000;
        const previousTime = w.time;
        try {
          w.renderAt(w.time + dt * w.s.time_scale);
        } catch (error) {
          callbacks.current.onError(error);
          callbacks.current.onReject?.(
            { ...w.s, time_s: previousTime },
            error,
            w.b,
          );
          return;
        }
        if (now - report > 100) {
          w.sampling(dt);
          callbacks.current.onTime(w.time);
          report = now;
        }
      } else if (w) {
        w.sampling(0);
        w.renderer.render(w.world, w.camera);
      }
      last = now;
      id = requestAnimationFrame(frame);
    }
    id = requestAnimationFrame(frame);
    return () => cancelAnimationFrame(id);
  }, [playing]);
  return (
    <div
      ref={el}
      className="viewport"
      aria-label={tr(
        'Normal-mode 3D field. Drag to rotate, scroll to zoom, double-click to track a material point',
      )}
    />
  );
}
