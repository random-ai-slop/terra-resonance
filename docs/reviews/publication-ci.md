# Public CI and release review

Ticket: PUB-CI/1. Scope: the two CI/release workflows, Dependabot configuration,
and `scripts/check_distribution.py`. Pages deployment is a separate root-owned
workflow. This report describes implemented gates; it does not claim a hosted
GitHub Actions run or a PyPI publication.

## Execution and artifact boundary

`CI` runs on pull requests, main pushes, manual requests, and reusable workflow
calls. Ubuntu Python 3.11 and 3.13 run the focused source test suite. Python 3.13
explicitly installs FFmpeg and ffprobe, so GIF/MP4 frame and timing tests cannot
silently disappear behind the optional-executable skip. Expensive evidence
generators that rewrite canonical scientific assets are deliberately excluded.
The canonical package/web assets must already agree with their sources.

Both matrix entries build a wheel and sdist. The archive checker selects the
exact current-version filenames, compares every packaged runtime file against
source bytes, checks SPDX metadata and license/resource presence, and rejects
bytecode or live coordination state. Python 3.11 installs the wheel; Python 3.13
installs each archive into its own fresh venv. Child checks run outside the
checkout with `-I`, no `PYTHONPATH`, and an explicit installed-import-path check.
They exercise all six independently loaded examples, the `terra example` CLI,
a small custom model through both numerical backends, PNG dimensions, parsed
SVG, numerical probe CSV, and decoded GLB accessors and non-key animation
reconstruction. `pip check` must also pass.

The Node 22 job runs `npm ci`, tests, type checking, lint, and `npm run build:pages`
from `apps/web`. Its `pages-static` artifact contains `dist/pages`, including
`.nojekyll`. Root's Pages workflow consumes this exact successful run artifact;
CI does not grant deployment permissions or rebuild a Sites output.

The `Release` workflow starts only for `v*` tag pushes. It first requires exact
agreement between the tag, Python metadata, package `__version__`, and web
package version, then calls the same CI workflow. Only after all jobs pass can
the publishing job download `python-dist`, verify `SHA256SUMS`, and attach the
two exact-version archives plus checksums. Publication creates a draft with
assets and then publishes it. An existing release is never overwritten; a
failed upload leaves a draft that maintainers must inspect before retrying.
PEP 440 prerelease versions are marked as prereleases. Historical local 0.1/0.2
archives cannot enter the new release through a broad file glob.

## Security and maintenance

Tests run with read-only repository permissions and no persisted checkout
credentials. Only the final release job receives `contents: write`; that job
does not check out or execute package source. There is no
`pull_request_target`, PyPI token, trusted-publisher assumption, or package
publication on ordinary pushes. Weekly Dependabot updates cover Actions,
Python, and npm; compatible dependency updates are grouped, with no automatic
approval or merge.

Every external action is pinned to a full commit SHA verified through its
official release/commit page:

| Action | Release | Verified commit |
| --- | --- | --- |
| checkout | v7.0.1 | [3d3c42e](https://github.com/actions/checkout/commit/3d3c42e5aac5ba805825da76410c181273ba90b1) |
| setup-python | v7.0.0 | [5fda3b9](https://github.com/actions/setup-python/commit/5fda3b95a4ea91299a34e894583c3862153e4b97) |
| setup-node | v7.0.0 | [8207627](https://github.com/actions/setup-node/commit/820762786026740c76f36085b0efc47a31fe5020) |
| upload-artifact | v7.0.1 | [043fb46](https://github.com/actions/upload-artifact/commit/043fb46d1a93c77aae656e7c1c64a875d1fc6a0a) |
| download-artifact | v8.0.1 | [3e5f45b](https://github.com/actions/download-artifact/commit/3e5f45b2cfb9172054b4087a40e8e0b5a5461e7c) |

The permission/pinning choices follow GitHub's [secure-use guidance](https://docs.github.com/en/actions/reference/security/secure-use).
Release behavior uses the official [gh release create](https://cli.github.com/manual/gh_release_create)
interface. Update scheduling follows the [Dependabot options reference](https://docs.github.com/en/code-security/reference/supply-chain-security/dependabot-options-reference).

## Local verification and limits

The three YAML files parse locally. The checker rejects an intentionally wrong
`v999.0.0` tag and a valid ZIP wheel with its Scene schema deliberately removed.
A temporary clean source copy builds 0.2.1 with GPL-3.0-only metadata. Both the
wheel and sdist pass fresh, separate macOS Python 3.13.7 installations using
cached dependency wheels, with no system-site-packages or editable installation.
Each archive has 38 runtime/resource files matching source bytes. Both installed
backends return four modes for the small custom model; all six examples, the
CLI, PNG/SVG/probe checks, and `pip check` pass. The decoded GLB's non-key maximum
displacement error is 1.802e-6 in display-radius units, below its explicit fixed
1% bound. These are local test candidates, not the final public release bytes.

Local macOS execution does not prove Ubuntu/Python 3.11 compatibility, hosted
Actions schema acceptance, repository token policy, artifact transfer, or
external publication. The first actual CI and release runs remain the required
integration evidence. No actionlint binary is installed locally; YAML parsing
and manual workflow-context review are not presented as actionlint validation.
CI checks supported interpreter compatibility against the resolver's current
dependencies; it does not claim a fully locked cross-platform environment or
replace the independent numerical benchmark reports.
