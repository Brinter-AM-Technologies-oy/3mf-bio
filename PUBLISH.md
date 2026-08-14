# Publishing

The whole path, in order. Supersedes `FIRST-PUSH.md` and `DEPLOY.md`, which remain for
reference.

**Check where you are at any point:**

```bash
python3 verify.py
```

15 automated checks, the blocker list, and the known gaps. Exit `0` means ready, `2` means
checks pass but a decision is outstanding, `1` means something is broken and you should not
publish.

---

## Current state

```
CHECKS     15/15 passing
BLOCKERS   5 outstanding, all decisions rather than code
GAPS       6 known, documented, not blocking
```

| Check | Result |
|---|---|
| XML Schema compiles, generated variant in sync | pass |
| Both exemplars: structure valid, 0 rule errors | pass |
| Schematron MUST-level assertions | pass |
| Fault injection | **54/54 Python, 49/49 Schematron** |
| Modality corpus (rules must be satisfiable) | **15/15** |
| Round-trip preservation | pass |
| Red team | 6/15 residual — expected, see below |
| Integrator round-trip | 5/5 |
| Site build, internal links | 21 pages, 0 broken |
| Namespace URI serves the schema | pass |
| Version consistency across 6 files | pass, 0.9.0 |
| Viewer has no network egress | pass |

---

# Step 0 — Decide who owns this

**Do this before anything else. It determines steps 2 and 3, and it is the only decision here
that cannot be undone.**

Which email you commit with does not determine ownership. Copyright follows from your
employment agreement and the circumstances the work was done in — whose time, whose equipment,
whose scope. What the address does is create *evidence*.

**The licences are irrevocable.** BSD-2 cannot be withdrawn from anyone who already has the
code, and CC0 on the schema files is a public-domain dedication. If your employer owns this
and you publish without authorisation, no later commit fixes it.

Get one line in writing, either way:

> Confirming the company is content for the 3MF Bio schema and tooling to be released
> publicly under BSD-2-Clause, with the schema files additionally under CC0.

| If | Repository | Git email | LICENSE holder |
|---|---|---|---|
| Company work, company content to publish | Company org | Company | The company |
| Personal time and equipment | Personal account | Personal | You |
| Company work, company not content | **Stop here** | — | — |

**Copyright holder and author are different things.** A company can hold the copyright while
you are named as author in `CITATION.cff` and cited by name in papers. That is the normal
arrangement for institutional work.

*Not legal advice. The point is that the question has an answer and it is cheaper now.*

---

# Step 1 — Configure the repository

```bash
python3 tools/setup_repo.py \
  --git-name  "Your Name" \
  --git-email "you@yourcompany.com" \
  --repo      "yourorg/3mf-bio" \
  --copyright "Your Institution" \
  --author    "Surname, Given, 0000-0002-1825-0097, Your Institution" \
  --security  github
```

Or run it with no arguments and it prompts. `--dry-run` previews, `--check` reports what is
outstanding.

This resolves all five blockers: commit authorship (a history rewrite, free before the first
push and disruptive after), the repository slug in two source files, the copyright holder,
the citation authors, and the security reporting channel.

It validates `CITATION.cff` stays valid YAML as it goes — if CFF stops parsing, GitHub
silently drops the citation widget and nobody notices until someone tries to cite you.

Then:

```bash
python3 verify.py      # expect: 15/15 checks, no blockers
git add -A && git commit -m "Configure repository for publication"
```

---

# Step 2 — Push

```bash
git remote add origin git@github.com:yourorg/3mf-bio.git
git branch -M main
git push -u origin main
```

Then in **Settings**:

- **Pages → Source: GitHub Actions.** Not "Deploy from a branch" — that would publish the
  repository instead of the built site.
- **Code security → Private vulnerability reporting → Enable**, if you chose `--security
  github`. `SECURITY.md` now points at a button that must actually exist.

Two workflows run on push:

| Workflow | Does |
|---|---|
| `validate.yml` | Version consistency, schema, both validators, 54 injected faults, modality corpus, round-trip, integrator, viewer egress |
| `pages.yml` | **Re-runs the validation gate**, rebuilds the `.3mf` artifacts, builds the site, checks internal links, verifies the namespace serves, deploys |

The gate in `pages.yml` is deliberate: a site documenting a schema whose own examples do not
validate is worse than no site, so publication fails rather than shipping something broken.

## Publishing somewhere other than GitHub

The repository is plain git with no GitHub-specific content outside `.github/`. For GitLab,
Codeberg or a self-hosted instance:

- `.github/workflows/*.yml` need translating to that platform's CI. Both are short and the
  steps are ordinary shell.
- `site/build_site.py` output is static HTML — any static host serves it. GitLab Pages wants
  it in `public/`; change `OUT` at the top of the script.
- `CNAME` is a GitHub Pages convention; other hosts configure the domain in their own settings.
- Everything else — schema, validators, tools, dossiers — is platform-neutral.

Mirroring to a second host is worth doing. A schema whose canonical copy lives on one
company's platform is a single point of failure for anyone depending on it.

---

# Step 3 — Get a DOI

**Do this before announcing, not after.** A DOI minted later does not retroactively cover the
version people already cited — and a project that requires others to cite their sources should
be citable itself.

1. Sign in at **zenodo.org** with GitHub.
2. **Account → GitHub**, find the repository, flip the switch **on**.
3. Back on GitHub: **Releases → Create a new release**, tag `v0.9.0`, publish.
4. Zenodo archives the tag and mints a DOI within a minute or two.

Then record it:

```bash
# add to CITATION.cff, above the authors block
#   doi: "10.5281/zenodo.XXXXXXX"
git commit -am "Record the Zenodo DOI"
git push
```

Zenodo issues **two** DOIs: one for the specific version, and a **concept DOI** that always
resolves to the latest. Put the concept DOI in `CITATION.cff` and the README badge; cite the
versioned one in papers.

### Alternatives

| Where | For |
|---|---|
| **Zenodo** | The default. Free, CERN-operated, GitHub integration, versioned DOIs |
| **Software Heritage** | Archival rather than citation. Harvests public repos automatically; worth submitting to as well |
| **figshare** | Similar to Zenodo; some institutions have arrangements |
| **Your institutional repository** | If there is a mandate, this may be required *in addition* |

---

# Step 4 — Point the domain

`site/build_site.py` writes a `CNAME` containing `3mfbio.com`, so Pages claims the domain once
DNS resolves.

At your registrar, for the apex:

```
A     3mfbio.com    185.199.108.153
A     3mfbio.com    185.199.109.153
A     3mfbio.com    185.199.110.153
A     3mfbio.com    185.199.111.153
```

And for `www`:

```
CNAME www.3mfbio.com    brinter-am-technologies-oy.github.io
```

Then **Settings → Pages → Custom domain → `3mfbio.com`**, and tick **Enforce HTTPS** once the
certificate issues.

> Verify those addresses against GitHub's current documentation. They have been stable for
> years but they are GitHub's to change, and this file is not authoritative.

## The namespace must keep resolving

The XML namespace is `https://3mfbio.com/ns/bio/2026/07`, and the site serves a real page
there linking the schema, the Schematron and the specification. **A namespace that 404s is a
broken promise** to anyone who pastes it into a browser to find out what it means. CI asserts
those files exist before deploying.

This means the domain is now load-bearing. If it lapses, every package in the wild has a
dangling namespace. Set the registration to auto-renew.

If the domain falls through, one command reverses it repository-wide:

```bash
python3 spec/set_namespace.py urn:3mf-bio:2026-07
python3 spec/make_conformance_corpus.py && python3 verify.py
```

---

# Step 5 — What to say when you announce it

Lead with the finding, not the schema. The most persuasive thing this project has produced is
not the XSD — it is that **a widely-copied InChIKey for a common bioprinting photoinitiator
describes the wrong protonation state**, found only because the format's own discipline forced
the value to be checked instead of copied. `dossier/Fact-Check.md` §1.

Then the two asks, because they are what the project actually needs:

1. **Someone qualified to read the regulatory annex** — `review/REGULATORY-REVIEW.md`, 28
   numbered items, 2–3 hours.
2. **Someone to record one real build** — `review/DATASET-SHEET.md`. Including, specifically,
   **one result that fails its acceptance criterion**, because a dossier containing only
   passes is evidence the criteria were written after the results were known.

State the gaps plainly. `verify.py` prints them; they are in the README, `SCOPE.md` and
`SUBMISSION.md`. A draft that names its own weaknesses is more credible than one that does
not, and someone will find them anyway.

---

# The six known gaps, in full

These do **not** block publication. They are documented in the repository and printed by
`verify.py`.

**1. No real dataset has been recorded in this schema.** Every exemplar is a template. This is
the one gap open licensing does not close, and it is chicken-and-egg: nobody records a dataset
in a format that is not published.

**2. The regulatory annex has not been professionally reviewed.** Correct as a map of which
instruments exist. Two claims rest on grade-E sources — an industry white paper and a law-firm
summary — and two more are our inference from sourced premises rather than positions taken
from a regulator. All four flagged in the review pack.

**3. Six of fifteen adversarial packages still validate clean.** A real reference cited for an
unrelated claim; an open item "resolved" with vacuous text; an acceptance criterion that
cannot fail. Structurally perfect and semantically false. **No schema will ever catch these**
— it is the boundary of what a format can enforce, and specification Chapter 12 says so
rather than implying a guarantee that does not exist.

**4. Five of twenty modalities are enumerated but unspecified.** Acoustic droplet ejection,
continuous SLA, magnetic levitation, spheroid bioassembly, in-situ. No parameter set, no
evidence base. Either fill them or remove them — open item `modality-evidence-thin`.

**5. Four paywalled standards are cited from abstracts.** ASTM F3659-24, ISO/ASTM 52900,
52902, ISO 10993. Scope and titles are reliable; **no clause requirements are quoted or
asserted anywhere**.

**6. One volumetric attachment mechanism is unverified.** How a core `<object>` attaches a
`<v:volumedata>` resource. The Volumetric specification is ~240 KB and could not be retrieved
in full, so it is flagged rather than guessed — open item `vol-attach-attribute`.

---

# Final sequence

```bash
python3 verify.py                      # 15/15, 5 blockers
python3 tools/setup_repo.py …          # resolve all 5
python3 verify.py                      # expect exit 0
git add -A && git commit -m "Configure repository for publication"
git remote add origin git@github.com:yourorg/3mf-bio.git
git branch -M main && git push -u origin main
# Settings → Pages → Source: GitHub Actions
# Settings → Code security → Private vulnerability reporting → Enable
# zenodo.org → GitHub → enable repo → cut release v0.9.0 → record DOI
# registrar → A records + www CNAME → Settings → Pages → Custom domain
```
