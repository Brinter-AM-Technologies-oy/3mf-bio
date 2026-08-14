# Regulatory review pack

**For a regulatory affairs professional. Estimated time: 2–3 hours.**

You are not being asked to approve anything, and there is no product here. You are being
asked whether a **map** is accurate, and whether the **fields** provided are the right ones.

Read `dossier/Regulatory-Annex.md` and `spec/3MF Bio Extension.md` Chapter 10, then answer
the numbered questions below. Answers of "wrong", "overstated" or "you have missed X" are the
useful outcome — a fact-check challenge template exists at
`.github/ISSUE_TEMPLATE/fact-check.md`.

---

## What the project is, in one paragraph

An open XML schema for recording biofabrication work — materials, cells, print process,
calibration, post-print culture, and measurements — in one file. **It is not a standard, it
asserts no thresholds, and it certifies nothing.** It provides fields; whether filling them
satisfies any regulator is the user's judgement against their own audit. The regulatory
resource exists so a determination can be recorded *and traced*, including when it has not
been made.

The design claim under review: **the format records how a classification was reached, rather
than computing one.**

---

## Part A — Are the factual claims right?

Each claim below appears in the annex. Mark each: **correct** · **overstated** · **wrong** ·
**incomplete**.

### United States

**A1.** 21 CFR Part 1271 rests on **PHS Act §361** authority to prevent communicable disease
transmission. *(source G4, grade E)*

**A2.** Some HCT/Ps are regulated **solely** under Part 1271; others under Part 1271 **and**
premarket/postmarket device, drug or biologics regulation. *(G4, grade E)*

**A3.** Cells that are **more than minimally manipulated** go through the biologics system via
**PHS Act §351**. *(G2, grade B)*

**A4.** "Minimal manipulation" for cells or nonstructural tissues means processing that does
not alter biological characteristics. *(G2, grade B)*

**A5.** The annex states that *"printing a cell into an engineered matrix is ordinarily well
beyond [minimal manipulation]"*. **This is our inference, not a quoted regulatory position.**
Is it defensible as written?

**A6.** **CBER** for biologics, **CDRH** for devices; combination products settled by a
**Request for Designation**. *(G2 grade B, G4 grade E)*

**A7.** **cGTP** (21 CFR 1271 subpart D) governs methods, facilities, controls, recordkeeping
and the quality programme for HCT/P establishments. *(G5, grade A)*

**A8.** **RMAT** designation created in 2016. *(R6, grade B)*

### European Union

**A9.** Regulation (EC) No 1394/2007 came into force **30 December 2008**. *(G1, grade E)*

**A10.** **Article 2(1)(d)** defines a *combined ATMP*: a substantially manipulated cell
product presented for tissue regeneration containing, as an integral part, scaffold material
performing a device function. *(G6, grade B)*

**A11.** The combined-ATMP route applies **unless** the cell/tissue component is non-viable
and its action is ancillary to the device. The annex then concludes *"a cell-laden construct
is viable by construction, so this exemption will rarely apply here"* — **our inference.**
Defensible? *(G1, grade E)*

**A12.** Premarket review is delegated to the **Committee for Advanced Therapies (CAT)**,
which issues an opinion to the Commission. *(R6, grade B)*

**A13.** MDR **Regulation (EU) 2017/745** governs the device component of a combined ATMP.

### Australia

**A14.** Tissue-engineered products are typically **Class 3 or Class 4 biologicals** depending
on manipulation and risk; compliance with **ARGB** and inclusion in the **ARTG** required
before supply. *(R6, grade B)*

### Standards

**A15.** ASTM F3659-24 cross-references Guide F2150, Guide F2027 and the ISO 10993 series.
*(R1, grade A — cited from the abstract and table of contents, not the full text.)*

**A16.** The annex says `contactduration` and `contactnature` are *"the inputs to ISO 10993
categorisation"*. Is that the right characterisation of how 10993-1 categorises devices?

---

## Part B — Are the fields the right fields?

This is where a reviewer adds most value. The schema forces certain vocabularies; if they are
wrong, every package built with it inherits the error.

**B1. `intendeduse`** — `research-only`, `in-vitro-model`, `drug-screening`, `preclinical`,
`clinical-investigation`, `implantable`, `veterinary`, `education`.
Does this partition intended use in a way a regulator would recognise? What is missing?
(Candidates we considered and dropped: *diagnostic*, *cosmetic testing*, *food*.)

**B2. `determination`** — `confirmed-by-authority`, `advice-sought`, `self-assessed`,
`undetermined`, `not-applicable`.
This is the load-bearing field. **Does it capture the states a regulatory position can
actually be in?** Is `advice-sought` meaningfully different from `undetermined` in practice?

**B3. `contactduration`** — `none`, `limited`, `prolonged`, `permanent`.
**`contactnature`** — `none`, `surface`, `external-communicating`, `implant`.
These mirror ISO 10993-1 categorisation. Are the values right, and are the boundaries where
10993 puts them?

**B4. `obligation status`** — `met`, `partial`, `not-met`, `not-applicable`, `unknown`.
Is `partial` meaningful, or does it invite exactly the vagueness a QA system should forbid?

**B5. `standardref applies`** — free text, so a standard can be marked *relevant but not yet
engaged*. Right call, or should it be constrained?

**B6.** `<b:jurisdiction framework>` is a **free token** rather than an enumeration,
deliberately, because not all authorities use the term "ATMP" and a closed list would force a
mapping the field has not settled. Right call?

**B7. What field is missing entirely?** Notified body, GMP status, manufacturing site,
batch/lot release, clinical trial authorisation number, MDR classification class, UDI —
which of these should be first-class, and which belong in a quality system rather than a
design file?

---

## Part C — Is the posture safe?

**C1.** The project asserts **no acceptance thresholds anywhere** — no viability floor, no
endotoxin limit. `acceptance` is a required attribute so each lab states its own. Is that the
right call, or does refusing to give any guidance create its own risk?

**C2.** `DISCLAIMER.md` states that filling these fields **is not compliance**. Is the wording
strong enough, and is it in the right places?

**C3.** Conformance classes are named **Bio-Core / Bio-Traceable / Bio-Reproducible** and
describe *data completeness only*. Could a reader mistake "Bio-Reproducible" for a quality
claim? Would different names be safer?

**C4.** Rule **R5** requires `determination="undetermined"` to link to a tracked open item.
Rule **R6** warns when a regulated intended use rests only on self-assessment. Rules **R7/R8**
require an ISO 10993 reference plus contact categorisation for `implantable` and
`clinical-investigation`. **Are these the right things to enforce, and are any of them wrong
to enforce?**

**C5.** Is there any way this format could be **misused to imply compliance** that we have not
guarded against?

---

## Known weaknesses, stated upfront

| Issue | Detail |
|---|---|
| **Two grade-E sources carry load** | G1 (EU pathways) is an industry white paper; G4 (FDA scheme overview) is a law-firm summary. Claims **A1, A2, A9, A11** rest on them. These need replacing with primary text, and that is the single most valuable thing a reviewer could redirect. |
| **No standard read in full** | ASTM F3659-24, ISO/ASTM 52900, 52902 and ISO 10993 are cited from abstracts, published definitions and secondary descriptions. Scope and titles are reliable; **no clause requirements are quoted or asserted.** |
| **Two inferences flagged, not sourced** | A5 and A11 are our reasoning from sourced premises, not positions taken from a regulator. |
| **Australia is thinnest** | A14 rests on a single grade-B source and no primary ARGB reading. |
| **No jurisdiction outside US/EU/AU** | UK post-Brexit, Canada, Japan, China are absent. Is that an acceptable v1 scope? |

---

## How to return the review

Whichever is easiest:

- **Annotate this file** and send it back — every item is numbered for that.
- **Open issues** using `.github/ISSUE_TEMPLATE/fact-check.md`, one per disputed claim.
- **A note listing item numbers** and what is wrong with each.

If a claim cannot be verified, the correct outcome is **not** deletion — it is an open item
with `kind="unverified"`, so the gap stays visible. That is the whole design.

### What happens to your review

Corrections go into `dossier/Fact-Check.md`, which already records one case where a
widely-copied chemical identifier turned out to describe the wrong species. Findings are
credited unless you would rather not be. **Nothing here is defended on the grounds that it
took effort to write.**
