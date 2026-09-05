# Public source and releases

The canonical complete source is [random-ai-slop/terra-resonance](https://github.com/random-ai-slop/terra-resonance). The Python distribution and interactive website share versioned scientific resources but have independent build products. GitHub Pages serves [the public observatory](https://random-ai-slop.github.io/terra-resonance/). The existing [Sites publication](https://terra-resonance.choi-wong-suen.chatgpt.site/) is also public at the user's explicit request.

## Build targets

Inside `apps/web`, `npm ci` installs the committed dependency lock. `npm run build:pages` creates a self-contained static artifact in `dist/pages`, mounted at `/terra-resonance/`. `TERRA_BASE_PATH` may be empty for an origin-root/custom-domain deployment, or a path without a trailing slash. It is a build-time setting. The build checks emitted asset addresses and required data, and records the source commit in `deployment.json` when running in CI.

For local inspection after that build, run `npx vite preview --outDir dist/client --base /terra-resonance/` and open the printed server URL at `/terra-resonance/`. This serves the physical prefixed export. The Pages upload itself uses `dist/pages`, whose root is mounted by GitHub at the project path; uploading `dist/client` would double-prefix the site.

`npm run build` keeps the existing Sites root-path export in `dist/client`. Only this target loads Sites/Cloudflare configuration. Both targets compile the same workbench and static scientific data. Neither runs Python on a web server. Pages builds do not need Sites credentials or hosting metadata. [Vite's deployment guide](https://vite.dev/guide/static-deploy.html#github-pages) explains the project-path requirement.

Canonical website source is tracked in the monorepo. The coordinator preserved the original Sites Git history in an ignored local publication mirror; it is a deployment destination, not a second editable source tree. Future Sites publication copies an accepted canonical source revision into that mirror and follows the Site owner's normal validated publishing process.

## Continuous integration and Pages

CI runs on pull requests, main pushes, manual dispatch and release reuse. It checks supported Python environments, existing meaningful tests, generated resource identity, both built Python distributions and web type/lint/scientific tests. FFmpeg exercises the actual media path in one environment. The installed distribution check runs outside the source checkout and creates actual scientific artifacts.

Only successful CI for a push to this repository's `main` can trigger Pages. The Pages workflow consumes that CI run's `pages-static` artifact, verifies its source identity and base path, and skips a superseded revision. The deployment queue retains pending runs so a late obsolete CI completion cannot replace the latest pending release; the revision guard runs after queue acquisition. It never executes code from pull-request artifacts in a privileged deployment workflow. Deployment permissions are scoped to the Pages job. [GitHub's custom-workflow documentation](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages) describes the artifact and permission contract.

Pinned action commits and the npm lockfile make dependencies reviewable. Dependabot proposes grouped updates; no dependency pull request merges itself. Solver accuracy campaigns remain explicit development/release evidence rather than expensive unconditional CI regeneration. In particular, scripts that rewrite canonical numerical data must run in a separate experiment before any resulting data change is reviewed.

## Python package delivery

The installable distribution is `terra-resonance` and its module/CLI are `earth_modes` / `terra`. Releases attach a wheel, source distribution and `SHA256SUMS` to the matching GitHub tag. These are genuine installable packages, not just repository snapshots. Download a wheel, check its checksum, then install it with `python -m pip install <wheel>` in a virtual environment.

To prepare a release, update `pyproject.toml`, `earth_modes.__version__` and the website manifest/lock root version together, finish affected reviews and push the accepted source to main. Create an annotated `vX.Y.Z` tag only for that accepted revision. The release workflow verifies tag/version agreement, runs reusable CI and publishes its exact validated package artifacts. Do not reuse an unrelated old `dist` directory.

The combined distribution is GPL-3.0-only, conservatively matching the retained Ouroboros GPLv3 grant. Upstream notices, local modifications, scientific references and asset licenses ship with the package. Historical 0.2.0 reports retain their earlier metadata statements; public 0.2.1 corrects the expression without claiming new upstream rights.

PyPI publication is not configured or claimed. A future PyPI release should first establish the package owner and trusted GitHub publisher, then add a separately scoped publishing job. No PyPI token is required for the current GitHub release/install workflow.

## Responsibility and recovery

Numerical methods owns physical contracts and evidence. Package/production owns installed APIs, CLI and Python outputs/distributions. Website/delivery owns assigned bilingual UI, browser exports, static targets and deployment preparation. The coordinator accepts cross-domain changes and releases; a standing role does not authorize unbounded writes or recurring automation. The [operating protocol](team/WORKFLOW.md) defines assignments and independent review.

Current live task IDs, machine paths and handoffs stay in ignored local coordination files, with a [public example](team/CURRENT.example.md). The initial private workflow checkpoint remains locally available but is not part of public history. Failed builds publish nothing. Recover from a bad deployment by reverting the offending source on main and letting the same checks redeploy; do not upload a manually edited artifact that lacks matching source.
