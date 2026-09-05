# Implementation review round 2 — Python user workflows

Date: 2026-09-04. R1 was formally closed before this review began. Scope: Python
CLI/export/analysis user flows, production settings, publication identity and failure
paths. This report records independent findings before implementation changes.

**Result: changes required.** One P1 output-protection issue and three P2 contract
violations were reproduced with small local artifacts. Existing successful journey
and comparison tests passed; neither the full numerical matrix nor long videos were
repeated.

## W1 · P1 · default export can overwrite a competing completed output

Location: `export_common.transaction`, initial existence check and commit loop.

`overwrite=False` checks only when the staging context opens. A renderer may run for
minutes. If another process creates the requested artifact and sidecar during that
time, the commit loop still backs them up and replaces both, then deletes the backup
with its temporary directory. This contradicts default no-overwrite protection and
can destroy another successful job's result.

Executed minimal reproduction:

```python
with transaction(path, overwrite=False) as (staged, info):
    staged.write_bytes(b"OUR_IMAGE")
    info["source"] = "our exporter"
    # Another producer wins the unused output while the first renderer runs.
    path.write_bytes(b"OTHER_VALID_IMAGE")
    Path(str(path) + ".json").write_text('{"source":"other producer"}')
```

Observed completion: final artifact `OUR_IMAGE`, sidecar `our exporter`; no error.
This exercises the real commit path with deterministic interleaving, not a simulated
rename failure already covered by the R1/preflight tests.

Required repair: an atomic no-clobber publication path when overwrite is false;
simply checking existence a second time still leaves a race. For files, exclusive
hard-link publication can provide this on the same filesystem. A failed second
member must only remove the first member if it is still this transaction's own
inode. Directory publication also needs an explicit no-clobber strategy, without
silently weakening the frames-directory contract. Preserve explicit overwrite and
its existing rollback behavior.

## W2 · P2 · scientific plot/probe sidecars report production settings never used

Locations: `export_plot`, `export_probe`, and the fallback ExportSpec in `manifest`.

Executed PNG exports of both a canonical eigenfunction plot and a probe with
`transparent=True, annotation=False`. Pillow decoded **800×500** pixels with alpha
range **0–255**, confirming the requested transparent output. Both manifests instead
recorded:

```json
{"format":"png","width":1200,"height":900,
 "transparent":false,"annotation":true}
```

Other default ExportSpec keys were also inserted. The root cause is that these
scientific functions do not pass the actual output settings into `manifest`, which
fills in generic visual-production defaults. Restoring that purported recipe cannot
reproduce the saved artifact.

Required repair: scientific outputs must state their actual layout dimensions,
transparency and annotation values. Do not invent support for arbitrary 3D width/fps
options in the scientific CLI: its documented fixed scientific layout is legitimate.
Record actual supported settings, and keep CSV's inapplicable background semantics
explicit. Add one PNG decode/sidecar comparison for each scientific output path.

## W3 · P2 · probe can include its explicitly excluded time endpoint

Location: CLI `_probe` sample-count adjustment.

The contract requires `[start,start+duration)`, removing a roundoff endpoint equal
to the end. Current code compares the relative offset `(count-1)*step` to duration,
but the exporter calculates absolute timestamps. Rounding during addition changes
the result.

Actual CLI input: `--start 1000 --duration 0.3000000000000001 --step 0.1`.
The command succeeds and writes times `[1000.0,1000.1,1000.2,1000.3]`; the computed
exclusive end is also `1000.3`. This is an extra sample at the excluded endpoint.

Required repair: decide endpoint inclusion using the same absolute-time floating
arithmetic as the field evaluator and persist the resulting count. Reject a request
whose time span or step is unrepresentable at its chosen origin instead of writing
duplicate/nonadvancing timestamps. Keep the ordinary integer-count ProbeSpec API
distinct from the CLI's duration-to-count conversion.

## W4 · P2 · GIF ExportSpec can silently encode MP4

Location: `export_artifact` dispatch into `export_video`.

An actual 2-frame, 64×64 export with `spec.format='gif'` and output path
`asked-gif.mp4` succeeds. The resulting manifest says `format='mp4'` and its binary
header contains `ftypisom`. The dispatcher groups gif/mp4, then the callee picks its
encoder from the extension without checking the original spec.

Required repair: visual ExportSpec format and output suffix must agree, or the
dispatcher must state one documented source of truth before work. Rejecting a
contradiction is the smallest consistent choice; PNG/GLB already reject mismatching
suffixes in their focused functions. CLI's explicit output suffix may continue to
override the saved project's format as currently documented by its request resolution.

## Checks that passed

- Re-ran the full small CLI journey test: model → solve with config/flag precedence
  → inspect → scene → scientific SVG → raw derivative probe → comparison → project
  PNG and saved probe. It passed in the same run as explicit domain comparison
  validation (2 tests, 2.38 s).
- The comparison API preserves separate model radii, canonical units, supplied
  eigenfunction signs and explicit identities/domain fields; it does not reinterpret
  a comparison as physical superposition. Ambiguous implicit domain pairing fails.
- Existing-image protection works in the ordinary nonconcurrent case, and the prior
  controlled overwrite rollback test already covers a failed rename between pair
  commits. W1 is specifically the missing no-clobber concurrency guarantee.
- The README and user guide commands map to implemented options. Scientific SVG is
  honestly documented as its own layout, and unsupported scientific width/fps options
  are rejected rather than ignored. Saved raw ProbeSpec normalization is honored.
- Format mismatch used a real short encoder run, not a stub; no long animation was
  necessary. All review artifacts were created in temporary directories.

## Useful bounded improvement

Add a small `production`/actual-output subsection to scientific sidecars (or correct
the existing ExportSpec fields) instead of implying every portable setting is active
for every format. The same explicit distinction already used for GLB omissions
should cover scientific raster layout and CSV's lack of visual annotations. A
format/suffix consistency check and a timestamp-representability helper are enough;
there is no need for a new job manager, storage service or serialization framework.

Root authorized implementing W1–W3 after this report; W4 was additionally sent for
integration. This section is an initial findings ledger, not a claim of completed
repair verification.

## R2 implementation follow-up

Root authorized repairing all four findings. The following implementation changes
are complete; independent round closure remains with root.

- W1: non-overwrite file publication uses `os.link` (exclusive by construction),
  while directory publication uses macOS `renamex_np(RENAME_EXCL)`, Linux
  `renameat2(RENAME_NOREPLACE)`, or Windows' nonreplacing `os.rename`. Unsupported
  exclusive-directory operations fail clearly. Rollback checks the published inode
  before removing a new artifact, preserving a competing replacement. Explicit
  overwrite retains the previous backup/restore path. Tests cover a late competing
  file, a late empty directory, second-member collisions for files/directories,
  another writer replacing the first published inode, and the existing injected
  overwrite commit failure.
- W2: plot/probe figures explicitly use their actual 800×500/100dpi defaults;
  optional Python width/height are implemented with the same resource validator.
  `production` and `export_spec` retain real transparency and annotation values.
  Pixel/alpha readback verifies the default scientific plot and a custom 640×400
  probe. CSV refuses image dimensions and declares visual options inapplicable.
- W3: CLI endpoint pruning now uses absolute timestamps and the same arithmetic as
  the exporter. The reproduced request writes only 1000.0, 1000.1, 1000.2 and saves
  count=3. Unrepresentable windows/steps fail. Python and TypeScript both reject a
  multi-sample step below the last timestamp's IEEE754 spacing, using actual exponent
  bits on the JS side rather than a rounded logarithm; shared boundary examples pass.
- W4: `export_artifact` rejects mismatching visual format/suffix before creating or
  encoding output. Focused direct export APIs retain their existing suffix checks.

Validation: **23 Python tests passed** across export/CLI/data, including real small
PNG/GIF/MP4/GLB readback; only the two expected explicit GLB capability warnings were
emitted. The **5 TypeScript parity groups**, TypeScript compilation and the complete
frontend scientific/app lint target also pass. No numerical matrix rerun was needed.
The supported publication and scientific-layout semantics are documented in DATA.md.

## Independent final recheck — PASS

Reviewer: visual_research (independent of the W1–W4 implementer), 2026-09-04.
The original four failure classes were rerun through the real APIs/CLI with a small
saved PREM input; no new numerical solve or long encoder run was required.

- **W1 PASS:** two actual threads entered separate staging transactions, then a
  barrier released both commit attempts simultaneously. For both a file and a
  frames-style directory, exactly one producer succeeded and the other raised
  FileExistsError. The resulting content and JSON sidecar both belonged to the
  winner. The directory case exercised macOS exclusive publication, not a mocked
  rename. This confirms the original no-clobber race is closed on the host; Linux
  and Windows branches were inspected but not executed here.
- **W2 PASS:** independent Pillow readback gave 800×500 for the transparent,
  unannotated eigenfunction figure and 640×400 for the corresponding probe figure.
  Both alpha ranges were 0–255; both sidecars reported those exact dimensions,
  transparent=true and annotation=false. No unused generic production defaults
  were substituted for these actual settings.
- **W3 PASS:** the exact `start=1000,duration=0.3000000000000001,step=0.1` CLI
  request saved only [1000.0,1000.1,1000.2], with sample_count=3 and every timestamp
  strictly below the computed end 1000.3. The unrepresentable `start=1e16,duration=1,
  step=0.1` request returned 2 and left no output.
- **W4 PASS:** GIF ExportSpec with a `.mp4` target raised the explicit suffix
  contradiction before encoding; neither media nor sidecar existed afterward.

Machine-readable local evidence: `/tmp/terra-r2-independent-results.json`.
No remaining blocker in W1–W4 was found. These results close this bounded R2
workflow recheck; they do not claim the later R3 release checks have run.
