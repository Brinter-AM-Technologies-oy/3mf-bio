# Publishing without a command line

Everything below is done in **GitHub Desktop** and your **browser**. No terminal.

You already have the hard part done: the repository exists at
`Brinter-AM-Technologies-oy/3mf-bio`, public and empty.

---

## Step 1 — Set your name and email in Desktop

**Do this before committing anything**, because Desktop stamps every commit with whatever is
configured here, and changing it afterwards means rewriting history.

- **Windows:** File → Options → Git
- **Mac:** GitHub Desktop → Settings → Git

Set:

```
Name:   Brinter AM Technologies Oy
Email:  contact@brinteram.com
```

> Commits authored to a company address show with a generic avatar rather than linking to a
> personal profile, unless that address is verified on a GitHub account. That is a perfectly
> normal choice for company-owned work — and `CITATION.cff` credits you personally, with your
> ORCID, which is the part that matters for academic credit.
>
> If you would rather commits link to you, use your personal Brinter address here instead.
> The copyright holder in `LICENSE` stays Brinter AM Technologies Oy either way.

## Step 2 — Clone the empty repository

In Desktop: **File → Clone repository → GitHub.com** tab.

Pick `Brinter-AM-Technologies-oy/3mf-bio`, choose where to put it, **Clone**.

You now have an empty folder that Desktop is watching. Note the path it tells you — something
like `C:\Users\you\Documents\GitHub\3mf-bio`.

## Step 3 — Unzip the files into that folder

Download **`3mf-bio-files.zip`** from this conversation.

**Windows:** right-click → *Extract All* → browse to the cloned `3mf-bio` folder → Extract.
**Mac:** double-click to unzip, then drag everything from inside into the cloned folder.

> **Get the nesting right.** You want `3mf-bio/README.md`, **not**
> `3mf-bio/3mf-bio-files/README.md`. If you end up with an extra folder in between, open it,
> select all, and move the contents up one level.

### The one thing that goes wrong

The zip contains a folder called **`.github`** — starting with a dot. It holds the automated
checks, and **without it nothing runs and the website never builds.**

Windows and Mac hide dotted names by default. *Extract All* and unzipping handle them fine;
manually dragging a selection in Explorer or Finder often does not.

**Verify in the next step**, where it is easy to spot.

## Step 4 — Check Desktop sees everything

Switch to GitHub Desktop. The **Changes** tab should now list **78 files** (the two `.3mf` packages are
deliberately excluded — CI rebuilds them from source, so tracking the binaries would let them
drift from the directories they came from).

Scroll to the top of that list. You should see entries beginning `.github/`:

```
.github/ISSUE_TEMPLATE/fact-check.md
.github/ISSUE_TEMPLATE/parameter-proposal.md
.github/ISSUE_TEMPLATE/spec-defect.md
.github/pull_request_template.md
.github/workflows/pages.yml
.github/workflows/validate.yml
.gitignore
```

**If the count is below 70, or you see no `.github/` entries**, the hidden folder did not
copy. Go back, turn on hidden files (Explorer: *View → Show → Hidden items*; Finder:
**⌘ ⇧ .**), and copy it across.

## Step 5 — Commit

Bottom left of Desktop, in the **Summary** box:

```
3MF Bio v0.9.0: open schema for recording biofabrication end to end
```

And in **Description**, optionally:

```
Schema, ISO Schematron rules, two validators, conformance corpus, red-team suite,
parameter/calibration/regulatory dossiers with 79 graded sources, questionnaire and
STL/OBJ integrator, browser viewer, static site, and two worked exemplars.

Not a standard; asserts no acceptance thresholds.
```

Click **Commit to main**.

> Confirm the button says **main**, not *master*. If it says master: **Branch → Rename
> branch** → `main`. The automated checks only run on `main`, and on `master` they would
> silently never fire.

## Step 6 — Push

Click **Push origin** in the top toolbar.

That is the publication done. Refresh
<https://github.com/Brinter-AM-Technologies-oy/3mf-bio> and the README should be rendering.

---

## Step 7 — Two settings, in the browser

On the repository page, **Settings**:

**a) Pages** — left sidebar → *Pages* → Build and deployment → **Source: GitHub Actions**.

Not *Deploy from a branch*. That would publish the raw repository instead of the built
website.

**b) Private vulnerability reporting** — left sidebar → *Code security* → find **Private
vulnerability reporting** → **Enable**.

`SECURITY.md` tells people to use that button, so it has to exist.

## Step 8 — Watch the checks

Click the **Actions** tab. Two workflows will be running:

| | |
|---|---|
| **validate** | Schema, both validators, 54 deliberate faults, 15 modality templates, round-trip, integrator |
| **pages** | Re-runs all of that, then builds and deploys the website |

Green ticks mean everything passed. **Roughly 2–4 minutes.**

If **pages** fails with a permissions error, it is step 7a — set it, then on the failed run
click **Re-run all jobs**.

---

## Step 9 — DOI

**Before telling anyone about it.** A DOI issued later does not cover the version people have
already cited.

1. Go to <https://zenodo.org>, **Log in → GitHub**, authorise.
2. Top-right menu → **GitHub**. Find `Brinter-AM-Technologies-oy/3mf-bio` in the list and
   flip its switch **ON**. (Hit *Sync now* if it is not listed.)
3. Back on GitHub: repository page → **Releases** (right sidebar) → **Create a new release**
   - **Choose a tag** → type `v0.9.0` → *Create new tag on publish*
   - Title: `3MF Bio v0.9.0`
   - Description: paste the `## [0.9.0]` section from `CHANGELOG.md`
   - **Publish release**
4. Wait a minute, refresh Zenodo. Your DOI is there.

Zenodo gives you **two**: a *version* DOI and a *concept* DOI that always points at the
latest. Copy the **concept** one.

Add it in the browser — no Desktop needed: open `CITATION.cff` on GitHub, click the **pencil**
icon, and under the `version:` line add:

```yaml
doi: "10.5281/zenodo.XXXXXXX"
```

**Commit changes** directly to main.

## Step 10 — The domain

At whoever you registered `3mfbio.com` with, add four **A** records for the bare domain:

```
185.199.108.153
185.199.109.153
185.199.110.153
185.199.111.153
```

and one **CNAME** for `www`:

```
www  →  brinter-am-technologies-oy.github.io
```

Then GitHub → **Settings → Pages → Custom domain** → `3mfbio.com` → Save. Tick **Enforce
HTTPS** once the certificate appears (minutes to an hour).

> Check those four addresses against GitHub's current Pages documentation first — they are
> GitHub's to change.

**Set the domain to auto-renew.** The XML namespace is `https://3mfbio.com/ns/bio/2026/07`
and the site serves the schema at that address. If the registration lapses, every file anyone
has made points at a dead link.

---

## What you will have

- **github.com/Brinter-AM-Technologies-oy/3mf-bio** — the repository, checks running on every
  change
- **3mfbio.com** — 21 pages: specification, dossiers, the working viewer, downloads
- **A DOI** — citable in papers
- **A namespace that resolves** — paste it in a browser and it explains itself

## And then the two asks

1. **`review/REGULATORY-REVIEW.md`** — 28 numbered questions for someone in regulatory
   affairs. 2–3 hours.
2. **`review/DATASET-SHEET.md`** — one real build on a Brinter, recorded completely. Nobody
   has ever put a real measurement in this schema, and you have the printers.

Including, specifically, **one result that fails its acceptance criterion**. A record
containing only passes is evidence the criteria were written after the results were known.
