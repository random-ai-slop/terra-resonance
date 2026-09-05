# Agreement version preparation

Task: WEB-VERSION/1  
Accepted base B: `f88431ce62eb0a73b0abd2a162795149eed6f0a1`  
Selected author model: `gpt-5.6-luna`

This bounded metadata update advances the synchronized project, Python package,
and web package versions from `0.2.1` to `0.3.0`. Only the package version
literal, the package `__version__` literal, the web package version, the two
root web lockfile versions, and this review record are in scope. No
dependencies, non-root lockfile package entries, runtime code, build, install, or
deployment work is included.

Checks run from the worktree with the primary interpreter
`/Users/veritaswang/Desktop/code/random-ai-slop/free-oscillation/.venv/bin/python`:

```text
/Users/veritaswang/Desktop/code/random-ai-slop/free-oscillation/.venv/bin/python -c \
  "import sys; sys.path.insert(0, '.'); from scripts.check_distribution import metadata_version; assert metadata_version('v0.3.0') == '0.3.0'"
PASS: metadata_version('v0.3.0') returned 0.3.0.

/Users/veritaswang/Desktop/code/random-ai-slop/free-oscillation/.venv/bin/python -c \
  "import sys; sys.path.insert(0, '.'); from scripts.check_distribution import metadata_version; metadata_version('v0.2.1')"
PASS: wrong tag rejected with ValueError: Tag 'v0.2.1' does not match v0.3.0.

/Users/veritaswang/Desktop/code/random-ai-slop/free-oscillation/.venv/bin/python -c \
  "import json,subprocess; b=json.loads(subprocess.check_output(['git','show','f88431ce62eb0a73b0abd2a162795149eed6f0a1:apps/web/package-lock.json'])); c=json.load(open('apps/web/package-lock.json')); b['version']='0.3.0'; b['packages']['']['version']='0.3.0'; assert c==b, 'lockfile differs beyond permitted root versions'"
PASS: lockfile baseline comparison found only the two permitted root version entries changed.
```

The lockfile comparison against `B` permits exactly its root `version` and
`packages[""]["version"]` entries to change; it reports no other differences.

## Independent domain verification

The domain parent inspected the actual diff and reran the metadata function
using the primary interpreter and `runpy.run_path` on this checkout's
`scripts/check_distribution.py`; its resolved `ROOT` matched this worktree.
The expected tag returned `0.3.0`; `v0.2.1` raised the expected `ValueError`.
The parent compared all four metadata files with `git show B:<path>`:
the TOML, Python and web manifest bytes matched exactly one version-literal
replacement each. The lockfile bytes matched exactly the two root version
replacements, and restoring those values in parsed JSON yielded the original
document. Dependency records and all other lockfile bytes were unchanged.
`git diff --check` passed. Exactly one transient author used `gpt-5.6-luna`,
with no children; the parent retained its configured domain model.

Limitations: this preparation does not establish release acceptance. No
distribution or web build, installation, numerical check or publication was
performed. The coordinator receives the bounded commit for integration and
the remaining release checks.
