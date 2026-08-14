#!/usr/bin/env python3
"""
Configure the repository for publication: the four things that must be decided before a
first push, done in one pass with validation.

    0. Git author identity  -- commits currently carry a placeholder address
    1. Repository slug      -- 19 files link to a repo that does not exist
    2. Copyright holder     -- LICENSE currently names a placeholder. This is a legal statement
    3. Citation authors     -- CITATION.cff decides how people credit this in papers
    4. Security channel     -- SECURITY.md asks for private reports and gives no private route

Why a script rather than four manual edits: the repository slug alone appears in 19 files,
CITATION.cff must stay valid YAML or GitHub silently stops rendering the citation widget, and
doing this by hand once means doing it wrong once. This is idempotent, validates as it goes,
and refuses to leave the tree half-configured.

Interactive:
    python3 tools/setup_repo.py

Non-interactive (for CI, or a scripted fork):
    python3 tools/setup_repo.py \\
        --repo myorg/3mf-bio \\
        --copyright "Example University" \\
        --author "Surname, Given, 0000-0002-1825-0097, Example University" \\
        --security github

    --author is repeatable. Fields: family, given, ORCID (optional), affiliation (optional).
    --security is 'github' (private vulnerability reporting) or an email address.
    --dry-run shows what would change and writes nothing.
"""
import argparse
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

# Assembled rather than written literally: this script rewrites the placeholder across every
# file, and a literal here would mean the script edits itself on first use.
PLACEHOLDER_REPO = "OWN" + "ER/3mf-bio"
PLACEHOLDER_EMAIL = "you@example.com"
PLACEHOLDER_HOLDER = "3MF Bio Extension contributors"
SKIP_DIRS = {".git", "__pycache__", "_build", "conformance"}
SKIP_FILES = {"FIRST-PUSH.md", "setup_repo.py"}
ORCID_RE = re.compile(r"^\d{4}-\d{4}-\d{4}-\d{3}[\dX]$")


def walk():
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for f in filenames:
            if f in SKIP_FILES or f.endswith((".3mf", ".png", ".pdf", ".bin")):
                continue
            yield os.path.join(dirpath, f)


def read(p):
    try:
        return open(p, encoding="utf-8").read()
    except (UnicodeDecodeError, OSError):
        return None


def rel(p):
    return os.path.relpath(p, ROOT)


# ------------------------------------------------------------------ 1. repository slug

SLUG_RE = re.compile(r"github\.com/([A-Za-z0-9._-]+)/3mf-bio")


def current_slug():
    """Whatever slug the files hold right now, placeholder or not.

    Replacing only the original placeholder means re-running with a corrected slug silently
    does nothing -- which is exactly what happens when an organisation turns out to be named
    something other than the first guess. Detect what is actually there instead.
    """
    seen = {}
    for p in walk():
        s = read(p)
        if s is None:
            continue
        for m in SLUG_RE.findall(s):
            seen[m] = seen.get(m, 0) + 1
    return seen


def set_repo(slug, dry):
    if "/" not in slug or slug.count("/") != 1 or not all(slug.split("/")):
        sys.exit(f"repository must look like 'org/name', got {slug!r}")
    new_org = slug.split("/")[0]
    seen = current_slug()
    orgs = [o for o in seen if o != new_org]
    if not orgs:
        return []
    if len(orgs) > 1:
        sys.exit(f"files disagree about the current slug: {sorted(orgs)}. Fix by hand.")
    old = f"{orgs[0]}/3mf-bio"
    changed = []
    for p in walk():
        s = read(p)
        if s is None or old not in s:
            continue
        changed.append(rel(p))
        if not dry:
            open(p, "w", encoding="utf-8").write(s.replace(old, slug))
    return changed


# ------------------------------------------------------------------ 2. copyright holder

def set_copyright(holder, dry):
    p = os.path.join(ROOT, "LICENSE")
    s = read(p)
    if PLACEHOLDER_HOLDER not in s:
        return []
    if not dry:
        open(p, "w", encoding="utf-8").write(s.replace(PLACEHOLDER_HOLDER, holder, 1))
    return ["LICENSE"]


# ------------------------------------------------------------------ 3. citation authors

def parse_author(spec):
    """'Family, Given, ORCID, Affiliation' -- last two optional."""
    parts = [x.strip() for x in spec.split(",")]
    if len(parts) < 2 or not parts[0] or not parts[1]:
        sys.exit(f"author needs at least 'Family, Given', got {spec!r}")
    a = {"family-names": parts[0], "given-names": parts[1]}
    for extra in parts[2:]:
        if not extra:
            continue
        if ORCID_RE.match(extra):
            a["orcid"] = f"https://orcid.org/{extra}"
        elif extra.startswith("https://orcid.org/"):
            if not ORCID_RE.match(extra.rsplit("/", 1)[-1]):
                sys.exit(f"malformed ORCID: {extra!r}")
            a["orcid"] = extra
        else:
            a["affiliation"] = extra
    return a


def set_authors(authors, dry):
    p = os.path.join(ROOT, "CITATION.cff")
    s = read(p)
    block = "authors:\n"
    for a in authors:
        block += f'  - family-names: "{a["family-names"]}"\n'
        block += f'    given-names: "{a["given-names"]}"\n'
        if "orcid" in a:
            block += f'    orcid: "{a["orcid"]}"\n'
        if "affiliation" in a:
            block += f'    affiliation: "{a["affiliation"]}"\n'
    new = re.sub(r"^authors:\n(?:  .*\n)+", block, s, count=1, flags=re.M)
    if new == s:
        sys.exit("could not locate the authors block in CITATION.cff")

    # CFF is YAML. If this stops parsing, GitHub silently drops the citation widget --
    # a failure nobody notices until someone tries to cite the work.
    try:
        import yaml
        d = yaml.safe_load(new)
        assert d.get("cff-version"), "cff-version missing"
        assert isinstance(d.get("authors"), list) and d["authors"], "authors did not parse"
        for a in d["authors"]:
            assert a.get("family-names") and a.get("given-names"), f"incomplete author: {a}"
    except ImportError:
        print("  note: pyyaml not installed, skipping CITATION.cff validation")
    except Exception as e:
        sys.exit(f"CITATION.cff would become invalid: {e}")

    if not dry:
        open(p, "w", encoding="utf-8").write(new)
    return ["CITATION.cff"]


# ------------------------------------------------------------------ 4. security channel

GH_TEXT = """## Reporting

This repository has **GitHub private vulnerability reporting** enabled. Use the *Report a
vulnerability* button on the Security tab; it creates a private advisory visible only to the
maintainers.

For a vulnerability in the validators, or a way to construct a package that validates clean
while misrepresenting its contents, please use that route rather than opening a public issue,
and allow time for a fix."""

EMAIL_TEXT = """## Reporting

Report privately to **{addr}**.

For a vulnerability in the validators, or a way to construct a package that validates clean
while misrepresenting its contents, please use that address rather than opening a public
issue, and allow time for a fix."""


def set_security(channel, dry):
    changed = []
    p = os.path.join(ROOT, "SECURITY.md")
    s = read(p)
    body = GH_TEXT if channel == "github" else EMAIL_TEXT.format(addr=channel)
    new = re.sub(r"## Reporting\n\n(?:>.*\n)*(?:.*\n)*?(?=\nA package that validates clean)",
                 body + "\n", s, count=1)
    if new == s:
        # fall back: replace from "## Reporting" to the next blank-line paragraph break
        new = re.sub(r"## Reporting\n\n(?:.|\n)*?(?=\n\nA package)", body, s, count=1)
    if new != s:
        changed.append("SECURITY.md")
        if not dry:
            open(p, "w", encoding="utf-8").write(new)

    p = os.path.join(ROOT, "CODE_OF_CONDUCT.md")
    s = read(p)
    if channel == "github":
        line = ("Report concerns privately using the *Report a vulnerability* button on the\n"
                "Security tab, which is visible only to maintainers, or by opening an issue if\n"
                "the matter is not sensitive.")
    else:
        line = (f"Report concerns privately to **{channel}**, or by opening an issue if the\n"
                f"matter is not sensitive.")
    new = re.sub(r"> \*\*Maintainer note.*?\n\nReport concerns to the maintainers via a private "
                 r"channel where one is available, or by\nopening an issue if the matter is not "
                 r"sensitive\.", line, s, flags=re.S)
    if new != s:
        changed.append("CODE_OF_CONDUCT.md")
        if not dry:
            open(p, "w", encoding="utf-8").write(new)
    return changed


# ------------------------------------------------------------------ 0. git identity

def set_git_identity(name, email, dry):
    """Rewrite commit authorship. Safe only while the history is unpushed.

    Author identity is baked into every commit object, so a placeholder address survives
    any amount of editing the files. Rewriting changes every commit hash, which is harmless
    now and disruptive once anyone has cloned.
    """
    import subprocess
    if subprocess.run(["git", "rev-parse", "--git-dir"], cwd=ROOT,
                      capture_output=True).returncode:
        print("  not a git repository, skipping identity")
        return []

    pushed = subprocess.run(["git", "config", "--get-regexp", r"^branch\..*\.remote"],
                            cwd=ROOT, capture_output=True, text=True).stdout.strip()
    if pushed:
        print("  ! this branch already tracks a remote. Rewriting history would change every")
        print("    commit hash and break anyone who has cloned. Setting identity for FUTURE")
        print("    commits only.")
        if not dry:
            subprocess.run(["git", "config", "user.name", name], cwd=ROOT, check=True)
            subprocess.run(["git", "config", "user.email", email], cwd=ROOT, check=True)
        return ["git config (future commits only)"]

    # filter-branch refuses on a dirty tree and says so only on stderr, which is easy to
    # swallow. Check first and say why.
    dirty = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT,
                           capture_output=True, text=True).stdout.strip()
    if dirty and not dry:
        print("  ! working tree has uncommitted changes, so history cannot be rewritten.")
        print("    Commit or stash them first, then re-run. Files:")
        for line in dirty.splitlines()[:5]:
            print("     ", line)
        return []

    n = subprocess.run(["git", "rev-list", "--count", "HEAD"], cwd=ROOT,
                       capture_output=True, text=True).stdout.strip()
    if dry:
        note = " (working tree is dirty; commit or stash first)" if dirty else ""
        return [f"would rewrite authorship on {n} commit(s){note}"]

    subprocess.run(["git", "config", "user.name", name], cwd=ROOT, check=True)
    subprocess.run(["git", "config", "user.email", email], cwd=ROOT, check=True)
    env = os.environ.copy()
    env.update({"GIT_AUTHOR_NAME": name, "GIT_AUTHOR_EMAIL": email,
                "GIT_COMMITTER_NAME": name, "GIT_COMMITTER_EMAIL": email,
                "FILTER_BRANCH_SQUELCH_WARNING": "1"})
    r = subprocess.run(
        ["git", "filter-branch", "-f", "--env-filter",
         f'export GIT_AUTHOR_NAME="{name}" GIT_AUTHOR_EMAIL="{email}" '
         f'GIT_COMMITTER_NAME="{name}" GIT_COMMITTER_EMAIL="{email}"', "--", "--all"],
        cwd=ROOT, capture_output=True, text=True, env=env)
    if r.returncode:
        print("  filter-branch failed:", (r.stderr or r.stdout)[-400:])
        return []
    check = subprocess.run(["git", "log", "--format=%ae"], cwd=ROOT,
                           capture_output=True, text=True).stdout
    if PLACEHOLDER_EMAIL in check:
        print("  ! rewrite reported success but the placeholder address is still present")
        return []
    return [f"rewrote authorship on {n} commit(s), verified"]


# ------------------------------------------------------------------ checks

def outstanding():
    out = []
    import subprocess
    try:
        authors = subprocess.run(["git", "log", "--format=%ae"], cwd=ROOT,
                                 capture_output=True, text=True).stdout
        if PLACEHOLDER_EMAIL in authors:
            out.append(f"commit history carries the placeholder address {PLACEHOLDER_EMAIL}")
    except Exception:
        pass
    n = sum(1 for p in walk() if (s := read(p)) and PLACEHOLDER_REPO in s)
    if n:
        out.append(f"repository slug still placeholder in {n} file(s)")
    seen = current_slug()
    if len(seen) > 1:
        out.append(f"files disagree about the repository slug: {sorted(seen)}")
    if PLACEHOLDER_HOLDER in (read(os.path.join(ROOT, "LICENSE")) or ""):
        out.append("LICENSE still names the placeholder copyright holder")
    if "contributors" in (read(os.path.join(ROOT, "CITATION.cff")) or ""):
        out.append("CITATION.cff still names placeholder authors")
    sec = read(os.path.join(ROOT, "SECURITY.md")) or ""
    if "Maintainer note" in sec or not re.search(r"@|private vulnerability reporting", sec, re.I):
        out.append("SECURITY.md has no reporting channel")
    return out


def prompt():
    print(__doc__.split("Interactive:")[0])
    print("Leave anything blank to skip it and come back later.\n")

    repo = input("1. GitHub repository as org/name  > ").strip()

    print("\n2. Copyright holder for LICENSE.")
    print("   This is a legal statement, not a label. If this work was done under")
    print("   employment or a grant, your employer or institution may own the copyright")
    print("   regardless of who typed it. Worth five minutes with your IP policy now")
    print("   rather than after publication.")
    holder = input("   Holder  > ").strip()

    print("\n3. Citation authors. Format: Family, Given, ORCID, Affiliation")
    print("   ORCID and affiliation optional. An ORCID makes the citation resolvable;")
    print("   without one nobody can disambiguate a common name.")
    print("   Blank line to finish.")
    authors = []
    while True:
        line = input(f"   author {len(authors) + 1}  > ").strip()
        if not line:
            break
        authors.append(line)

    print("\n4. Security reporting channel.")
    print("   'github' enables the private-advisory button (recommended: no address to")
    print("   maintain), or give an email address.")
    sec = input("   Channel  > ").strip()

    return repo, holder, authors, sec


def main():
    ap = argparse.ArgumentParser(add_help=True,
                                 formatter_class=argparse.RawDescriptionHelpFormatter,
                                 description=__doc__)
    ap.add_argument("--repo")
    ap.add_argument("--git-name", help="rewrite commit authorship (safe only before pushing)")
    ap.add_argument("--git-email")
    ap.add_argument("--copyright")
    ap.add_argument("--author", action="append", default=[])
    ap.add_argument("--security")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--check", action="store_true", help="report what is outstanding, change nothing")
    a = ap.parse_args()

    if a.check:
        out = outstanding()
        for o in out:
            print("  [!]", o)
        if not out:
            print("  all four resolved")
        return 1 if out else 0

    repo, holder, authors, sec = a.repo, a.copyright, a.author, a.security
    if not any([repo, holder, authors, sec, a.git_name, a.git_email]):
        repo, holder, authors, sec = prompt()
        if not a.git_name:
            print("\n0. Git commit identity. The 7 existing commits carry a placeholder")
            print("   address. Author identity is baked into every commit object, so this")
            print("   cannot be fixed by editing files -- it needs a history rewrite, which")
            print("   is free now and disruptive once anyone has cloned.")
            a.git_name = input("   Name   > ").strip() or None
            a.git_email = input("   Email  > ").strip() or None

    if sec and sec != "github" and "@" not in sec:
        sys.exit(f"--security must be 'github' or an email address, got {sec!r}")

    changed = []
    if bool(a.git_name) != bool(a.git_email):
        sys.exit("--git-name and --git-email must be given together")
    if a.git_name and a.git_email:
        c = set_git_identity(a.git_name, a.git_email, a.dry_run)
        print(f"\n[0] git identity -> {a.git_name} <{a.git_email}>")
        for x in c:
            print("           ", x)
        changed += c
    if repo:
        c = set_repo(repo, a.dry_run)
        print(f"\n[1] repository -> {repo}   ({len(c)} file(s))")
        changed += c
    if holder:
        c = set_copyright(holder, a.dry_run)
        print(f"[2] copyright  -> {holder}" + ("" if c else "   (already set)"))
        changed += c
    if authors:
        parsed = [parse_author(x) for x in authors]
        c = set_authors(parsed, a.dry_run)
        print(f"[3] authors    -> {len(parsed)} author(s), CITATION.cff validated as CFF/YAML")
        for p in parsed:
            bits = [f"{p['given-names']} {p['family-names']}"]
            if "orcid" in p:
                bits.append(p["orcid"])
            if "affiliation" in p:
                bits.append(p["affiliation"])
            print("            ", " · ".join(bits))
        changed += c
    if sec:
        c = set_security(sec, a.dry_run)
        label = "GitHub private vulnerability reporting" if sec == "github" else sec
        print(f"[4] security   -> {label}   ({len(c)} file(s))")
        changed += c

    if a.dry_run:
        print(f"\ndry run: {len(changed)} file(s) would change, nothing written")
        return 0

    print(f"\n{len(changed)} file(s) written")
    out = outstanding()
    if out:
        print("\nstill outstanding:")
        for o in out:
            print("  [!]", o)
    else:
        print("\nall four resolved. Next:")
        print("  python3 spec/conformance_tests.py")
        print("  python3 site/build_site.py")
        print("  git add -A && git commit -m 'Configure repository for publication'")
        print("  git push -u origin main")
        if sec == "github":
            print("\n  Remember to actually enable it: Settings -> Code security ->")
            print("  Private vulnerability reporting -> Enable")
    return 0


if __name__ == "__main__":
    sys.exit(main())
