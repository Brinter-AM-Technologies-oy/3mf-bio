> **See [PUBLISH.md](PUBLISH.md) for the whole path in order.** This file covers hosting, DNS and the namespace in more
> detail and remains accurate.

# Deploying 3mfbio.com

Everything is committed and the site builds. Three things remain, and two of them need
credentials or DNS that only you have.

---

## 1. Push the repository

```bash
cd 3mf-bio
git remote add origin git@github.com:YOUR-ORG/3mf-bio.git
git branch -M main
git push -u origin main
```

Then replace the placeholder in three places — a quick sweep:

```bash
grep -rln "Brinter-AM-Technologies-oy/3mf-bio" . | xargs sed -i 's|Brinter-AM-Technologies-oy/3mf-bio|YOUR-ORG/3mf-bio|g'
git commit -am "Point links at the real repository"
git push
```

## 2. Turn on GitHub Pages

**Settings → Pages → Build and deployment → Source: GitHub Actions.**

Do not pick "Deploy from a branch". The workflow in `.github/workflows/pages.yml` builds the
site from source and uploads it as an artifact; a branch deploy would publish the repository
instead of the built site.

The first push to `main` triggers it. Two workflows run:

| Workflow | Does |
|---|---|
| `validate.yml` | Schema, both validators, 54 injected faults, modality corpus, round-trip, integrator |
| `pages.yml` | **Re-runs the validation gate**, rebuilds the `.3mf` artifacts, builds the site, deploys |

The gate in `pages.yml` is deliberate. A site documenting a schema whose own examples do not
validate is worse than no site, so publication fails rather than shipping something broken.

## 3. Point the DNS

`site/build_site.py` writes a `CNAME` file containing `3mfbio.com`, so Pages will claim the
domain once DNS resolves.

At your registrar, for the apex domain:

```
A     3mfbio.com    185.199.108.153
A     3mfbio.com    185.199.109.153
A     3mfbio.com    185.199.110.153
A     3mfbio.com    185.199.111.153
```

And for the `www` subdomain:

```
CNAME www.3mfbio.com    brinter-am-technologies-oy.github.io
```

Then **Settings → Pages → Custom domain → `3mfbio.com`**, and tick **Enforce HTTPS** once the
certificate is issued (usually minutes, occasionally an hour).

> Verify those IP addresses against GitHub's current documentation before relying on them.
> They have been stable for years but they are GitHub's to change, and this file is not
> authoritative.

---

## Why the namespace changed, and how to undo it

The XML namespace moved from `urn:3mf-bio:2026-07` to **`https://3mfbio.com/ns/bio/2026/07`**.

The URN was chosen earlier precisely because it squatted on nobody's domain. Once you control
a domain, an `https` URI is better: it follows 3MF Consortium convention, and — the part most
projects skip — **it resolves**. The site serves a real page at that path, linking the schema,
the Schematron and the specification. A namespace that returns 404 is a broken promise to
anyone who pastes it into a browser to find out what it means. `pages.yml` asserts those files
exist before deploying.

**This assumes you actually control `3mfbio.com`.** If that falls through, one command
reverses it across the whole repository:

```bash
python3 spec/set_namespace.py urn:3mf-bio:2026-07
python3 spec/make_conformance_corpus.py
python3 spec/conformance_tests.py
```

---

## What the site contains

| Path | |
|---|---|
| `/` | Landing page: the one rule, what a package holds, three commands from an STL, and an honest section on what it does not do |
| `/spec/` | The specification, rendered with a table of contents |
| `/dossier/` | Parameters, calibration, regulatory, references, fact check |
| `/tools/` | Integrator and viewer documentation |
| `/viewer/` | **The working viewer.** Drop a `.3mf` on it — no server, nothing uploaded |
| `/download/` | Schema files and both example packages |
| `/ns/bio/2026/07/` | The namespace document |
| `/scope/`, `/submission/`, `/changelog/`, `/disclaimer/`, `/security/`, `/contributing/` | Repository documents |

Rebuild and preview locally:

```bash
pip install markdown lxml
python3 site/build_site.py --serve      # http://localhost:8000
```

18 pages, 0 broken internal links at last build.

---

## Before you announce it

Two things worth doing first, both from `SUBMISSION.md`:

1. **Get a regulatory professional to read `dossier/Regulatory-Annex.md`.** It is correct as a
   map of which instruments exist, and nobody qualified has reviewed it.
2. **Record one real dataset.** Every example in the repository is a template or an
   illustration. A format for recording real data that has never recorded real data is
   untested exactly where it matters, and this is the one gap that open licensing does not
   close.

Neither blocks publishing a clearly-labelled draft, which is what the site says it is. But the
first person who tries to use this in anger will find whichever of the two you skipped.
