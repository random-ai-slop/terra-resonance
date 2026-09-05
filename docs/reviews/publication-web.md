# Public website delivery and durable website ownership

PUB-WEB/1, 2026-09-04. Read-only inspection of the existing website and installed vinext 1.0.0-beta.9/Vite 8.2.2 sources. Only this report was written. No Site tools, source changes, build, task creation or external publication were performed by this reviewer.

## Result

Historical target note: this first review used the initially proposed `free-oscillation` repository name. The user subsequently selected `terra-resonance`; implemented configuration and the second review use `/terra-resonance/`.

The existing single-page application is suitable for static GitHub Pages delivery. Keep vinext and the present client architecture. Add one explicit build target/base-path configuration and repair the small set of origin-root data requests. Preserve the existing Sites configuration as the default root-path target.

The implementation and actual subpath browser proof belong to the coordinator. Existing root-path static output is observed; subpath behavior described below is supported by the pinned implementation, not yet a completed Pages deployment.

## Found paths and constraints

| Source or resource | Actual behavior | Necessary action |
| --- | --- | --- |
| `next.config.ts` | Already sets `output: 'export'`; no basePath/trailingSlash | Add target-dependent basePath and a directory-index export for Pages |
| `vite.config.ts` | Imports `.openai/hosting.json` and the Sites plugin unconditionally; dynamically imports Cloudflare on every build | Keep these imports/bindings in the Sites branch. A public static build must not require private checkout metadata or Worker bindings |
| `Workbench.tsx` | Initial requests for `/data/prem-modes.json` and `/data/lessons.json`, another catalog request in applyPreset, and a PREM request when restoring defaults | Route all four requests through one build-base-aware public-asset helper; setting Vite base does not rewrite arbitrary fetch strings |
| `geometry.ts` | Coastlines are imported from `public/data/coastlines.json` into the bundle | No geography URL rewrite needed; retain canonical-copy checks |
| Workbench/Viewport/browser export | Palette JSON is statically imported | No palette runtime URL fix needed |
| `globals.css`, layout, public inventory | System font stacks; no font files, `@font-face`, external font loader or font fetch found | No font hosting change is currently required |
| Download helpers | Project JSON and artifact ZIPs use Blob object URLs, with local filenames | No deployment prefix should be added to Blob URLs or download filenames |
| Locale provider | Updates the current URL's query through `replaceState`; it does not replace pathname | The subpath, other query parameters and fragment are retained; verify this in the deployed path |
| `public/favicon.svg` | Static public resource exists | Ensure it is included in the prefixed artifact; any explicit icon URL added later must use the deployment base |
| Existing `dist/client/index.html` | Uses origin-root `/_next/static/...` script/CSS URLs | This old build cannot simply be uploaded unchanged under a repository subpath |

The app consists of the root layout/page and client workbench. No application server action, API route, middleware, cookie/header-dependent rendering, dynamic route or runtime image optimization was found in the inspected application paths. Its calculations, imports, figures and GLB downloads execute in the browser. GitHub Pages therefore does not need to simulate a Python backend or Cloudflare Worker. These are observed properties of this revision, not a guarantee that future server features would remain statically deployable.

## Minimal dual-target build

Use a nonsecret explicit target such as `TERRA_WEB_TARGET=pages`, with a single agreed base path `/free-oscillation` for this project. The default target remains Sites and uses an empty base path. Validate any configurable path to prevent accidental double slashes or disagreement between build and runtime URLs.

For Pages, use `output: 'export'`, `basePath: '/free-oscillation'` and `trailingSlash: true` in Next config. The pinned vinext implementation already derives Vite base from Next basePath, and derives assetPrefix from basePath when assetPrefix is absent. Do not independently set three competing prefix values. Standard Vite repository-site guidance also requires a repository subpath rather than root `/`. [Vite static deployment](https://vite.dev/guide/static-deploy)

For application fetches, prefer a small helper using the same resolved build base, for example joining Vite's resolved `import.meta.env.BASE_URL` with `data/lessons.json`. Verify that helper against both `/` and `/free-oscillation/`. Avoid ad hoc `location.pathname` inference, which couples data paths to future routes and trailing-slash redirects.

In the Pages configuration branch, use vinext plus the existing Tailwind PostCSS processing. Only import the Sites plugin, hosting JSON and Cloudflare bindings in the Sites branch. Keep the Sites branch's existing behavior intact. This changes deployment configuration rather than replatforming the application; vinext explicitly supports static export. [vinext upstream](https://github.com/cloudflare/vinext)

### Important pinned export layout

Local source inspection gives a concrete layout rule:

- `dist/config/next-config.js` fills an absent assetPrefix from basePath.
- `dist/index.js` sets Vite base and copies public files into `clientOutDir/basePath` for static export.
- `dist/utils/prerender-output-paths.js` emits `/` with a nonempty basePath and trailingSlash as `free-oscillation/index.html`, and the root Flight payload as `free-oscillation/index.txt`.
- The asset-prefix helper is used for compiled static asset directories.

Thus the expected Pages upload root is **`apps/web/dist/client/free-oscillation`**, containing index files, `_next` and `data`, while the generated URLs still begin `/free-oscillation/`. Uploading all of `dist/client` would put a second directory level below the Pages mount. With trailingSlash omitted, the HTML helper instead emits `free-oscillation.html`, which is unsuitable for simply uploading the namespaced subtree as the site root.

Assert the actual emitted tree before uploading; the build remains the authority. Do not patch generated HTML with a broad search/replace. Existing Sites delivery continues to consume its root-target `dist/client` output.

The present preview config serves `dist/client`. A faithful local Pages smoke test can serve its parent output tree and visit `/free-oscillation/`, then verify that the selected artifact subtree represents exactly the files mounted by Pages. Testing only localhost `/` would miss the known issue.

## Pages workflow and evidence

Use GitHub Actions to build from the public source/lockfile, upload only the static artifact and deploy that artifact to the Pages environment. Restrict publication to the intended branch or explicit manual dispatch; pull requests can validate/build without publishing. The deploy job needs Pages and OIDC permissions and must depend on the artifact-producing build. The official workflow separates setup, artifact upload and deployment, and reports the final page URL. [GitHub Pages custom workflows](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)

The public build should start without `.openai` metadata, credentials, `.wrangler`, a Cloudflare login or generated local caches. This is a required test of the proposed conditional configuration, not a claim that the current unconditional configuration already passes it. Avoid making publication dependent on access to the existing Sites account.

Minimum proof before calling Pages complete:

1. Clean install and successful checks/build for both targets; verify canonical web assets and source commit identity.
2. Confirm the Pages artifact contains a root `index.html`, expected CSS/JS and scientific data; inspect emitted URLs for one correct prefix and no unexpected root `/data` requests.
3. Serve the actual prefixed path. Load the default 47-mode data/catalog, choose a lesson, restore defaults, and confirm all expected fetches succeed with no console errors.
4. Switch English/Chinese while playing; preserve pathname, physical time, probe and scene. Reload a URL with `?lang=zh-CN` and an unrelated query/fragment.
5. Import/save a project and download a real PNG or SVG ZIP with English artifact annotations and provenance. These operations must work from the prefixed origin, not only from the development server.
6. Verify the deployed public URL and audience after the Pages job succeeds. Separately verify that the root-path Sites build still works. A green build is not proof of either live destination.

No service worker, SPA rewrite framework, custom server or 404 router is needed for the current one-page application. Additional routes would require their own exported-route and direct-load checks; they are not a present blocker.

## A bounded third durable domain is justified

The website now has an ongoing responsibility beyond occasional UI edits: bilingual scientific presentation, browser/Python compatibility, interactive performance, real downloads, dependency maintenance and two public deployment targets. A durable **website and delivery** task can retain that context and reduce repeated coordinator reconstruction. This does not justify a permanent always-running deployment daemon or separate QA department.

Its charter should be:

- Own assigned frontend changes, localization/accessibility, browser rendering/export integration, static target configuration and website-specific checks.
- Prepare reviewable build artifacts and deployment evidence for the exact accepted source revision. Execute external deployment only within a coordinator dispatch carrying the already authorized destination/audience and release conditions.
- Consume canonical bundles/catalog/palette/coastline resources and the package's scientific contracts. Do not independently rewrite default eigenfunctions, normalization or solver evidence to repair a visual problem.
- Report browser/Python differences to science and package/production through explicit counterexamples and agreed contract changes. Maintain frontend parity fixtures, not a competing scientific authority.
- Retain an operational handoff for both Sites and Pages: source revision, build target/base, deployed artifact/URL, validation and known limitations.

The coordinator retains goal/scope, canonical CURRENT, cross-domain priorities, integration, release decision and authorization interpretation. Science retains physical methods/evidence. Package/production retains installed APIs/CLI, Python outputs and distributions. Website ownership is transferred explicitly for a dispatch; the coordinator and third task must not edit the same Site files concurrently. Existing Sites skill obligations still apply to whichever owner receives those edits.

The third task is dormant between bounded assignments. Three durable contexts do not imply three simultaneous implementations: the existing capacity allowance and independent-review budget still apply. A small package-only change can remain wholly outside the website domain. Do not create separate permanent development and deployment tasks—the same website owner should carry a change through its inspected static artifact, while the coordinator integrates and accepts release.

This recommendation is based on observed phase-2 SVG/locale/export issues and the new two-target publication work. It is not a claim that a third task has already improved throughput; evaluate actual handoff quality, repeated setup, avoided ownership collisions and deployed-artifact consistency after use.
