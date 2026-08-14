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

    python3 tools/ci_local.py                 both workflows
    python3 tools/ci_local.py validate        one workflow
"""
import os
import re
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


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else None
    wfdir = os.path.join(ROOT, ".github", "workflows")
    files = sorted(f for f in os.listdir(wfdir) if f.endswith(".yml"))
    if which:
        files = [f for f in files if f.startswith(which)]
    if not files:
        sys.exit(f"no workflow matching {which!r}")

    total_fail = 0
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
