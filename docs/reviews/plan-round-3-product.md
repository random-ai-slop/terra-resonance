# Planning round 3: pre-freeze product acceptance

Historical review of PLAN/CONTRACT v0.4, ACCEPTANCE, WORKFLOWS and planning dispositions. This was a document walkthrough, not resumed implementation or a claim of successful execution.

## Three workflow walkthroughs

| Workflow | Proposed path | Judgment at the time |
| --- | --- | --- |
| Teaching GIF | Real bundled mode → gains/fixed scale → self-contained project → default 20 fps → fixed-time PNG → two-pass palette → read count/duration | Default fps conflict resolved: 20 fps is exactly 50 ms; eight seconds/period gives 160 adequately sampled frames; project restores inputs. |
| Research probe/raw/compare | SolveSpec/quality → ProbeSpec → normalized/raw CSV/SVG → explicit-ID comparison | APIs/units are concrete rather than manually assembled hidden helpers; CLI duration expansion still needed B1. |
| MP4 and GLB production | Same project → 24 fps MP4 → independent GLB density/non-key 1% test → camera/manifest/omissions → readback | Keys, Q curvature, budgets/static-color limits are executable; example commands still needed enabled-layer omissions, B2. |

The fixed x>0,y<0 cut and two actual sections are consistent. Orthographic direction/span, fixed scales and arrow gain guide both renderers without demanding pixel identity. Shared palettes/coastlines are installable; geography is surface-only.

## Only two necessary clarifications

### B1: CLI probe interval is ambiguous

WORKFLOWS used `--duration 7200 --step 5`, but ProbeSpec needed start/step/count. It was unclear whether sampling started at zero or scene.time_s, used 1440 or 1441 points, or appended a nonintegral endpoint. A valid-looking CSV could thus represent the wrong time.

Specify default start=scene.time_s with explicit `--start`; use half-open `[start,start+duration)`, nominal count ceil(duration/step), and samples `start+k*step` strictly before the endpoint. An inclusive policy could also work, but only one may be chosen. Save resolved ProbeSpec rather than infer it later from a CLI string. Two small cases—nonzero start and nonintegral duration—are sufficient; no general time framework.

### B2: show the explicit GLB omission path

The contract correctly rejected unsupported enabled arrows/geography unless explicitly omitted, but the complete WORKFLOWS command only supplied `--out mode.glb`. A user enabling teaching arrows would then hit an undocumented interruption.

Add `--omit-arrows --omit-geography`, explaining that it affects only GLB and does not rewrite the project; retain the simple command for compatible scenes. Expose both choices before export without silently selecting them. No extra approval dialog or new feature is required.

## Implementation notes that do not block freeze

- GLB orthographic aspect needs one source; proposed export default 4:3 with override and actual manifest ratio avoids a new Scene camera system. Compare vertices in common coordinates/units.
- A default camera toward the cut, such as azimuth −45°/elevation25°, is a saved preset choice, not an interface blocker.
- Regular center limits allow real sections to reach the center rather than an artificial hole; the scientific reviewer must still test directional limits.
- Two files are not a universal filesystem transaction. Staging media/manifest and rolling back controlled failure suffices; no power-loss database is required.
- Paired signed morph bases and the fixed-bound 1% tolerance are reasonable. Test non-key times and low Q without adding curve compression or adaptive-render frameworks before freeze.

## Resources and scope

Concrete point/cache/target/key/pixel/disk constants permit preflight before field computation. Limits constrain combinations rather than promise l64×32 terms everywhere. Two-tier validation avoids running the full topology/high-resolution media matrix after every edit.

The required scope now maps to APIs, files, public commands and independent judgments. Probes/comparison reuse existing machinery. At this planning point, trajectories, node surfaces and dual viewports did not need expansion simply to claim richness; the later strategy review reconsidered narrower explanatory additions separately.

## Freeze decision

**Conditionally approve v1 freeze after B1 and B2.** No product blocker required a different stack, module redesign or fourth general planning round. Implementation notes can follow the contract, and actual quality still requires the three subsequent independent implementation reviews.
