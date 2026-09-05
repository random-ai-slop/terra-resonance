"""Terra Resonance: normal-mode calculations and reproducible scientific scenes.

Rendering lives in :mod:`earth_modes.export`; importing the numerical API does
not initialize a plotting backend or require a browser.
"""

__version__ = "0.2.1"

from .data import (
    bundle_hash,
    default_scene,
    load_bundle,
    load_project,
    make_project,
    save_bundle,
    save_project,
    validate_bundle,
    validate_model,
    validate_scene,
)
from .examples import list_examples, load_example
from .fields import evaluate_field, real_harmonic, sample_probe
from .models import homogeneous_model, prem_model
from .solver import SolverError, solve

__all__ = [
    "__version__",
    "list_examples",
    "load_example",
    "SolverError",
    "solve",
    "homogeneous_model",
    "prem_model",
    "bundle_hash",
    "default_scene",
    "load_bundle",
    "load_project",
    "make_project",
    "save_bundle",
    "save_project",
    "validate_bundle",
    "validate_model",
    "validate_scene",
    "evaluate_field",
    "real_harmonic",
    "sample_probe",
]
