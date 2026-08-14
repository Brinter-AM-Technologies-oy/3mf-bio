# Next steps — GitHub Desktop

The repository is configured and verified. `python3 verify.py` reports **15/15 checks passing,
0 blockers**.

| | |
|---|---|
| Copyright | Brinter AM Technologies Oy |
| Author | Dhayakumar Rajan Prakash — ORCID 0000-0003-2941-0604 |
| Commits | `Brinter AM Technologies Oy <contact@brinteram.com>`, all 11 rewritten |
| Repository | `Brinter-AM-Technologies-oy/3mf-bio` |
| Security | GitHub private vulnerability reporting |

---

## 1. Create the repository on GitHub

**In the browser**, not in Desktop — Desktop's "publish" flow will try to create it under your
personal account, and this belongs to the company.

1. If Brinter has no GitHub organisation yet: **your avatar → Your organizations → New
   organization**. The Free plan is enough. Name it so `Brinter-AM-Technologies-oy/3mf-bio` matches what is
   already written into the files.
2. **New repository** inside that organisation:
   - Name: `3mf-bio`
   - **Public**
   - **Do not** tick "Add a README", "Add .gitignore" or "Choose a license" — all three exist,
     and adding them creates a commit that conflicts with the history you are about to push.

If Brinter's org ends up named something other than `brinter`, tell me and one command fixes
every reference:

```bash
python3 tools/setup_repo.py --repo actualorg/3mf-bio
```

## 2. Add the repository to Desktop

**File → Add local repository**, select the `3mf-bio` folder, **Add repository**.

Desktop will show it with the full history — 11 commits, no uncommitted changes.

## 3. Publish

The repository already exists on GitHub, so **do not use "Publish repository"** — that tries
to create a new one. Point Desktop at the existing remote instead:

**Repository → Repository settings → Remote**, set the primary remote URL to:

```
https://github.com/Brinter-AM-Technologies-oy/3mf-bio.git
```

Save, then click **Push origin** in the toolbar.

If Desktop will not let you add a remote to a repository it did not clone, the command line is
one line and Desktop will pick it up afterwards:

```bash
git remote add origin https://github.com/Brinter-AM-Technologies-oy/3mf-bio.git
git branch -M main
git push -u origin main
```

You will be asked to authenticate. Desktop's credentials work, or use a personal access token
as the password — GitHub stopped accepting account passwords for git operations.

> **Verify the branch is called `main`.** Desktop shows it in the branch dropdown. If it says
> `master`, rename it: **Branch → Rename**, to `main`. The workflows trigger on `main`.

## 4. Turn on two settings

In the repository **Settings** on github.com:

- **Pages → Build and deployment → Source: GitHub Actions.**
  Not "Deploy from a branch" — that publishes the repository instead of the built site.
- **Code security → Private vulnerability reporting → Enable.**
  `SECURITY.md` now points at a button that has to actually exist.

Then check **Actions**. Two workflows run:

| | |
|---|---|
| `validate` | Version consistency, schema, both validators, 54 injected faults, modality corpus, round-trip, integrator, viewer egress |
| `pages` | Re-runs the validation gate, rebuilds the `.3mf` files, builds the site, checks links, verifies the namespace serves, deploys |

Both should go green. If `pages` fails on permissions, it is step 4's Pages setting — set it
and re-run from the Actions tab.

## 5. Zenodo DOI

**Before announcing.** A DOI minted later does not cover the version people already cited.

1. **zenodo.org** → log in with GitHub → **Account → GitHub**
2. Find `Brinter-AM-Technologies-oy/3mf-bio`, flip the switch **on**
3. On GitHub: **Releases → Create a new release**, tag `v0.9.0`, title
   "3MF Bio v0.9.0", publish
4. Zenodo mints a DOI within minutes

Zenodo issues two: a **version DOI** and a **concept DOI** that always resolves to the latest.
Put the concept DOI in `CITATION.cff` and the README badge; cite the version DOI in papers.

```bash
# in CITATION.cff, under version:
#   doi: "10.5281/zenodo.XXXXXXX"
```

Commit and push that from Desktop.

## 6. DNS for 3mfbio.com

At the registrar, apex:

```
A     3mfbio.com    185.199.108.153
A     3mfbio.com    185.199.109.153
A     3mfbio.com    185.199.110.153
A     3mfbio.com    185.199.111.153
```

And `www`:

```
CNAME www.3mfbio.com    brinter-am-technologies-oy.github.io
```

Then **Settings → Pages → Custom domain → `3mfbio.com`**, and **Enforce HTTPS** once the
certificate issues. Verify those addresses against GitHub's current documentation first.

**The domain is now load-bearing.** The XML namespace is
`https://3mfbio.com/ns/bio/2026/07` and the site serves the schema there. If the registration
lapses, every package in the wild has a dangling namespace. Set auto-renew.

---

## Two things worth knowing

### Commits will show as unlinked unless the email is on the account

GitHub links a commit to a profile by matching the author email. Commits are authored as
`contact@brinteram.com`, so unless that address is added and verified on a GitHub account,
they display as an unlinked author with a generic avatar.

Two ways to handle it, both fine:

- **Leave it.** Company-authored commits under a company address is a coherent choice, and
  `CITATION.cff` credits you personally with your ORCID — which is the part that matters for
  academic credit. Copyright holder and author are different things.
- **Link it.** Add `contact@brinteram.com` under **Settings → Emails** on the GitHub account
  that should own the history, and verify it.

### The Brinter profile is now the wrong kind of source

`tools/machine_profiles/brinter.json` was compiled from public product material and press
coverage, and deliberately omits bore sizes, pressure ranges and speeds because they were not
published in a form worth copying.

**Published by Brinter, that compilation is no longer the best available source.** It is
flagged `status: compiled-from-public-sources` with a maintainer note, and it stays flagged
until someone replaces it with figures from the product documentation. Anything else would be
the exact overclaim this project exists to prevent.

---

## And the thing your affiliation actually changes

`review/DATASET-SHEET.md` names the one gap that open licensing cannot close: **no real
measurement has ever been recorded in this schema.** Every exemplar is a template.

I wrote that assuming whoever read it would need to find a bioprinter. You have them.

`examples-extrusion/` is a three-head extrusion build with a coaxial vascular head, a 21-day
perfusion maturation and nine assays — currently **30 estimated parameters, 6 blocking open
items, 19 assay readings with no values**. Running one real build on a Brinter and filling
those in would make this the only bioprinting format with a real dataset recorded in it.

Including, specifically, **one result that fails its acceptance criterion**. A dossier
containing only passes is evidence the criteria were written after the results were known.

The defect reports matter more than the dataset. Every place the schema gets in the way — a
missing field, a field that does not fit, a rule that fires wrongly — is something 54 injected
faults cannot find, and `.github/ISSUE_TEMPLATE/spec-defect.md` exists for exactly that.
