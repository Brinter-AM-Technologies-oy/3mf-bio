# Submission Readiness

> **Superseded in part.** The project has since chosen the open-schema route described in
> [SCOPE.md](SCOPE.md) rather than pursuing 3MF Consortium adoption. The governance items
> below (membership, sponsorship, IP commitment, namespace assignment) are therefore no
> longer blockers — the namespace has moved to a neutral URN and the licence already permits
> unrestricted reuse.
>
> **What survives, and still matters, is §4: the data.** No real dataset has been recorded
> in this schema. That gap is unchanged by any licensing decision, and it is the one thing
> the authors cannot close alone. §5 and §6 (the red-team findings and the defects found by
> testing) also stand.

**Original verdict, retained for the record: not ready to submit.**

This document is the output of a red-team pass over the whole repository. It is deliberately
pessimistic. Read `README.md` for what the project does; read this for what would stop a
reviewer signing it off.

---

## 1. Where this can go, and what each route demands

There are three distinct destinations and they have different bars. Conflating them is the
commonest way a format proposal stalls.

| Route | What it is | Realistic bar |
| --- | --- | --- |
| **A. 3MF Consortium extension** | The stated goal. Extensions reach 0.5 as a pre-release with a public call for feedback, then 1.0 | Membership + IP commitment + working-group sponsorship + reference implementation |
| **B. Peer-reviewed paper** | A methods/standards paper in *Biofabrication*, *Additive Manufacturing*, or similar | A real dataset, an independent reproduction, and standards read in full |
| **C. Public draft** | GitHub release under a neutral namespace, soliciting comment | Achievable now, after the P0 legal and naming items |

**Recommendation: C first, then B, then A.** Route A realistically requires an existing
member company to sponsor the work; arriving with a public draft, a paper, and a working
lib3mf branch is a far stronger position than arriving with a specification alone.

### The governance facts that constrain Route A

- The 3MF Consortium is a **Joint Development Foundation Projects, LLC series — an affiliate
  of the Linux Foundation.** It is not an informal group; contribution runs through a legal
  entity.
- Members have agreed to make necessary patent claims available for implementations of the
  Core Specification **and all public extensions** on a **royalty-free** basis. Contributing
  an extension therefore carries an IP commitment that the current BSD-2 licence does
  **not** discharge.
- Development runs through a **technical working group** with a chair, under a steering
  committee of member companies.
- The observed extension lifecycle is pre-release at 0.5 → public feedback → 1.0.
- **3MF Core and its extensions are now ISO/IEC 25422:2025.** Anything added to the suite
  inherits that scrutiny.

**Implication:** the single largest blocker is not technical. It is that nobody has agreed
to sponsor this, and no IP position has been taken. Do that before polishing prose.

---

## 2. P0 — blocks any submission

| # | Item | Why it blocks | Effort |
| --- | --- | --- | --- |
| P0-1 | **Move to a namespace you control.** Change `schemas.3mf.io/…/bio/2026/07` to a URI on a domain you own | Squatting a Consortium namespace in a public repo is discourteous at best and will read as bad faith. It is currently the only thing in the repo that misrepresents its own status | Hours |
| P0-2 | **Decide the IP position.** If Route A is the goal, the contribution must be royalty-free-compatible. Confirm no employer or funder claim encumbers it | The Consortium's model is royalty-free patent commitments; an unclear position stops a submission dead | Legal review |
| P0-3 | **Read the four paywalled standards in full**: ASTM F3659-24, ISO/ASTM 52900:2021, ISO/ASTM 52902:2023, ISO 10993-1 | Currently cited from abstracts and published definitions. Titles and scope are reliable; **no clause requirements are asserted**, which is honest but not sufficient for a normative document that leans on them | ~£1,200 and a week |
| P0-4 | **Secure a working-group sponsor** (Route A) or **choose Route C** and say so | Route A cannot proceed without one | Weeks |
| P0-5 | **Produce one real, complete package** — see §4 | Every current example is a template or an illustration. A format for recording real data that has never recorded real data is untested where it matters most | 1 build + assays |

---

## 3. P1 — needed for a credible submission

| # | Item | Notes |
| --- | --- | --- |
| P1-1 | **Reference implementation in lib3mf** | Consortium adoption tracks implementations. A branch that reads and writes the extension is worth more than another draft |
| P1-2 | **Resolve `vol-attach-attribute`** | The mechanism by which an `<object>` attaches a `<v:volumedata>` resource is still unverified — the Volumetric spec is ~240 KB and could not be retrieved in full. Currently flagged, not guessed. A reviewer will notice |
| P1-3 | **Re-base `<b:toolpath>`** on the Consortium's machine-toolpath extension once it publishes | Shipping a parallel mechanism invites rejection |
| P1-4 | **Upgrade grade C/E references** | R15, R19, R37 rest on aggregators or unconfirmed attribution. R19's Z-number window is *contested between two conventions* and currently records both, which is right but needs a primary source |
| P1-5 | **Second independent implementation** | Two implementations from one author is one implementation. A third party parsing the corpus is the real interoperability evidence |
| P1-6 | **Decide the modality enumeration honestly** | Four modalities (acoustic droplet, magnetic levitation, spheroid bioassembly, in-situ) are enumerated with no parameter set and no evidence. Either fill them or **remove them**. Enumerating a modality you cannot specify is a promise the format does not keep |
| P1-7 | **CITATION.cff and a Zenodo DOI** | Needed before anyone can cite this in a paper |
| P1-8 | **Versioning and compatibility policy** | `b:SpecVersion` now exists and is required, but the repository states no policy on what a minor-version bump may break |

---

## 4. The data you actually need

This is the part that cannot be written. It has to be measured.

> **Now packaged as a worklist:** [`review/DATASET-SHEET.md`](review/DATASET-SHEET.md)
> generates this list from what is actually missing in each exemplar, with the current counts
> — 13 and 30 estimated parameters, 19 assay readings with no values.

### 4.1 One complete exemplar package — the minimum

The strongest possible artifact is **one construct, built once, recorded completely**. Not
fourteen templates. One real build, with every field populated from a real measurement,
reaching **Bio-Reproducible**. Concretely:

**Material**
- [ ] Synthesis record with **isolated yield** — currently open item `gelma-yield`, unreported anywhere in the consulted literature
- [ ] DS by ¹H-NMR **and** a colourimetric amine assay, with both raw spectra attached
- [ ] Certificate of analysis, real lot numbers, endotoxin figure with its assay
- [ ] Molecular weight distribution, with method

**Rheology** — currently blocking open item `gelma-rheology`
- [ ] Herschel–Bulkley or power-law constants at the printing temperature
- [ ] Raw flow curve and amplitude sweep as attached CSV
- [ ] Repeat at the working cell density, not cell-free

**Cells**
- [ ] Real ethics/IRB reference
- [ ] Donor age, sex, tissue bank record
- [ ] Cell Ontology and UBERON terms
- [ ] STR profile if a line; mycoplasma certificate; passage at print
- [ ] Serum lot number

**Process and calibration** — currently blocking `vol-dose-threshold`
- [ ] Dose test at the **working cell density**. A dose calibration on cell-free resin does not transfer, because scattering mean free path is inversely related to cell density
- [ ] Optical power at the vial, with the power meter's own calibration date
- [ ] Rotation speed, projection count, vial diameter from the machine job file
- [ ] Resin refractive index at the printing wavelength
- [ ] ISO/ASTM 52902 artefact printed **in the build resin**, measured
- [ ] Machine vendor, model, firmware, serial, calibration date

**Results** — currently blocking `results-placeholder`
- [ ] Post-print viability with replicate count and raw image data
- [ ] Compressive modulus from the test coupon printed in the same run
- [ ] At least one **failing** result against its acceptance criterion. A dossier containing only passes is not evidence that the acceptance criteria bite

**Toolpath**
- [ ] The real projection stack or G-code, with a checksum that verifies (rule T4 now checks this)

### 4.2 An independent reproduction

For Route B this is close to mandatory: a second laboratory receives the `.3mf` and rebuilds
the construct **from the package alone**. What they cannot reconstruct is the specification's
real gap list, and it will be more informative than any amount of internal review.

### 4.3 A negative corpus from the wild

Ten to twenty real packages from other groups, validated, with the resulting error and
warning distribution published. That tells you which rules are too strict to live with —
information no amount of self-testing produces.

---

## 5. What the red team found, and what it means

Fourteen adversarial packages were built to try to obtain a clean bill of health for garbage.
**Thirteen succeeded.** After hardening, six do — and the residual set is the interesting
part.

**Fixed in response** (rules U1–U3, D1–D2, C7–C8, T4, M1–M2): dimensionally wrong units, values
outside physical possibility, negative quantities, dates in the future, an item resolved
before it was raised, a *positive* mycoplasma result being silently accepted as satisfying the
requirement for a mycoplasma test, and — most embarrassingly — a toolpath checksum that
nothing verified, while `SECURITY.md` instructed implementers to verify it.

**Residual and unfixable by machine:** a real reference cited for an unrelated claim; an open
item "resolved" with a vacuous resolution; an acceptance criterion that cannot fail. These are
structurally perfect and semantically false, and no schema will ever catch them.

**This is now Chapter 12 of the specification** rather than a footnote, because a reviewer
will ask, and the honest answer is a strength: the format enforces well-formedness and
traceability, and directs human attention at the rest. A format claiming more would be lying.

---

## 6. Defects found by testing the untested

Three test artifacts were added during this pass. Each found something that the existing
thirty-five negative tests had not.

**The modality corpus** (`make_conformance_corpus.py`) generates a minimal *passing* package
per modality. Thirteen of fourteen modality rule sets had never been exercised by anything
expected to succeed. It immediately found:

1. `total_light_dose` was simultaneously **required** by P0 and constrained to
   `provenance="derived"` by P3 — a rule interaction no negative test can reveal.
2. A **three-way disagreement** between this specification's prose, the Python `REQUIRED`
   table and the Schematron over whether embedded extrusion inherits the base extrusion
   parameters. The prose was right. Fixed by making the table inherit, so the drift cannot
   recur.

**The round-trip test** (`roundtrip_test.py`) makes Chapter 7's preservation rule testable.
A lossy consumer drops 374 attributes from the example — **and the re-exported file still
validates.** That is the failure mode the rule exists to prevent, and it now has a
demonstration.

**The version marker.** There was none. A consumer could not tell which pre-1.0 draft it was
reading. `b:SpecVersion` is now required by both engines.

---

## 7. Honest status by area

| Area | State |
| --- | --- |
| Schema | Solid. Follows Consortium conventions, verified against the published Displacement Extension |
| Rule coverage | Strong. 35 faults, both engines, plus 14 positive modality templates |
| Evidence discipline | Strong, and it caught a real error — the LAP InChIKey published nearly everywhere is the wrong protonation state |
| Parameter dossier | Good breadth; several sources are grade C/E and need upgrading |
| Calibration | Structurally sound, **never exercised on real equipment** |
| Regulatory | Correct as a map. Not reviewed by anyone qualified. **Get a regulatory professional to read it before publishing** |
| Real data | **None.** The largest single gap |
| Interoperability | **Untested.** No second implementation, no third-party file |
| Governance | **Not started.** No sponsor, no IP position, no namespace you control |

---

## 8. A realistic path

**Now (days).** P0-1 namespace. P0-2 IP position. Add `CITATION.cff`. Remove or fill the four
unspecified modalities. Publish as a clearly-labelled public draft under your own namespace —
Route C.

**Next (1–2 months).** P0-3 buy and read the four standards; correct anything they contradict.
Run the exemplar build in §4.1. Get a regulatory professional to review the annex.

**Then (3–6 months).** lib3mf branch. Independent reproduction. Submit the paper — Route B.
Approach the working group with a draft, an implementation, a dataset and a paper — Route A.

**Do not** approach the Consortium with the current artifact. It is a good draft with no
implementation, no data, no sponsor, and a namespace it does not own. The technical work is
further along than the process work, and the process work is what gates it.

---

## 9. One thing worth keeping in view

The most valuable output of this project so far is not the schema. It is the discovery that a
widely-copied chemical identifier for a common bioprinting photoinitiator describes the wrong
species, found only because the format's own discipline forced the value to be checked rather
than copied.

That is the argument for the format, and it is worth leading with — in the paper, in the
README, and in any conversation with the working group. A format that makes people notice
things they would otherwise copy is doing the job. The schema is just how it does it.
