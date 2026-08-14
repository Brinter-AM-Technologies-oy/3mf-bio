# Review packs

Two things need outside eyes before this is worth relying on. Both are named in
`SUBMISSION.md`; these files make them concrete rather than aspirational.

| Pack | For | Time |
|---|---|---|
| [REGULATORY-REVIEW.md](REGULATORY-REVIEW.md) | A regulatory affairs professional | 2–3 hours |
| [DATASET-SHEET.md](DATASET-SHEET.md) | Whoever runs a real build | One build + assays |

## Why these two and nothing else

Everything else in this repository can be checked by machine, and is: 54 injected faults, two
validators, 15 modality templates, a red-team suite, a round-trip test.

These two cannot be.

**The regulatory annex** is a map of which instruments exist. A validator cannot tell whether
the map is accurate. Two claims currently rest on grade-E sources — an industry white paper
and a law-firm summary — and two more are our own inference from sourced premises rather than
positions taken from a regulator. All four are marked in the pack.

**The dataset gap** is more fundamental. The schema has never held a real measurement. Every
example is a template. That means the one thing untested is whether the fields are the right
fields when someone sits down with real data in front of them — and no amount of fault
injection produces that answer.

## What a reviewer is not being asked

Not to approve anything. Not to certify. Not to endorse. There is no product here and the
project asserts no thresholds.

The regulatory reviewer is asked whether a map is accurate and whether the fields are the
right fields. The person running a build is asked to fill fields in and **report every place
the schema got in the way**.

## The most useful outcome

For the regulatory pack: "claim A11 is wrong, and here is why."

For the dataset sheet: "there is no field for X", or "field Y exists but does not fit what I
actually measured", or "rule Z fired and should not have".

Those are defect reports the test suite cannot generate. They are worth more than agreement.

`.github/ISSUE_TEMPLATE/fact-check.md` and `.github/ISSUE_TEMPLATE/spec-defect.md` exist for
exactly this.
