# Fact-Check Record

Every load-bearing factual claim made across the development of this extension, re-checked
against primary or registry sources, with a verdict. Written so a reviewer can disagree
with a specific line rather than with the document as a whole.

**Verdicts:** ✅ confirmed · ⚠️ confirmed with a caveat · ❌ was wrong, now corrected ·
🔍 could not be confirmed, recorded as an open item.

---

## 1. Corrections — things that were wrong or unverified and are now fixed

### ❌ → ✅ The LAP InChIKey

**Earlier state.** The `inchikey` attribute was left empty with the note "not confirmed
from a primary registry", and `References.md` carried a caveat.

**What was found.** The InChIKey most widely reproduced by chemical aggregators for
CAS 85073-19-4 is `CVDUWYDMNPODNA-UHFFFAOYSA-N`. That key **does not correspond to the
formula those same vendors state for the product.** Its final block is `-N`, denoting the
neutral species, and it derives from an InChI of composition `C16H17O3P.Li.H` — the free
phosphinic acid plus lithium hydride, not the lithium salt.

**Resolution.** Computed from the isomeric SMILES published for PubChem CID 68384915:

```
SMILES    [Li+].CC1=CC(=C(C(=C1)C)C(=O)P(=O)(C2=CC=CC=C2)[O-])C
formula   C16H16LiO3P                          (matches the vendor-stated formula)
InChI     InChI=1S/C16H17O3P.Li/c1-11-9-12(2)15(13(3)10-11)16(17)20(18,19)
          14-7-5-4-6-8-14;/h4-10H,1-3H3,(H,18,19);/q;+1/p-1
InChIKey  JUYQFRXNMVWASF-UHFFFAOYSA-M          ← correct for the salt
```

**Cross-check.** The computed InChI string matches, character for character, the InChI
published independently by two registry aggregators (BOC Sciences, Watson International).
The `-M` suffix denotes the deprotonated species, consistent with the salt.

Recorded in the example as resolved open item `lap-inchikey`. This is the clearest
vindication of the provenance discipline in the whole project: a value copied without
checking would have been wrong, and wrong in a way that silently identifies a different
chemical species.

### 🔍 → ✅ ISO/ASTM 52900 process categories

**Earlier state.** Gap #7 in `References.md`: "a crosswalk to ISO/ASTM 52900 terminology for
the AM process categories" was listed as not covered.

**Now confirmed.** ISO/ASTM 52900:2021 classifies AM into **seven** process categories with
abbreviations, and carries a **normative Annex A** for identifying processes within a
category. Definitions seen directly: vat photopolymerization (**VPP**) — a process in which
liquid photopolymer in a vat is selectively cured by light-activated polymerization; powder
bed fusion (**PBF**); sheet lamination (**SHL**); material jetting — droplets of feedstock
material selectively deposited; material extrusion. Binder jetting and directed energy
deposition complete the seven.

Implemented as the `iso52900` attribute on `<b:process>`, with validator rule N1 checking
the mapping. The mapping is **many-to-one and informative**: bio modalities are finer than
52900, and modalities whose category is genuinely arguable (melt electrowriting,
electrospinning, magnetic levitation, spheroid bioassembly) are left unmapped rather than
forced.

### ⚠️ Corrected framing: "the volumetric extension is pre-release"

**Earlier state.** Described as a "pre-release volumetric design extension."

**Correction.** The extension was announced at version 0.5 in November 2021 with a call for
public feedback before 1.0. Its namespace `http://schemas.3mf.io/3dmanufacturing/volumetric/2022/01`
is in production use — it appears in exported files from at least one open-source CAD tool
via lib3mf, alongside `http://schemas.3mf.io/3dmanufacturing/implicit/2023/12`. "Pre-release"
understated its deployment. The namespace used in this extension's example is confirmed
correct.

---

## 2. Confirmed claims

### ✅ 3MF is now an ISO/IEC standard
**ISO/IEC 25422:2025**, *Information technology — 3D Manufacturing Format (3MF)
specification suite*, first edition, June 2025, status Published. Defines the Core
Specification and extensions. Raises the bar for any proposed addition, and is recorded as
blocking open item `namespace-unregistered`.

### ✅ 3MF namespaces and schema conventions
Core: `http://schemas.microsoft.com/3dmanufacturing/core/2015/02`. Newer extensions moved to
`schemas.3mf.io` — displacement `/displacement/2023/10`, volumetric `/volumetric/2022/01`,
implicit `/implicit/2023/12`. Schema conventions verified directly against the published
Displacement Extension XSD: `elementFormDefault="unqualified"`,
`attributeFormDefault="unqualified"`, `blockDefault="#all"`, `CT_`/`ST_` naming, globals
referenced by `ref`, `xs:anyAttribute namespace="##other"` on every complex type,
`CT_Resources` redefined with a choice, `maxOccurs="2147483647"`.

### ✅ ST_ResourceID and ST_ResourceIndex definitions
`ST_ResourceID` is `xs:positiveInteger` with `maxExclusive="2147483648"`;
`ST_ResourceIndex` is `xs:nonNegativeInteger` with the same bound. Copied verbatim from the
Displacement Extension schema, not reconstructed.

### ✅ Required-extension semantics
Confirmed by the Displacement Extension's own reasoning: because it declares a different
type of object, a package using it "MUST enlist the 3MF Displacement Extension as
'required extension'". The Beam Lattice Extension shows the converse — a producer SHOULD
NOT mark an extension required when the file does not contain the feature. This extension
follows the same rule for cell-laden material.

### ✅ Volumetric extension carries fields, not meanings
`<v:volumedata>` is a resource; `<v:property>` children are driven by `functionid` and
`channel`; the referenced function must have appropriate input and output types;
`<v:functionfromimage3d>` maps an image stack; `<levelset>` uses a function with scalar
output. Nothing in it carries units, admissible range or provenance — which is the gap
`<b:fieldbinding>` fills.

### ✅ ISO/ASTM 52902 covers calibration, not only assessment
ISO/ASTM 52902:2023 (superseding 2019) — *Test artefacts — Geometric capability assessment
of additive manufacturing systems*. Explicitly serves two purposes: capability assessment
**and calibration** of the AM system. Describes a suite of benchmark test geometries,
prescribes quantities and qualities to be measured, does **not** dictate measurement
methods, and defers specimen procedure and machine settings to **ASTM F2971**.

### ✅ ASTM F3659-24 scope
*Standard Guide for Bioinks Used in Bioprinting*, ASTM International 2024, Committee
F04.42, 20 pp. Covers pre-printing, printing and post-print stabilisation, sterility and
cytocompatibility including post-printing viability. Cross-references Guide F2150, Guide
F2027 and the ISO 10993 series.

### ✅ US regulatory structure
21 CFR Part 1271 rests on **PHS Act §361** authority to prevent communicable disease spread.
Some HCT/Ps are regulated **solely** under Part 1271; others under Part 1271 *and* premarket
and postmarket device, drug or biologics regulation. More-than-minimally-manipulated HCT/Ps
go through the biologics system via **PHS Act §351**. "Minimal manipulation" for cells or
nonstructural tissues means processing that does not alter biological characteristics.
**CBER** for biologics, **CDRH** for devices. **cGTP** (21 CFR 1271 subpart D) governs
methods, facilities, controls, recordkeeping and quality programme. **RMAT** designation
created 2016.

### ✅ EU regulatory structure
**Regulation (EC) No 1394/2007** on ATMPs, in force 30 December 2008; defines ATMPs, their
authorisation, supervision and monitoring. **Combined ATMP** at **Article 2(1)(d)** — a
substantially manipulated cell product presented for tissue regeneration containing integral
scaffold material that fulfils a device function. The combined-ATMP route applies unless the
cell/tissue component is non-viable and ancillary to the device. Premarket review delegated
to the **Committee for Advanced Therapies (CAT)**. Supporting: Directive 2009/120/EC,
Regulation (EC) No 726/2004, and Regulation (EU) 2017/745 for the device component.

### ✅ Australian pathway
Tissue-engineered products regulated under the biologicals framework, typically **Class 3
or Class 4** depending on manipulation and risk; compliance with the **ARGB** and inclusion
in the **ARTG** required before supply.

### ✅ Printability calibration metrics
**Pr value** — the printability index derived from the circularity of the area enclosed by
grid holes, equal to 1 for a perfect square pore, i.e. ideal gelation (Ouyang et al.,
*Biofabrication*). Under-gelation produces extrudate swell, filament swelling and rounded
pores; over-gelation produces irregular, lumpy extrusion and unpredictable pore geometry.
**Filament collapse test** — deflection angle as a function of half-gap distance, with a
model based on the equilibrium between gravitational force on the filament and its
resistance to deformation. **Filament fusion test** — filament distance, filament thickness
and fused filament length. Both from the shape-fidelity literature.

### ✅ LAP identity, other than the InChIKey
CAS 85073-19-4; IUPAC lithium phenyl-2,4,6-trimethylbenzoylphosphinate; formula
C16H16LiO3P; MW 294.21; PubChem CID 68384915. Preferred over Irgacure 2959 for biological
use on water solubility, polymerisation rate at 365 nm, and absorbance at 400 nm permitting
visible-light polymerisation — enabling encapsulation at lower initiator concentration and
longer wavelength.

---

## 3. Standing caveats

### ⚠️ Z-number window for inkjet printability
Two conventions circulate. An aggregator entry gives a stable-drop window of Z between 1 and
10. A separate treatment bounds the regime jointly in (Z, We) space with 2 < We_jet < 25 —
lower bound where capillary forces prevent ejection, upper bound at satellite-drop onset.
**These are not the same claim.** The dossier records both and requires the convention used
to be stated. Not resolvable by picking one.

### ⚠️ Reference R19 attribution
Retrieved via a secondary index; full author and venue attribution not confirmed. Marked
grade C and flagged in `References.md`. Verify before formal citation.

### ⚠️ Reference R37 attribution
Same situation — MEW scaffold design-parameter sweep, retrieved via secondary index, marked
grade C.

### ⚠️ Grade E sources are aggregators
R15 (drop-on-demand topic entry) and R44 (LAP vendor pages) are not primary literature. R44's
chemical identity is corroborated across four independent vendors plus PubChem, so the CAS,
formula and MW are solid; its InChIKey was not, as §1 records.

---

## 4. Could not be confirmed — now tracked as open items

| Open item key | Claim | Why unresolved |
|---|---|---|
| `vol-attach-attribute` | The attribute by which a core `<object>` attaches a `<v:volumedata>` resource | The Volumetric Extension specification is ~240 KB and its raw text could not be retrieved; the rendered page returned navigation chrome only. The example flags the attachment rather than guessing it |
| `gelma-yield` | Isolated yield for one-pot GelMA methacryloylation | Widely performed, apparently not reported in the consulted literature |
| `endotoxin-threshold` | Endotoxin limits for bioprinting-grade polymers | Application- and jurisdiction-specific; no general threshold exists to cite |
| `modality-evidence-thin` | Parameter sets for acoustic droplet ejection, magnetic levitation, spheroid bioassembly, in-situ printing | Enumerations exist; the evidence base was not assembled |

---

## 5. Method

Claims were checked against, in order of preference: the primary specification or standard
text; the publisher's own record (ISO Online Browsing Platform, ASTM, PubChem); then two or
more independent secondary sources agreeing. Where only aggregators were available, the
entry is graded E and says so.

Chemical structure verification used RDKit with the InChI toolkit, computing the InChIKey
from a published SMILES and comparing the intermediate InChI string against independent
registry listings — the comparison, not the computation, is what makes it evidence.

**What was not done.** No paywalled standard was read in full; ASTM F3659-24, ISO/ASTM
52900:2021, ISO/ASTM 52902:2023, ISO 10993 and ISO/IEC 25422:2025 are cited from their
abstracts, tables of contents, published definitions and secondary descriptions. Scope and
titles are reliable; specific clause requirements are not quoted, and none are asserted.
