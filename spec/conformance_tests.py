#!/usr/bin/env python3
"""
Conformance test suite for the 3MF Bio Extension.

Mutates a known-good package once per rule and asserts the fault is caught. Each mutation
is run through BOTH validators:

  schematron  spec/bio.sch      via lxml.isoschematron  (intra-document rules)
  python      spec/validate_bio.py                      (all rules, incl. cross-part)

The output is a coverage matrix. Rules that only Python catches are the cross-part ones --
OPC relationships and the CSL-JSON bibliography -- which are outside any single XML
document and cannot be expressed in Schematron. That gap is by design and is documented in
the header of bio.sch.

Usage:  python3 spec/conformance_tests.py [--verbose]
"""
import os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, "examples")
SRC_EXT = os.path.join(ROOT, "examples-extrusion")
MODEL = ("3D", "3dmodel.model")

# (label, expected rule, kind, payload)
#   kind "model": (old, new) string replacement in the model part
#   kind "rels" / "csl": structural package mutation
CASES = [
    ("cited param with no evidence", "V1", "model",
     ('name="print_duration"          unit="s"      setpoint="30"  provenance="cited" evid="1" evindices="2"',
      'name="print_duration"          unit="s"      setpoint="30"  provenance="cited"')),
    ("measured param with no value", "V2", "model",
     ('name="build_temp"              unit="Cel"    setpoint="37" measured="37" provenance="measured"',
      'name="build_temp"              unit="Cel"    setpoint="37" provenance="measured"')),
    ("derived param with no method", "V3", "model",
     ('method="dose = optical power x exposure time / illuminated area; threshold from per-resin dose test"',
      'x-was-method="removed"')),
    ("evindices out of range", "V1", "model",
     ('evid="1" evindices="4"/>', 'evid="1" evindices="99"/>')),
    ("synthesis yield omitted", "S3", "model",
     ('<b:yield kind="isolated" unit="%" measured="" provenance="estimated"\n\t\t\t\t\t\tnote="TODO-VERIFY - no isolated yield figure found in the consulted sources; measure and record"/>', '')),
    ("mycoplasma record removed", "C2", "model",
     ('<b:authentication assay="mycoplasma" method="PCR" date="2026-06-01" result="negative"\n\t\t\t\t\treport="/bio/coa/myco_20260601.pdf"/>', '')),
    ("antibiotics left silent", "C4", "model",
     ('antibiotics="none"', 'antibiotics=""')),
    ("rheology without temperature", "I2", "model",
     ('<b:param name="temp_of_measurement" unit="Cel"  setpoint="37" measured="37" provenance="measured"/>', '')),
    ("required modality param removed", "P0", "model",
     ('<b:param name="rotation_speed"          unit="1/min"  setpoint=""    provenance="estimated" note="TODO-VERIFY"/>', '')),
    ("derived quantity mislabelled", "P3", "model",
     ('name="total_light_dose"        unit="mJ/cm2" setpoint=""    provenance="derived"',
      'name="total_light_dose"        unit="mJ/cm2" setpoint="200" provenance="measured" measured="200"')),
    ("toolpath checksum removed", "T1", "model",
     ('checksum="sha256:', 'x-checksum="sha256:')),
    ("toolpath checksum does not match the file", "T4", "model",
     ('checksum="sha256:',
      'checksum="sha256:deadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef" x-old="sha256:')),
    ("SpecVersion metadata removed", "M1", "model",
     ('<metadata name="b:SpecVersion">0.5.0</metadata>\n\t', '')),
    ("unit does not match the quantity's dimension", "U1", "model",
     ('name="build_temp"              unit="Cel"', 'name="build_temp"              unit="kg"')),
    ("value outside physical possibility", "U2", "model",
     ('name="cell_viability_post_print" unit="%"    measured="90"',
      'name="cell_viability_post_print" unit="%"    measured="400"')),
    ("date in the future", "D2", "model",
     ('performed="2026-06-05"', 'performed="2099-01-01"')),
    ("mycoplasma result reports contamination", "C7", "model",
     ('assay="mycoplasma" method="PCR" date="2026-06-01" result="negative"',
      'assay="mycoplasma" method="PCR" date="2026-06-01" result="positive"')),
    ("field range minimum is negative", "U4", "model",
     ('<b:range min="1000000"', '<b:range min="-1000000"')),
    ("duplicate resource id", "X3", "model",
     ('<b:protocol id="7"', '<b:protocol id="6"')),
    ("pindex out of range", "G1", "model",
     ('pid="4" pindex="0"\n\t\t\tb:processid="5" b:regionrole="parenchyma"',
      'pid="4" pindex="9"\n\t\t\tb:processid="5" b:regionrole="parenchyma"')),
    ("dangling processid", "G2", "model",
     ('b:processid="5" b:regionrole="vasculature"', 'b:processid="77" b:regionrole="vasculature"')),
    ("dangling substanceid", "I3", "model",
     ('<b:component substanceid="2" substanceindex="1"', '<b:component substanceid="88" substanceindex="1"')),
    ("dangling field volumeid", "F1", "model",
     ('<b:fieldbinding id="15" volumeid="14"', '<b:fieldbinding id="15" volumeid="66"')),
    ("field property name mismatch", "F2", "model",
     ('property="bio_cell_density"\n\t\t\tquantity="cell_density"', 'property="bio_wrong_name"\n\t\t\tquantity="cell_density"')),
    ("cell load both scalar and field", "F3", "model",
     ('<b:cellload cellpopid="3" cellpopindex="0" fieldid="15"',
      '<b:cellload cellpopid="3" cellpopindex="0" fieldid="15" density="2e6" unit="/mL"')),
    ("dangling fieldid", "F4", "model",
     ('fieldid="15"\n\t\t\t\t\tprovenance="derived"', 'fieldid="55"\n\t\t\t\t\tprovenance="derived"')),
    ("cell load bound to a non-cell field", "F6", "model",
     ('quantity="cell_density" unit="/mL"', 'quantity="porosity" unit="/mL"')),
    ("dangling maps bioinkid", "F8", "model",
     ('<b:maps bioinkid="4" bioinkindex="0"/>', '<b:maps bioinkid="44" bioinkindex="0"/>')),
    ("calibration with no performed date", "K1", "model",
     ('performed="2026-06-05" operator="ILLUSTRATIVE"', 'operator="ILLUSTRATIVE"')),
    ("calibration test passed without a measurement", "K3", "model",
     ('measured="" outcome="not-performed" frequency="per-resin-lot"\n\t\t\t\tevid="1" evindices="1"',
      'measured="" outcome="pass" frequency="per-resin-lot"\n\t\t\t\tevid="1" evindices="1"')),
    ("calibration artifact object does not exist", "K4", "model",
     ('artifactobjectid="13" stdref="ISO/ASTM 52902:2023"', 'artifactobjectid="131" stdref="ISO/ASTM 52902:2023"')),
    ("calibration modality mismatch", "K7", "model",
     ('<b:calibration id="16" modality="volumetric-tomographic"', '<b:calibration id="16" modality="vat-dlp"')),
    ("undetermined jurisdiction not tracked", "R5", "model",
     ("note=\"see openitem 'reg-au-class' - tissue-engineered", 'note="tissue-engineered')),
    ("implantable use without ISO 10993", "R7", "model2",
     [('intendeduse="research-only"', 'intendeduse="implantable"'),
      ('<b:standardref stdno="ISO 10993-1"', '<b:standardref stdno="x-removed-10993"')]),
    ("implantable use without contact categorisation", "R8", "model",
     ('intendeduse="research-only"\n\t\t\tcontactduration="none" contactnature="none"',
      'intendeduse="implantable"')),
    ("duplicate open item key", "J1", "model",
     ('<b:openitem key="gelma-yield"', '<b:openitem key="lap-inchikey"')),
    ("resolved open item with no resolution", "J2", "model",
     ('resolution="Correct key for the salt', 'x-resolution="Correct key for the salt')),
    ("open item affects a nonexistent resource", "J4", "model",
     ('<b:affects targetid="2" targetindex="1"/>', '<b:affects targetid="222" targetindex="1"/>')),
    ("estimated param with no open item", "J5", "model",
     ('<b:affects targetid="5" paramname="rotation_speed"/>', '')),
    ("wrong ISO 52900 category", "N1", "model",
     ('iso52900="VPP"', 'iso52900="MEX"')),
    # --- extrusion / deposition faults, run against examples-extrusion ---
    ("X:coaxial nozzle with no channel description", "H2", "ext",
     ('<b:nozzle geometry="conical" innerdiameter="410" length="12.7" unit="um"',
      '<b:nozzle geometry="coaxial" innerdiameter="410" length="12.7" unit="um"')),
    ("X:hollow tube claimed but core carries bioink", "H4", "ext",
     ('<b:channel role="core" content="crosslinker"',
      '<b:channel role="core" content="bioink" bioinkid="4" bioinkindex="1" x-old="crosslinker"')),
    ("X:object printed by a head loaded with a different ink", "H3", "ext",
     ('pid="4" pindex="1"\n\t\t\tb:processid="6" b:printheadid="5" b:printheadindex="1"',
      'pid="4" pindex="0"\n\t\t\tb:processid="6" b:printheadid="5" b:printheadindex="1"')),
    ("X:duplicate tool identifier", "H1", "ext",
     ('tool="T2"', 'tool="T0"')),
    ("X:shear declared without a nozzle length", "X1", "ext",
     ('<b:param name="nozzle_length" unit="um" setpoint="12700" measured="12700"',
      '<b:param name="x_nozzle_length" unit="um" setpoint="12700" measured="12700"')),
    ("X:coaxial process without core/shell flows", "P0", "ext",
     ('<b:param name="core_flow_rate" unit="uL/min" setpoint="" provenance="estimated"/>\n\t\t\t\t<b:param name="shell_flow_rate"',
      '<b:param name="x_shell_flow_rate"')),
    ("X:channel carries bioink but names none", "H5", "ext",
     ('bioinkid="4" bioinkindex="1">\n\t\t\t\t\t\t<b:param name="shell_flow_rate"',
      '>\n\t\t\t\t\t\t<b:param name="shell_flow_rate"')),
    ("X:perfusion stage with no flow rate", "Q3", "ext",
     ('<b:param name="flow_rate" unit="mL/min" setpoint="" provenance="estimated"\n\t\t\t\t\t\tnote="see openitem \'mat-flow\'"/>',
      '<b:param name="x_flow_rate" unit="mL/min" setpoint="" provenance="estimated"/>')),
    ("X:cyclic loading without cycle count", "Q5", "ext",
     ('<b:param name="cycles_per_day" unit="1" setpoint="2000" measured="2000"',
      '<b:param name="x_cycles_per_day" unit="1" setpoint="2000" measured="2000"')),
    ("X:two assay readings at the same timepoint", "Q9", "ext",
     ('<b:reading timepoint="P7D"  value="" provenance="estimated" n="3" outcome="not-assessed"/>',
      '<b:reading timepoint="P1D"  value="" provenance="estimated" n="3" outcome="not-assessed"/>')),
    ("X:assay with no method", "Q8", "ext",
     ('method="hydroxyproline assay normalised to PicoGreen DNA"', 'x-method="hydroxyproline"')),
    ("X:maturation stage ends before it begins", "Q2", "ext",
     ('from="P2D" to="P14D"', 'from="P14D" to="P2D"')),
    ("X:extrusion with no layer stacking test", "K8", "ext",
     ('<b:test name="layer_stacking_test"', '<b:test name="x_layer_stacking_test"')),
    ("OPC relationship removed", "O3", "rels", None),
    ("bibliography key mismatch", "E5", "csl", None),
]


def build(case_dir, kind, payload):
    mp = os.path.join(case_dir, *MODEL)
    if kind == "ext":
        old, new = payload
        t = open(mp).read()
        if old not in t:
            return False
        open(mp, "w").write(t.replace(old, new, 1))
        return True
    if kind == "model2":
        # chained mutations: several replacements must apply together
        text = open(mp).read()
        for old, new in payload:
            if old not in text:
                return False
            text = text.replace(old, new, 1)
        open(mp, "w").write(text)
        return True
    if kind == "model":
        old, new = payload
        s = open(mp).read()
        if old not in s:
            return False
        open(mp, "w").write(s.replace(old, new, 1))
    elif kind == "rels":
        p = os.path.join(case_dir, "3D", "_rels", "3dmodel.model.rels")
        r = open(p).read().replace(
            '<Relationship Id="rel1" Target="/bio/references.json"\n'
            '    Type="https://3mfbio.com/ns/rel/2026/07/biobibliography"/>', '')
        open(p, "w").write(r)
    elif kind == "csl":
        p = os.path.join(case_dir, "bio", "references.json")
        # read fully BEFORE opening for write: open(p,"w") truncates immediately
        text = open(p).read().replace('"id": "shirahama2016"', '"id": "shirahama2016_TYPO"')
        open(p, "w").write(text)
    return True


def run_python(case_dir):
    out = subprocess.run([sys.executable, os.path.join(HERE, "validate_bio.py"), case_dir],
                         capture_output=True, text=True).stdout
    return out


def run_schematron(case_dir):
    try:
        from lxml import etree, isoschematron
    except ImportError:
        return None
    sch = isoschematron.Schematron(
        etree.parse(os.path.join(HERE, "bio.sch")),
        error_finder=isoschematron.Schematron.ASSERTS_AND_REPORTS)
    sch.validate(etree.parse(os.path.join(case_dir, *MODEL)))
    return "\n".join(e.message for e in sch.error_log)


def main():
    verbose = "--verbose" in sys.argv
    OUT_OF_SCOPE = ("O3", "E5", "T4", "D2", "Q2")
    rows, py_pass, sch_pass = [], 0, 0

    for label, rule, kind, payload in CASES:
        tmp = tempfile.mkdtemp()
        case_dir = os.path.join(tmp, "pkg")
        shutil.copytree(SRC_EXT if kind == "ext" else SRC, case_dir)
        if not build(case_dir, kind, payload):
            print(f"  SKIP  {label}: mutation anchor not found")
            continue
        po = run_python(case_dir)
        so = run_schematron(case_dir)
        p_hit = f"[{rule}]" in po
        s_hit = so is not None and f"[{rule}]" in so
        rows.append((label, rule, p_hit, s_hit))
        py_pass += p_hit
        sch_pass += s_hit
        if verbose and not p_hit:
            print("  python output:", " | ".join(l.strip() for l in po.splitlines() if l.strip())[:240])
        shutil.rmtree(tmp, ignore_errors=True)

    w = max(len(r[0]) for r in rows)
    print(f"{'fault':<{w}}  rule  python  schematron")
    print("-" * (w + 26))
    for label, rule, p, s in rows:
        print(f"{label:<{w}}  {rule:<4}  {'PASS' if p else 'FAIL':<6}  "
              f"{'PASS' if s else ('n/a' if rule in OUT_OF_SCOPE else 'FAIL')}")
    cross = sum(1 for _, r, _, _ in rows if r in OUT_OF_SCOPE)
    print("-" * (w + 26))
    print(f"\n{len(rows)} faults injected")
    print(f"  python     {py_pass}/{len(rows)} caught")
    print(f"  schematron {sch_pass}/{len(rows) - cross} caught "
          f"({cross} out of scope by design: {', '.join(OUT_OF_SCOPE)} need the package "
          f"or XPath 2.0)")

    ok = py_pass == len(rows) and sch_pass == len(rows) - cross
    print("\nALL PASS" if ok else "\nFAILURES PRESENT")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
