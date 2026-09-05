# Wire schemas · Bundle/Project 1.0, Scene 1.0–1.1

These Draft 2020-12 JSON Schemas document the published structural contract.
The links point to the canonical copies shipped in `earth_modes/assets/schema`;
there is no second generated schema source. Keep all three files together so
the project schema's relative references resolve without network access.

Unknown metadata is preserved. `ProbeSpec` and `ExportSpec` deliberately reject
unknown keys because these are executable requests. JSON Schema defaults are
documentation; schema validation does not fill them in.

Always finish import with `earth_modes.data.validate_bundle` or
`validate_project` (and the TypeScript counterpart in the browser). Structural
validation cannot establish mass normalization, regularity, material topology,
matching hashes, array-length relationships, quality evidence, or sampling
budgets. See `docs/DATA.md` for conventions and practical examples.

Installed schemas are accessible without this repository:

```python
from importlib.resources import files
schema_dir = files("earth_modes").joinpath("assets/schema")
schema_text = schema_dir.joinpath("project.schema.json").read_text()
```

Scene 1.0 accepts an absent/null `wireframe_spacing_deg` and rejects a non-null setting. Scene 1.1 requires the field, accepting null/5/10/15/30. New scenes default to 1.1 with 15 degrees. Reading a legacy scene never implicitly upgrades it; the Bundle and Project versions remain 1.0. Spacing applies only to wireframe surfaces, independently of numerical or field sampling.

Agreement Report 1.0 is an additional package analysis format documented by `earth_modes/assets/schema/agreement.schema.json`. It embeds two ModeBundles and references `mode-bundle.schema.json` beside it. Always finish with `earth_modes.agreement.validate_agreement`: structure alone cannot establish source hashes, connected support, metric consistency or budgets. This is independent of the browser Scene/Project formats.
