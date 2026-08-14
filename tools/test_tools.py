#!/usr/bin/env python3
"""
Round-trip test for the integrator: mesh + answers -> package -> validators.

The tool's contract is that it always emits, and that what it emits always validates. Those
are different claims and both need testing: a tool that emitted an invalid package rather
than refusing would be worse than one that refused.
"""
import json, os, struct, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def make_stl(path, ascii_mode=False):
    tris = [((0,0,0),(10,0,0),(5,8,0)), ((0,0,0),(10,0,0),(5,3,9)),
            ((10,0,0),(5,8,0),(5,3,9)), ((5,8,0),(0,0,0),(5,3,9))]
    if ascii_mode:
        with open(path, "w") as f:
            f.write("solid t\n")
            for t in tris:
                f.write(" facet normal 0 0 1\n  outer loop\n")
                for v in t:
                    f.write(f"   vertex {v[0]} {v[1]} {v[2]}\n")
                f.write("  endloop\n endfacet\n")
            f.write("endsolid t\n")
    else:
        with open(path, "wb") as f:
            f.write(b"\0"*80 + struct.pack("<I", len(tris)))
            for t in tris:
                f.write(struct.pack("<3f", 0, 0, 1))
                for v in t:
                    f.write(struct.pack("<3f", *v))
                f.write(struct.pack("<H", 0))


def make_obj(path):
    with open(path, "w") as f:
        f.write("v 0 0 0\nv 10 0 0\nv 5 8 0\nv 5 3 9\n")
        f.write("f 1 2 3\nf 1 2 4\nf 2 3 4\nf 3 1 4\n")


def run(args):
    return subprocess.run([sys.executable] + args, capture_output=True, text=True, cwd=ROOT)


CASES = [
    ("empty answers, binary STL", {}, "stl"),
    ("empty answers, ASCII STL", {}, "stl-ascii"),
    ("empty answers, OBJ", {}, "obj"),
    ("partially answered", {
        "title": "partial", "intendeduse": "research-only", "mesh_units": "millimeter",
        "bioink_class": "bioink", "cell_name": "HDF", "mycoplasma_result": "negative",
        "passage_at_print": "5", "antibiotics": "none", "cell_density": "1500000",
        "nozzle_inner_diameter": "410", "nozzle_geometry": "conical", "nozzle_length": "12700",
        "print_speed": "8", "cartridge_temp": "37", "build_temp": "22",
        "extrusion_pressure": "60", "layer_height": "200", "strand_spacing": "400",
        "print_duration": "20", "sterility_method": "aseptic",
        "cell_viability_post_print": "90",
        "substances": [{"name": "alginate", "role": "polymer", "casrn": "9005-38-3",
                        "value": "3", "unit": "%{w/v}"}],
        "calibration_performed": "2026-07-01", "cal_filament_width": "430",
        "assays": [{"name": "viability", "domain": "viability", "endpoint": "live_fraction",
                    "unit": "%", "method": "calcein/EthD", "timepoints": ["P1D"], "n": 3}],
    }, "stl"),
    ("mycoplasma positive must still emit, and must then FAIL validation", {
        "mycoplasma_result": "positive", "mesh_units": "millimeter",
    }, "stl-expect-fail"),
]

def main():
    passed = failed = 0
    for label, extra, meshkind in CASES:
        d = tempfile.mkdtemp()
        mesh = os.path.join(d, "m." + ("obj" if meshkind == "obj" else "stl"))
        if meshkind == "obj":
            make_obj(mesh)
        else:
            make_stl(mesh, ascii_mode=(meshkind == "stl-ascii"))

        tpl = run([os.path.join("tools", "questionnaire.py"), "--profile", "brinter",
                   "--head", "pneuma", "--format", "template"])
        if tpl.returncode:
            print(f"  FAIL  {label}: questionnaire failed\n{tpl.stderr[:300]}")
            failed += 1
            continue
        ans = json.loads(tpl.stdout)
        ans.update(extra)
        ap = os.path.join(d, "a.json")
        json.dump(ans, open(ap, "w"))

        out = os.path.join(d, "pkg")
        r = run([os.path.join("tools", "integrate.py"), ap, "--mesh", mesh, "--out", out,
                 "--profile", "brinter"])
        if r.returncode:
            print(f"  FAIL  {label}: integrator refused to emit\n{r.stderr[:400]}")
            failed += 1
            continue

        v = run([os.path.join("spec", "validate_bio.py"), out])
        sc = run([os.path.join("spec", "validate_schema.py"), out])
        nerr = int(v.stdout.split("error(s)")[0].strip().split("\n")[-1]) if "error(s)" in v.stdout else -1
        schema_ok = "0 invalid" in sc.stdout

        if meshkind == "stl-expect-fail":
            ok = nerr > 0 and "[C7]" in v.stdout
            note = "correctly rejected" if ok else "should have been rejected"
        else:
            ok = nerr == 0 and schema_ok
            note = f"{nerr} error(s), schema {'ok' if schema_ok else 'INVALID'}"
        print(f"  {'PASS' if ok else 'FAIL'}  {label}: {note}")
        passed += ok
        failed += (not ok)

    print(f"\n{passed} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
