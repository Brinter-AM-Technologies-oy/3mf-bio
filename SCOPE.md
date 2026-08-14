# Scope: what this is, and what it deliberately is not

## The position

**This is an open, reusable schema for recording biofabrication work. It is not a standard,
and it does not certify anything.**

Those two sentences are the whole design philosophy, and everything below follows from them.

The format supplies **fields**. What goes in them, whether it is enough, and whether it
satisfies any particular standard or regulator is a judgement for the person filling them
in — against their own audit, their own product portfolio, their own roadmap. The format's
job is to make sure that when they make that judgement, the information they need is present
and its origin is recorded.

## Why not a standard

A standard needs an authority, a membership, a patent policy, and a committee. All of those
are useful eventually and all of them are gates *now*. The earlier plan spent its effort on
securing permission; this one spends it on being useful enough that people adopt it without
asking.

There is a real cost, and it should be stated: without an authority there is no forcing
function for interoperability, and a format can fragment into incompatible dialects. The
mitigation is that **the validators and the conformance corpus are the specification in
practice.** If a package passes `validate_bio.py` and `bio.sch`, it is conformant. Those
files are the arbiter, they are open, and anyone can run them. That is how a good many
formats have actually converged, standards body or not.

## What this means concretely

| The format does | The format does not |
| --- | --- |
| Provide a field for endotoxin, with its unit and assay | Assert an endotoxin limit |
| Require an `acceptance` criterion on every result | Say what the criterion should be |
| Record which regulatory framework was considered and **how the determination was reached** | Determine anything, or claim compliance |
| Require every number to declare its origin | Judge whether the origin is good enough |
| Reference ISO, ASTM and other standards as identifiers you may point at | Reproduce, interpret or certify against them |
| Check that a claim is well formed and internally consistent | Check that a claim is true |

`<b:regulatory>` therefore **stays**, and its value goes *up* under this positioning. A
manufacturer looking at the schema can see the fields their quality system will need to fill
and decide what to incorporate into their own process. That is exactly the "look at what you
need to incorporate" use the format is for. What is removed is any suggestion that filling
those fields constitutes compliance.

The same applies to `<b:calibration>`: it records that a test was run, against a criterion
the laboratory chose, with a result. It does not define acceptable calibration.

## Who it is for

**Researchers** — so a construct can be reproduced. Everything needed to rebuild it travels
in one file: the material and how it was made, the cells and their provenance, the machine
and its parameters, the calibration state, the maturation regime, and the assay timecourse.
The package is the methods section, in a form a machine can check.

**Manufacturers** — as a checklist of what a serious record contains. Not a compliance
artifact; a map of the fields a quality system tends to need, with the registry identifiers
already chosen (CAS, InChIKey, ChEBI, PubChem CID, Cellosaurus RRID, Cell Ontology, UBERON,
NCBI Taxonomy, DOI, UCUM).

**Tool authors** — a schema to read and write, with two reference validators, a conformance
corpus of one passing package per modality, and a round-trip test.

**Anyone** — reuse it, fork it, cut it down, embed it in a product, change the namespace,
build something incompatible. The licence permits all of that and no permission is required.

## The amalgam

The distinctive claim is narrow and, as far as we know, unoccupied: **this is the only place
where a CAS number and a G-code command map sit in the same file, under the same provenance
discipline.**

Engineering formats describe the machine and stop at the material boundary. Life-science
formats describe the biology and treat fabrication as a black box. A bioprinted construct is
not describable by either alone, because the thing that determines whether it works is the
*interaction*: nozzle geometry acting on a shear-sensitive cell suspension, light dose
interacting with a scattering that depends on cell density, a perfusion flow rate that is
simultaneously a mass-transport parameter and a differentiation cue.

That is why the schema carries substance synthesis routes next to toolpath checksums, and
why a `<b:param>` for wall shear stress and a `<b:param>` for passage number are the same
element with the same provenance requirement.

## Scope, in and out

**In scope**
- Materials: identity, synthesis route, yield, verification assay, grade, hazard
- Cells: origin, authentication, culture, passage, differentiation
- Formulations: composition, cell loading, crosslinking, rheology
- Process: 20 modalities with parameter sets, heads and nozzles, environment, toolpath
- Calibration: dated events with criteria and outcomes
- **Maturation: staged culture, bioreactors, stimulation regimes, media schedules**
- **Characterization: what you measured on the construct, and when**
- Evidence: graded references bound to the values that rest on them
- Open items: what is not known, as data
- Regulatory context: as a record of consideration, never as a claim

**Out of scope, permanently**
- Acceptance thresholds of any kind
- Compliance determination
- Reproducing standards text
- Certifying, endorsing or approving anything
- Judging whether a record is *good*, as opposed to *complete and internally consistent*

**Out of scope, for now**
- Modalities with no assembled evidence base (acoustic droplet ejection, magnetic
  levitation, spheroid bioassembly, in-situ) — enumerated but unspecified, and honestly
  labelled as such
- Serial measurement of a graded volumetric field over a timecourse
- A GUI or authoring tool

## On relationship to 3MF

The schema follows 3MF Consortium conventions closely and deliberately: `CT_`/`ST_` naming,
resource IDs, property groups, OPC packaging, extension of `<object>` by namespaced
attributes. A package produced by this extension is a valid 3MF package, and a 3MF reader
that ignores unknown namespaces will read the geometry correctly.

**It is not a 3MF Consortium extension**, has not been submitted to them, and uses a
namespace that is not theirs — `https://3mfbio.com/ns/bio/2026/07`, a URN precisely because it squats on
nobody's domain. Use `spec/set_namespace.py` to change it to something you control.

Following their conventions is a compatibility decision and a compliment, not a claim of
affiliation. If the Consortium ever wants this, the conventions mean the conversation starts
from a familiar shape. Until then, nothing is waiting on them.
