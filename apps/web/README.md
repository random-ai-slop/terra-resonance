# Terra Resonance web workbench

A static research and demonstration workbench for planetary normal modes. Scientific data, eigenfunctions, display settings and reproducible projects are processed locally in the browser; numerical solving belongs to the independent Python package.

```sh
npm ci
npm run build:pages
npx vite preview --outDir dist/client --base /terra-resonance/
npm run check
npm run lint
npm test
npm run build
npm start
```

Requires Node.js 22.13+. The public Pages target needs no Sites account and is mounted at `/terra-resonance/`; `TERRA_BASE_PATH` selects a different build-time path. Its deployable root is `dist/pages`. The existing Sites target uses `npm run dev` / `npm run build` and the retained hosting configuration. `npm start` previews `dist/client` with a local static server; no Worker or database is needed. Production uses the same static directory. Scientific downloads contain the artifact and its provenance JSON in one ZIP. Save the project JSON to preserve the full original bundle.

The UI supports English and Simplified Chinese, defaulting to English. `?lang=en` or `?lang=zh-CN` overrides the saved preference. Locale does not change physical time, camera, scientific data or project metadata. Downloaded owned annotations are English; user-supplied names remain verbatim. Scene 1.1 adds explicit surface grid spacing, independent of the solver mesh. Legacy Scene 1.0 projects retain their version and triangle wires.

The full repository's `scripts/sync_web_assets.py` synchronizes `public/data` and scientific test fixtures. Do not edit these generated copies. The Python package, theory, benchmarks, independent examples and development roadmap live in the full Terra Resonance repository; this directory can independently install and build the viewer.

Scientific scope: linear R/S/T modes of spherical, non-rotating, isotropic bodies. Display gain and physical frequency are stored separately. Point records are not source-calibrated seismograms. The default PREM bundle includes explicit per-mode numerical quality and source evidence.

GPL-3.0-only; see LICENSE. Coastlines use Natural Earth 110m public-domain data. Palette and scientific-model sources are retained in the data resources. Frontend dependencies retain their own distributed licenses.
