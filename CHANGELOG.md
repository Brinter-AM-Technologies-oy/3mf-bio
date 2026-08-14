# Changelog

Format follows [Keep a Changelog](https://keepachangelog.com/). This project is a working
draft and is not yet versioned for stability.

## [0.9.0] — 2026-08-07

### Added
- **`layer_stacking_test`** as an expected extrusion calibration. This was a genuine gap. A
  bridge test and a grid test both load a *single layer*; what collapses a tall construct is
  the weight of the layers above it, and no single-layer test applies that load. An ink can
  pass both and slump at twenty layers.
  Procedure: cylinder to a fixed layer count, then compare wall thickness in the lowest five
  layers against the highest five. Metrics: `wall_thickness_ratio` (1.0 = no spreading),
  `layers_before_collapse`, `max_stable_height`, `aspect_ratio`.
- Sources K8-K10 covering all three shape-fidelity tests, including two caveats worth
  recording: filament collapse continues **over time** after deposition, so an immediate
  reading and a ten-minute reading differ; and a published collapse model **overestimated**
  the deflection angle while following the experimental trend.

### Changed
- **`printability_Pr` → `grid_test`; `filament_collapse` → `bridge_test`.** Named for what
  you do at the bench rather than for the paper the metric came from. `CALIBRATION_ALIASES`
  keeps the old names valid, so existing packages continue to satisfy rule K8.
- The grid test is now treated as one procedure yielding several metrics — `printability_Pr`,
  `normalized_pore_number`, `pore_area`, `shape_fidelity_index` — rather than being conflated
  with the Pr index alone.
- **"Assay battery" removed throughout.** A domain expert read the phrase and could not tell
  what it meant, which is decisive: the term was jargon doing no work. `<b:characterization>`
  is now described as *what you measured on the printed thing, and when*, with a plain-language
  opening added to specification Chapter 8b.4.

## [0.8.0] — 2026-08-07

An on-ramp. The schema was complete and unusable by anyone who was not editing XML by hand.

### Added
- **`tools/questionnaire.py`** — generates the question set by importing the validator's own
  rule tables. Not a hand-written form: a hand-written form drifts, and a drifted form
  produces packages that fail their own validation.
- **`tools/integrate.py`** — STL or OBJ plus a JSON answer file, out comes a validating 3MF
  package. Binary and ASCII STL, OBJ with n-gon triangulation, vertex welding.
- **`tools/viewer.html`** — single file, no build step, no server, nothing uploaded. Leads
  with a **run sheet**: an ordered operator checklist assembled from the package, with open
  items and acceptance criteria attached to the steps where they bite. Plus open items,
  dossier, maturation schedule and a Three.js geometry view coloured by region role.
- **`tools/machine_profiles/brinter.json`** — first vendor profile. Nine printheads with
  their drive principles and head-specific prompts. Records what was published; omits bore
  sizes and pressure ranges, which are configuration-dependent.
- `tools/test_tools.py`, wired into CI, asserting the contract in both directions.

### The contract, and what it cost
The integrator **always emits and never fabricates.** Getting the second half right took
three fixes: early versions emitted a calibration record with no date, a placeholder
substance named "TODO", and a formulation built on it. Each satisfied the *shape* of a valid
record while asserting something false — that a dated calibration happened, that a material
existed. Now, if it was not supplied it is not emitted: no substances means no formulation,
which means objects carry no `pid`, which is an honest geometry-plus-skeleton package.

Tested both ways: entirely empty answers must still produce **zero validation errors**, and a
positive mycoplasma result must still be emitted and must then be **rejected**.

### Note
CI asserts `viewer.html` contains no `fetch(`, `XMLHttpRequest`, `sendBeacon` or `action=`.
A tool for handling unpublished experimental data should not be able to phone home, and that
should be checked rather than promised.

## [0.7.0] — 2026-08-07

Repositioned as an open schema rather than a candidate standard, and extended past the print
into maturation and characterization.

### Changed — positioning
- **No longer pursuing 3MF Consortium adoption.** Published as an open, reusable schema. The
  governance blockers in `SUBMISSION.md` (membership, sponsorship, IP commitment, namespace
  assignment) are dissolved rather than solved. `SCOPE.md` states the new position.
- **Namespace moved to `https://3mfbio.com/ns/bio/2026/07`** — a URN, chosen because it squats on nobody's
  domain. `spec/set_namespace.py` rewrites it across the repository in one command.
- **Schema files released into the public domain (CC0)** alongside BSD-2 for code. A schema
  embedded in a tool should not carry attribution friction.
- The regulatory, calibration and standards machinery **stays**, with claims removed rather
  than fields removed. The fields are what a manufacturer needs in order to see what to
  incorporate; the claims were never the useful part.

### Added — maturation and characterization
- **`<b:maturation>`** with `<b:stage>`, `<b:bioreactor>`, `<b:stimulation>`, `<b:medium>`.
  A printed construct is not the product; the matured construct is. Everything before this
  described about a day of work.
- **`<b:characterization>`** with `<b:assay>` and `<b:reading timepoint>`. Assays as a
  timecourse — "92% at day 1, 74% at day 21" is the shape of the information that decides
  whether a construct works, and a single-valued result cannot express it.
- `ST_Timepoint` as an ISO 8601 offset from end-of-print, so timepoints are orderable and
  comparable between packages.
- **Rule Q5**: a stimulation regime must record magnitude, rate and duration together. The
  perfusion-bioreactor literature specifically observes that these circuit parameters "as a
  group" are routinely omitted from reporting; this is the response.
- Rules Q1–Q12 covering stage ordering, perfusion flow rate, destructive-assay coupons,
  duplicate timepoints and measured readings without values.
- 21-day perfusion maturation with cyclic conditioning and nine assays added to the
  extrusion exemplar.

### Fixed
- Open item `timecourse-fields`, raised in v0.4, is **resolved** by the characterization
  timecourse. Graded volumetric fields measured serially remain deferred, and the resolution
  says so rather than overclaiming.

### Notes
- Conformance suite 48 → 53 faults. Q2 joins the documented Schematron scope exclusions:
  comparing two ISO 8601 durations needs XPath 2.0.

## [0.6.0] — 2026-08-01

Extrusion and deposition deepened. Extrusion is the modality most laboratories use, and it
had thinner coverage than laser-assisted transfer — four required parameters against ten.

### Added
- **`<b:printheads>` / `<b:printhead>` / `<b:nozzle>` / `<b:coaxial>` / `<b:channel>`.**
  Multi-head deposition is normal and had no representation at all. The head carries the
  drive, the nozzle and the formulation it is loaded with; `<object>` names the head that
  deposited it. Rules H1–H7.
- **`extrusion-coaxial` modality** with core/shell channel modelling. Rule H4 rejects a
  claimed product that the channel contents cannot produce — `hollow-tube` with a bioink
  core describes something that cannot be built, and every individual number in such a
  record is plausible.
- **Drive-specific required sets.** Pneumatic commands a pressure; piston and screw command a
  displacement. `extrusion-pneumatic` requires `extrusion_pressure`, `extrusion-piston` and
  `-screw` require `volumetric_flow_rate`, screw additionally `screw_speed`.
- **Rule X1, derivation completeness.** A declared `wall_shear_stress_max` must carry its
  inputs: nozzle bore, nozzle length, a driving term, and a fitted rheology.
- `examples-extrusion/` — a three-head exemplar with a coaxial vascular head, exercising
  everything above.
- Path and layer strategy parameters: `infill_pattern`, `raster_angle`, `perimeter_count`,
  `layer_offset`, `preflow_delay`, `z_hop`.
- Extrusion calibration expectations: filament width, Pr, filament collapse,
  filament fusion, flow-rate check, plus concentricity and wall thickness for coaxial.
- Specification Chapter 8a; ten new references (R53–R62).

### Changed
- **`nozzle_length` is now REQUIRED for extrusion.** The wall shear relation is
  τ_w = ΔP·R/(2L); without a length there is nothing to derive, and shear is the quantity the
  cell-damage literature rests on.
- `layer_height` and `strand_spacing` promoted to required.
- Conformance suite 42 → 48 faults, now run against both exemplars.

### Fixed
- `note` was not permitted on `component`, `crosslink`, `cellload`, `authentication` or
  `standardref` — found by writing an exemplar that needed it.

## [0.5.0] — 2026-08-01

Red-team pass. The theme: things that were normatively required but never tested.

### Added
- `SUBMISSION.md` — submission readiness assessment. Verdict: not ready, and the blockers
  are governance and data, not code.
- `spec/redteam_tests.py` — 15 adversarial packages that break no rule and are still garbage.
  **Before hardening, 13 of 15 produced a clean bill of health.** Now 6, and the residual
  set is documented as the boundary of what a format can enforce.
- `spec/make_conformance_corpus.py` — one minimal *passing* package per modality. Thirteen of
  fourteen modality rule sets had never been exercised by anything expected to succeed.
- `spec/roundtrip_test.py` — makes the Chapter 7 preservation rule testable. A lossy consumer
  drops 374 attributes from the example and the result still validates.
- Specification **Chapter 12, Threat Model** — what the format can and cannot enforce.
- Rules M1–M2 (`b:SpecVersion` required), U1–U4 (unit dimensions, physical bounds,
  setpoint/measured divergence, field-range sanity), D1–D2 (date sanity), C7–C8
  (authentication results), **T4 (toolpath checksum is verified against the file)**,
  W1–W2 (`--online` DOI and RRID resolution).
- `CITATION.cff`.

### Fixed
- **The toolpath checksum was never verified.** `SECURITY.md` instructed implementers to
  verify it — "a recorded hash that nobody checks is decoration" — while the reference
  validator did not. T4 now hashes the referenced part, and immediately caught the
  example's own placeholder.
- **A positive mycoplasma result satisfied the mycoplasma requirement.** Rule C2 checked
  that a record existed, not what it said. C7 now treats reported contamination as an error.
- **`total_light_dose` was required by P0 and forbidden by P3.** A parameter simultaneously
  mandatory and constrained to `derived` made a conformant volumetric template impossible.
  Found by generating a package expected to pass.
- **Three-way disagreement on embedded extrusion.** The specification prose, the Python
  `REQUIRED` table and the Schematron disagreed over whether embedded extrusion inherits the
  base extrusion parameters. The prose was right. The table now inherits, so the drift
  cannot recur.
- **No version marker existed.** A consumer could not tell which pre-1.0 draft it was
  reading.

### Changed
- Conformance suite grew from 35 to 42 injected faults; Schematron scope exclusions are now
  explicit (T4 needs the package, D2 needs XPath 2.0).

## [0.4.0] — 2026-08-01

### Added
- `<b:openitem>` / `<b:openitems>` — unknowns as structured data rather than comments.
  Every TODO, gap and caveat accumulated during development is now a record with a `kind`,
  `severity`, `status`, the `action` that would close it, and `<b:affects>` links to the
  resources it touches. Rules J1–J6.
- `<b:calibration>` with `<b:test>` children — calibration as a dated event with an
  operator, per-test acceptance criteria and pass/fail outcomes. Binds a printed artefact
  object via `artifactobjectid`. Rules K1–K8.
- `<b:regulatory>` with `<b:jurisdiction>`, `<b:obligation>` and `<b:standardref>` —
  jurisdiction-mapped regulatory determination, translatable across regimes without
  restructuring. Rules R4–R9.
- `iso52900` attribute on `<b:process>` — crosswalk to the seven ISO/ASTM 52900:2021
  process categories. Many-to-one and informative; ambiguous modalities deliberately
  unmapped. Rule N1.
- `pubchemcid` and `unii` on `<b:identity>`.
- `dossier/Calibration-Dossier.md`, `dossier/Regulatory-Annex.md`, `dossier/Fact-Check.md`.
- Package-level translation catalogue convention, `/bio/i18n/{lang}.json`.
- GitHub repository scaffolding: CI, issue and PR templates, contributing guide, licences.

### Fixed
- **LAP InChIKey was wrong everywhere it is usually copied.** The key aggregators publish
  for CAS 85073-19-4, `CVDUWYDMNPODNA-UHFFFAOYSA-N`, is the neutral species and does not
  match the salt formula those same vendors state. Correct key for the salt is
  `JUYQFRXNMVWASF-UHFFFAOYSA-M`, verified by computing the InChI from PubChem CID 68384915's
  SMILES and matching it against two independent registry listings.
- **Rule J5 coverage was too coarse.** A resource-wide `<b:affects>` silently excused every
  estimated parameter in that resource — so an open item about a missing firmware version
  accounted for an unmeasured light dose. Coverage is now by exact parameter name.

### Changed
- Two long-standing gaps closed: the ISO/ASTM 52900 crosswalk, and the LAP InChIKey.
- Conformance suite grew from 23 to 35 injected faults.

## [0.3.0] — 2026-07-30

### Added
- `spec/bio.sch` — ISO Schematron companion covering every intra-document rule, runnable in
  any XSLT toolchain.
- `<b:fieldbinding>` — binds a 3MF Volumetric Extension property field to a biological
  quantity with units, admissible range and provenance. Volumetric carries the field; bio
  carries its meaning. Rules F1–F9.
- `<b:cellload>` accepts either a scalar density or a `fieldid`, never both.
- `spec/conformance_tests.py` — fault injection through both engines with a coverage matrix.

### Fixed
- **Three Schematron rules were silently dead.** Within a `<sch:pattern>` only the first
  matching `<sch:rule>` fires for a node; broader contexts earlier in the same pattern
  shadowed V2, V3 and G2. They compiled and validated the good file without complaint.
  Only fault injection exposed them.
- Test harness truncation bug: `open(p, "w")` truncated before the read expression
  evaluated, masking a passing check as a failure.

## [0.2.0] — 2026-07-29

### Changed
- Rewritten to actual 3MF Consortium conventions after reading the published Displacement
  Extension. Namespace moved to `schemas.3mf.io`; resources moved into `<resources>` in the
  model part; `ST_ResourceID` integers replaced `xs:ID` strings.
- `<b:bioinkgroup>` became a **property group**, so ink assignment uses the core
  `pid`/`pindex` mechanism instead of a bespoke attribute — which also yields per-triangle
  ink assignment for free.

### Added
- OPC package structure with content types and relationships.
- `spec/bio.libxml.xsd`, because libxml2 rejects the `maxOccurs="2147483647"` that
  Consortium schemas use.

## [0.1.0] — 2026-07-28

### Added
- Initial draft: the evidence rule, modality-typed parameter sets, substance synthesis
  records, cell population records, and the parameter dossier with sources.
