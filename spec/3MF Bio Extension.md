# 3MF Bio Extension

## Specification & Reference Guide

| **Version** | 0.9.0 (working draft)                                        |
| ----------- | ------------------------------------------------------------ |
| **Status**  | Open schema. Not a standard; not a 3MF Consortium specification. |

> **Notice.** This document imitates the structure, language and schema conventions of the
> published 3MF extension specifications so that it could be evaluated as a candidate
> extension. It has not been submitted to, reviewed by, or endorsed by the 3MF Consortium.
> The namespace URI follows the Consortium's pattern but is **not registered**, and MUST be
> changed if this is deployed outside evaluation.

## Disclaimer

THESE MATERIALS ARE PROVIDED "AS IS." The contributors expressly disclaim any warranties
(express, implied, or otherwise), including implied warranties of merchantability,
non-infringement, fitness for a particular purpose, or title, related to the materials.
The entire risk as to implementing or otherwise using the materials is assumed by the
implementer and user.

## Table of Contents

- [Preface](#preface)
  * [About this Specification](#about-this-specification)
  * [Document Conventions](#document-conventions)
  * [Language Notes](#language-notes)
  * [Software Conformance](#software-conformance)
- [Part I: 3MF Documents](#part-i-3mf-documents)
  * [Chapter 1. Overview of Additions](#chapter-1-overview-of-additions)
  * [Chapter 2. Evidence and Parameters](#chapter-2-evidence-and-parameters)
  * [Chapter 3. Resources](#chapter-3-resources)
  * [Chapter 4. Object and Item](#chapter-4-object-and-item)
  * [Chapter 5. Modality Parameter Sets](#chapter-5-modality-parameter-sets)
  * [Chapter 6. Package Parts and Relationships](#chapter-6-package-parts-and-relationships)
  * [Chapter 6a. Graded Properties and the Volumetric Extension](#chapter-6a-graded-properties-and-the-volumetric-extension)
  * [Chapter 7. Usage Rules](#chapter-7-usage-rules)
  * [Chapter 8. Open Items](#chapter-8-open-items)
  * [Chapter 8a. Deposition Heads](#chapter-8a-deposition-heads)
  * [Chapter 8b. Maturation and Characterization](#chapter-8b-maturation-and-characterization)
  * [Chapter 9. Calibration](#chapter-9-calibration)
  * [Chapter 10. Regulatory Context and Translation](#chapter-10-regulatory-context-and-translation)
  * [Chapter 11. Conformance](#chapter-11-conformance)
  * [Chapter 12. Threat Model](#chapter-12-threat-model)
- [Part II. Appendices](#part-ii-appendices)
  * [Appendix A. Glossary](#appendix-a-glossary)
  * [Appendix B. 3MF XSD Schema](#appendix-b-3mf-xsd-schema)
  * [Appendix C. Standard Namespace and Content Types](#appendix-c-standard-namespace-and-content-types)
  * [Appendix D. Example File](#appendix-d-example-file)
  * [Appendix E. Rule Index](#appendix-e-rule-index)
- [References](#references)

---

# Preface

## About this Specification

This 3MF bio specification is an extension to the core 3MF specification. This document
cannot stand alone and only applies as an addendum to the core 3MF specification. Usage of
this and any other 3MF extensions follows an a la carte model, defined in the core 3MF
specification.

Part I, "3MF Documents," presents the details of the XML markup added by this extension.
Part II, "Appendices," contains the schema, namespace and example material.

This extension MUST be used only with Core specification 1.x.

## Document Conventions

See the 3MF Core Specification conventions.

In this extension specification, as an example, the prefix "b" maps to the xml-namespace
`https://3mfbio.com/ns/bio/2026/07`, and the prefix "v" maps to
`http://schemas.3mf.io/3dmanufacturing/volumetric/2022/01` as defined by the 3MF Volumetric
Extension. See Appendix C.

Units are expressed as **UCUM** codes in the `unit` attribute (`Cel`, `kPa`, `mW/cm2`,
`%{w/v}`, `1` for dimensionless). Model geometry units remain those of the core `<model>`
element; the `unit` attribute applies only to `<b:param>` and its siblings.

## Language Notes

See the 3MF Core Specification language notes.

## Software Conformance

See the 3MF Core Specification software conformance, plus Chapter 8 of this document.

---

# Part I: 3MF Documents

# Chapter 1. Overview of Additions

The core specification and its published extensions describe what to build and, through the
production and slice extensions, how a build is organised. They cannot describe *what the
built thing is made of biologically*, *how the material came to exist*, or *what evidence
supports any of the values used*. For a plastic bracket that is a reasonable omission. For
a cell-laden construct it is not: the same geometry printed from a different cell passage,
a different photoinitiator concentration, or a different degree of substitution is a
different product.

This extension adds seven non-object resources and two attributes to existing elements.

**Resources**

| Element | Kind | Purpose |
| --- | --- | --- |
| `<b:evidence>` | group | Literature and standards that parameters cite |
| `<b:substances>` | group | Chemical and biological raw materials, with synthesis records |
| `<b:cellpopulations>` | group | Cells, their provenance, authentication and culture |
| `<b:bioinkgroup>` | **property group** | Printable formulations, referenceable by `pid`/`pindex` |
| `<b:process>` | resource | Machine, modality-typed parameters, environment, toolpath |
| `<b:protocol>` | resource | Pre-print, print, post-print, culture and assay procedures |
| `<b:results>` | group | Measured outcomes with acceptance criteria |
| `<b:fieldbinding>` | resource | Meaning, units and provenance of a volumetric property field |
| `<b:calibration>` | resource | A dated calibration event with per-test acceptance and outcome |
| `<b:regulatory>` | resource | Jurisdiction-mapped regulatory determination |
| `<b:openitems>` | group | What is not known, as data rather than as comments |
| `<b:printheads>` | group | Deposition heads: drive, nozzle, coaxial channels, loaded formulation |
| `<b:maturation>` | resource | Staged post-print culture, bioreactors, stimulation, media |
| `<b:characterization>` | resource | What you measured on the construct, and when |

**Element extensions**

| Element | Added attributes |
| --- | --- |
| `<object>` | `b:processid`, `b:regionrole`, `b:printheadid`, `b:printheadindex` |
| `<item>` | `b:processid` |
| `<b:process>` | `iso52900`, `calibrationid`, `regulatoryid` |

`<b:bioinkgroup>` is deliberately a **property group** in the core sense. Assigning a
formulation to geometry therefore uses the existing `pid`/`pindex` mechanism on `<object>`
and the existing `pid`/`p1`/`p2`/`p3` mechanism on `<triangle>` — no bespoke attribute is
introduced. A construct with a cell-laden parenchyma and an acellular vascular ink is
expressed exactly as a two-material part already is.

Because this extension changes what the object *is* rather than merely annotating it, a
package that encodes cells, live material, or any parameter affecting biological outcome
MUST enlist the 3MF Bio Extension as a **required extension**, as defined in the core
specification. A package using `bio` purely for annotation MAY mark it RECOMMENDED.

# Chapter 2. Evidence and Parameters

## 2.1 The evidence rule

Every quantity in this extension is expressed as a `<b:param>`, and every `<b:param>` MUST
declare where its value came from. This is the organising constraint of the extension:

> A `<b:param>` MUST carry a `provenance` attribute.
> Where `provenance` is `cited`, it MUST resolve to one or more `<b:reference>` entries.
> Where `provenance` is `derived`, it MUST name the model or equation in `method`.
> Where `provenance` is `measured`, it MUST carry a `measured` value.

The intent is that fabricating a number requires explicitly labelling it `estimated`, and
that a reviewer or a release gate can filter on exactly that. Provenance is not metadata
about the record; it is part of the claim.

## 2.2 Param

Element **`<b:param>`**

| Name | Type | Use | Default | Annotation |
| --- | --- | --- | --- | --- |
| name | **xs:token** | required | | Parameter name, from Chapter 5 or `x-` prefixed |
| unit | **xs:token** | | | UCUM code. Omit only for dimensionless quantities |
| setpoint | **xs:string** | | | Commanded value |
| measured | **xs:string** | | | Achieved value |
| tolerance | **xs:string** | | | `±x` or `[lo,hi]` |
| provenance | **ST\_Provenance** | required | | `measured`, `derived`, `cited`, `vendor`, `estimated` |
| evid | **ST\_ResourceID** | | | Evidence resource cited |
| evindices | **ST\_ResourceIndices** | | | 0-based indices into that resource |
| method | **xs:string** | | | Instrument, assay, or named model |
| n | **ST\_ResourceIndex** | | | Replicate count |
| note | **xs:string** | | | |
| @anyAttribute | | | | |

**Empty versus absent.** An attribute present with an empty value denotes *declared but not
yet known*; an absent attribute denotes *not applicable or not declared*. These are
different claims, and the constrained simple types union with the zero-length string so
that both are expressible. This distinction is why Rule S3 requires an unmeasured yield to
be emitted rather than omitted.

## 2.3 Evidence

Element **`<b:evidence>`**

| Name | Type | Use | Default | Annotation |
| --- | --- | --- | --- | --- |
| id | **ST\_ResourceID** | required | | ResourceID of this evidence resource |
| path | **ST\_UriReference** | | | Path to the CSL-JSON bibliography part |
| @anyAttribute | | | | |

A `<b:evidence>` element acts as a container for `<b:reference>` elements. The order of
these elements forms an implicit 0-based index referenced by `evindices` attributes
elsewhere in the model.

Element **`<b:reference>`**

| Name | Type | Use | Default | Annotation |
| --- | --- | --- | --- | --- |
| key | **xs:token** | required | | MUST match an `id` in the CSL-JSON bibliography |
| kind | **ST\_ReferenceKind** | required | | `peer-reviewed`, `preprint`, `standard`, `book`, `protocol`, `vendor-doc`, `internal-report`, `dataset` |
| doi | **ST\_DOI** | | | |
| stdno | **xs:token** | | | Standard designation, e.g. `ASTM F3659-24` |
| url | **xs:anyURI** | | | |
| grade | **ST\_EvidenceGrade** | | | `A`–`F`, see below |
| @anyAttribute | | | | |

At least one of `doi`, `stdno` or `url` SHOULD be present.

The bibliography part is **CSL-JSON**, which means the dossier's references drop directly
into reference managers and document processors, and each entry retains its DOI. A
conformant consumer SHOULD be able to render the bibliography without parsing geometry.

**Evidence grades** are advisory and exist for the reader, not the validator:

| Grade | Meaning |
| --- | --- |
| A | Consensus standard (ISO/ASTM) or systematic review |
| B | Peer-reviewed primary study, parameters explicitly reported |
| C | Peer-reviewed, parameters inferred from figures or methods |
| D | Preprint or conference abstract |
| E | Vendor documentation or aggregator |
| F | Internal, unpublished |

A dossier in which every process parameter is grade F is still valid. It is simply honest
about being unpublished.

# Chapter 3. Resources

## 3.1 Substances

Element **`<b:substances>`** — container, `id` of type **ST\_ResourceID** required. Child
`<b:substance>` elements form an implicit 0-based index referenced by
`substanceindex` and `agentindex`.

Element **`<b:substance>`**

| Name | Type | Use | Annotation |
| --- | --- | --- | --- |
| name | **xs:string** | required | Human-readable name. Not an identifier |
| role | **ST\_SubstanceRole** | required | `polymer`, `monomer`, `photoinitiator`, `photoabsorber`, `crosslinker`, `buffer`, `sacrificial`, `support-bath`, `additive`, `growth-factor`, `mineral-precursor`, `solvent` |

Children: `<b:identity>` (required), `<b:synthesis>`, `<b:grade>`, `<b:hazard>`\*.

`<b:identity>` carries `kind` (`pure`, `mixture`, `biological`), `casrn`, `iupac`,
`formula`, `inchikey`, `smiles`, `chebi`, `mw`, `mwunit`.

`<b:synthesis>` carries `route` and contains `<b:step>`+, `<b:yield>`, `<b:verification>`+.
`<b:step>` has `index`, `op`, `reagent`, `note` and contains `<b:param>`\*.
`<b:yield>` has `kind` (`isolated`, `mass`, `molar`), `unit`, `measured`, `provenance`.
`<b:verification>` has `assay`, `endpoint`, `unit`, `measured`, `provenance`, `method`.

`<b:grade>` carries `purity`, `endotoxin`, `endotoxinunit`, `sterility`, `supplier`, `lot`,
`coa`.

**Why `assay` is required on `<b:verification>`.** For a modified biopolymer such as GelMA,
`1H-NMR` and a colourimetric amine assay do not return the same degree of substitution for
the same batch. A degree of substitution recorded without its assay is not a measurement.

## 3.2 CellPopulations

Element **`<b:cellpopulations>`** — container, `id` required. Children form an implicit
0-based index referenced by `cellpopindex`.

Element **`<b:cellpopulation>`** — `name` required. Children: `<b:origin>` (required),
`<b:authentication>`+ (required), `<b:culture>` (required), `<b:differentiation>`.

`<b:origin>`: `kind` (`line`, `primary`, `iPSC-derived`, `ESC-derived`, `organoid`,
`spheroid`, `co-culture`), `rrid` (Cellosaurus `CVCL_…`), `celltype` (Cell Ontology),
`uberon`, `taxon`, `donorage`, `donorsex`, `ethicsref`, `bank`.

`<b:authentication>`: `assay`, `method`, `date`, `result` (required), `report`.

`<b:culture>`: `medium` (required), `basal`, `serum`, `serumlot`, `antibiotics`
(**required**), `substrate`, `dissociation`; contains `<b:supplement>`\* and `<b:param>`\*.

Registry identifiers are required where a registry exists, because names are not
identifiers. Cell-line misidentification and cross-contamination are the two
best-documented reproducibility failures in cell-based work, and both are cheap to test and
cheap to declare.

## 3.3 BioInkGroup

Element **`<b:bioinkgroup>`** — a **property group**. `id` required. Children form an
implicit 0-based index referenced by the core `pindex`, `p1`, `p2` and `p3` attributes.

Element **`<b:bioink>`**

| Name | Type | Use | Annotation |
| --- | --- | --- | --- |
| name | **xs:string** | required | |
| class | **ST\_InkClass** | required | `bioink`, `biomaterial-ink`, `bioresin`, `support-bath`, `fugitive`, `sacrificial` |
| displaycolor | **ST\_ColorValue** | | Colour a consumer MAY use to render this formulation |

Children: `<b:component>`+, `<b:cellload>`\*, `<b:crosslink>`\*, `<b:rheology>`.

The `class` distinction is not cosmetic. A formulation containing cells and one that does
not are different objects both regulatorily and in process terms, and the field has an
explicit definitional convention separating bioinks from biomaterial inks [R2].

`<b:rheology>` carries `model` (`newtonian`, `power-law`, `Herschel-Bulkley`, `Bingham`,
`Carreau-Yasuda`, `Cross`) and MUST include a `temp_of_measurement` param. A viscosity
without a temperature is not a measurement.

## 3.4 Process

Element **`<b:process>`**

| Name | Type | Use | Annotation |
| --- | --- | --- | --- |
| id | **ST\_ResourceID** | required | |
| modality | **ST\_Modality** | required | Closed vocabulary, see Chapter 5. `x-` prefix for vendor extensions |
| evid / evindices | | | Evidence for the process as a whole |

Children: `<b:machine>` (required), `<b:parameters>` (required), `<b:environment>`,
`<b:toolpath>`.

`<b:toolpath>` carries `path`, `dialect` and `checksum` (all required) and contains
`<b:commandmap>` and `<b:layerevent>`\*.

**On the command map.** `M106` is a part-cooling fan on a thermoplastic printer and a
crosslinking lamp on several bioprinters. The same G-code emitted into the wrong firmware
is a physical hazard, not an inconvenience. `<b:commandmap>` binds bio-relevant codes to
their meaning explicitly, so the binding is machine-checkable rather than assumed. Motion
commands need not be mapped.

The 3MF Consortium has a machine-toolpath extension under review. When it publishes,
`<b:toolpath>` SHOULD be re-based on it rather than continuing as a parallel mechanism.

## 3.5 Protocol

Element **`<b:protocol>`** — `id`, `stage` (`pre-print`, `print`, `post-print`, `culture`,
`assay`), `title` required; `doi`, `path`, `evid`, `evindices` optional. At least one of
`doi` or `path` SHOULD be present.

## 3.6 Results

Element **`<b:results>`** — container, `id` required.

Element **`<b:result>`** — `endpoint` required; `acceptance`, `timepoint`, `path`,
`targetid`, `targetindex` optional; contains `<b:param>`+.

A `<b:result>` whose measurement fails its `acceptance` criterion is valid and valuable.
Recording only passing results is a way of losing the information that matters.

# Chapter 4. Object and Item

Element **`<object>`** is extended with:

| Name | Type | Use | Annotation |
| --- | --- | --- | --- |
| b:processid | **ST\_ResourceID** | | The process that builds this object |
| b:regionrole | **ST\_RegionRole** | | `parenchyma`, `vasculature`, `interface`, `sacrificial`, `support`, `fiducial`, `test-coupon` |

Element **`<item>`** is extended with `b:processid`, which overrides the object-level value
for that build item. A hybrid build — melt-electrowritten reinforcement plus extruded
cell-laden ink — is expressed as two objects with different `b:processid` values.

`b:regionrole` carries information that is not recoverable from geometry. Two meshes of
identical shape may be parenchyma and sacrificial template. The value `test-coupon` marks
geometry printed in the same run solely for destructive testing; recording it is what makes
a mechanical or viability result traceable to the build that produced it.

# Chapter 5. Modality Parameter Sets

`modality` is a closed vocabulary. Each value dispatches a set of parameters that MUST be
present in `<b:parameters>`. The rationale and literature basis for each set is given in
the companion parameter dossier; this chapter states only the requirement.

**Required for every modality:** `build_temp`, `print_duration`, `sterility_method`,
`cell_viability_post_print`.

| Modality | Additionally required |
| --- | --- |
| **all `extrusion-*`** (base set) | `nozzle_inner_diameter`, `nozzle_geometry`, **`nozzle_length`**, `print_speed`, `cartridge_temp`, `layer_height`, `strand_spacing` |
| `extrusion-pneumatic` | base plus `extrusion_pressure` |
| `extrusion-piston` | base plus `volumetric_flow_rate` |
| `extrusion-screw` | base plus `volumetric_flow_rate`, `screw_speed` |
| `extrusion-embedded` | base plus `bath_composition`, `bath_particle_diameter`, `bath_yield_stress`, `bath_temp` |
| `extrusion-coaxial` | base plus `core_flow_rate`, `shell_flow_rate`, `core_shell_ratio`, `core_inner_diameter`, `shell_inner_diameter` |
| `inkjet-piezo`, `microvalve` | `droplet_volume`, `droplet_velocity`, `jetting_frequency`, `nozzle_orifice_diameter` |
| `inkjet-thermal` | the above plus `heater_temp` |
| `laser-lift` | `laser_wavelength`, `pulse_duration`, `pulse_energy`, `laser_fluence`, `spot_size`, `absorbing_layer_material`, `absorbing_layer_thickness`, `donor_film_thickness`, `donor_receiver_gap`, `receiver_coating_thickness` |
| `vat-sla` | `light_wavelength`, `irradiance`, `exposure_time_per_layer`, `layer_thickness`, `photoinitiator_conc` |
| `vat-dlp` | the above plus `photoabsorber_identity`, `photoabsorber_conc` |
| `vat-2pp` | `laser_wavelength`, `pulse_duration`, `average_power`, `NA`, `scan_speed` |
| `volumetric-tomographic` | `light_wavelength`, `optical_power`, `total_light_dose`, `print_duration`, `rotation_speed`, `number_of_projections` |
| `melt-electrowriting` | `nozzle_temp`, `applied_voltage`, `collector_distance`, `collector_speed`, `critical_translation_speed` |
| `electrospinning` | `nozzle_temp`, `applied_voltage`, `collector_distance` |

**`nozzle_length` is required for extrusion, not optional.** The wall shear relation is
τ_w = ΔP·R/(2L). Without a length there is no derivable shear stress, and shear is the
quantity on which the cell-damage literature for this modality rests.

**Rule X1 — derivation completeness.** A package declaring `wall_shear_stress_max` MUST also
carry `nozzle_inner_diameter`, `nozzle_length`, a pressure or a flow rate, and a fitted
`<b:rheology>` on the ink. Shear stress is computed from geometry, driving term and
rheology; without all four the value is not derived but guessed, and a guess wearing a
`derived` label is worse than an honest estimate.

**Derived parameters.** `wall_shear_stress_max`, `residence_time_in_nozzle`, `Z_number`,
`Weber_number`, `penetration_depth_Dp`, `critical_energy_Ec`, `speed_ratio` and
`total_light_dose` MUST carry `provenance="derived"` and MUST name the model in `method`.
They are computed from rheology, geometry and flow, and MUST NOT be presented as
measurements.

**Environment.** `<b:environment>` accepts `chamber_temp`, `chamber_RH`, `chamber_CO2`,
`chamber_O2`, `laminar_flow`, `biosafety_level`, `sterility_assurance` and
`time_out_of_incubator`. The last is recommended for all modalities: cumulative excursion
from the incubator is a common uncontrolled variable in viability outcomes.

# Chapter 6. Package Parts and Relationships

Bio resources live in the 3D Model part, in `<resources>`, alongside core resources. Their
IDs share the model's single resource-ID space and MUST be unique across core and all
extensions.

Supporting documents are separate OPC parts referenced by `ST_UriReference`:

```
package.3mf
├── [Content_Types].xml
├── _rels/.rels
├── 3D/
│   ├── 3dmodel.model
│   └── _rels/3dmodel.model.rels
└── bio/
    ├── references.json          CSL-JSON bibliography
    ├── protocols/               SOPs, protocols.io exports
    ├── coa/                     certificates of analysis, NMR, endotoxin, mycoplasma
    ├── results/                 viability, rheology, mechanics data
    └── toolpath/                modality toolpaths
```

Every part referenced by a `path`, `coa` or `report` attribute MUST exist in the package
and MUST be the target of a relationship from the 3D Model part, mirroring the core rule
for textures. Relationship types are listed in Appendix C.

# Chapter 6a. Graded Properties and the Volumetric Extension

A cell-laden construct is rarely homogeneous. Cell density, target stiffness, mineral
fraction and oxygen tension are frequently designed as gradients, and a format that can
only express a scalar per object cannot describe them.

This extension does **not** introduce a field mechanism. The 3MF Volumetric Extension
already has one: a `<v:volumedata>` resource carries `<v:property>` children, each driven
by a function via `functionid` and `channel`, with the field itself supplied either as an
implicit function or as a `<v:functionfromimage3d>` over an image stack.

What the volumetric extension cannot say is what a field *means*. A scalar field named
`bio_cell_density` is, to a volumetric consumer, an anonymous number between zero and one.
It has no units, no admissible range, and no indication of whether it was measured,
designed, or guessed.

`<b:fieldbinding>` supplies exactly that and nothing more:

```xml
<v:volumedata id="14">
  <v:property name="bio_cell_density" functionid="99" channel="density"/>
</v:volumedata>

<b:fieldbinding id="15" volumeid="14" property="bio_cell_density"
                quantity="cell_density" unit="/mL"
                provenance="derived"
                method="design-intent gradient: 1e6/mL at the periphery rising to 8e6/mL in the core"
                evid="1" evindices="2">
  <b:maps bioinkid="4" bioinkindex="0"/>
  <b:range min="1000000" max="8000000" fallback="2000000"/>
</b:fieldbinding>
```

The division of labour is: **volumetric carries the field, bio carries its meaning.**
Neither duplicates the other, no voxel data is copied, and the evidence rule of Chapter 2
reaches graded quantities on the same terms as scalar ones.

Element **`<b:fieldbinding>`**

| Name | Type | Use | Annotation |
| --- | --- | --- | --- |
| id | **ST\_ResourceID** | required | |
| volumeid | **ST\_ResourceID** | required | The `<v:volumedata>` resource carrying the field |
| property | **xs:token** | required | The `name` of the `<v:property>` within it |
| quantity | **ST\_BioQuantity** | required | `cell_density`, `stiffness_target`, `photoinitiator_conc`, `polymer_conc`, `porosity`, `mineral_fraction`, `growth_factor_conc`, `degradation_rate`, `oxygen_tension`, `crosslink_density`, or `x-` prefixed |
| unit | **xs:token** | required | UCUM |
| provenance | **ST\_Provenance** | required | As for `<b:param>` |
| evid / evindices / method | | | As for `<b:param>` |

Children: `<b:maps>` (which bioink the field modulates) and `<b:range>` (`min`, `max`,
`fallback`).

## 6a.1 Uniform and graded cell loads

`<b:cellload>` accepts either a scalar or a field, and MUST carry exactly one of them:

```xml
<b:cellload cellpopid="3" cellpopindex="0" density="2000000" unit="/mL" .../>   <!-- uniform -->
<b:cellload cellpopid="3" cellpopindex="0" fieldid="15" .../>                   <!-- graded  -->
```

A `<b:cellload>` that binds a field MUST bind one whose `quantity` is `cell_density`, and a
`cell_density` field MUST NOT be mapped to a formulation of class `biomaterial-ink`, which
by definition contains no cells.

## 6a.2 Boundaries

The attribute by which an `<object>` attaches a `<v:volumedata>` resource is governed by
the Volumetric Extension, not by this one. The function resource referenced by `functionid`
is likewise defined by the Volumetric and Implicit extensions. This extension specifies
only the binding between a named volumetric property and a biological quantity.

# Chapter 7. Usage Rules

**Round-trip preservation.** Consumers MUST NOT silently discard `b:` elements or
attributes they do not recognise. A slicer re-exporting a package it does not fully
understand MUST carry unknown bio content through verbatim. Loss of a process parameter is
a safety event.

**Precedence.** Where the same quantity appears in both `<b:parameters>` and a
`<b:layerevent>`, the layer event governs that layer. A consumer MUST surface the
discrepancy rather than resolving it silently.

**Nominal versus achieved.** `setpoint` and `measured` are independent. A parameter with
only a setpoint records an intent; one with only a measurement records an observation.
Neither substitutes for the other.

**Registry precedence.** Where an external registry exists, the registry identifier is
authoritative and the free-text `name` is advisory: CAS Registry Number for substances,
InChIKey and ChEBI for structures, Cellosaurus RRID for cell lines, Cell Ontology for cell
types, UBERON for tissue, NCBI Taxonomy for organism, DOI for publications and protocols,
UCUM for units.

# Chapter 8. Open Items

## 8.1 Why unknowns are data

Every dossier contains things nobody has measured yet. The usual fate of those gaps is an
XML comment or a `TODO` in a note attribute — which is lost on round-trip, cannot be
counted, filtered, assigned or closed, and quietly disappears the moment a tool re-exports
the file.

`<b:openitem>` makes a gap a first-class record with the same standing as a measurement.
An unmeasured yield is not an absence in the file; it is a statement that a yield exists
and has not been determined, with an owner and an action that would close it.

This complements the provenance rule rather than duplicating it. `provenance="estimated"`
marks *a value* as unsupported. An open item says *what would fix it and who is doing so*.

## 8.2 Element

Element **`<b:openitem>`** (child of `<b:openitems>`)

| Name | Type | Use | Annotation |
| --- | --- | --- | --- |
| key | **xs:token** | required | Stable identifier, unique in the model |
| kind | **ST\_OpenItemKind** | required | `unmeasured`, `unverified`, `unavailable`, `disputed`, `out-of-scope`, `blocked`, `placeholder` |
| severity | **ST\_Severity** | required | `blocking`, `material`, `minor` |
| status | **ST\_OpenItemStatus** | required | `open`, `in-progress`, `resolved`, `wont-fix` |
| summary | **xs:string** | required | What is not known |
| action | **xs:string** | required | What would close it |
| owner, raised, due | | | Accountability |
| resolved, resolution | | | Required when `status="resolved"` |
| evid / evindices | | | Evidence bearing on the item |

Children: `<b:affects targetid targetindex paramname>`, linking the item to the resources or
individual parameters it concerns.

**Rule J5** warns when a parameter carries `provenance="estimated"` and no open item names
it. Coverage is by **exact parameter name**: a resource-wide `<b:affects>` refers to the
resource's own attributes and deliberately does not excuse individual estimated parameters
inside it. An open item about a missing firmware version must not silently account for an
unmeasured light dose.

**Rule J6** reports unresolved `blocking` items. A package may be structurally valid and
still carry blocking gaps; the two are different questions and the format keeps them
separate.

# Chapter 8a. Deposition Heads

## 8a.1 Why extrusion needs a head resource

Extrusion is the most widely used biofabrication modality, and the only one where the
machine routinely has several independent material paths: a cell-laden parenchymal ink in
one head, a fugitive support in another, a coaxial vascular head in a third.

A flat parameter list cannot express that. It can record *a* nozzle diameter, but not which
of three nozzles, nor which formulation each was loaded with. `<b:printhead>` carries the
drive, the nozzle and the loaded formulation, and `<object>` names the head that deposited
it. That makes a specific contradiction detectable: an object that selects one bioink via
`pid`/`pindex` while being deposited by a head loaded with another (Rule H3).

## 8a.2 Elements

Element **`<b:printhead>`** (child of `<b:printheads>`)

| Name | Type | Use | Annotation |
| --- | --- | --- | --- |
| name | **xs:string** | required | |
| drive | **ST\_Drive** | required | `pneumatic`, `piston`, `screw`, `thermoplastic-filament`, `solenoid` |
| tool | **xs:token** | | Tool identifier as it appears in the toolpath, e.g. `T1`. MUST be unique within the group |
| bioinkid / bioinkindex | | | The formulation this head is loaded with |
| temperaturecontrolled | **xs:boolean** | | |

Children: `<b:nozzle>` (required), `<b:coaxial>`, `<b:param>`.

Element **`<b:nozzle>`** — `geometry` (`cylindrical`, `conical`, `tapered-conical`,
`coaxial`, `triaxial`, `microfluidic`), `innerdiameter` and `unit` required;
`length`, `gauge`, `material`, `taperangle` optional.

`length` is only optional at the head level because it is **required** at process level for
extrusion (§5). It is recorded in both places because the head is the physical object and
the process is what was run.

## 8a.3 Drive determines the controlled variable

A pneumatic system commands a **pressure**. A piston or screw commands a **displacement or
rotation**. Demanding `extrusion_pressure` from a piston system is a category error, so the
modality vocabulary splits and the required sets diverge:

| Modality | Additionally required |
| --- | --- |
| `extrusion-pneumatic` | `extrusion_pressure` |
| `extrusion-piston` | `volumetric_flow_rate` |
| `extrusion-screw` | `volumetric_flow_rate`, `screw_speed` |

## 8a.4 Coaxial channels

Element **`<b:coaxial>`** — `product` required (`hollow-tube`, `solid-fibre`, `core-shell`);
`outerdiameter`, `unit` optional. Contains two or more `<b:channel>`.

Element **`<b:channel>`** — `role` (`core`, `shell`, `sheath`) and `content` (`bioink`,
`crosslinker`, `crosslinker-mist`, `sacrificial`, `buffer`, `air`) required.

**Rule H2**: a coaxial or triaxial nozzle MUST describe a core and at least one shell or
sheath channel. **Rule H5**: a channel carrying bioink MUST name it.

**Rule H4 checks that the claimed product and the channel contents can coexist.** A package
claiming `hollow-tube` while the core carries bioink is describing something that cannot be
built: the lumen comes from a core that is removed, that only crosslinks, or that is a mist.
Conversely `solid-fibre` with a sacrificial core is a contradiction.

This is the kind of error that survives arbitrarily detailed parameter recording, because
every individual number is plausible. Only the relation between them is wrong.

# Chapter 8b. Maturation and Characterization

## 8b.1 The print is not the end

Everything in Chapters 1–8a describes roughly a day of work. A cell-laden construct then
spends days or weeks in culture, and that period determines whether it becomes tissue or
becomes debris. A format that stops at the print records the less biologically consequential
half.

`<b:maturation>` describes what happens next; `<b:characterization>` describes what was
measured, and when.

## 8b.2 Maturation

Element **`<b:maturation>`** — `id` required; `targetid`, `totalduration`, `protocolid`
optional. Contains one or more `<b:stage>`.

Element **`<b:stage>`** — `index`, `name`, `culture`, `from` and `to` required.

`culture` is one of `static`, `orbital`, `spinner`, `rotating-wall`, `perfusion`,
`air-liquid-interface`, `microfluidic`, `in-vivo`.

Maturation is **staged** because it usually is: a static recovery period, then perfusion
conditioning, then mechanical loading. The transitions are as much a part of the record as
the conditions, and a single flat description loses them.

`from` and `to` are **ST\_Timepoint** — an ISO 8601 duration measured from the end of
printing. `P0D` is immediately post-print, `P7D` is day seven, `PT4H` is four hours. Using a
duration rather than a free-text label keeps timepoints orderable and comparable between
packages, which a label like "day 7 (late)" does not.

Children of a stage: `<b:bioreactor>`, `<b:stimulation>`\*, `<b:medium>`\*, `<b:param>`\*.

**Rule Q3**: a `perfusion` stage MUST describe a bioreactor and MUST record `flow_rate`.
Flow rate is the parameter that sets wall shear stress at the construct, and shear is a
differentiation cue, not merely a mass-transport convenience.

## 8b.3 Stimulation regimes

Element **`<b:stimulation>`** — `mode` required, from `fluid-shear`, `cyclic-tension`,
`cyclic-compression`, `hydrostatic-pressure`, `electrical`, `electromagnetic`, `ultrasound`,
`photostimulation`, `biochemical`. Optional `onset` and `dutycycle`.

**Rule Q5 requires magnitude, rate and duration together**, per mode:

| Mode | Required parameters |
| --- | --- |
| `fluid-shear` | `flow_rate`, `wall_shear_stress`, `stimulation_duration` |
| `cyclic-tension` / `cyclic-compression` | `strain_amplitude`, `stimulation_frequency`, `cycles_per_day` |
| `hydrostatic-pressure` | `pressure_amplitude`, `stimulation_frequency`, `stimulation_duration` |
| `electrical` | `field_strength`, `stimulation_frequency`, `pulse_width` |
| `electromagnetic` / `ultrasound` | `field_strength` or `intensity`, `stimulation_frequency`, `stimulation_duration` |

This is a MUST rather than a SHOULD for a specific reason. The perfusion-bioreactor
literature observes that circuit parameters — viscosity, flow rate, frequency, pressure —
are "as a group often overlooked" in reporting, with the consequence that the mechanical
environment a construct actually experienced cannot be reconstructed. A frequency without an
amplitude, or an amplitude without a duration, describes nothing.

## 8b.4 Characterization

**In plain terms: this is what you measured on the printed thing, and when you measured it.**

Nothing more abstract than that. `<b:characterization>` is a container; each `<b:assay>` is
one kind of measurement (viability, stiffness, pore size, lumen patency); each `<b:reading>`
is that measurement taken once, at one point in time.

It exists separately from `<b:results>` because they answer different questions.
`<b:results>` records a single verdict against an acceptance criterion — did the build pass.
`<b:characterization>` records how a property *moved over the culture period*, which is
usually the more informative record and which a single value cannot express.

Element **`<b:characterization>`** — `id` required; `targetid`, `targetindex` optional.

Element **`<b:assay>`** — `name`, `domain`, `endpoint` and **`method`** required;
`unit`, `destructive`, `acceptance`, `protocolid`, `evid` optional.

`domain` is one of `structural`, `mechanical`, `viability`, `proliferation`, `phenotype`,
`matrix-deposition`, `function`, `transport`, `degradation`, `sterility`, `metabolic`.

**Rule Q8**: `method` is required. An endpoint without a method is not a measurement — two
laboratories reporting "compressive modulus" from unconfined compression and from
nanoindentation are not reporting the same quantity.

Element **`<b:reading>`** — one assay at one timepoint. `timepoint` and `provenance`
required; `value`, `sd`, `n`, `path`, `outcome` optional.

Several readings form a **timecourse**, which is the point. A construct at 92 % viability on
day 1 and 74 % on day 21 is a different object from one holding 90 % throughout, and a
single-valued result element cannot say so. This resolves the `timecourse-fields` open item
raised in v0.4.

**Rule Q9** forbids two readings at the same timepoint — replicates belong in `n` and `sd`.
**Rule Q10** warns when a `destructive` assay carries several timepoints, since each
timepoint then consumes its own specimen, which should appear as separate `test-coupon`
objects in the build. **Rule Q11** requires a `measured` reading to carry a value.

**Rule Q12** warns when a package records a maturation regime and no characterization: the
regime was specified but its effect was not recorded, which is the most common way a
maturation dataset ends up unusable.

# Chapter 9. Calibration

## 9.1 Parameters are not calibration

A parameter is what you set. A calibration test is the independent measurement that says
the setting means what you think it means. A package can be full of exact parameters and be
unreproducible because none of them were tied to a machine whose behaviour was checked.

`<b:calibration>` is therefore a **dated event with an operator and outcomes**, not a
machine attribute (Rule K1).

## 9.2 Elements

Element **`<b:calibration>`** — `id`, `modality` required; `performed`, `operator`,
`standard` optional. Its `modality` MUST match that of any process referencing it (K7).

Element **`<b:test>`**

| Name | Type | Use | Annotation |
| --- | --- | --- | --- |
| name | **xs:token** | required | |
| kind | **ST\_CalibrationKind** | required | `geometric`, `dosimetric`, `optical`, `flow`, `rheological`, `printability`, `thermal`, `biological`, `sterility` |
| metric | **xs:token** | required | What is measured |
| acceptance | **xs:string** | required | The laboratory's own criterion (K2) |
| measured | **xs:string** | | Required if `outcome="pass"` (K3) |
| outcome | **ST\_CalibrationOutcome** | required | `pass`, `fail`, `not-performed`, `inconclusive` |
| frequency | **xs:token** | | e.g. `per-session`, `per-resin-lot`, `monthly` |
| artifactobjectid | **ST\_ResourceID** | | The printed artefact that evidenced the test (K4) |
| stdref | **xs:token** | | e.g. `ISO/ASTM 52902:2023` |

`artifactobjectid` is the mechanism that makes calibration traceable to a build: the
artefact is an ordinary `<object>` in the same package, ordinarily carrying
`b:regionrole="test-coupon"`.

`acceptance` is required and this specification asserts **no thresholds**. Per-modality test
catalogues, with sources, are in `dossier/Calibration-Dossier.md`.

## 9.3 The ISO/ASTM 52900 crosswalk

`<b:process iso52900>` records the process category from ISO/ASTM 52900:2021 — the standard
that classifies additive manufacturing into seven categories with abbreviations and provides
a normative annex for identifying processes within a category.

The mapping is **many-to-one and informative**. Bio modalities are finer-grained than
52900: `extrusion-pneumatic`, `-piston`, `-screw` and `-embedded` are all `MEX`;
`vat-sla`, `vat-dlp`, `vat-2pp` and `volumetric-tomographic` are all `VPP`; droplet and
laser-transfer modalities are `MJT`.

Modalities whose category is genuinely arguable — melt electrowriting, electrospinning,
magnetic levitation, spheroid bioassembly — are **deliberately unmapped**. Rule N1 checks
only the mappings that are unambiguous, and forcing the rest would assert a classification
the field has not made.

# Chapter 10. Regulatory Context and Translation

## 10.1 Why regulatory status belongs in the file

A construct's regulatory status is not a property of its geometry. It follows from intended
use, from how far the cells were manipulated, and from whether a scaffold component performs
a device function — all of which this package already records. `<b:regulatory>` ties them
together so the determination travels with the design.

## 10.2 Elements

Element **`<b:regulatory>`** — `id`, `intendeduse` required; `contactduration`,
`contactnature` optional but required for regulated uses (R8).

Element **`<b:jurisdiction>`** — `region`, `framework`, `instrument`, `determination`
required; `classification`, `authority`, `determinedby`, `determineddate` optional.
Children: `<b:obligation ref status>`.

Element **`<b:standardref>`** — `stdno` required; `applies`, `status`, `title` optional.
`applies` lets a standard be recorded as relevant but not yet engaged, which is the normal
state of research work heading toward clinical use.

**`determination` is the load-bearing attribute.** The contested part of a regulatory record
is rarely the classification — it is how the classification was reached and whether anyone
with authority agreed:

`confirmed-by-authority` · `advice-sought` · `self-assessed` · `undetermined` ·
`not-applicable`

**Rule R5**: `undetermined` MUST link to an open item. An undetermined status is a tracked
gap, not silence. **Rule R6** warns when a regulated intended use rests only on
self-assessment. **Rules R7 and R8**: `implantable` and `clinical-investigation` require an
ISO 10993 `standardref` plus contact categorisation, because contact duration and nature are
the inputs to that series.

The specification asserts no classification and no thresholds. Jurisdiction detail is in
`dossier/Regulatory-Annex.md`.

## 10.3 Translation

Two senses, both supported.

**Across jurisdictions.** `<b:jurisdiction>` repeats. Intended use, contact categorisation
and cell-manipulation history are jurisdiction-neutral inputs; each jurisdiction element
records how that regime reads them. Adding a region adds an element; it does not restructure
the dossier.

**Across languages.** Human-readable strings are authored in the language declared by the
core `<model xml:lang>` attribute. Translations live in a package part,
`/bio/i18n/{lang}.json`, keyed by `{resource-id}.{key}.{attribute}`, attached by a
relationship of type
`http://schemas.3mf.io/3dmanufacturing/2026/07/biotranslation`.

This is deliberately **not** an `xml:lang` attribute per element. An attribute holds one
value and so cannot carry more than one language; 3MF core already establishes document
language at `<model>`; and a catalogue keyed by resource and attribute is the only structure
that scales past two languages while keeping the authoritative text in one place.

# Chapter 11. Conformance

A conformant consumer MUST enforce the rules in Appendix E. Those rules cannot be expressed
in XSD 1.0. Two reference implementations are provided:

| Artifact | Scope |
| --- | --- |
| `spec/bio.sch` | ISO Schematron. Every **intra-document** rule. Runs in any standard XML toolchain |
| `spec/validate_bio.py` | All rules, including the **cross-part** ones |

Schematron validates one XML document, so it cannot express rules O2, O3 and E5 — whether
referenced parts exist, whether they are OPC relationship targets, and whether reference
keys match the CSL-JSON bibliography. Those are properties of the package, not of the model
part, and remain procedural. The split is stated rather than hidden.

The Schematron is written against XPath 1.0, because the reference runner compiles to
XSLT 1.0. Bounds-checking a whitespace-separated `evindices` list is therefore performed
only for the single-index case; `validate_bio.py` checks every index. A rule that silently
half-fires is worse than one that declares its scope.

Three test artifacts support this:

| Artifact | Proves |
| --- | --- |
| `spec/conformance_tests.py` | Each rule **fires** on a fault, in both engines |
| `spec/make_conformance_corpus.py` | Each modality's required set is **satisfiable** — one minimal passing package per modality |
| `spec/roundtrip_test.py` | The Chapter 7 preservation rule is testable, and a lossy consumer is detectable |

The corpus matters because negative tests alone cannot show that a required-parameter set is
achievable. Generating a passing package for every modality immediately exposed two defects
that thirty-five negative tests had not: a parameter that was simultaneously required by P0
and constrained to `derived` by P3, and a three-way disagreement between this specification's
prose, the Python table and the Schematron over whether embedded extrusion inherits the base
extrusion parameters. It does.

`spec/conformance_tests.py` injects thirty-five deliberate faults and runs each through both
engines, emitting a coverage matrix. At the time of writing: 35/35 caught by the Python
validator, 33/33 by Schematron, with the two cross-part faults out of scope by design.

Validating against `bio.xsd` alone checks structure, not evidence, and is **not**
conformance checking.

**Conformance classes**

| Class | Requirement |
| --- | --- |
| **Bio-Core** | Bio resources present, all required parameters for the declared modality, evidence rule satisfied, resource IDs and part relationships resolve |
| **Bio-Traceable** | Bio-Core, plus every parameter `measured`, `cited` or `vendor` — no `estimated` — and certificates of analysis embedded |
| **Bio-Reproducible** | Bio-Traceable, plus protocols embedded, toolpath present with checksum, and results carrying acceptance criteria |

Bio-Core is the minimum for a package to be machine-safe. Bio-Reproducible is the target
for a package intended to let a second laboratory rebuild the construct.

# Chapter 12. Threat Model

## 12.1 What this extension can and cannot enforce

A validator can check that a claim is **well formed, internally consistent, and traceable**.
It cannot check that a claim is **true**. This distinction is the most important thing an
implementer or reviewer needs to understand about a conformant package, and stating it
plainly is more useful than implying a guarantee the format cannot provide.

Fourteen adversarial packages were constructed to test the boundary. Before hardening,
thirteen produced a clean bill of health. Rules U1–U3, D1–D2, C7–C8 and T4 were added in
response. The residual set is instructive:

| Attack | Status |
| --- | --- |
| Light dose recorded in kilograms | Caught — U1 dimension check |
| Viability of 400 %, passage number 400 | Caught — U2 physical bounds |
| Negative cell density | Caught — U2 |
| Measured value wildly inconsistent with setpoint | Caught — U3 (warning) |
| Calibration dated in the future | Caught — D2 |
| Mycoplasma test present, result "POSITIVE" | Caught — C7 |
| Toolpath checksum that is a plausible-looking lie | Caught — T4 verifies the hash |
| Regulated intended use resting on self-assessment | Caught — R6 (warning) |
| A **real** reference cited for an **unrelated** claim | **Not caught.** Needs human review |
| A fabricated but well-formed DOI | Only with `--online` |
| A syntactically valid but non-existent RRID | Only with `--online` |
| An open item "resolved" with a vacuous resolution | **Not caught.** Needs human review |
| An acceptance criterion that cannot fail | **Not caught.** Legitimate cases exist |

## 12.2 The residual class

Three of the residual attacks share a shape: **the record is structurally perfect and
semantically false.** No schema, Schematron rule or validator will ever catch them, because
distinguishing a correct citation from an incorrect one requires reading the cited work.

This is not a defect to be fixed in a later version. It is the boundary of what a file
format can do, and the reason this extension carries evidence grades, `determination`
values that distinguish self-assessment from authority confirmation, and open items with
named owners. Those exist to direct **human** attention, not to replace it.

Consumers MUST NOT present a clean validation result as an assurance of correctness.
Suggested wording for tooling: *"Validates against 3MF Bio 0.5.0: the record is complete and
internally consistent. It has not been checked for accuracy."*

## 12.3 Package-parsing hazards

A `.3mf` is a ZIP archive containing XML. Implementers MUST:

- disable DTD loading and external entity resolution (XXE);
- normalise and confirm every `ST_UriReference` resolves inside the package (zip-slip);
- bound decompressed size before extracting (zip bombs);
- treat toolpaths as data and never execute them.

## 12.4 What conformance means

The conformance classes describe **data completeness**, not safety, accuracy or regulatory
compliance. A package may be Bio-Reproducible and still be scientifically wrong, unapproved,
and unsafe to build. A validator reporting zero errors states that the record is
well-formed and self-consistent — nothing more.

---

# Part II. Appendices

## Appendix A. Glossary

See the 3MF Core Specification glossary, plus:

**bioink** — a formulation of cells suitable for processing by an automated biofabrication
technology, which may also contain biologically active components and biomaterials [R2].

**biomaterial ink** — a biomaterial used for printing where cell contact occurs
post-fabrication [R2].

**provenance** — the declared origin of a numeric value: measured, derived, cited, vendor
or estimated.

**modality** — the physical mechanism by which material is placed, e.g. extrusion,
droplet ejection, laser-induced forward transfer, vat photopolymerisation, tomographic
volumetric projection, melt electrowriting.

**critical translation speed (CTS)** — in melt electrowriting, the collector speed matching
the jet velocity, above which straight fibres are written.

## Appendix B. 3MF XSD Schema

The schema is provided as `spec/bio.xsd` rather than inlined here, to keep a single
authoritative copy. It follows the Consortium schema conventions: `elementFormDefault` and
`attributeFormDefault` unqualified, `blockDefault="#all"`, `CT_`/`ST_` naming, globally
declared elements referenced with `ref`, `xs:anyAttribute namespace="##other"` on every
complex type, and `CT_Resources` redefined with a choice over the new resource elements.

`spec/bio.sch` is the ISO Schematron companion carrying the rules XSD cannot express.

`spec/bio.libxml.xsd` is a generated variant in which `maxOccurs="2147483647"` is replaced
by `maxOccurs="unbounded"`. The two are semantically identical. libxml2-based validators
(lxml, xmllint) use 2^30 as their internal UNBOUNDED sentinel and reject the literal
`2147483647` that the Consortium schemas use, although it is valid XSD. Use the canonical
file for reference and the variant for validation.

## Appendix C. Standard Namespace and Content Types

| | |
| --- | --- |
| Bio | `https://3mfbio.com/ns/bio/2026/07` |
| Volumetric (referenced, not defined here) | `http://schemas.3mf.io/3dmanufacturing/volumetric/2022/01` |
| Implicit (referenced, not defined here) | `http://schemas.3mf.io/3dmanufacturing/implicit/2023/12` |

**Relationship types**

| Part | Relationship type |
| --- | --- |
| Bibliography | `http://schemas.3mf.io/3dmanufacturing/2026/07/biobibliography` |
| Protocol | `http://schemas.3mf.io/3dmanufacturing/2026/07/bioprotocol` |
| Certificate of analysis | `http://schemas.3mf.io/3dmanufacturing/2026/07/biocoa` |
| Result data | `http://schemas.3mf.io/3dmanufacturing/2026/07/bioresult` |
| Toolpath | `http://schemas.3mf.io/3dmanufacturing/2026/07/biotoolpath` |

**Content types**

| Extension | Content type |
| --- | --- |
| json | `application/vnd.3mf.biodossier.bibliography+json` |
| md | `application/vnd.3mf.biodossier.protocol+markdown` |
| bin | `application/vnd.3mf.biodossier.toolpath` |

These strings are proposals and would require registration alongside the namespace.

## Appendix D. Example File

A complete illustrative package is provided under `examples/`, comprising
`[Content_Types].xml`, `_rels/.rels`, `3D/3dmodel.model`, `3D/_rels/3dmodel.model.rels`
and the `bio/` payload parts. It validates clean against both
`spec/validate_schema.py` and `spec/validate_bio.py`.

## Appendix E. Rule Index

| Rule | Statement |
| --- | --- |
| X1 | A package encoding cell-laden material MUST list the bio prefix in `requiredextensions` |
| X3 | Resource IDs MUST be unique across core and all extensions |
| V1 | `provenance="cited"` MUST resolve to evidence; `evindices` MUST be in range |
| V2 | `provenance="measured"` MUST carry a `measured` value |
| V3 | `provenance="derived"` MUST name the model in `method` |
| S1 | A commercially available CAS-registered substance MUST carry `casrn` |
| S1a | A `mixture` without CAS MUST give `supplier` and `lot` |
| S2 | A substance synthesised or modified in-house MUST carry `<b:synthesis>` |
| S3 | `<b:synthesis>` MUST contain `<b:yield>`, emitted empty with `provenance="estimated"` if unmeasured |
| S4 | `<b:synthesis>` MUST contain at least one `<b:verification>` with an `assay` |
| C1 | `kind="line"` MUST carry an RRID |
| C2 | Every cell population MUST carry a mycoplasma authentication record |
| C3 | `passage_at_print` MUST be present |
| C4 | `antibiotics` MUST be stated explicitly, including the value `none` |
| I1 | `class="bioink"` MUST contain at least one `<b:cellload>` |
| I2 | `<b:rheology>` MUST include `temp_of_measurement` |
| I3/I4 | Component and cellload references MUST resolve, indices in range |
| P0 | All parameters required by the declared modality MUST be present |
| P1 | `critical_translation_speed` MUST be `measured`, never `cited` |
| P2 | Electrohydrodynamic modalities MUST record `chamber_temp` and `chamber_RH` |
| P3 | Derived quantities MUST carry `provenance="derived"` |
| T1 | A toolpath MUST carry a `checksum` |
| T3 | Contradictions between `<b:parameters>` and a `<b:layerevent>` MUST be surfaced |
| G1 | An object selecting a bioink group MUST carry an in-range `pindex` |
| G2 | `b:processid` MUST resolve to a `<b:process>` |
| O2/O3 | Referenced parts MUST exist and MUST be relationship targets |
| E5 | Every `<b:reference key>` MUST match an entry in the CSL-JSON bibliography |
| F1 | `<b:fieldbinding volumeid>` MUST resolve to a `<v:volumedata>` resource |
| F2 | The named `property` MUST be a `<v:property>` of that volumedata |
| F3 | `<b:cellload>` MUST carry exactly one of `density`+`unit` or `fieldid` |
| F4 | `fieldid` MUST resolve to a `<b:fieldbinding>` |
| F6 | A cell load MUST bind a `cell_density` field, and such a field MUST NOT map to a `biomaterial-ink` |
| F7 | A cited or derived field binding MUST carry evidence or a method |
| F8 | `<b:maps bioinkid>` MUST resolve, with `bioinkindex` in range |
| K1 | A calibration record MUST carry a performed date |
| K2 | Every calibration test MUST state an acceptance criterion |
| K3 | A test marked `pass` MUST record a measured value |
| K4 | `artifactobjectid` and `calibrationid` MUST resolve |
| K7 | A calibration record's modality MUST match the process referencing it |
| R4 | A regulatory resource MUST declare at least one jurisdiction; `regulatoryid` MUST resolve |
| R5 | `determination="undetermined"` MUST link to an open item |
| R7 | `implantable` or `clinical-investigation` MUST carry an ISO 10993 standardref |
| R8 | Those uses MUST carry `contactduration` and `contactnature` |
| J1 | Open item keys MUST be unique |
| J2 | A resolved open item MUST record a resolution and a resolution date |
| J3 | An open or in-progress item MUST state a closing action |
| J4 | `<b:affects targetid>` MUST resolve to a resource |
| N1 | Where the ISO/ASTM 52900 category is unambiguous, `iso52900` MUST match it |
| H1 | Tool identifiers MUST be unique within a printhead group |
| H2 | A coaxial nozzle MUST describe a core and a shell or sheath channel |
| H3 | `b:printheadid`/`printheadindex` MUST resolve, and the head's loaded ink MUST match the object's |
| H4 | The claimed coaxial `product` MUST be consistent with the channel contents |
| H5 | A channel carrying bioink MUST name it |
| X1 | A declared `wall_shear_stress_max` MUST have its derivation inputs present |
| Q2 | A maturation stage MUST NOT end before it begins |
| Q3 | A perfusion stage MUST describe a bioreactor and record `flow_rate` |
| Q5 | A stimulation regime MUST record magnitude, rate and duration together |
| Q8 | An assay MUST name its method |
| Q9 | An assay MUST NOT carry two readings at the same timepoint |
| Q11 | A `measured` reading MUST carry a value |
| M1 | A package MUST declare `<metadata name="b:SpecVersion">` |
| U1 | A parameter's unit MUST match the dimension of the quantity it names |
| U2 | A value MUST lie within the physically possible range for its quantity |
| D1 | Dates MUST be valid ISO dates |
| D2 | Dates MUST NOT be in the future, and an item MUST NOT be resolved before it was raised |
| C7 | A mycoplasma authentication reporting contamination MUST NOT be treated as satisfying C2 |
| T4 | A recorded toolpath checksum MUST match the referenced part |

Warning-level checks (V4, C1b, C5, C6, C8, E2, E3, F9, G3, G4, G5, J5, J6, K5, K6, K8, M2,
N2, P4, P5, R1, R2, R6, R9, T2, U3, O1, O5) are listed in the validator and Schematron
sources. `W1`–`W2` (DOI and RRID resolution) require `--online`.

---

# References

**3MF Core Specification** — 3MF Consortium.
<https://github.com/3MFConsortium/spec_core>

**3MF Materials and Properties Extension** — 3MF Consortium.
<https://github.com/3MFConsortium/spec_materials>

**3MF Displacement Extension**, version 1.0.0 — 3MF Consortium.
<https://github.com/3MFConsortium/spec_displacement>
Used as the structural and schema-convention template for this document.

**3MF Volumetric Extension** — 3MF Consortium.
<https://github.com/3MFConsortium/spec_volumetric>

**ISO/IEC 25422:2025** — Information technology — 3D Manufacturing Format (3MF)
specification suite. Published June 2025, first edition. 3MF Core and extensions are now an
ISO/IEC standard, which raises the bar for any proposed addition.

**Open Packaging Conventions** — Ecma International, "Office Open XML Part 2: Open
Packaging Conventions," 2006.

**RFC 2119** — Bradner, S. "Key words for use in RFCs to Indicate Requirement Levels."
The Internet Society, 1997.

**CSL-JSON** — Citation Style Language item schema.

**UCUM** — Unified Code for Units of Measure.

[R2] Groll J. et al. "A definition of bioinks and their distinction from biomaterial inks."
*Biofabrication* 11(1):013001, 2019. DOI: 10.1088/1758-5090/aaec52

The biofabrication literature underpinning Chapter 5 is catalogued separately in
`dossier/References.md`.
