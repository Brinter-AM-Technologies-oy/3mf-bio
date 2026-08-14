> **See [PUBLISH.md](PUBLISH.md) for the whole path in order.** This file covers the five pre-push blockers in more
> detail and remains accurate.

# Before the first push

Six things. Four are one command each; two need a decision only you can make.

Run the sweep at the bottom to confirm none are outstanding.

---

## 0. Decide who owns this — before anything else

The other items are mechanical. This one is not, and it determines the answers to items 2 and
3.

**Which email address you use does not decide ownership.** Copyright follows from your
employment agreement and the circumstances the work was done in — on whose time, with whose
equipment, within whose scope of employment. Using a personal address on work your employer
owns does not make it yours; using a company address on work you own personally does not make
it theirs. What the address does is create *evidence*, and evidence pointing the wrong way is
worth avoiding.

**The reason to settle it now rather than later:** the licences here are irrevocable. BSD-2
cannot be withdrawn from anyone who already has the code, and CC0 on the schema files is a
dedication to the public domain — the most irreversible grant there is. If your employer owns
this and you publish it without authorisation, that is not something a later commit fixes.

So, in whichever direction, **get one line in writing** from whoever handles IP:

> Confirming the company is content for the 3MF Bio schema and tooling to be released
> publicly under BSD-2-Clause, with the schema files additionally under CC0.

An email reply is enough. It costs an afternoon and removes the only category of problem here
that cannot be undone.

### Then the practical shape follows

| If | Repository | Git email | LICENSE holder |
|---|---|---|---|
| Company work, company content to publish | Company org | Company address | The company |
| Personal work, personal time and equipment | Personal account | Personal address | You |
| Company work, company *not* content | **Do not publish yet** | — | — |

The combination worth avoiding is a personal repository with a company email address, or the
reverse. It muddles the record in exactly the place you would later want it clear.

**Copyright holder and author are different things**, and `CITATION.cff` is separate from
`LICENSE` for this reason. A company can hold the copyright while you are named as the author
and cited by name in papers. That is the normal arrangement for institutional work and is
probably what you want.

Also worth noting: whoever paid for `3mfbio.com` is another signal in the same direction.

*Not legal advice. The point is that the question has an answer and it is cheaper to get it
now.*

---

## Do all four at once

```bash
python3 tools/setup_repo.py
```

It prompts for each, validates as it goes, and refuses to leave the tree half-configured. It
also rewrites the commit authorship, which currently carries a placeholder address — author
identity is baked into every commit object, so it cannot be fixed by editing files. That
rewrite is free before the first push and disruptive afterwards.

Non-interactive form:

```bash
python3 tools/setup_repo.py \
  --git-name "Your Name" --git-email "you@yourcompany.com" \
  --repo yourorg/3mf-bio \
  --copyright "Your Institution" \
  --author "Surname, Given, 0000-0002-1825-0097, Your Institution" \
  --security github
```

`--dry-run` shows what would change without writing. `--check` reports what is outstanding.

---

## 1. Repository slug

Two source files link to `OWNER/3mf-bio`, which does not exist: `site/build_site.py` (the
footer and source link on every generated page) and `DEPLOY.md`. Seventeen files in
`site/_build/` also contain it, but those are generated — fixing the source fixes them on the
next build, which is why the script only touches two.

## 2. Copyright holder

`LICENSE` says **"3MF Bio Extension contributors"**. That is a placeholder, not a decision,
and it is a legal statement rather than a label.

**If this work was done under employment or a grant, your employer or institution may own the
copyright regardless of who wrote it.** Worth five minutes with your IP policy now rather than
after publication, when changing it means changing what you already told people.

## 3. Citation authors

`CITATION.cff` decides how anyone citing this in a paper credits it. Same placeholder.

Give at least family and given names; ORCID and affiliation are optional but an ORCID makes
the citation resolvable — without one nobody can disambiguate a common surname. The script
validates that the file stays valid YAML/CFF, because if it stops parsing GitHub silently
drops the citation widget and nobody notices until someone tries to cite you.

Repeat `--author` for each person.

## 4. Security reporting channel

`SECURITY.md` asks people to report privately and gives them **no private route**.
`CODE_OF_CONDUCT.md` has the same gap.

`--security github` is the better answer: it points at GitHub's private advisory button, so
there is no address to maintain and reports thread into the repository. **You still have to
turn it on** — Settings → Code security → Private vulnerability reporting → Enable. The
script reminds you.

Otherwise pass an email address.

---

## 5. Get a DOI, before anyone cites it

Link the repo to Zenodo (**zenodo.org → GitHub → flip the switch on the repository**), then
cut a release. Zenodo mints a DOI and archives the tag.

Do this **before** announcing, not after. A DOI minted later does not retroactively cover the
version people already cited, and this project asks others to cite their sources properly —
it should be citable itself.

Then add the DOI to `CITATION.cff` and the README badge.

## 6. Decide what "0.9.0" promises

The version now appears consistently in six places, and CI fails if they drift. But nothing
states what a version *means*. Before others build against it, say so — three lines in the
README is enough. A suggestion:

> Pre-1.0. Minor versions may change the schema in ways that invalidate existing packages.
> `b:SpecVersion` is required in every package so a consumer can tell what it is reading.
> From 1.0, minor versions will be additive only.

---

## Sweep

```bash
# 1. no placeholders left
grep -rn "OWNER/3mf-bio\|YOUR-ORG\|you@example.com" . --exclude-dir=.git --exclude=FIRST-PUSH.md \
  && echo "PLACEHOLDERS REMAIN" || echo "ok: no placeholders"

# 2. attribution decided
grep -q "contributors" CITATION.cff && echo "TODO: CITATION.cff authors" || echo "ok: authors named"

# 3. security contact
grep -qiE "@|private vulnerability reporting" SECURITY.md \
  && echo "ok: security contact" || echo "TODO: no way to report a vulnerability"

# 4. everything still passes
python3 spec/validate_bio.py examples
python3 spec/validate_bio.py examples-extrusion
python3 spec/conformance_tests.py
python3 tools/test_tools.py
python3 site/build_site.py
```

---

## Not blocking, but the first thing anyone will ask

**No real dataset has been recorded in this schema.** Every example is a template or an
illustration. That is stated plainly in the README, `SCOPE.md` and `SUBMISSION.md`, so
publishing is honest — but the first person who tries to use this seriously will hit it, and
it is the one gap that open licensing does not close.

`SUBMISSION.md` §4 lists exactly what one complete exemplar needs. The single most valuable
addition to this repository is one real build, recorded end to end, **including at least one
result that fails its acceptance criterion**. A dossier containing only passes is not evidence
that the criteria bite.

The second is a regulatory professional reading `dossier/Regulatory-Annex.md`. It is correct
as a map of which instruments exist. Nobody qualified has checked it.
