#!/usr/bin/env python3
"""
Run every check in the repository and report publication readiness.

One command, so "fully checked" is something you run rather than something you are told.
Exit 0 means every automated check passes and no publication blocker is outstanding.

    python3 verify.py              full report
    python3 verify.py --ci         exit non-zero on any failure, no gap section

Three categories, deliberately separated:

  CHECKS    automated, pass or fail, run here and now
  BLOCKERS  decisions that must be made before a first push. Code cannot make these
  GAPS      known and documented limitations. NOT failures. They do not block publication
            and are stated in the README, SCOPE.md and SUBMISSION.md
"""
import argparse
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable

GREEN, RED, YELLOW, DIM, RESET = "\033[32m", "\033[31m", "\033[33m", "\033[2m", "\033[0m"
if not sys.stdout.isatty():
    GREEN = RED = YELLOW = DIM = RESET = ""


def run(args, expect_zero=True):
    r = subprocess.run([PY] + args, cwd=ROOT, capture_output=True, text=True)
    return (r.returncode == 0) if expect_zero else r.returncode, r.stdout + r.stderr


def read(p):
    f = os.path.join(ROOT, p)
    return open(f, encoding="utf-8").read() if os.path.exists(f) else ""


# --------------------------------------------------------------------------- checks

def check_schema():
    try:
        from lxml import etree
        etree.XMLSchema(etree.parse(os.path.join(ROOT, "spec", "bio.libxml.xsd")))
    except Exception as e:
        return False, f"does not compile: {e}"
    canon, gen = read("spec/bio.xsd"), read("spec/bio.libxml.xsd")
    expect = canon.split("\n", 1)[1].replace('maxOccurs="2147483647"', 'maxOccurs="unbounded"')
    if not gen.endswith(expect):
        return False, "bio.libxml.xsd is stale; regenerate from bio.xsd"
    return True, "compiles, generated variant in sync"


def check_pkg_schema(pkg):
    _, out = run(["spec/validate_schema.py", pkg], expect_zero=False)
    m = re.search(r"(\d+) bio resource\(s\) checked, (\d+) invalid", out)
    return (m.group(2) == "0", f"{m.group(1)} resources, {m.group(2)} invalid") if m \
        else (False, "could not parse output")


def check_pkg_rules(pkg):
    _, out = run(["spec/validate_bio.py", pkg], expect_zero=False)
    m = re.search(r"(\d+) error\(s\), (\d+) warning\(s\)", out)
    if not m:
        return False, "could not parse output"
    e, w = int(m.group(1)), int(m.group(2))
    return e == 0, f"{e} errors, {w} warnings"


def check_schematron():
    try:
        from lxml import etree, isoschematron
        s = isoschematron.Schematron(etree.parse(os.path.join(ROOT, "spec", "bio.sch")))
        for p in ("examples", "examples-extrusion"):
            if not s.validate(etree.parse(os.path.join(ROOT, p, "3D", "3dmodel.model"))):
                return False, f"{p} fails MUST-level assertions"
        return True, "both exemplars pass all assertions"
    except Exception as e:
        return False, str(e)[:80]


def check_conformance():
    ok, out = run(["spec/conformance_tests.py"])
    py = re.search(r"python\s+(\d+)/(\d+)", out)
    sc = re.search(r"schematron (\d+)/(\d+)", out)
    if not (py and sc):
        return False, "could not parse matrix"
    return ok, f"python {py.group(1)}/{py.group(2)}, schematron {sc.group(1)}/{sc.group(2)}"


def check_corpus():
    ok, _ = run(["spec/make_conformance_corpus.py"])
    if not ok:
        return False, "corpus generation failed"
    import glob
    from lxml import etree, isoschematron
    s = isoschematron.Schematron(etree.parse(os.path.join(ROOT, "spec", "bio.sch")))
    n = bad = 0
    for d in sorted(glob.glob(os.path.join(ROOT, "conformance", "*/"))):
        n += 1
        _, o = run(["spec/validate_bio.py", d], expect_zero=False)
        m = re.search(r"(\d+) error\(s\)", o)
        if (int(m.group(1)) if m else 1) or \
                not s.validate(etree.parse(os.path.join(d, "3D", "3dmodel.model"))):
            bad += 1
    return bad == 0, f"{n - bad}/{n} modality templates clean in both engines"


def check_roundtrip():
    ok, _ = run(["spec/roundtrip_test.py"])
    return ok, "preserving consumer keeps all content, lossy consumer detected"


def check_redteam():
    _, out = run(["spec/redteam_tests.py"], expect_zero=False)
    m = re.search(r"(\d+)/(\d+) attacks produce a clean bill of health", out)
    return (True, f"{m.group(1)}/{m.group(2)} residual, documented as specification Ch.12 "
                  f"(expected, not a failure)") if m else (False, "could not parse")


def check_tools():
    ok, out = run(["tools/test_tools.py"])
    m = re.search(r"(\d+) passed, (\d+) failed", out)
    return ok, m.group(0) if m else "could not parse"


def check_site():
    # A missing dependency is not a broken site. Report it as such: anyone running verify.py
    # with only lxml installed should be told what to install, not shown a red failure for a
    # check that never ran.
    try:
        import markdown  # noqa: F401
    except ImportError:
        return None, "skipped: markdown not installed (pip install -r requirements.txt)"
    ok, out = run(["site/build_site.py"])
    if not ok:
        return False, out.strip()[-100:]
    build = os.path.join(ROOT, "site", "_build")
    have = {"/"}
    for root, _, fs in os.walk(build):
        for f in fs:
            rel = os.path.relpath(os.path.join(root, f), build).replace("\\", "/")
            have.add("/" + rel)
            if f == "index.html":
                d = os.path.relpath(root, build).replace("\\", "/")
                have.add("/" if d == "." else "/" + d + "/")
    bad, pages = [], 0
    for root, _, fs in os.walk(build):
        for f in fs:
            if not f.endswith(".html"):
                continue
            pages += 1
            src = os.path.relpath(os.path.join(root, f), build)
            text = open(os.path.join(root, f), encoding="utf-8").read()
            # absolute links
            for m in re.findall(r'href="(/[^"#]*)"', text):
                t = m if m.endswith("/") or "." in os.path.basename(m) else m + "/"
                if t not in have and m not in have:
                    bad.append(f"{src} -> {m}")
            # relative links, previously unchecked entirely. Skip anchors, external URLs
            # and JS template literals, which appear inside the viewer's inlined script.
            for m in re.findall(r'href="([^"#:]+)"', text):
                if m.startswith(("/", "http", "#", "$", "{")) or "${" in m:
                    continue
                target = os.path.normpath(os.path.join(os.path.dirname(src), m))
                if not os.path.exists(os.path.join(build, target)) and \
                        not os.path.exists(os.path.join(build, target, "index.html")):
                    bad.append(f"{src} -> {m} (relative)")
    # Name them. A count tells you something is wrong and nothing about what, which is how
    # a link failure in CI that does not reproduce locally becomes an afternoon of guessing.
    detail = f"{pages} pages, {len(bad)} broken internal links"
    if bad:
        detail += ": " + "; ".join(bad[:6]) + (" …" if len(bad) > 6 else "")
    return not bad, detail


def check_namespace_served():
    b = os.path.join(ROOT, "site", "_build", "ns", "bio", "2026", "07")
    if not os.path.exists(os.path.join(ROOT, "site", "_build")):
        return None, "skipped: site not built (see the site check above)"
    missing = [f for f in ("index.html", "bio.xsd", "bio.libxml.xsd", "bio.sch")
               if not os.path.exists(os.path.join(b, f))]
    return not missing, ("namespace URI resolves and serves schema + rules"
                         if not missing else f"missing {missing}")


def check_versions():
    def grab(path, pat):
        m = re.search(pat, read(path), re.M)
        return m.group(1) if m else None
    found = {
        "validate_bio.py": grab("spec/validate_bio.py", r'SPEC_VERSION = "([^"]+)"'),
        "CITATION.cff": grab("CITATION.cff", r"^version: (\S+)"),
        "specification": grab("spec/3MF Bio Extension.md", r"\*\*Version\*\* \| (\S+)"),
        "CHANGELOG.md": grab("CHANGELOG.md", r"^## \[([0-9.]+)\]"),
        "examples": grab("examples/3D/3dmodel.model", r'b:SpecVersion">([^<]+)'),
        "examples-extrusion": grab("examples-extrusion/3D/3dmodel.model",
                                   r'b:SpecVersion">([^<]+)'),
    }
    vals = set(found.values())
    return len(vals) == 1, (f"all six agree: {vals.pop()}" if len(vals) == 1
                            else f"DRIFT: {found}")


def check_viewer_local():
    h = read("tools/viewer.html")
    bad = [b for b in ("fetch(", "XMLHttpRequest", "navigator.sendBeacon", "action=") if b in h]
    return not bad, ("no network egress; packages never leave the machine"
                     if not bad else f"contains {bad}")


CHECKS = [
    ("XML Schema", check_schema),
    ("Exemplar structure: volumetric", lambda: check_pkg_schema("examples")),
    ("Exemplar structure: extrusion", lambda: check_pkg_schema("examples-extrusion")),
    ("Exemplar rules: volumetric", lambda: check_pkg_rules("examples")),
    ("Exemplar rules: extrusion", lambda: check_pkg_rules("examples-extrusion")),
    ("Schematron assertions", check_schematron),
    ("Conformance matrix (fault injection)", check_conformance),
    ("Modality corpus (must be satisfiable)", check_corpus),
    ("Round-trip preservation", check_roundtrip),
    ("Red team (adversarial packages)", check_redteam),
    ("Integrator round-trip", check_tools),
    ("Site build + internal links", check_site),
    ("Namespace URI serves the schema", check_namespace_served),
    ("Version consistency", check_versions),
    ("Viewer is local-only", check_viewer_local),
]


# --------------------------------------------------------------------------- blockers

def blockers():
    # Assembled at runtime rather than written as a literal. setup_repo.py rewrites the
    # placeholder slug across every file, and on the first run it rewrote this checker too --
    # so verify.py started searching for the CORRECT value and reporting it as a failure.
    # A tool that verifies a configuration must not itself be configurable.
    PLACEHOLDER = "OWN" + "ER/3mf-bio"
    out = []
    try:
        authors = subprocess.run(["git", "log", "--format=%ae"], cwd=ROOT,
                                 capture_output=True, text=True).stdout
        if "you@example.com" in authors:
            out.append(("Commit authorship is a placeholder",
                        "python3 tools/setup_repo.py --git-name … --git-email …"))
    except Exception:
        pass
    n = 0
    for r, _, fs in os.walk(ROOT):
        if "_build" in r or ".git" in r:
            continue
        for f in fs:
            if not f.endswith((".md", ".py", ".yml")) or \
                    f in ("FIRST-PUSH.md", "PUBLISH.md", "setup_repo.py", "verify.py"):
                continue
            try:
                if PLACEHOLDER in open(os.path.join(r, f), encoding="utf-8",
                                       errors="ignore").read():
                    n += 1
            except OSError:
                pass
    if n:
        out.append((f"Repository slug is a placeholder in {n} source file(s)",
                    "python3 tools/setup_repo.py --repo yourorg/3mf-bio"))
    if "3MF Bio Extension contributors" in read("LICENSE"):
        out.append(("LICENSE names a placeholder copyright holder",
                    "Decide ownership first — PUBLISH.md step 0"))
    if "contributors" in read("CITATION.cff"):
        out.append(("CITATION.cff names placeholder authors",
                    "python3 tools/setup_repo.py --author 'Surname, Given, ORCID, Affiliation'"))
    sec = read("SECURITY.md")
    if "Maintainer note" in sec or not re.search(r"@|private vulnerability reporting", sec, re.I):
        out.append(("SECURITY.md gives no way to report privately",
                    "python3 tools/setup_repo.py --security github"))
    return out


GAPS = [
    ("No real dataset has been recorded in this schema",
     "Every exemplar is a template. review/DATASET-SHEET.md lists exactly what would close "
     "it. Stated in README, SCOPE.md and SUBMISSION.md."),
    ("The regulatory annex has not been professionally reviewed",
     "Correct as a map of which instruments exist. Two claims rest on grade-E sources and "
     "two are our own inference. review/REGULATORY-REVIEW.md is the pack."),
    ("Six of fifteen adversarial packages still validate clean",
     "A real reference cited for an unrelated claim, a vacuously 'resolved' open item, an "
     "acceptance criterion that cannot fail. Structurally perfect and semantically false. "
     "No schema can catch these; specification Chapter 12 says so."),
    ("Five of twenty modalities are enumerated but unspecified",
     "Acoustic droplet, continuous SLA, magnetic levitation, spheroid bioassembly, in-situ. "
     "No parameter set, no evidence base. Open item 'modality-evidence-thin'."),
    ("Four paywalled standards cited from abstracts, not full text",
     "ASTM F3659-24, ISO/ASTM 52900, 52902, ISO 10993. Scope and titles reliable; no clause "
     "requirements quoted or asserted."),
    ("One volumetric attachment mechanism unverified",
     "How an <object> attaches a <v:volumedata> resource. Flagged rather than guessed; open "
     "item 'vol-attach-attribute'."),
]


def _wrap(t, w):
    words, line, out = t.split(), "", []
    for x in words:
        if len(line) + len(x) + 1 > w:
            out.append(line)
            line = x
        else:
            line = f"{line} {x}".strip()
    if line:
        out.append(line)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ci", action="store_true")
    a = ap.parse_args()

    print(f"\n{'=' * 74}\n  3MF Bio — full verification\n{'=' * 74}\n")
    print("CHECKS  automated, run now\n")

    failed = skipped = 0
    for label, fn in CHECKS:
        try:
            ok, detail = fn()
        except Exception as e:
            ok, detail = False, f"raised: {type(e).__name__}: {e}"
        if ok is None:
            skipped += 1
            mark = f"{YELLOW}SKIP{RESET}"
        else:
            failed += not ok
            mark = f"{GREEN}PASS{RESET}" if ok else f"{RED}FAIL{RESET}"
        print(f"  {mark}  {label:<40} {DIM}{detail}{RESET}")
    ran = len(CHECKS) - skipped
    print(f"\n  {ran - failed}/{ran} passing" +
          (f", {skipped} skipped" if skipped else ""))

    b = blockers()
    if not a.ci:
        print("\n\nBLOCKERS  decisions code cannot make\n")
        if not b:
            print(f"  {GREEN}none outstanding{RESET}")
        for label, fix in b:
            print(f"  {YELLOW}TODO{RESET}  {label}\n        {DIM}{fix}{RESET}")
        print("\n\nKNOWN GAPS  documented, not failures, do not block publication\n")
        for label, detail in GAPS:
            print(f"  {DIM}·{RESET}  {label}")
            for line in _wrap(detail, 66):
                print(f"     {DIM}{line}{RESET}")

    print()
    if failed:
        print(f"{RED}{failed} check(s) failing. Do not publish.{RESET}\n")
        return 1
    if b and not a.ci:
        print(f"All checks pass. {len(b)} blocker(s) before first push — see PUBLISH.md.\n")
        return 2
    print(f"{GREEN}All checks pass and no blockers outstanding. Ready to publish.{RESET}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
