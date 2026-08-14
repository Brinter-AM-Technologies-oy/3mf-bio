# Data collection sheet — one real exemplar

**For whoever runs the build. Not a review; a worklist.**

Every example in this repository is a template. This sheet is the exact set of values that
would turn one of them into a real record. It is generated from what is actually missing, not
written from memory.

**Scope: one construct, built once, recorded completely.** Not a study, not replicates across
conditions. One build where every field is filled from a real measurement rather than a
placeholder — that single package is worth more to this project than another fourteen
templates.

---

## Where the two exemplars stand

| | `examples/` | `examples-extrusion/` |
|---|---|---|
| Modality | volumetric tomographic | three-head extrusion + coaxial |
| Estimated parameters | 13 | 30 |
| Blocking open items | 4 | 6 |
| Assay readings declared | 0 | 19, **all without values** |
| TEMPLATE / ILLUSTRATIVE strings | 17 | 61 |

**Start with `examples/` if you have a volumetric printer** — it needs roughly half as much.
**Start with `examples-extrusion/` if you extrude**, which is most labs, and it is the one
that would demonstrate the most: multi-head, coaxial, maturation and a real timecourse.

Neither has a single real measured value in it today.

---

## Part 1 — Before printing

### 1.1 The polymer

- [ ] **Isolated yield** of the synthesis — mass of lyophilised product ÷ mass of input
      polymer, as a percentage.
      *Open item `gelma-yield`. Not reported in any source we consulted, which is itself worth
      publishing.*
- [ ] **Degree of substitution by ¹H-NMR** — with the spectrum attached as a package part
- [ ] **Degree of substitution by a colourimetric amine assay** (TNBS or equivalent)
      *Both, not either. They do not agree, which is why `<b:verification assay>` is required.*
- [ ] Molecular weight distribution, with method
- [ ] **Real lot numbers** and a certificate of analysis for every purchased substance
- [ ] Endotoxin, with the assay used *(record the number; assert no limit)*

### 1.2 Rheology — blocking

Open items `gelma-rheology` / `ext-rheology`. Nothing downstream can be derived without these.

- [ ] Fitted model — Herschel–Bulkley or power-law — with **yield stress, consistency index,
      flow index**
- [ ] **Temperature of measurement** *(rule I2: a viscosity without a temperature is not a
      measurement)*
- [ ] Raw flow curve and amplitude sweep as attached CSV
- [ ] **Repeat at the working cell density.** Cell-free rheology does not transfer, and this
      is the measurement most often skipped

### 1.3 Cells

- [ ] Real IRB / ethics approval reference
- [ ] Donor age, sex, tissue bank record
- [ ] Cellosaurus RRID if a line; **STR profile**
- [ ] Mycoplasma certificate with date
- [ ] Passage number at print
- [ ] Serum lot number
- [ ] Cell Ontology and UBERON terms

---

## Part 2 — The machine

- [ ] Vendor, model, **firmware version**, serial number
- [ ] Last calibration date
- [ ] **The calibration instrument's own calibration date** — a radiometer or power meter that
      is itself uncalibrated measures nothing

### 2.1 Calibration — blocking

**For extrusion**, all four shape-fidelity tests, because each applies a different load:

- [ ] `filament_width` — measured strand width vs nozzle bore
- [ ] `grid_test` — Pr, normalized pore number, pore area, shape fidelity index
- [ ] `bridge_test` — deflection angle vs half-gap, **and the time at which you measured it**
- [ ] `layer_stacking_test` — cylinder to a fixed layer count, wall thickness in the lowest
      five layers vs the highest five. **Record layer height and extrusion width**, or the
      number does not transfer
- [ ] `flow_rate_check` — extrude to a tared vessel; flow is highly non-linear in pressure
- [ ] For coaxial: `core_shell_concentricity`, `wall_thickness`

**For volumetric** — open item `vol-dose-threshold`:

- [ ] Dose test **at the working cell density**, not on cell-free resin. Scattering mean free
      path depends inversely on cell density, so a cell-free calibration describes a different
      material
- [ ] Optical power at the vial position
- [ ] Resin refractive index at the printing wavelength
- [ ] Rotation speed, projection count, vial diameter from the machine job file

**And, whatever the modality:**

- [ ] An **acceptance criterion you set** for each test. The project asserts none
- [ ] The date and operator *(rule K1: calibration is a dated event)*

---

## Part 3 — The print

- [ ] Every parameter the modality requires, **measured or cited, not estimated**.
      Run `python3 spec/validate_bio.py <pkg> --release` — it fails on any remaining
      `estimated`, which is the fastest way to see what is left
- [ ] For extrusion: pressure or flow rate, print speed, layer height, strand spacing,
      standoff height, **nozzle length**
- [ ] For coaxial: core and shell flow rates and their ratio
- [ ] Derived values with the model named — `wall_shear_stress_max`,
      `residence_time_in_nozzle`. Rule X1 checks the inputs are present
- [ ] Chamber temperature and humidity, and cumulative time out of the incubator
- [ ] **The real toolpath file**, with a checksum that verifies. Rule T4 hashes it

---

## Part 4 — After the print

This is the half most records omit entirely.

- [ ] Culture stages with real start and end times as ISO 8601 offsets — `P0D`, `P2D`, `P14D`
- [ ] If perfused: **flow rate, medium viscosity, circuit pressure** — open item `mat-flow`.
      The perfusion literature specifically notes these are "as a group often overlooked"
- [ ] If mechanically loaded: **strain amplitude, frequency, cycles per day** measured on
      *your* rig, not cited from a paper
- [ ] Medium composition, exchange interval and volume, per stage

---

## Part 5 — What you measured

Open items `results-placeholder` / `mat-readings`. The extrusion exemplar declares **19
readings and has values for none of them.**

For each assay: the method, an acceptance criterion you set, and a value at each timepoint
with **n and standard deviation**.

- [ ] Post-print viability — at more than one timepoint, so it is a timecourse
- [ ] Mechanical property from a coupon printed **in the same run**
- [ ] Structural fidelity — strand width, pore size
- [ ] If vascular: lumen patency
- [ ] Phenotype, if the point was differentiation
- [ ] Metabolic activity from spent medium — the cheapest longitudinal signal there is

### The one that matters most

- [ ] **At least one result that fails its acceptance criterion.**

A dossier containing only passes is not evidence that the criteria bite. It is evidence that
the criteria were written after the results were known. A real record with one honest failure
in it is more persuasive than a perfect one, and it is the single most valuable thing this
repository could contain.

- [ ] Destructive assays: **one coupon per timepoint**, each recorded as its own
      `test-coupon` object. Rule Q10 warns when this is missing — the extrusion exemplar
      currently trips it

---

## How to check progress

```bash
python3 spec/validate_bio.py <pkg>            # 0 errors = structurally sound
python3 spec/validate_bio.py <pkg> --release  # fails on every remaining estimated value
python3 spec/validate_bio.py <pkg> --strict   # warnings become errors
python3 spec/validate_bio.py <pkg> --online   # resolves DOIs and RRIDs
```

Then open the package in `tools/viewer.html`. The **run sheet** tab shows what a second
laboratory would see, and the **open items** tab counts what is still missing.

**Done** = `--release` passes and the open item list is empty of blocking entries.

---

## Why this is worth the effort

The schema has been red-teamed, fault-injected 54 ways, and validated against 15 modality
templates. None of that tests the thing that actually matters: **whether the fields are the
right fields when you sit down with real measurements in front of you.**

Every gap you hit — a field that does not exist, a field that exists but does not fit, a unit
that is wrong, a rule that fires when it should not — is a defect report the test suite cannot
produce. Those are more valuable than the dataset itself.

Please record them as you go, in `.github/ISSUE_TEMPLATE/spec-defect.md`, rather than working
around them.
