# Disclaimer

## This is not a standard, and not a 3MF Consortium specification

This repository is an **open schema**, published for anyone to use, fork and modify. It has
not been submitted to, reviewed by, or endorsed by the 3MF Consortium, and it is not on a
path to becoming an official extension. It follows their structural and schema conventions
because that keeps packages readable by ordinary 3MF tools — a compatibility decision, not a
claim of affiliation.

The namespace is `https://3mfbio.com/ns/bio/2026/07`. It is a URN rather than an `https://schemas.3mf.io/…`
URI specifically so that it squats on nobody's domain. Change it with
`python3 spec/set_namespace.py <your-uri>` if you want one you control.

3MF Core and its extensions are ISO/IEC 25422:2025. This schema is not part of that
standard and makes no claim to be.

## Filling these fields is not compliance

The schema provides fields for regulatory context, calibration, standards references and
characterization. **Populating them does not make a product compliant with anything.** They
exist so that a laboratory or manufacturer can record, against their own audit criteria and
their own roadmap, what they did and why. The judgement remains theirs.

## This is not regulatory advice

`dossier/Regulatory-Annex.md` maps which instruments exist and which fields this format
reserves for recording a determination. It does not classify any product.

Classification of a specific construct depends on intended use, degree of cell
manipulation, and whether a scaffold component performs a device function — and is a matter
for the manufacturer and the competent authority. Nothing here substitutes for that.

The format's contribution is narrower and, we would argue, more useful: it makes a
determination **explicit and traceable**, including when it has not been made. That is what
`determination="undetermined"` plus a linked open item exists for.

## This is not clinical or laboratory guidance

Parameter and calibration dossiers catalogue what to *record* and cite sources establishing
why each parameter is process-relevant. **They do not recommend settings.** Numeric values
quoted from publications are labelled with their source and context and are examples of what
a real record looks like — not settings for your machine, your ink, or your cells.

No acceptance thresholds are asserted anywhere in this project. Viability floors, endotoxin
limits, dimensional tolerances and sterility assurance levels are application- and
jurisdiction-specific. `acceptance` is a required attribute precisely so that each
laboratory states its own and is held to it.

## Conformance is about data, not safety

The conformance classes — Bio-Core, Bio-Traceable, Bio-Reproducible — describe **data
completeness**. A package can be Bio-Reproducible and still be unsafe, unapproved, and
nowhere near a regulatory submission. A validator that reports zero errors is telling you
the record is well-formed and self-consistent, not that the process is sound.

## Verification status

`dossier/Fact-Check.md` records what was verified, against what, and what could not be.
Paywalled standards are cited from abstracts, published definitions and secondary
descriptions; scope and titles are reliable, and no specific clause requirements are
quoted or asserted.

Claims that could not be confirmed are carried as `<b:openitem kind="unverified">` rather
than removed or softened. If you find an error, please open a `fact-check` issue —
one such correction is already recorded in the changelog.
