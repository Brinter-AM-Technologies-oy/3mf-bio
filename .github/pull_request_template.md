## What this changes

## Checklist

- [ ] `python3 spec/validate_schema.py examples` passes
- [ ] `python3 spec/validate_bio.py examples` reports 0 errors
- [ ] `python3 spec/conformance_tests.py` reports ALL PASS
- [ ] If a rule was added, a negative test was added for it in `spec/conformance_tests.py`
- [ ] If a rule was added, it exists in **both** `validate_bio.py` and `bio.sch`, or the
      Schematron gap is documented as a cross-part rule
- [ ] If `bio.xsd` changed, `bio.libxml.xsd` was regenerated
- [ ] If a factual claim was added, it has an entry in `dossier/References.md` with a grade
- [ ] If something could not be verified, it is an `<b:openitem>` rather than a comment
