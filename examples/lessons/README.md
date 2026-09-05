# Six scientific normal-mode lessons

Each `.terra.json` contains the complete 47-mode PREM bundle, SceneSpec, ProbeSpec, ExportSpec and English teaching notes for independent import. The catalog does not duplicate the bundle; its hash must match the canonical PREM bundle. Package examples and website copies use this same catalog.

Frequencies and eigenfunctions come from the validated default solution. Illustration normalization is fixed per mode; geometric gain is not source calibration. Curated color limits use 1.05 times the all-time analytic component envelope, including both material sides on sections. No per-frame rescaling or change to general scene defaults is applied. See `teaching.verification.color_policy` and each mode's quality provenance.

Regenerate with `OPENBLAS_NUM_THREADS=1 .venv/bin/python scripts/generate_lessons.py`. `--no-previews` skips only PNG/CSV production; projects and scientific assertions are still generated and checked.

## A breathing sphere

Project: [01-breathing.terra.json](01-breathing.terra.json)

1. Play one period and compare radial arrows in different directions on the sphere.
2. Pause and change time from 0 to T/2; verify that expansion and contraction exchange.
3. Halve the geometric gain and confirm that the eigenfrequency and material-point period stay fixed.

Checkable conclusion: The surface radial coefficient of R0_0 is independent of direction; displacement reverses after half a period.

Interpretation caution: Display gain makes motion visible; these amplitudes are not earthquake displacements in metres. This lesson uses a fixed component color range without changing the modes or physical amplitudes.

## Purely tangential motion?

Project: [02-tangential.terra.json](02-tangential.terra.json)

1. Check whether displacement arrows are perpendicular to the reference radius.
2. Follow the gold material point for one period; it moves back and forth along a fixed tangent.
3. Increase and decrease geometric gain to distinguish first-order tangential displacement from the radius change of the exaggerated position.

Checkable conclusion: Displacement of this surface-solid-domain T0_2 mode is tangential everywhere; a single real mode gives a local line-segment trajectory.

Interpretation caution: Tangential oscillation is not planetary rotation; finite displayed displacement creates a second-order geometric radius change. This lesson uses a fixed component color range without changing the modes or physical amplitudes.

## What do n, l and m change?

Project: [03-indices.terra.json](03-indices.terra.json)

1. Keep S0_2 and change only m from 0 to 2; compare the node pattern and frequency.
2. Return to S0_2, m=0, then select S0_3; compare only angular degree l.
3. Return to the baseline again, then select S1_2; compare radial eigenfunctions at the same l.

Checkable conclusion: In a spherical model, m selects a degenerate angular basis without changing frequency; changing n or l selects a different eigenmode.

Interpretation caution: The branch label n is not the total zero count of every U/V/W component in a layered solid-fluid model. This lesson uses a fixed component color range without changing the modes or physical amplitudes.

## Across the liquid core boundary

Project: [04-liquid-core.terra.json](04-liquid-core.terra.json)

1. Use the cutaway and U/V curves to locate the outer-core–mantle boundary.
2. Compare U on the fluid and solid sides at the same boundary radius; normal displacement is continuous.
3. Switch the linked point from the fluid material side to the solid side; tangential displacement may jump.

Checkable conclusion: A fluid-solid interface couples normal motion, but tangential displacement need not be continuous; interpolation must not smooth across it.

Interpretation caution: The fluid is not stationary: it participates in S/R modes; an ideal fluid does not support elastic T modes. This lesson uses a fixed component color range without changing the modes or physical amplitudes.

## Building a traveling pattern

Project: [05-traveling.terra.json](05-traveling.terra.json)

1. Inspect the two terms: m=+2 and m=-2 of S0_2, with equal amplitudes and a phase difference of π/2.
2. Advance from t=0 to T/8; the pattern shifts 22.5° toward decreasing longitude.
3. Observe the closed local trajectory of a fixed material point, then remove one term to compare a standing wave.

Checkable conclusion: Two degenerate real bases in quadrature produce cos(2φ+ωt), a traveling pattern with angular speed −ω/2.

Interpretation caution: The pattern moves; material points oscillate locally rather than following its peaks around the planet. This lesson uses a fixed component color range without changing the modes or physical amplitudes.

## Beats at a fixed point

Project: [06-beats.terra.json](06-beats.terra.json)

1. Read the x time series at the gold point on the equator at zero longitude; the two local amplitudes are explicitly balanced.
2. Inspect at least two envelope periods and compare cancellation near T_beat/2 and 3T_beat/2.
3. Disable each term in turn, then restore the sum to confirm that the slow envelope follows the frequency difference.

Checkable conclusion: The frequency difference is 0.0328136 mHz; the amplitude-envelope period at this point is 1/Δf ≈ 8.465 hours.

Interpretation caution: The x component is balanced at this receiver; beat depth can change at another location. Two-frequency superposition does not guarantee a seamless loop. This lesson uses a fixed component color range without changing the modes or physical amplitudes.

## Outputs from the same projects

Each named PNG is exported from its lesson SceneSpec. `06-beats-probe.png` and the CSV use the sixth lesson's ProbeSpec. JSON sidecars retain the scene, sampling and bundle hash; a hash is not a replacement for the input data.

The beat case uses 0S4 and 1S2 with m=0 at the equator/zero-longitude surface point. Explicit amplitudes and π phases balance the local x components. Its 4097 samples include the endpoint of two envelope periods. The traveling case uses ±m=2 of 0S2 in quadrature, without an artificial frequency difference.

Generation verifies these teaching constructions and data contracts. Release-level implementation review is recorded separately in the review log.
