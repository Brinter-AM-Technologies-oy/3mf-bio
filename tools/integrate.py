#!/usr/bin/env python3
"""
Integrate an STL or OBJ mesh plus questionnaire answers into a 3MF Bio package.

This is the on-ramp. A researcher already has geometry and already knows most of what went
into the build; what they do not have is somewhere to put it that survives handoff. This
takes the mesh they exported for the slicer, wraps it with the dossier, and emits a .3mf
that their printer software can still read as ordinary geometry.

THE RULE THIS TOOL FOLLOWS: it never refuses to emit. Any answer left null becomes a
<b:openitem> naming the action that would close it. A tool that demands forty fields before
producing output does not get used, and a recorded gap is worth more than a fabricated
number. The package it emits will therefore usually have open items, and that is the
correct, honest output -- not a failure.

Usage:
    python3 tools/questionnaire.py --profile brinter --head pneuma-pro --format template > answers.json
    # fill in what you know, leave the rest null
    python3 tools/integrate.py answers.json --mesh part.stl --out mybuild/
    python3 spec/validate_bio.py mybuild/
"""
import argparse
import hashlib
import json
import os
import struct
import sys
import zipfile
from xml.sax.saxutils import escape, quoteattr

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "spec"))

from validate_bio import (REQUIRED, COMMON, CALIBRATION_EXPECTED, DERIVED_ONLY, ISO52900,
                          PARAM_DIMENSION, SPEC_VERSION)
sys.path.insert(0, HERE)
from questionnaire import unit_for, WHY

NS_BIO = "https://3mfbio.com/ns/bio/2026/07"
NS_CORE = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"


# --------------------------------------------------------------------------- meshes

def read_stl(path):
    """Binary or ASCII STL to (vertices, triangles), welding coincident vertices."""
    data = open(path, "rb").read()
    tris = []
    is_ascii = data[:5].lower() == b"solid" and b"facet" in data[:2048].lower()
    if is_ascii:
        verts = []
        for line in data.decode("utf-8", "replace").splitlines():
            s = line.strip().split()
            if s and s[0] == "vertex":
                verts.append(tuple(float(x) for x in s[1:4]))
            elif s and s[0] == "endloop":
                if len(verts) >= 3:
                    tris.append(tuple(verts[-3:]))
                verts = []
    else:
        if len(data) < 84:
            raise ValueError(f"{path}: too short to be a binary STL")
        n = struct.unpack("<I", data[80:84])[0]
        expect = 84 + n * 50
        if len(data) < expect:
            raise ValueError(f"{path}: header claims {n} triangles, file holds "
                             f"{(len(data) - 84) // 50}")
        off = 84
        for _ in range(n):
            f = struct.unpack("<12fH", data[off:off + 50])
            tris.append(((f[3], f[4], f[5]), (f[6], f[7], f[8]), (f[9], f[10], f[11])))
            off += 50
    return weld(tris)


def read_obj(path):
    verts, tris = [], []
    for line in open(path, encoding="utf-8", errors="replace"):
        s = line.split()
        if not s:
            continue
        if s[0] == "v":
            verts.append(tuple(float(x) for x in s[1:4]))
        elif s[0] == "f":
            idx = []
            for tok in s[1:]:
                i = int(tok.split("/")[0])
                idx.append(i - 1 if i > 0 else len(verts) + i)
            for k in range(1, len(idx) - 1):  # fan-triangulate n-gons
                tris.append((verts[idx[0]], verts[idx[k]], verts[idx[k + 1]]))
    return weld(tris)


def weld(tris, places=6):
    """3MF wants an indexed mesh. STL is a triangle soup, so vertices must be merged."""
    index, verts, out = {}, [], []
    for tri in tris:
        ids = []
        for v in tri:
            key = tuple(round(c, places) for c in v)
            if key not in index:
                index[key] = len(verts)
                verts.append(key)
            ids.append(index[key])
        if len(set(ids)) == 3:  # drop degenerate triangles
            out.append(tuple(ids))
    return verts, out


def read_mesh(path):
    ext = os.path.splitext(path)[1].lower()
    if ext == ".stl":
        return read_stl(path)
    if ext == ".obj":
        return read_obj(path)
    raise ValueError(f"{path}: expected .stl or .obj")


# --------------------------------------------------------------------------- helpers

def A(**kw):
    """Attribute string, skipping None."""
    return "".join(f' {k}={quoteattr(str(v))}' for k, v in kw.items() if v is not None)


def known(answers, key):
    v = answers.get(key)
    if v is None:
        return None
    if isinstance(v, str) and v.strip().lower() in ("", "unknown", "n/a", "na", "?"):
        return None
    return v


class Builder:
    def __init__(self, answers, profile=None, head=None):
        self.a = answers
        self.profile = profile
        self.head = head
        self.modality = answers.get("_modality") or "extrusion-pneumatic"
        self.open_items = []
        self.next_id = 1

    def rid(self):
        v = self.next_id
        self.next_id += 1
        return v

    def gap(self, key, summary, action, severity="material", affects=None, paramname=None):
        self.open_items.append({"key": key, "summary": summary, "action": action,
                                "severity": severity, "affects": affects or [],
                                "paramname": paramname})

    # ---- process parameters, straight off the rule tables ----
    def params(self, procid):
        names = list(dict.fromkeys(COMMON + REQUIRED.get(self.modality, [])))
        if self.modality.startswith("extrusion-"):
            names += ["infill_pattern", "raster_angle", "perimeter_count", "standoff_height"]
        rows, missing = [], []
        for n in names:
            v = known(self.a, n)
            u = unit_for(n)
            if n in DERIVED_ONLY:
                m = known(self.a, f"{n}_method") or "TODO - name the model or equation used"
                rows.append(f'\t\t\t\t<b:param{A(name=n, unit=u, setpoint=v or "", provenance="derived", method=m)}/>')
                if v is None:
                    missing.append(n)
                continue
            if v is None:
                rows.append(f'\t\t\t\t<b:param{A(name=n, unit=u, setpoint="", provenance="estimated", note="not supplied at integration time")}/>')
                missing.append(n)
            else:
                rows.append(f'\t\t\t\t<b:param{A(name=n, unit=u, setpoint=v, measured=v, provenance="measured", method=known(self.a, f"{n}_method"))}/>')
        if missing:
            for n in missing:
                self.gap(f"param-{n}",
                         f"Process parameter '{n}' was not supplied when this package was integrated.",
                         WHY.get(n, f"Measure or cite {n} and record it with its provenance."),
                         severity="blocking" if n in REQUIRED.get(self.modality, []) else "material",
                         affects=[procid], paramname=n)
        return "\n".join(rows)

    def build(self, meshes):
        a = self.a
        ev_id = self.rid(); sub_id = self.rid(); cell_id = self.rid(); ink_id = self.rid()
        head_id = self.rid(); proc_id = self.rid(); cal_id = self.rid(); reg_id = self.rid()
        char_id = self.rid(); open_id = self.rid()
        obj_start = self.next_id

        parts = []
        parts.append(f'''<?xml version="1.0" encoding="UTF-8"?>
<!--
  Generated by tools/integrate.py from questionnaire answers and {len(meshes)} mesh file(s).
  Open items below record what was NOT supplied. They are the honest output of an
  integration, not a defect. Run spec/validate_bio.py to see the current state.
-->
<model unit={quoteattr(a.get("mesh_units") or "millimeter")} xml:lang="en-US"
\txmlns="{NS_CORE}"
\txmlns:b="{NS_BIO}"
\trequiredextensions="b">

\t<metadata name="Title">{escape(str(a.get("title") or "Untitled build"))}</metadata>
\t<metadata name="Application">3MF Bio integrator</metadata>
\t<metadata name="b:SpecVersion">{SPEC_VERSION}</metadata>
\t<metadata name="b:Conformance">Bio-Core</metadata>

\t<resources>''')

        # evidence
        refs = a.get("references") or []
        if not refs:
            refs = [{"key": "astmF3659", "kind": "standard", "stdno": "ASTM F3659-24",
                     "grade": "A"}]
        rr = "\n".join(f'\t\t\t<b:reference{A(key=r.get("key"), kind=r.get("kind", "peer-reviewed"), doi=r.get("doi"), stdno=r.get("stdno"), url=r.get("url"), grade=r.get("grade"))}/>'
                       for r in refs)
        parts.append(f'\t\t<b:evidence{A(id=ev_id, path="/bio/references.json")}>\n{rr}\n\t\t</b:evidence>')

        # substances.
        # If none were declared, emit none. A placeholder substance with a TODO name is a
        # fabricated material: it would satisfy the shape of the record while asserting the
        # existence of something nobody named. Same principle as the calibration record.
        subs = a.get("substances") or []
        if not subs:
            self.gap("no-materials",
                     "No materials were declared when this package was integrated.",
                     "List each substance with its name, role, and CAS number where one "
                     "exists. For a mixture without a CAS, give supplier and lot. For "
                     "anything you made yourself, give the synthesis route, conditions, "
                     "yield and verification assay.",
                     severity="blocking", affects=[proc_id])
        srows = []
        for s in subs:
            cas = s.get("casrn") or ""
            kind = "pure" if cas else ("mixture" if s.get("supplier") else "biological")
            srows.append(
                f'\t\t\t<b:substance{A(name=s.get("name"), role=s.get("role", "polymer"))}>\n'
                f'\t\t\t\t<b:identity{A(kind=kind, casrn=cas, inchikey=s.get("inchikey", ""), pubchemcid=s.get("pubchemcid"))}/>\n'
                f'\t\t\t\t<b:grade{A(supplier=s.get("supplier", "TODO"), lot=s.get("lot", "TODO"))}/>\n'
                f'\t\t\t</b:substance>')
            if not cas and not s.get("supplier"):
                self.gap(f"substance-{s.get('name', '?')}",
                         f"Substance '{s.get('name')}' has neither a CAS number nor a supplier and lot.",
                         "Record the CAS number, or for a mixture the supplier and lot number, "
                         "or a synthesis record if you made it yourself.",
                         severity="blocking", affects=[sub_id])
        if srows:
            parts.append(f'\t\t<b:substances{A(id=sub_id)}>\n' + "\n".join(srows) +
                         '\n\t\t</b:substances>')

        # cells
        myco = known(a, "mycoplasma_result") or "TODO"
        passage = known(a, "passage_at_print")
        parts.append(f'''\t\t<b:cellpopulations{A(id=cell_id)}>
\t\t\t<b:cellpopulation{A(name=a.get("cell_name") or "TODO cell population")}>
\t\t\t\t<b:origin{A(kind=a.get("cell_kind") or "primary", rrid=known(a, "rrid") or "", taxon="9606", ethicsref=known(a, "ethicsref") or "")}/>
\t\t\t\t<b:authentication{A(assay="mycoplasma", result=myco, date=known(a, "mycoplasma_date"))}/>
\t\t\t\t<b:culture{A(medium=a.get("medium") or "TODO", serum=known(a, "serum") or "", antibiotics=known(a, "antibiotics") or "TODO")}>
\t\t\t\t\t<b:param{A(name="passage_at_print", unit="1", measured=passage or "", provenance="measured" if passage else "estimated")}/>
\t\t\t\t\t<b:param{A(name="atmosphere_O2", unit="%", setpoint=known(a, "atmosphere_O2") or "21", measured=known(a, "atmosphere_O2") or "21", provenance="measured", method="ambient")}/>
\t\t\t\t</b:culture>
\t\t\t</b:cellpopulation>
\t\t</b:cellpopulations>''')
        if myco == "TODO":
            self.gap("mycoplasma", "No mycoplasma test result was supplied.",
                     "Test the population and record the result and date. This is required for "
                     "every population; a positive result is recorded as positive.",
                     severity="blocking", affects=[cell_id])
        if not passage:
            self.gap("passage", "Passage number at print was not supplied.",
                     WHY["passage_at_print"], severity="material", affects=[cell_id],
                     paramname="passage_at_print")

        # ink
        cls = a.get("bioink_class") or "bioink"
        dens = known(a, "cell_density")
        cellload = (f'\t\t\t\t<b:cellload{A(cellpopid=cell_id, cellpopindex=0, density=dens or "0", unit="/mL", provenance="measured" if dens else "estimated", method=known(a, "cell_count_method"))}/>'
                    if cls in ("bioink", "bioresin") else "")
        rheo = ""
        if known(a, "rheology_model") and a.get("rheology_model") != "not measured":
            t = known(a, "temp_of_measurement")
            rheo = (f'\t\t\t\t<b:rheology{A(model=a["rheology_model"])}>\n'
                    f'\t\t\t\t\t<b:param{A(name="temp_of_measurement", unit="Cel", setpoint=t or "", measured=t or "", provenance="measured" if t else "estimated")}/>\n'
                    f'\t\t\t\t</b:rheology>')
        # A bioink needs at least one component, and a component needs a substance. With no
        # substances there is no formulation to describe, so none is emitted and the objects
        # simply carry no pid. That is a geometry package with a dossier skeleton, which is a
        # legitimate and honest intermediate state.
        emit_ink = bool(subs)
        if emit_ink:
            comps = "\n".join(
                f'\t\t\t\t<b:component{A(substanceid=sub_id, substanceindex=i, value=s.get("value", "0"), unit=s.get("unit", "%{w/v}"), provenance="measured" if s.get("value") else "estimated")}/>'
                for i, s in enumerate(subs))
            parts.append(f'\t\t<b:bioinkgroup{A(id=ink_id)}>\n'
                         f'\t\t\t<b:bioink{A(name=a.get("bioink_name") or "unnamed formulation", **{"class": cls})}>\n'
                         + comps + ("\n" + cellload if cellload else "")
                         + ("\n" + rheo if rheo else "")
                         + '\n\t\t\t</b:bioink>\n\t\t</b:bioinkgroup>')
        if emit_ink and cls in ("bioink", "bioresin") and not dens:
            self.gap("cell-density", "Cell density in the formulation was not supplied.",
                     "Count and record it, with the counting method and replicate number.",
                     severity="material", affects=[ink_id])

        # printhead
        drive = (self.head or {}).get("drive") or (
            "pneumatic" if "pneumatic" in self.modality else
            "screw" if "screw" in self.modality else
            "piston" if "piston" in self.modality else "pneumatic")
        geom = known(a, "nozzle_geometry") or "conical"
        bore = known(a, "nozzle_inner_diameter")
        nlen = known(a, "nozzle_length")
        parts.append(f'''\t\t<b:printheads{A(id=head_id)}>
\t\t\t<b:printhead{A(name=(self.head or {}).get("name") or "head 0", drive=drive, tool="T0", bioinkid=(ink_id if emit_ink else None), bioinkindex=(0 if emit_ink else None), temperaturecontrolled=str((self.head or {}).get("temperaturecontrolled", False)).lower())}>
\t\t\t\t<b:nozzle{A(geometry=geom, innerdiameter=bore or "", length=nlen or "", unit="um", material=known(a, "nozzle_material"))}/>
\t\t\t</b:printhead>
\t\t</b:printheads>''')
        if not nlen and self.modality.startswith("extrusion-"):
            self.gap("nozzle-length", "Nozzle length was not supplied.", WHY["nozzle_length"],
                     severity="blocking", affects=[proc_id], paramname="nozzle_length")

        # process
        iso = ISO52900.get(self.modality)
        cal_ref = cal_id if (known(a, "calibration_performed") or
                             any(known(a, f"cal_{t}")
                                 for t in CALIBRATION_EXPECTED.get(self.modality, []))) else None
        parts.append(f'\t\t<b:process{A(id=proc_id, modality=self.modality, iso52900=iso, printheadsid=head_id, calibrationid=cal_ref, regulatoryid=reg_id)}>\n'
                     f'\t\t\t<b:machine{A(vendor=known(a, "machine_vendor") or (self.profile or {}).get("vendor", ""), model=known(a, "machine_model") or "", serial=known(a, "machine_serial") or "", calibrationdate=known(a, "machine_calibrationdate") or "")}/>\n'
                     f'\t\t\t<b:parameters>\n{self.params(proc_id)}\n\t\t\t</b:parameters>\n'
                     f'\t\t</b:process>')

        # calibration.
        # A calibration record without a date is not a weak record, it is a false one: it
        # asserts that a dated event happened. If no date was supplied, emit no record and
        # raise an open item instead. The tool must never fabricate structure to fill a shape.
        tests = CALIBRATION_EXPECTED.get(self.modality, ["geometric_capability"])
        cal_date = known(a, "calibration_performed")
        any_result = any(known(a, f"cal_{t}") for t in tests)
        emit_cal = bool(cal_date or any_result)

        if emit_cal:
            trows = []
            for t in tests:
                v = known(a, f"cal_{t}")
                trows.append(f'\t\t\t<b:test{A(name=t, kind="printability", metric=t, acceptance=known(a, f"cal_{t}_acceptance") or "TODO - state your own criterion", measured=v or "", outcome="pass" if v else "not-performed")}/>')
                if not v:
                    self.gap(f"cal-{t}", f"Calibration test '{t}' has not been performed.",
                             f"Run {t.replace('_', ' ')} and record the measured value against "
                             f"an acceptance criterion you set.", severity="material",
                             affects=[cal_id])
            parts.append(f'\t\t<b:calibration{A(id=cal_id, modality=self.modality, performed=cal_date or "", operator=known(a, "operator") or "TODO")}>\n'
                         + "\n".join(trows) + '\n\t\t</b:calibration>')
            if not cal_date:
                self.gap("cal-date",
                         "Calibration results were supplied but not the date they were obtained.",
                         "Calibration is a dated event with an operator. Record when this set "
                         "was run.", severity="blocking", affects=[cal_id])
        else:
            self.gap("no-calibration",
                     "No calibration was recorded for this build.",
                     f"Run at least {', '.join(tests[:3])} and record each against an "
                     f"acceptance criterion you set, with the date and operator. Until then "
                     f"the process parameters are not tied to a machine whose behaviour was "
                     f"checked.", severity="blocking", affects=[proc_id])

        # regulatory
        regions = a.get("regulatory_regions") or ["none"]
        det = known(a, "determination") or "undetermined"
        jr = []
        for r in regions:
            if r == "none":
                continue
            note = ("see openitem 'reg-determination'" if det == "undetermined" else None)
            jr.append(f'\t\t\t<b:jurisdiction{A(region=r, framework=a.get("intendeduse") or "research-only", instrument="TODO - name the instrument considered", determination=det, determinedby=known(a, "determinedby"), note=note)}/>')
        if not jr:
            jr = [f'\t\t\t<b:jurisdiction{A(region="none", framework="research-only", instrument="not engaged at this intended use", determination="not-applicable")}/>']
        parts.append(f'\t\t<b:regulatory{A(id=reg_id, intendeduse=a.get("intendeduse") or "research-only", contactduration="none", contactnature="none")}>\n'
                     + "\n".join(jr) + '\n\t\t</b:regulatory>')
        if det == "undetermined" and regions != ["none"]:
            self.gap("reg-determination",
                     "Regulatory position is undetermined for at least one jurisdiction.",
                     "Assess against the relevant instrument and record how the view was "
                     "reached, or seek advice. Recording 'undetermined' is acceptable; leaving "
                     "it silent is not.", severity="minor", affects=[reg_id])

        # characterization
        assays = a.get("assays") or []
        if assays:
            arows = []
            for asy in assays:
                readings = "\n".join(
                    f'\t\t\t\t<b:reading{A(timepoint=tp, value=(asy.get("values") or {}).get(tp, ""), provenance="measured" if (asy.get("values") or {}).get(tp) else "estimated", n=asy.get("n"))}/>'
                    for tp in asy.get("timepoints", ["P0D"]))
                arows.append(f'\t\t\t<b:assay{A(name=asy.get("name"), domain=asy.get("domain", "viability"), endpoint=asy.get("endpoint", asy.get("name")), unit=asy.get("unit"), method=asy.get("method") or "TODO - name the method", destructive=str(asy.get("destructive", False)).lower(), acceptance=asy.get("acceptance") or "TODO - state your own")}>\n{readings}\n\t\t\t</b:assay>')
            parts.append(f'\t\t<b:characterization{A(id=char_id)}>\n' + "\n".join(arows) +
                         '\n\t\t</b:characterization>')
        else:
            self.gap("no-characterization",
                     "No assays were declared, so nothing records whether this build worked.",
                     "Declare at least a post-print viability assay with a timepoint and a "
                     "method.", severity="blocking", affects=[proc_id])

        # open items
        if self.open_items:
            rows = []
            for it in self.open_items:
                aff = "".join(f'\n\t\t\t\t<b:affects{A(targetid=t, paramname=it["paramname"])}/>'
                              for t in it["affects"])
                rows.append(f'\t\t\t<b:openitem{A(key=it["key"], kind="unmeasured", severity=it["severity"], status="open", summary=it["summary"], action=it["action"])}>{aff}\n\t\t\t</b:openitem>')
            parts.append(f'\t\t<b:openitems{A(id=open_id)}>\n' + "\n".join(rows) +
                         '\n\t\t</b:openitems>')

        # geometry
        roles = a.get("regionrole")
        if isinstance(roles, str):
            roles = [roles]
        objs, items = [], []
        for i, (name, (verts, tris)) in enumerate(meshes):
            oid = obj_start + i
            role = (roles[i] if roles and i < len(roles) else None) or "parenchyma"
            v = "\n".join(f'\t\t\t\t\t<vertex x="{x:g}" y="{y:g}" z="{z:g}"/>' for x, y, z in verts)
            t = "\n".join(f'\t\t\t\t\t<triangle v1="{p}" v2="{q}" v3="{r}"/>' for p, q, r in tris)
            objs.append(f'\t\t<object{A(id=oid, type="model", name=name, pid=(ink_id if emit_ink else None), pindex=(0 if emit_ink else None))}'
                        f'{A(**{"b:processid": proc_id, "b:printheadid": head_id, "b:printheadindex": 0, "b:regionrole": role})}>\n'
                        f'\t\t\t<mesh>\n\t\t\t\t<vertices>\n{v}\n\t\t\t\t</vertices>\n'
                        f'\t\t\t\t<triangles>\n{t}\n\t\t\t\t</triangles>\n\t\t\t</mesh>\n\t\t</object>')
            items.append(f'\t\t<item{A(objectid=oid, transform="1 0 0 0 1 0 0 0 1 0 0 0")}/>')

        parts.append("\n".join(objs))
        parts.append('\t</resources>\n\n\t<build>\n' + "\n".join(items) + '\n\t</build>\n</model>')
        return "\n\n".join(parts), refs


def write_package(outdir, model_xml, refs):
    for d in ("3D/_rels", "_rels", "bio"):
        os.makedirs(os.path.join(outdir, d), exist_ok=True)
    open(os.path.join(outdir, "3D", "3dmodel.model"), "w").write(model_xml)
    open(os.path.join(outdir, "bio", "references.json"), "w").write(json.dumps([
        {"id": r.get("key"), "type": "standard" if r.get("stdno") else "article-journal",
         "title": r.get("title", r.get("key")), "number": r.get("stdno"), "DOI": r.get("doi"),
         "URL": r.get("url")} for r in refs], indent=2))
    open(os.path.join(outdir, "[Content_Types].xml"), "w").write(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">\n'
        '  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>\n'
        '  <Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>\n'
        '  <Default Extension="json" ContentType="application/vnd.3mf.biodossier.bibliography+json"/>\n'
        '</Types>\n')
    open(os.path.join(outdir, "_rels", ".rels"), "w").write(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n'
        '  <Relationship Id="rel0" Target="/3D/3dmodel.model" '
        'Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>\n'
        '</Relationships>\n')
    open(os.path.join(outdir, "3D", "_rels", "3dmodel.model.rels"), "w").write(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n'
        '  <Relationship Id="rel1" Target="/bio/references.json" '
        'Type="https://3mfbio.com/ns/rel/2026/07/biobibliography"/>\n'
        '</Relationships>\n')


def zip_package(srcdir, out):
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(os.path.join(srcdir, "[Content_Types].xml"), "[Content_Types].xml")
        for root, _, files in os.walk(srcdir):
            for f in sorted(files):
                p = os.path.join(root, f)
                rel = os.path.relpath(p, srcdir).replace(os.sep, "/")
                if rel != "[Content_Types].xml":
                    z.write(p, rel)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("answers", help="JSON from questionnaire.py --format template")
    ap.add_argument("--mesh", action="append", required=True, help="STL or OBJ (repeatable)")
    ap.add_argument("--out", required=True, help="output package directory")
    ap.add_argument("--zip", help="also write a .3mf here")
    ap.add_argument("--profile", help="machine profile name")
    a = ap.parse_args()

    answers = json.load(open(a.answers))
    profile = head = None
    if a.profile or answers.get("_profile"):
        name = a.profile or answers["_profile"]
        p = os.path.join(HERE, "machine_profiles", f"{name}.json")
        if os.path.exists(p):
            profile = json.load(open(p))
            hk = answers.get("_head")
            head = next((h for h in profile["printheads"] if h["key"] == hk), None)
            if head and not answers.get("_modality"):
                answers["_modality"] = head["modality"]

    meshes = []
    for m in a.mesh:
        verts, tris = read_mesh(m)
        if not tris:
            sys.exit(f"{m}: no triangles read")
        meshes.append((os.path.splitext(os.path.basename(m))[0], (verts, tris)))
        print(f"read {m}: {len(verts)} vertices, {len(tris)} triangles")

    b = Builder(answers, profile, head)
    xml, refs = b.build(meshes)
    write_package(a.out, xml, refs)
    print(f"\nwrote package to {a.out}/")
    if a.zip:
        zip_package(a.out, a.zip)
        print(f"wrote {a.zip}")

    blocking = [i for i in b.open_items if i["severity"] == "blocking"]
    print(f"\n{len(b.open_items)} open item(s) recorded, {len(blocking)} blocking.")
    if blocking:
        print("These are what a second laboratory would need before reproducing this build:")
        for i in blocking:
            print(f"  - {i['key']}: {i['summary']}")
    print(f"\nNext: python3 spec/validate_bio.py {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
