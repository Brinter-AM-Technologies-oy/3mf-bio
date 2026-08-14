# Getting the DOI

## What has already been ruled out

For this repository, both usual causes were checked and neither applies:

| Checked | Result |
|---|---|
| Organisation third-party application access policy | **No restrictions.** Applications authorised by members already have access to organisation data, so there is nothing to grant |
| Zenodo listed in Authorized OAuth Apps | **Present.** The grant exists |

That eliminates the permission explanation. What remains is on Zenodo's side, and the symptom
matches a known one: the repository is listed, the toggle is inert, and the detail page
returns "Page not found".

**One detail worth acting on:** GitHub reported the Zenodo app as *"Never used"*. A token that
has never been exercised is consistent with a stale or incomplete authorisation, so a single
re-authorisation is worth thirty seconds before giving up on the integration.

1. **<https://github.com/settings/connections/applications/>** → Zenodo → **…** → **Revoke**
2. Sign in again at **<https://zenodo.org>** with GitHub and authorise
3. **<https://zenodo.org/account/settings/github/>** → **Sync now**

If the toggle still does nothing, stop. Take Route B. A DOI is not worth an afternoon spent
on somebody else's OAuth bug, and the result is identical.

---

## Route A — the integration, for reference

Your symptom (repository listed, toggle inert, detail page 404s) has one usual cause:
**Zenodo's OAuth app has not been granted access to the organisation.** Zenodo can see the
repository exists but cannot act on it, so the toggle does nothing and the detail page has
nothing to show.

Zenodo's own support page states the requirements:

> To access GitHub repositories belonging to an organisation you need **Admin permission**
> on those repositories, as an admin of the repository or of the organisation. Ensure the
> OAuth application is granting permissions to your organisational repositories, not only
> your personal ones — under **Organization access** there must be a **green tick** for your
> organisation. After changing permissions you must click **Sync now** in Zenodo.

### Do this

1. **<https://github.com/settings/connections/applications/>** — this is the *personal*
   OAuth settings page, which is easier than the organisation policy route in the docs you
   found.
2. Click **Zenodo**.
3. Scroll to **Organization access**. Next to `Brinter-AM-Technologies-oy` you will see
   either:
   - a **green tick** — already granted, so this is not your problem; or
   - a **Grant** button — click it. You can do this yourself if you own the organisation.
   - a **Request** button — you are not an owner. An owner must approve it, which is the
     flow in the documentation you pasted.
4. Back on **<https://zenodo.org/account/settings/github/>**, click **Sync now**.
5. The toggle should now work.

### If the organisation is not listed at all

The account you linked Zenodo with must be a **member** of the organisation. Commits here
were pushed by `3mfbioadmin`; if you linked Zenodo with a different GitHub account, link the
one that owns the organisation, or add the linked account to it.

---

## Route B — upload manually

Completely legitimate, gives the same kind of DOI, and takes about five minutes. For a first
release it has a real advantage: you control exactly what is archived and what the metadata
says, rather than relying on Zenodo's extraction.

1. **On GitHub**: repository → **Releases** → **Create a new release**
   - tag `v0.9.0`, title `3MF Bio v0.9.0`, publish
   - this is worth doing regardless, so the tag exists
2. Download the release zip: on the release page, **Source code (zip)**
3. **<https://zenodo.org/uploads/new>**
4. Drag the zip in
5. Fill in:

   | Field | Value |
   |---|---|
   | Upload type | Software |
   | Title | 3MF Bio: an open schema for recording biofabrication end to end |
   | Authors | Prakash, Dhayakumar Rajan — ORCID `0000-0003-2941-0604` — Brinter AM Technologies Oy |
   | Description | Paste the first two paragraphs of the README |
   | Version | v0.9.0 |
   | Licence | BSD 2-Clause |
   | Keywords | bioprinting, biofabrication, 3MF, additive manufacturing, file format, reproducibility, provenance |
   | Related identifiers | `https://github.com/Brinter-AM-Technologies-oy/3mf-bio` — *is supplement to*<br>`https://3mfbio.com` — *is documented by* |

6. **Publish**

You can switch to the automatic integration later. Route B does not prevent it.

---

## Either way, then record the DOI

Zenodo issues **two** DOIs: one for this version, and a **concept DOI** that always resolves
to the latest.

Put the **concept** DOI in `CITATION.cff` — edit it on GitHub with the pencil icon, no local
work needed. Under the `version:` line add:

```yaml
doi: "10.5281/zenodo.XXXXXXX"
```

And add a badge at the top of `README.md`:

```markdown
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.XXXXXXX.svg)](https://doi.org/10.5281/zenodo.XXXXXXX)
```

Cite the **version** DOI in papers; point people at the **concept** DOI everywhere else.

---

## About `.zenodo.json`

The repository now contains `.zenodo.json`, which Route A reads to populate the record.
Without it Zenodo infers authorship from commit identities — which here would credit
*Brinter AM Technologies Oy \<contact@brinteram.com\>* as the creator and drop the ORCID
entirely.

Route B ignores the file, because you type the same information into the form.
