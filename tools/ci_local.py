#!/usr/bin/env python3
"""
Run the GitHub Actions workflow steps locally, with the same shell semantics.

Why this exists: the first push failed CI. Every check passed locally, but the workflow step
`python3 spec/validate_bio.py examples` aborted, because that script exits **2** when a
package has warnings and no errors -- and GitHub Actions runs each `run:` block under
`bash -e`, where any non-zero status ends the step. Both exemplars carry warnings on purpose:
unresolved blocking open items are the demonstration.

Running the commands by hand and reading the output never caught it. Nothing checked the exit
codes the way Actions does.

This extracts every `run:` block from the workflows and executes it under `bash -e` in the
repository root, exactly as the runner would. It cannot reproduce the runner image, the
`uses:` actions, or the deploy steps -- those are skipped and listed -- but it catches the
class of failure that actually bit: a command whose exit code means something other than
"broken".

    python3 tools/ci_local.py                 both workflows, in a pristine copy
    python3 tools/ci_local.py validate        one workflow
    python3 tools/ci_local.py --dirty         use the working tree instead

PRISTINE BY DEFAULT. This is the second lesson. The site check reported 0 broken links here
and 2 in CI, for a long time, because the .3mf packages are gitignored: they existed in the
working tree so the site copied them, and did not exist on a fresh checkout so the download
page linked to nothing. Testing against the working tree cannot see that class of bug at all.
Everything is copied to a temporary directory with ignored and untracked files excluded,
which is what the runner actually gets.
"""
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

# Steps that cannot run outside the runner. Skipped and reported, not silently ignored.
SKIP = ("upload-pages-artifact", "configure-pages", "deploy-pages", "upload-artifact",
        "actions/checkout", "actions/setup-python", "Install dependencies")


def steps(path):
    """Pull (name, run-block) pairs out of a workflow. Deliberately simple: the workflows
    here are flat, and a YAML dependency would be one more thing to install."""
    out, name, buf, indent = [], None, None, None
    for line in open(path, encoding="utf-8"):
        m = re.match(r"^(\s*)- name:\s*(.+?)\s*$", line)
        if m:
            if name and buf is not None:
                out.append((name, "".join(buf)))
            name, buf, indent = m.group(2), None, None
            continue
        m = re.match(r"^(\s*)run:\s*\|\s*$", line)
        if m and name:
            buf, indent = [], len(m.group(1)) + 2
            continue
        m = re.match(r"^(\s*)run:\s*(\S.*)$", line)
        if m and name:
            out.append((name, m.group(2) + "\n"))
            name, buf = None, None
            continue
        if buf is not None:
            if line.strip() and not line.startswith(" " * indent):
                out.append((name, "".join(buf)))
                name, buf = None, None
            else:
                buf.append(line[indent:] if len(line) > indent else "\n")
    if name and buf is not None:
        out.append((name, "".join(buf)))
    return out


def third_party_imports():
    """Modules imported anywhere in the repository that are not stdlib and not local."""
    import ast
    local = {os.path.splitext(f)[0] for r, d, fs in os.walk(ROOT) for f in fs
             if f.endswith(".py")}
    stdlib = set(sys.stdlib_module_names)
    found = {}
    for root, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in {".git", "_build", "conformance", "__pycache__"}]
        for f in files:
            if not f.endswith(".py"):
                continue
            path = os.path.join(root, f)
            try:
                tree = ast.parse(open(path, encoding="utf-8").read())
            except (SyntaxError, UnicodeDecodeError):
                continue
            for node in ast.walk(tree):
                mod = None
                if isinstance(node, ast.Import):
                    mod = node.names[0].name.split(".")[0]
                elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                    mod = node.module.split(".")[0]
                if mod and mod not in stdlib and mod not in local:
                    found.setdefault(mod, set()).add(os.path.relpath(path, ROOT))
    return found


# Imported only by tools a workflow never invokes.
NOT_IN_CI = {"yaml": "tools/setup_repo.py, not run in CI"}


def check_dependencies(files, wfdir):
    """Compare each workflow's pip install line against what the repository imports."""
    print(f"\n{'=' * 74}\n  dependency declarations\n{'=' * 74}")
    imports = third_party_imports()
    fails = 0
    for wf in files:
        s = open(os.path.join(wfdir, wf), encoding="utf-8").read()
        m = re.search(r"pip install ([^\n]+)", s)
        spec = m.group(1).strip() if m else ""
        if spec.startswith("-r "):
            req = os.path.join(ROOT, spec.split(None, 1)[1])
            declared = set()
            if os.path.exists(req):
                for line in open(req, encoding="utf-8"):
                    line = line.split("#")[0].strip()
                    if line:
                        declared.add(re.split(r"[<>=!\[]", line)[0].strip())
            else:
                print(f"  FAIL  {wf}: installs from {spec.split()[1]}, which does not exist")
                fails += 1
                continue
        else:
            declared = set(spec.split())
        # which scripts does this workflow actually invoke
        invoked = set(re.findall(r"python3 ([\w/\.\-]+\.py)", s))
        needed = set()
        for mod, users in imports.items():
            if mod in NOT_IN_CI:
                continue
            if any(u in invoked for u in users):
                needed.add(mod)
        # verify.py runs the whole suite, so it pulls in everything those scripts need
        if "verify.py" in invoked:
            needed |= {m for m in imports if m not in NOT_IN_CI}
        missing = needed - declared
        if missing:
            fails += 1
            print(f"  FAIL  {wf}: installs {sorted(declared)} but needs {sorted(missing)}")
        else:
            print(f"  PASS  {wf}: installs {sorted(declared)}, covers {sorted(needed)}")
    return fails


def pristine_copy():
    """A temp copy holding only what git tracks -- what the runner checks out."""
    import tempfile
    r = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True)
    if r.returncode:
        print("  not a git repository; falling back to the working tree")
        return None
    dest = tempfile.mkdtemp(prefix="ci-pristine-")
    for rel in r.stdout.splitlines():
        src, dst = os.path.join(ROOT, rel), os.path.join(dest, rel)
        if not os.path.exists(src):
            continue
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
    # A runner checkout is a git repository, and some steps depend on that -- the
    # line-ending check reads .gitattributes via `git check-attr`, which needs a repo.
    # Without this the harness reports a failure that only exists in the harness.
    subprocess.run(["git", "init", "-q"], cwd=dest, capture_output=True)
    subprocess.run(["git", "add", "-A"], cwd=dest, capture_output=True)
    return dest


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    dirty = "--dirty" in sys.argv
    which = args[0] if args else None
    global ROOT
    if not dirty:
        p = pristine_copy()
        if p:
            n = len(subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True,
                                   text=True).stdout.splitlines())
            print(f"\nrunning against a pristine copy of {n} tracked file(s), as the runner "
                  f"would\n(use --dirty to test the working tree instead)")
            ROOT = p
    wfdir = os.path.join(ROOT, ".github", "workflows")
    files = sorted(f for f in os.listdir(wfdir) if f.endswith(".yml"))
    if which:
        files = [f for f in files if f.startswith(which)]
    if not files:
        sys.exit(f"no workflow matching {which!r}")

    total_fail = 0

    # The simulator runs in whatever environment it finds, so it cannot notice a module the
    # workflow forgets to install -- which is exactly what failed the second push:
    # validate.yml installed lxml but not markdown, and verify.py builds the site. Check the
    # declared dependencies against what the code actually imports, statically.
    total_fail += check_dependencies(files, wfdir)

    for wf in files:
        path = os.path.join(wfdir, wf)
        print(f"\n{'=' * 74}\n  {wf}\n{'=' * 74}")
        for name, script in steps(path):
            if any(s in name for s in SKIP) or any(s in script for s in SKIP):
                print(f"  SKIP  {name}   (needs the runner)")
                continue
            # bash -e is what Actions uses: any non-zero status ends the step.
            r = subprocess.run(["bash", "-e", "-c", script], cwd=ROOT,
                               capture_output=True, text=True)
            if r.returncode == 0:
                print(f"  PASS  {name}")
            else:
                total_fail += 1
                print(f"  FAIL  {name}   (exit {r.returncode})")
                tail = (r.stdout + r.stderr).strip().splitlines()
                for line in tail[-8:]:
                    print(f"          {line}")

    print()
    if total_fail:
        print(f"{total_fail} step(s) would fail on GitHub. Fix before pushing.\n")
        return 1
    print("every runnable step passes under bash -e, as Actions runs them.\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
