# Security

## What "security" means for this project

This repository ships a specification, schemas and validators. The realistic risks are:

1. **Malicious package content.** A `.3mf` is a ZIP. Parsing untrusted packages can expose
   consumers to zip-slip path traversal, zip bombs, and XML external entity (XXE) attacks.
2. **A validator that reports a clean result on a package that is not clean.** For a format
   whose purpose is traceability, a false negative is the serious failure.

## Guidance for implementers

- **Do not resolve external entities.** Disable DTD loading and entity expansion in your XML
  parser. `spec/validate_bio.py` uses the standard library and does not enable them, but a
  hardened implementation should use `defusedxml` or an equivalent.
- **Do not trust `ST_UriReference` paths.** They begin with `/` and are package-relative.
  Normalise and confirm the resolved path stays inside the package before opening anything.
  `validate_bio.py` extracts to a temporary directory; production code should validate
  entry names before extraction.
- **Bound decompression.** Check the uncompressed size before extracting.
- **Treat `checksum` as a claim, not a guarantee.** Rule T1 requires a toolpath checksum so
  process claims are bound to an executed file. Verify it; a recorded hash that nobody
  checks is decoration.
- **Do not execute anything from a package.** Toolpaths are data.

## Reporting

This repository has **GitHub private vulnerability reporting** enabled. Use the *Report a
vulnerability* button on the Security tab; it creates a private advisory visible only to the
maintainers.

For a vulnerability in the validators, or a way to construct a package that validates clean
while misrepresenting its contents, please use that route rather than opening a public issue,
and allow time for a fix.

A package that validates clean while misrepresenting its process is precisely the failure
this project exists to prevent, and such a report is treated as a serious defect.
