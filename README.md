[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21939414.svg)](https://doi.org/10.5281/zenodo.21939414)
# 3MF Bio Extension

**An open schema for recording biofabrication work end to end — material synthesis, cells,
formulation, print process, calibration, maturation and characterization — in a single file,
with every number declaring where it came from.**

Built on 3MF so the geometry stays readable by ordinary 3D-printing tools.

> **This is not a standard and it certifies nothing.** It supplies fields; what goes in them
> and whether that satisfies your auditor is your judgement. Not affiliated with the 3MF
> Consortium. See [SCOPE.md](SCOPE.md).

**Licence: BSD-2 / CC-BY-4.0. Fork it, cut it down, embed it, change the namespace. No
permission required.**

---

## The idea in one paragraph

Engineering formats describe the machine and stop at the material boundary. Life-science
formats describe the biology and treat fabrication as a black box. A bioprinted construct is
describable by neither alone, because what decides whether it works is the *interaction* —
nozzle geometry acting on a shear-sensitive cell suspension, light dose against a scattering
that depends on cell density, a perfusion rate that is simultaneously mass transport and a
differentiation cue. This schema is the amalgam: **the only place a CAS number and a G-code
command map sit in the same file under the same discipline.** That discipline is one rule:

> **Every numeric parameter must declare where its value came from.**

Fabricating a number requires explicitly labelling it `estimated` — which a reviewer, a
release gate, or a CI job can filter on. And every `estimated` value must be owned by an
open item that says what would close it.

## Try it on your own mesh

You have an STL. Three commands and you have a package with a dossier:

```bash
python3 tools/questionnaire.py --profile brinter                    # what heads exist
python3 tools/questionnaire.py --profile brinter --head pneuma-pro --format template > answers.json
# fill in what you know, leave the rest null
python3 tools/integrate.py answers.json --mesh part.stl --out mybuild/ --zip mybuild.3mf
```

Then open [`tools/viewer.html`](tools/viewer.html) in a browser and drop the `.3mf` on it.
No install, no server, nothing uploaded.

**The integrator never refuses to emit.** Anything you leave blank becomes a tracked open
item naming what would close it — because a recorded gap beats an invented number, and a
tool that demands forty fields before producing output does not get used.

**The viewer leads with a run sheet, not a 3D preview.** An ordered operator checklist built
from the package, with constraints attached where they bite: a contaminated mycoplasma result
appears at *prepare cells* and says do not proceed. Without a standards body, that red banner
is the enforcement mechanism.

See [tools/README.md](tools/README.md).

## Quick start

```bash
pip install lxml

python3 spec/validate_schema.py    examples             # XSD structure
python3 spec/validate_bio.py       examples             # all rules, incl. cross-part
python3 spec/validate_bio.py       examples-extrusion   # the deposition exemplar
python3 spec/conformance_tests.py             # 42 injected faults, both engines
python3 spec/make_conformance_corpus.py       # one passing package per modality
python3 spec/roundtrip_test.py                # Chapter 7 preservation rule
python3 spec/redteam_tests.py                 # packages that break no rule and are garbage
python3 tools/test_tools.py                   # integrator round-trip
```

`validate_bio.py` accepts an unpacked directory or a `.3mf` zip. Flags: `--strict`
(warnings become errors), `--release` (fail on any `estimated` value).

**Current state:** both exemplars valid against the XSD with 0 errors ·
**54/54 faults caught by the Python validator, 49/49 by Schematron** · 15/15 modality
templates pass in both engines · round-trip preservation demonstrated.

Read [SCOPE.md](SCOPE.md) for what this is and is not. [SUBMISSION.md](SUBMISSION.md)
records a red-team pass and the honest gap list — chiefly that **no real dataset has been
recorded in it yet**, which is the one thing the authors cannot supply alone.

## What is in a package

| Resource | Carries |
| --- | --- |
| `<b:evidence>` | Literature and standards, graded A–F, with DOIs |
| `<b:substances>` | Materials, with synthesis route → conditions → **yield** → verification assay |
| `<b:cellpopulations>` | Cells: origin, RRID, authentication, culture, passage at print |
| `<b:bioinkgroup>` | Formulations — a **property group**, assigned via core `pid`/`pindex` |
| `<b:process>` | Machine, modality-typed parameters, environment, toolpath + checksum |
| `<b:calibration>` | Dated calibration events with acceptance criteria and outcomes |
| `<b:regulatory>` | Jurisdiction-mapped determination, translatable across regimes |
| `<b:openitems>` | **What is not known** — as data, not comments |
| `<b:printheads>` | Deposition heads: drive, nozzle, coaxial channels, loaded formulation |
| `<b:maturation>` | Staged post-print culture: bioreactors, stimulation regimes, media schedules |
| `<b:characterization>` | What you measured on the construct, and when |
| `<b:fieldbinding>` | Meaning and provenance of a volumetric property field |
| `<b:protocol>`, `<b:results>` | Procedures and measured outcomes with acceptance criteria |

Twenty modalities. **Extrusion and deposition get the deepest treatment**, since they are
what most laboratories actually use: five sub-modalities (pneumatic, piston, screw, embedded,
coaxial), a printhead resource for multi-head builds, core–shell channel modelling, and the
only fully specified derivation chain in the format.

Two exemplar packages ship: `examples/` (volumetric tomographic) and `examples-extrusion/`
(three-head deposition with a coaxial vascular head).

## Four design decisions worth arguing about

**Unknowns are first-class records.** A `TODO` comment is lost on round-trip, cannot be
counted, filtered, assigned or closed. `<b:openitem>` has a `kind`, a `severity`, an
`action` that would close it, an owner, and `<b:affects>` links to the exact parameters it
touches. Every gap accumulated while building this is in the example package as data.

**Calibration is an event, not an attribute.** A parameter is what you set; a calibration
test is the independent measurement saying the setting means what you think. Tests bind to
a printed artefact object, so the coupon that evidenced the calibration is part of the same
build record.

**No acceptance thresholds are asserted. Anywhere.** No viability floor, no endotoxin
limit, no dimensional tolerance. Those are application- and jurisdiction-specific, and
asserting one would be exactly the invention this format exists to prevent. `acceptance` is
a *required* attribute so each lab states its own and is held to it.

**The controlled variable follows the drive.** A pneumatic head commands a pressure; a
piston or screw commands a displacement. Requiring `extrusion_pressure` from a piston system
is a category error, so the modality vocabulary splits and the required sets diverge.

**A derived value must have its inputs.** Wall shear stress is τ_w = ΔP·R/(2L) with the
rheology supplying the velocity profile — so `nozzle_length` is *required* for extrusion, and
Rule X1 rejects a declared shear stress whose inputs are absent. A guess wearing a `derived`
label is worse than an honest estimate.

**A printed construct is not the product; the matured construct is.** Everything up to the
print is about a day of work. `<b:maturation>` covers the three weeks after it, where most
of the biology happens — and `<b:characterization>` records assays as readings over a
timecourse, because "viability was 92% at day 1 and 74% at day 21" is the shape of the
information that decides whether a construct works, and a single-valued result cannot say it.

**Volumetric carries the field; bio carries its meaning.** No new field mechanism was
invented. The 3MF Volumetric Extension already has one; `<b:fieldbinding>` supplies only
what it cannot — quantity, units, admissible range, provenance.

## How it follows 3MF

| Convention | Conformance |
| --- | --- |
| Namespace | `https://3mfbio.com/ns/bio/2026/07`, matching the displacement extension's pattern |
| Resources | In `<resources>` in the 3D Model part, not a side-car file |
| IDs | `ST_ResourceID` positive integers, unique across core and all extensions |
| Groups | Children form implicit 0-based indices, referenced by `ST_ResourceIndex` |
| Property binding | `<b:bioinkgroup>` is a property group — core `pid`/`pindex`, no bespoke attribute |
| Schema | `CT_`/`ST_` naming, unqualified forms, `blockDefault="#all"`, globals by `ref`, `anyAttribute namespace="##other"`, `CT_Resources` redefined with a choice |
| Required extension | A package encoding living material MUST enlist bio as required |
| External parts | `ST_UriReference`, and MUST be relationship targets from the model part |
| Vocabulary | `iso52900` crosswalk to the seven ISO/ASTM 52900:2021 process categories |

## Repository layout

```
spec/
  3MF Bio Extension.md      specification, in Consortium document structure
  bio.xsd                   canonical schema
  bio.libxml.xsd            generated variant for libxml2 toolchains (see below)
  bio.sch                   ISO Schematron - every intra-document rule
  validate_bio.py           reference validator - all rules
  validate_schema.py        XSD structural validation
  conformance_tests.py      fault injection through both engines
dossier/
  Parameter-Dossier.md      per-modality parameters, with sources
  Calibration-Dossier.md    per-modality calibration tests, with sources
  Regulatory-Annex.md       jurisdiction map and standards
  References.md             bibliography, graded, saying what each source supports
  Fact-Check.md             every claim re-checked, with verdicts and corrections
examples/                   volumetric tomographic exemplar
examples-extrusion/         three-head deposition exemplar, with maturation
tools/
  questionnaire.py          question set, generated FROM the rule tables
  integrate.py              STL/OBJ + answers -> validating package
  viewer.html               run sheet, open items, dossier, maturation, geometry
  machine_profiles/         vendor profiles; brinter.json is the first
site/
  build_site.py             static site for 3mfbio.com; markdown in, HTML out
```

## Two validators, and why

Schematron validates one XML document, so it covers every intra-document rule and runs
anywhere XSLT does, with no Python dependency. It **cannot** express whether a referenced
part exists, whether it is an OPC relationship target, or whether a reference key matches
the CSL-JSON bibliography — those are properties of the *package*. Those three stay
procedural, and the split is documented in the header of `bio.sch` rather than papered over.

The Schematron is XPath 1.0, since the reference runner compiles to XSLT 1.0.
Bounds-checking a whitespace-separated `evindices` list is therefore done only for the
single-index case, with Python checking every index. A rule that silently half-fires is
worse than one that declares its scope.

## Findings from building this

**The LAP InChIKey is wrong nearly everywhere it is published.** The key aggregators list
for CAS 85073-19-4, `CVDUWYDMNPODNA-UHFFFAOYSA-N`, is the *neutral* species and does not
match the salt formula those same vendors state. Correct for the salt is
`JUYQFRXNMVWASF-UHFFFAOYSA-M` — verified by computing the InChI from PubChem CID 68384915's
SMILES and matching it against two independent registry listings. A value copied without
checking would have identified a different chemical species.
([Fact-Check §1](dossier/Fact-Check.md))

**A validator can check that a claim is well formed. It cannot check that it is true.**
Fifteen adversarial packages were built to obtain a clean bill of health for garbage;
thirteen succeeded. Hardening cut that to six, and the residual six — a real reference cited
for an unrelated claim, an open item "resolved" with vacuous text, an acceptance criterion
that cannot fail — are structurally perfect and semantically false. No schema will ever catch
them. That boundary is now Chapter 12 of the specification rather than a footnote.

**Testing only for failure hides defects.** Thirteen of fourteen modality rule sets had never
been exercised by a package expected to *pass*. Generating one immediately found a parameter
that was simultaneously required and forbidden, and a three-way disagreement between the spec
prose and both reference implementations.

**Schematron's first-match rule is a live trap.** Within a `<sch:pattern>` only the first
matching `<sch:rule>` fires for a node. Three rules here were silently dead — they compiled
fine and validated the good file fine and caught nothing. Only fault injection exposed them.

**libxml2 cannot parse Consortium schemas verbatim.** 3MF uses `maxOccurs="2147483647"`,
which is valid XSD, but libxml2's internal UNBOUNDED sentinel is 2³⁰ and it rejects the
literal. Anyone validating 3MF with lxml or xmllint hits this. Hence `bio.libxml.xsd`.

**"Declared but unknown" must be expressible.** An absent yield and an unmeasured yield are
different claims, so constrained types union with the empty string: an empty attribute means
*declared, not yet known*; an absent one means *not applicable*.

## Status and open items

Four blocking items are open in the example package, deliberately — it demonstrates the
mechanism rather than pretending completeness. The one that matters for adoption:

- **`namespace-unregistered`** — the namespace, relationship types and content types need
  registration with the 3MF Consortium. 3MF Core is now **ISO/IEC 25422:2025**, which raises
  the bar for any proposed addition.

Others: re-base `<b:toolpath>` on the Consortium's machine-toolpath extension once it
publishes; confirm how an `<object>` attaches a `<v:volumedata>` resource; assemble evidence
for the thin modalities (acoustic droplet ejection, magnetic levitation, spheroid
bioassembly, in-situ); represent field measurement over a culture timecourse.

Run `python3 spec/validate_bio.py examples` to see the current list.

## Standards and regulatory posture

The schema carries a `<b:regulatory>` resource and references ISO, ASTM and other standards
as identifiers. **It asserts no compliance and defines no thresholds** — no viability floor,
no endotoxin limit, no dimensional tolerance. `acceptance` is a *required* attribute
precisely so each laboratory states its own and is held to it, and `determination` records
*how* a regulatory classification was reached rather than computing one.

If you have an audit to satisfy, the fields are there to fill against your own criteria and
your own roadmap. That is the intended use. Filling them is not compliance, and this project
will never claim otherwise.

## Verify everything

```bash
python3 verify.py
```

15 automated checks, the outstanding blocker list, and the known gaps — one command, so
"fully checked" is something you run rather than something you are told. Currently **15/15
passing**.

[PUBLISH.md](PUBLISH.md) is the whole path from here to a live site with a DOI, and
[ZENODO.md](ZENODO.md) covers the DOI specifically.
[GUI-PUBLISH.md](GUI-PUBLISH.md) is the same path using only GitHub Desktop and a browser,
with no command line.

## Two things needing outside eyes

Everything else here is machine-checked. These two cannot be, and both are packaged as
concrete worklists in [`review/`](review/):

- **[Regulatory review](review/REGULATORY-REVIEW.md)** — 16 numbered factual claims, 7
  questions about whether the schema's vocabularies are the right ones, and 5 on whether the
  posture is safe. Two claims rest on grade-E sources and two are our own inference; all four
  are flagged. 2–3 hours for someone qualified.
- **[Dataset collection sheet](review/DATASET-SHEET.md)** — exactly which values would turn a
  template into a real record. **No real measurement has ever been recorded in this schema**,
  so the one untested thing is whether the fields are the right fields when you have data in
  front of you.

## Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md). The short version: **nothing gets a number without
a source**, and a new rule needs a negative test in `conformance_tests.py` — three rules
here were silently dead until fault injection found them.

Fact-check challenges are welcome and have their own issue template. One correction is
already in the changelog.

## Versioning

Pre-1.0. **Minor versions may change the schema in ways that invalidate existing packages.**
Every package declares `<metadata name="b:SpecVersion">` so a consumer can tell what it is
reading, and the validator warns on a mismatch. From 1.0, minor versions will be additive
only.

## Hosting

The site at [3mfbio.com](https://3mfbio.com) is built from this repository by
`site/build_site.py` and deployed by `.github/workflows/pages.yml`. The namespace URI
`https://3mfbio.com/ns/bio/2026/07` resolves and serves the schema, because a namespace that
404s is a broken promise.

```bash
pip install markdown lxml
python3 site/build_site.py --serve      # http://localhost:8000
```

See [DEPLOY.md](DEPLOY.md) for DNS, Pages setup, and how to move the namespace if you fork.

**Forking?** `python3 tools/setup_repo.py` sets the repository slug, copyright holder,
citation authors and security channel in one pass, then
`python3 spec/set_namespace.py <your-uri>` moves the namespace.

## Licence

BSD 2-Clause for code and schemas; specification prose and dossiers additionally CC BY 4.0.
See [LICENSE](LICENSE). Cited standards remain the copyright of their publishers.
