#!/usr/bin/env python3
"""
Rewrite the bio namespace URI across the whole repository.

The namespace is a decision only the project owner can make, so it is not baked in. The
default is a URN, which is a legitimate XML namespace, requires no domain ownership, and
cannot squat on anyone else's. If you own a domain, switch to an https URI under it -- that
follows 3MF Consortium convention and is resolvable, which is friendlier to implementers.

Usage:
    python3 spec/set_namespace.py https://YOUR-DOMAIN/ns/bio/2026/07
    python3 spec/set_namespace.py --show

Run the full test suite afterwards; the namespace appears in the schemas, the Schematron,
the validators, the exemplars and the generated corpus.
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATTERN = re.compile(r'(https://3mfbio.com/ns/bio/2026/07|https?://(?!YOUR-DOMAIN)[^\s"\'<>]*?/bio/2026/07)')
SKIP_DIRS = {".git", "__pycache__", "conformance", ".github/workflows"}
# .html matters: tools/viewer.html hardcodes the namespace to read packages. Omitting it
# left the viewer looking for the old URI, so it rendered an empty run sheet for every
# package produced after a namespace change -- silently, with no error anywhere.
EXTS = {".xsd", ".sch", ".py", ".model", ".md", ".xml", ".rels", ".json", ".yml", ".cff",
        ".html", ".txt"}


def files():
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for f in filenames:
            if os.path.splitext(f)[1] in EXTS or f.endswith(".rels"):
                yield os.path.join(dirpath, f)


def current():
    found = {}
    for p in files():
        try:
            text = open(p, encoding="utf-8").read()
        except (UnicodeDecodeError, OSError):
            continue
        for m in PATTERN.findall(text):
            found.setdefault(m, []).append(os.path.relpath(p, ROOT))
    return found


def main():
    if "--show" in sys.argv or len(sys.argv) < 2:
        found = current()
        if not found:
            print("no bio namespace found")
            return 0
        for ns, where in sorted(found.items()):
            print(f"{ns}\n  in {len(where)} file(s)")
        return 0

    new = sys.argv[1]
    if not (new.startswith("http://") or new.startswith("https://") or new.startswith("urn:")):
        sys.exit("namespace must be an http(s) URI or a URN")

    found = current()
    if len(found) != 1:
        sys.exit(f"expected exactly one existing namespace, found {list(found)}")
    old = next(iter(found))
    if old == new:
        print("already set")
        return 0

    changed = 0
    for p in files():
        try:
            text = open(p, encoding="utf-8").read()
        except (UnicodeDecodeError, OSError):
            continue
        if old in text:
            open(p, "w", encoding="utf-8").write(text.replace(old, new))
            changed += 1
    print(f"{old}\n  ->  {new}\n{changed} file(s) rewritten")
    print("\nNow run:")
    print("  python3 spec/make_conformance_corpus.py")
    print("  python3 spec/conformance_tests.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
