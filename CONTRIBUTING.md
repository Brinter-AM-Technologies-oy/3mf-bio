# Contributing

## The one rule that matters

**Nothing gets a number without a source.**

This extension exists because biofabrication data routinely loses the provenance of its own
parameters. If a contribution adds a value, it must say where the value came from. If it
adds a *parameter*, it must cite a source establishing that the parameter is
process-relevant — the source justifies the parameter, not the value.

Concretely: every `<b:param>` carries `provenance`. If you cannot honestly mark a value
`measured`, `cited`, `derived` or `vendor`, mark it `estimated` and open a
`<b:openitem>` for it. That is a valid, expected outcome — not a failure.

## Before you open a PR

```bash
pip install lxml
python3 spec/validate_schema.py    examples   # XSD structure
python3 spec/validate_bio.py       examples   # rules, all of them
python3 spec/conformance_tests.py             # fault injection, both engines
```

All three must be clean. CI runs the same chain.

## Adding a rule

A rule lives in up to three places. Adding it to only one is the commonest mistake.

1. **`spec/bio.xsd`** — if it is expressible as structure or a type.
2. **`spec/bio.sch`** — if it is an intra-document rule. Most are.
3. **`spec/validate_bio.py`** — always, plus the cross-part rules Schematron cannot see.
4. **`spec/conformance_tests.py`** — a negative test. **Not optional.**

### Why the negative test is not optional

Three Schematron rules in this repository were once silently dead. They compiled without
error and validated the good example without complaint, and caught nothing at all, because
within a `<sch:pattern>` only the *first* matching `<sch:rule>` fires for a node and a
broader context earlier in the same pattern shadowed them. Nothing revealed this except
injecting the faults they were supposed to catch.

A rule with no negative test should be assumed not to work.

### Rule naming

| Prefix | Domain |
|---|---|
| `V` | provenance / evidence |
| `E` | evidence resources and bibliography |
| `S` | substances and synthesis |
| `C` | cells |
| `I` | inks and their references |
| `P` | process and modality parameters |
| `T` | toolpaths |
| `G` | geometry binding |
| `F` | volumetric field bindings |
| `K` | calibration |
| `R` | regulatory and results |
| `J` | open items |
| `N` | ISO/ASTM 52900 crosswalk |
| `X`, `O` | model integrity, OPC package |

MUST-level rules are errors. SHOULD-level are warnings. Be sparing with MUST: it makes
existing valid packages invalid.

## Adding a modality

`ST_Modality` is a closed vocabulary, deliberately. To add one:

1. Add the enumeration value to `bio.xsd`.
2. Add its required-parameter set to `REQUIRED` in `validate_bio.py` **and** a pattern in
   `bio.sch`.
3. Add its calibration expectations to `CALIBRATION_EXPECTED`.
4. Add a section to `dossier/Parameter-Dossier.md` and
   `dossier/Calibration-Dossier.md`, with sources.
5. Map it in `ISO52900` **only if the category is unambiguous.** Leaving it unmapped is
   better than forcing a category. Several modalities are deliberately unmapped.

If you cannot do steps 4 and 5 honestly, the modality is not ready. Vendor-specific
processes can use an `x-` prefix without touching the schema.

## Changing the schema

`spec/bio.xsd` is canonical. `spec/bio.libxml.xsd` is **generated** — do not edit it. After
changing the canonical schema:

```bash
python3 - <<'PY'
s = open("spec/bio.xsd").read()
hdr = open("spec/bio.libxml.xsd").read().split('<xs:schema', 1)[0]
open("spec/bio.libxml.xsd", "w").write(
    hdr + s.split("\n", 1)[1].replace('maxOccurs="2147483647"', 'maxOccurs="unbounded"'))
PY
```

CI checks the two are in sync. The variant exists because libxml2 uses 2^30 as its internal
UNBOUNDED sentinel and rejects the `maxOccurs="2147483647"` that the 3MF Consortium schemas
use, though it is valid XSD.

## Fact-checks and corrections

Challenges to factual claims are welcome and are tracked with the `fact-check` label.
`dossier/Fact-Check.md` already records a case where a widely-copied chemical identifier
described the wrong species. Finding another such error is a contribution, not an
embarrassment.

If a claim cannot be verified, the correct outcome is an `<b:openitem>` with
`kind="unverified"` — **not** removal, and not a softened phrasing that hides the gap.

## Style

- Follow the 3MF Consortium schema conventions already in the files: `CT_`/`ST_` naming,
  unqualified forms, globals by `ref`, `anyAttribute namespace="##other"` on every complex
  type.
- Specification prose follows the published 3MF extension document structure.
- Explain *why* a rule exists where the reason is not obvious. Most of the rules encode a
  specific failure mode; say which one.

## Scope

In scope: the schema, validators, specification, dossiers, examples.

Out of scope: acceptance thresholds. This project does not assert that viability must
exceed some percentage or that endotoxin must be below some limit. Those are
application- and jurisdiction-specific, and asserting them would be exactly the invention
the format exists to prevent. `acceptance` is a required attribute so that each laboratory
states its own.
