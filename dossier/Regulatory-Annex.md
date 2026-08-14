# Regulatory Annex

Companion to `spec/3MF Bio Extension.md` Chapter 10. Reference keys (G…) resolve in
`dossier/References.md`.

> **This is not regulatory advice.** It is a map of which instruments exist and which
> fields the format reserves for recording a determination. Classification of a specific
> construct is a matter for the manufacturer and the competent authority. The format's job
> is to make the determination *explicit and traceable*, including when it has not been
> made — which is what `determination="undetermined"` plus a linked open item is for.

---

## 1. Why this is in the file at all

A bioprinted construct's regulatory status is not a property of its geometry. It follows
from **intended use**, from **how much the cells were manipulated**, and from **whether a
scaffold component performs a device function**. All three are recorded elsewhere in this
package already — `intendeduse`, the cell `<b:origin kind>` and processing history, the
ink `class`. The regulatory resource ties them together so the determination travels with
the design instead of living in a separate binder.

The design goal is **translatability**: the same construct re-read against a different
jurisdiction without rewriting the dossier. Hence `<b:jurisdiction>` repeats per region
rather than the format picking one regime as canonical.

---

## 2. The determination attribute

The contested part of a regulatory record is rarely the classification. It is *how the
classification was arrived at*, and whether anyone with authority agreed.

| `determination` | Meaning |
|---|---|
| `confirmed-by-authority` | The competent authority has agreed in writing |
| `advice-sought` | Formal advice requested, not yet received |
| `self-assessed` | The manufacturer's own reading |
| `undetermined` | Not yet assessed. **MUST link to an open item** (Rule R5) |
| `not-applicable` | The framework does not engage at this intended use |

Rule R6 warns when a regulated intended use — `implantable`, `clinical-investigation`,
`preclinical`, `veterinary` — rests only on `self-assessed`.

---

## 3. United States

| Instrument | Engages when |
|---|---|
| **21 CFR Part 1271** — Human Cells, Tissues, and Cellular and Tissue-Based Products | HCT/Ps generally. Grounded in **PHS Act §361**, the authority to prevent communicable disease spread (G3, G4) |
| **PHS Act §351** biologics pathway | Cells that are **more than minimally manipulated**. Regulated through the biologics system rather than solely under Part 1271 (G2) |
| **FD&C Act** device/drug pathways | Where a device or drug component is present |

Structure worth recording accurately:

- Some HCT/Ps are eligible for regulation **solely** under Part 1271; others fall under
  Part 1271 *and* premarket/postmarket device, drug or biologics regulation (G4).
- "Minimal manipulation" for cells or nonstructural tissues means processing that does not
  alter biological characteristics (G2). Printing a cell into an engineered matrix is
  ordinarily well beyond that, which is the point at which §351 engages.
- Centres: **CBER** for biologics, **CDRH** for devices (G2). Assignment for a combination
  product is settled by a **Request for Designation**.
- **cGTP** — current good tissue practice — governs methods, facilities, controls,
  recordkeeping and the quality programme for HCT/P establishments (G5).
- **RMAT** (Regenerative Medicine Advanced Therapy) designation was created in 2016 (R6).

Suggested `framework` tokens: `21CFR1271`, `PHSA-351`, `FDCA-device`, `combination-product`,
`research-use-only`.

## 4. European Union

| Instrument | Engages when |
|---|---|
| **Regulation (EC) No 1394/2007** on Advanced Therapy Medicinal Products | ATMPs. Defines ATMPs, their authorisation procedure, supervision and monitoring. In force 30 December 2008 (G1) |
| **Article 2(1)(d)** of the same — *combined ATMP* | A substantially manipulated cell product presented for tissue regeneration that contains, as an integral part, scaffold material performing a device function (G6) |
| **Regulation (EU) 2017/745 (MDR)** | The device component of a combined ATMP |
| Directive 2009/120/EC, Regulation (EC) No 726/2004 | Supporting framework (G1) |

Notes that matter for classification:

- The combined-ATMP route applies **unless** the cell or tissue component is non-viable and
  its action is ancillary to the device component (G1). A cell-laden construct is viable by
  construction, so this exemption will rarely apply here.
- Premarket review is delegated to the **Committee for Advanced Therapies (CAT)**, which
  issues an opinion to the Commission for final approval (R6).
- In practice a manufacturer may lack the data to substantiate the principal mode of action
  early in development, and therefore cannot yet identify the candidate ATMP classification
  (G6) — which is precisely the situation `determination="undetermined"` exists to record
  honestly rather than guessing.

Suggested `framework` tokens: `ATMP-1394/2007`, `combined-ATMP`, `MDR-2017/745`,
`research-use-only`.

## 5. Australia

Tissue-engineered products are regulated under the biologicals framework and are typically
classified as **Class 3 or Class 4 biologicals**, depending on the degree of cell or tissue
manipulation and the associated risk. The pathway involves compliance with the **Australian
Regulatory Guidelines for Biologicals (ARGB)**, appropriate clinical trials, and inclusion
in the **ARTG** before lawful supply (R6).

Suggested `framework` tokens: `ARGB`, `biologicals-class-3`, `biologicals-class-4`.

## 6. A cross-jurisdiction caution

Reviews of this area note that not all authorities use the term "ATMP", and that bioinks
and bioprinted constructs are addressed as "medical devices" or "combination products" as a
universal notation. In both the EU and FDA frameworks, bioinks would fall into the category
of combination products (R6).

This is why `<b:jurisdiction framework>` is a free token rather than a closed enumeration:
a closed list would force a mapping that the field itself has not settled. `region` and
`instrument` are the stable parts; `classification` is where the local vocabulary goes.

---

## 7. Standards, and when they engage

`<b:standardref>` carries `applies` so a standard can be recorded as *relevant but not yet
engaged* — the common case in research work heading toward clinical use.

| Standard | Applies at |
|---|---|
| **ISO 10993 series** — biological evaluation of medical devices | `clinical-investigation`, `implantable`. Cross-referenced by ASTM F3659 (R1) |
| **ASTM F3659-24** — Standard Guide for Bioinks | All intended uses. Sterility, cytocompatibility, post-printing viability (R1) |
| **ASTM F2150** — scaffold characterisation | Referenced by F3659 (R1) |
| **ASTM F2027** — source materials | Referenced by F3659 (R1) |
| **ISO/ASTM 52900:2021** — fundamentals and vocabulary | All. Drives the `iso52900` attribute (K2) |
| **ISO/ASTM 52902:2023** — test artefacts | All, via calibration (K1) |
| **ASTM F2971** — reporting data for AM test specimens | All, via calibration (K1) |
| **GCCP 2.0** — good cell and tissue culture practice | Any package containing cells (R14) |
| **ISO/IEC 25422:2025** — 3MF specification suite | The container format itself (G7) |

**Rule R7** requires an `ISO 10993` standardref when `intendeduse` is `implantable` or
`clinical-investigation`. **Rule R8** requires `contactduration` and `contactnature`
alongside, because those two are the inputs to ISO 10993 categorisation — a construct
cannot be evaluated against the series without them.

---

## 8. Translation

Two distinct senses of "translatable", both supported:

**Across jurisdictions.** `<b:jurisdiction>` repeats. The intended use, contact
categorisation and cell-manipulation record are jurisdiction-neutral inputs; each
jurisdiction element records how *that* regime reads them. Adding a region means adding an
element, not restructuring the dossier.

**Across languages.** Human-readable strings — `summary`, `action`, `note`, `title` — are
authored in the language declared by the core `<model xml:lang>` attribute. Translations
live in a package part, `/bio/i18n/{lang}.json`, keyed by `resource-id.attribute`:

```json
{
  "lang": "de",
  "source": "en-US",
  "strings": {
    "18.gelma-yield.summary": "Für die hauseigene GelMA-Synthese wurde keine isolierte Ausbeute erfasst.",
    "17.US.note": "..."
  }
}
```

Attached by an OPC relationship of type
`https://3mfbio.com/ns/rel/2026/07/biotranslation`.

This is deliberately *not* an `xml:lang` attribute on each element. An attribute holds one
value, so it cannot carry a string in more than one language; and the 3MF core already
establishes document language at `<model>`. A catalogue keyed by resource and attribute is
the only structure that scales past two languages, and it keeps the authoritative text in
one place.

---

## 9. What is deliberately absent

- **No numeric acceptance thresholds** — endotoxin limits, viability floors, sterility
  assurance levels. All are application- and jurisdiction-specific.
- **No classification decision procedure.** The format records a determination; it does not
  compute one. A validator that guessed a regulatory class would be worse than useless.
- **No claim of regulatory sufficiency.** A package can be `Bio-Reproducible` and still be
  nowhere near a submission. Conformance classes describe data completeness, not compliance.
