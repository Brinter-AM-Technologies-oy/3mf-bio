"""
Red team: construct packages that SHOULD fail and see which validate clean.

This is the complement to conformance_tests.py. That suite proves rules fire when a rule is
broken. This one asks a harder question: can a package be built that breaks no rule and is
still garbage?

Fourteen attacks. Before hardening, thirteen produced a clean bill of health. The ones that
still do are not bugs -- they are the boundary of what a file format can enforce, and they
are documented in Chapter 12 of the specification. Run this after any rule change; a drop in
the caught count is a regression.
"""
import os, shutil, subprocess, sys, tempfile

import os as _os
HERE=_os.path.dirname(_os.path.abspath(__file__))
_os.chdir(_os.path.dirname(HERE))
SRC="examples"; MODEL=("3D","3dmodel.model")
def run(d):
    return subprocess.run([sys.executable,"spec/validate_bio.py",d],capture_output=True,text=True).stdout

ATTACKS = [
 ("A1 nonsense units: light dose in kilograms",
  ('name="total_light_dose"        unit="mJ/cm2"','name="total_light_dose"        unit="kg"')),
 ("A2 physically impossible: negative cell density",
  ('<b:range min="1000000" max="8000000" fallback="2000000"/>',
   '<b:range min="-1000000" max="8000000" fallback="2000000"/>')),
 ("A2b negative parameter value",
  ('name="print_duration"          unit="s"      setpoint="30"',
   'name="print_duration"          unit="s"      setpoint="-30"')),
 ("A3 impossible viability: 400%",
  ('measured="90"  provenance="cited"','measured="400"  provenance="cited"')),
 ("A4 setpoint and measured wildly inconsistent",
  ('setpoint="37" measured="37" provenance="measured"','setpoint="37" measured="912" provenance="measured"')),
 ("A5 evidence cited for an unrelated claim (wrong index, in range)",
  ('name="print_duration"          unit="s"      setpoint="30"  provenance="cited" evid="1" evindices="2"',
   'name="print_duration"          unit="s"      setpoint="30"  provenance="cited" evid="1" evindices="7"')),
 ("A6 fabricated DOI that looks well-formed",
  ('doi="10.1002/adma.201904209"','doi="10.9999/fabricated.99999"')),
 ("A7 calibration performed AFTER the results it certifies",
  ('performed="2026-06-05"','performed="2099-01-01"')),
 ("A8 mycoplasma test present but result is 'POSITIVE'",
  ('assay="mycoplasma" method="PCR" date="2026-06-01" result="negative"',
   'assay="mycoplasma" method="PCR" date="2026-06-01" result="POSITIVE"')),
 ("A9 passage number absurd (p=400)",
  ('name="passage_at_print" unit="1"   measured="4"','name="passage_at_print" unit="1"   measured="400"')),
 ("A10 toolpath checksum is a plausible-looking lie",
  ('checksum="sha256:',
   'checksum="sha256:deadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef" x-old="sha256:')),
 ("A11 open item marked resolved with a vacuous resolution",
  ('resolution="Correct key for the salt','resolution="Done.  x-old="')),
 ("A12 acceptance criterion that cannot fail",
  ('acceptance="&gt;= 80%"','acceptance="any value"')),
 ("A13 regulatory: implantable but determination not-applicable everywhere",
  ('intendeduse="research-only"','intendeduse="preclinical"')),
 ("A14 cell line kind with a syntactically valid but fake RRID",
  ('kind="primary" rrid=""','kind="line" rrid="CVCL_0000"')),
]

print(f"{'attack':<58} {'errors':>6}  {'verdict'}")
print("-"*95)
missed=[]
for label,(old,new) in ATTACKS:
    d=tempfile.mkdtemp(); c=os.path.join(d,"pkg"); shutil.copytree(SRC,c)
    mp=os.path.join(c,*MODEL); s=open(mp).read()
    if old not in s:
        print(f"{label:<58} {'--':>6}  ANCHOR NOT FOUND"); continue
    open(mp,"w").write(s.replace(old,new,1))
    out=run(c)
    nerr=int(out.split("error(s)")[0].strip().split("\n")[-1]) if "error(s)" in out else -1
    caught = nerr>0
    print(f"{label:<58} {nerr:>6}  {'caught' if caught else 'MISSED — validates clean'}")
    if not caught: missed.append(label)
    shutil.rmtree(d,ignore_errors=True)
print("-"*95)
print(f"\n{len(missed)}/{len(ATTACKS)} attacks produce a clean bill of health:")
for m in missed: print("  -",m)
