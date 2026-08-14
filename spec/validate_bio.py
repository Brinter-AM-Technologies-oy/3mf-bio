#!/usr/bin/env python3
"""
Reference validator for the 3MF Bio Extension, working draft v0.2.

Validates an unpacked 3MF package directory (or a .3mf zip) against the rules that XSD
cannot express: the evidence rule, resource-ID integrity across the core and bio
namespaces, property-group binding, OPC relationship coverage for every referenced part,
and the modality-dispatched required-parameter sets.

Usage:
    python3 validate_bio.py <package-dir-or-.3mf> [--strict] [--release]

    --strict   treat warnings as errors
    --release  additionally fail on any provenance="estimated"
    --online   resolve DOIs and RRIDs against public registries (needs network)

Exit codes: 0 clean, 1 errors, 2 warnings only (unless --strict).
"""
import datetime
import hashlib
import json
import os
import re
import sys
import tempfile
import zipfile
from xml.etree import ElementTree as ET

CORE = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
BIO = "https://3mfbio.com/ns/bio/2026/07"
VOL = "http://schemas.3mf.io/3dmanufacturing/volumetric/2022/01"
OPC_REL = "http://schemas.openxmlformats.org/package/2006/relationships"

C = lambda t: f"{{{CORE}}}{t}"
B = lambda t: f"{{{BIO}}}{t}"
V = lambda t: f"{{{VOL}}}{t}"

errors, warnings = [], []


def _where(el):
    if el is None:
        return ""
    tag = el.tag.split("}")[-1]
    ident = el.get("id") or el.get("name") or el.get("endpoint") or ""
    return f" <{tag}{' ' + repr(ident) if ident else ''}>"


def err(rule, msg, el=None):
    errors.append(f"[{rule}]{_where(el)} {msg}")


def warn(rule, msg, el=None):
    warnings.append(f"[{rule}]{_where(el)} {msg}")


# --------------------------------------------------------------------------- rules

SPEC_VERSION = "0.9.0"


def check_version(model):
    """M1-M2: a package must declare which draft of this extension it was written against."""
    declared = None
    for md in model.findall(C("metadata")):
        if md.get("name") in ("b:SpecVersion", "SpecVersion"):
            declared = (md.text or "").strip()
    if not declared:
        err("M1", f"package declares no <metadata name=\"b:SpecVersion\">. A consumer cannot "
                  f"tell which draft it is reading; this extension is pre-1.0 and changing")
        return
    try:
        major_minor = tuple(int(x) for x in declared.split(".")[:2])
        ours = tuple(int(x) for x in SPEC_VERSION.split(".")[:2])
    except ValueError:
        err("M1", f"SpecVersion {declared!r} is not a dotted numeric version")
        return
    if major_minor > ours:
        warn("M2", f"package declares SpecVersion {declared}, newer than this validator "
                   f"({SPEC_VERSION}); unknown content will be reported but not understood")
    elif major_minor < ours:
        warn("M2", f"package declares SpecVersion {declared}; this validator implements "
                   f"{SPEC_VERSION}. Pre-1.0 drafts are not compatible across minor versions")


def check_declaration(model):
    """The extension must be declared required when the package encodes living material."""
    req = (model.get("requiredextensions") or "").split()
    prefixes = [p.split(":")[1] for p in model.attrib
                if p.startswith("{http://www.w3.org/2000/xmlns/}")]
    has_cells = model.find(f".//{B('cellload')}") is not None
    bio_prefix = None
    for k, v in model.attrib.items():
        if v == BIO and k.startswith("{http://www.w3.org/2000/xmlns/}"):
            bio_prefix = k.split("}")[1]
    if bio_prefix is None:
        # ElementTree drops xmlns declarations; fall back to accepting any declared prefix
        bio_prefix = "b"
    if has_cells and bio_prefix not in req:
        err("X1", f"package encodes cell-laden material but does not list the bio prefix "
                  f"{bio_prefix!r} in requiredextensions={req!r}")


def collect_resource_ids(model):
    """3MF requires resource IDs to be unique across the whole model, core and extensions."""
    res = model.find(C("resources"))
    ids, dupes = {}, []
    if res is None:
        err("X2", "model has no <resources> element")
        return ids
    for el in res:
        rid = el.get("id")
        if rid is None:
            continue
        if rid in ids:
            dupes.append(rid)
            err("X3", f"resource id {rid} is used by both <{ids[rid].tag.split('}')[-1]}> "
                      f"and <{el.tag.split('}')[-1]}>; 3MF resource ids MUST be unique "
                      f"across core and all extensions", el)
        ids[rid] = el
    return ids


def build_evidence_index(model):
    """evid -> number of <reference> children, for evindices bounds checking."""
    idx = {}
    for ev in model.iter(B("evidence")):
        refs = ev.findall(B("reference"))
        idx[ev.get("id")] = refs
        for r in refs:
            if not (r.get("doi") or r.get("stdno") or r.get("url")):
                warn("E2", f"reference {r.get('key')!r} has no resolvable identifier", ev)
    return idx


def check_evidence_pointer(el, ev_index, rule="V1"):
    """Shared evid/evindices resolution used by param, yield, verification, component..."""
    evid, raw = el.get("evid"), (el.get("evindices") or "").strip()
    if not evid:
        return False
    if evid not in ev_index:
        err(rule, f"evid={evid} does not resolve to an <evidence> resource", el)
        return False
    n = len(ev_index[evid])
    ok = True
    for tok in raw.split():
        if not tok.isdigit() or int(tok) >= n:
            err(rule, f"evindices entry {tok!r} is out of range for evidence group "
                      f"{evid} which has {n} references", el)
            ok = False
    return ok and bool(raw)


def check_params(model, ev_index):
    for p in model.iter(B("param")):
        prov, name = p.get("provenance"), p.get("name")
        resolved = check_evidence_pointer(p, ev_index)
        if prov == "cited" and not resolved:
            err("V1", f"param {name!r} is provenance='cited' but cites no resolvable evidence", p)
        if prov == "measured" and p.get("measured") is None:
            err("V2", f"param {name!r} is provenance='measured' but has no measured attribute", p)
        if prov == "derived" and not p.get("method"):
            err("V3", f"param {name!r} is provenance='derived' but names no model in @method", p)
        if p.get("setpoint") is None and p.get("measured") is None:
            warn("V4", f"param {name!r} carries neither setpoint nor measured", p)


def check_substances(model, ev_index):
    for grp in model.iter(B("substances")):
        for s in grp.findall(B("substance")):
            ident = s.find(B("identity"))
            casrn = (ident.get("casrn") if ident is not None else "") or ""
            kind = (ident.get("kind") if ident is not None else "pure") or "pure"
            syn = s.find(B("synthesis"))
            grade = s.find(B("grade"))
            traced = grade is not None and (grade.get("supplier") or "") and (grade.get("lot") or "")
            if not casrn and syn is None:
                if kind == "mixture" and traced:
                    pass
                elif kind == "mixture":
                    err("S1a", "mixture without CAS must give supplier and lot in <grade>", s)
                else:
                    err("S1/S2", "no CAS number and no synthesis record: substance is "
                                 "unidentifiable", s)
            if syn is not None:
                if syn.find(B("yield")) is None:
                    err("S3", "synthesis present but <yield> absent; emit it with "
                              "provenance='estimated' if unmeasured", s)
                if syn.find(B("verification")) is None:
                    err("S4", "synthesis present with no <verification>: material is "
                              "uncharacterised", s)
                for v in syn.findall(B("verification")):
                    if v.get("provenance") == "cited":
                        check_evidence_pointer(v, ev_index, "S4")
                y = syn.find(B("yield"))
                if y is not None and y.get("provenance") == "cited":
                    check_evidence_pointer(y, ev_index, "S3")


def check_cells(model):
    for grp in model.iter(B("cellpopulations")):
        for c in grp.findall(B("cellpopulation")):
            origin = c.find(B("origin"))
            kind = origin.get("kind") if origin is not None else None
            if kind == "line" and not (origin.get("rrid") or ""):
                err("C1", "kind='line' requires a Cellosaurus RRID; a name is not an "
                          "identifier", c)
            assays = {a.get("assay") for a in c.findall(B("authentication"))}
            if "mycoplasma" not in assays:
                err("C2", "no mycoplasma authentication record", c)
            if kind == "line" and "STR" not in assays:
                warn("C1b", "cell line without an STR authentication record", c)
            cul = c.find(B("culture"))
            if cul is None:
                err("C3", "no <culture> block", c)
                continue
            names = {p.get("name") for p in cul.findall(B("param"))}
            if "passage_at_print" not in names:
                err("C3", "passage_at_print missing: passage number is a process parameter", c)
            if cul.get("antibiotics") in (None, ""):
                err("C4", "antibiotics must be stated explicitly, including the value 'none'", c)
            if "atmosphere_O2" not in names:
                warn("C5", "atmosphere_O2 not recorded; normoxia is a choice, not a default", c)
            serum = cul.get("serum") or ""
            if serum not in ("", "0") and not (cul.get("serumlot") or ""):
                warn("C6", "serum used but serumlot not recorded", c)


def check_inks(model, ids):
    for grp in model.iter(B("bioinkgroup")):
        for i in grp.findall(B("bioink")):
            if i.get("class") == "bioink" and i.find(B("cellload")) is None:
                err("I1", "class='bioink' requires at least one <cellload>", i)
            rh = i.find(B("rheology"))
            if rh is not None:
                names = {p.get("name") for p in rh.findall(B("param"))}
                if "temp_of_measurement" not in names:
                    err("I2", "rheology without temp_of_measurement is uninterpretable", i)
            for comp in i.findall(B("component")):
                tid = comp.get("substanceid")
                tgt = ids.get(tid)
                if tgt is None or tgt.tag != B("substances"):
                    err("I3", f"component substanceid={tid} does not resolve to a "
                              f"<substances> resource", i)
                else:
                    n = len(tgt.findall(B("substance")))
                    if int(comp.get("substanceindex", -1)) >= n:
                        err("I3", f"substanceindex out of range for resource {tid} "
                                  f"({n} substances)", i)
            for cl in i.findall(B("cellload")):
                has_scalar = cl.get("density") is not None
                has_field = bool(cl.get("fieldid") or "")
                if has_scalar and has_field:
                    err("F3", "cellload declares both a scalar density and a fieldid; a load "
                              "is either uniform or graded, not both", i)
                elif not has_scalar and not has_field:
                    err("F3", "cellload declares neither density nor fieldid", i)
                if has_scalar and not (cl.get("unit") or ""):
                    err("F3", "scalar cellload density requires a unit", i)
                tid = cl.get("cellpopid")
                tgt = ids.get(tid)
                if tgt is None or tgt.tag != B("cellpopulations"):
                    err("I4", f"cellload cellpopid={tid} does not resolve to a "
                              f"<cellpopulations> resource", i)
                else:
                    n = len(tgt.findall(B("cellpopulation")))
                    if int(cl.get("cellpopindex", -1)) >= n:
                        err("I4", f"cellpopindex out of range for resource {tid} "
                                  f"({n} populations)", i)


BIO_QUANTITY_NEEDS_CELLS = ("cell_density",)

# ISO/ASTM 52900:2021 process categories. Bio modalities are finer-grained than 52900, so
# the mapping is many-to-one. Only clearly-attributable mappings are asserted; modalities
# whose 52900 category is genuinely arguable are absent and are not checked.
ISO52900 = {
    "extrusion-pneumatic": "MEX", "extrusion-piston": "MEX", "extrusion-screw": "MEX",
    "extrusion-embedded": "MEX", "extrusion-coaxial": "MEX",
    "inkjet-piezo": "MJT", "inkjet-thermal": "MJT", "microvalve": "MJT",
    "acoustic-droplet": "MJT", "laser-lift": "MJT",
    "vat-sla": "VPP", "vat-dlp": "VPP", "vat-2pp": "VPP",
    "stereolithography-continuous": "VPP", "volumetric-tomographic": "VPP",
}

# Calibration tests each modality should have evidenced before a build is reproducible.
# Named for what you do, not for the paper the metric came from. "bridge_test" and
# "grid_test" are what people at the bench actually call these; filament_collapse and
# printability_Pr are the literature terms for the same procedures and remain accepted
# as aliases so older packages keep validating.
#
# layer_stacking_test is a distinct third thing and was previously missing. Bridge and grid
# tests both assess ONE layer. An ink can pass both and still slump at twenty layers,
# because the load that collapses a tall construct is the weight of the layers above it,
# which a single-layer test never applies.
_EXTRUSION_CAL = ["filament_width", "grid_test", "bridge_test", "layer_stacking_test",
                  "filament_fusion", "flow_rate_check"]

# Older names accepted in place of the current ones, so rule K8 does not fire spuriously.
CALIBRATION_ALIASES = {
    "bridge_test": {"filament_collapse", "overhang_test"},
    "grid_test": {"printability_Pr", "lattice_test", "pore_test"},
    "layer_stacking_test": {"stackability", "stacking_test", "cylinder_test"},
    "filament_width": {"strand_width", "line_width"},
}
CALIBRATION_EXPECTED = {
    "extrusion-pneumatic": _EXTRUSION_CAL,
    "extrusion-piston":    _EXTRUSION_CAL,
    "extrusion-screw":     _EXTRUSION_CAL,
    "extrusion-embedded":  _EXTRUSION_CAL + ["bath_rheology", "bath_particle_size"],
    "extrusion-coaxial":   _EXTRUSION_CAL + ["core_shell_concentricity", "wall_thickness"],
    "inkjet-piezo":        ["droplet_volume", "droplet_velocity"],
    "inkjet-thermal":      ["droplet_volume", "droplet_velocity"],
    "microvalve":          ["droplet_volume"],
    "laser-lift":          ["fluence_threshold", "spot_size"],
    "vat-sla":             ["working_curve"],
    "vat-dlp":             ["working_curve", "irradiance_uniformity"],
    "vat-2pp":             ["voxel_size"],
    "volumetric-tomographic": ["dose_threshold", "optical_power_at_vial"],
    "melt-electrowriting": ["critical_translation_speed", "fibre_diameter"],
    "electrospinning":     ["fibre_diameter"],
}

# Intended uses at which a regulatory determination is not optional.
# --- Plausibility: dimension expected for a parameter name, and hard physical bounds.
# These catch transcription and unit-conversion errors, NOT dishonesty. See the threat
# model in the specification: a validator can check that a claim is well formed; it cannot
# check that it is true.
DIMENSION = {
    "length": ["m", "cm", "mm", "um", "nm"],
    "temperature": ["Cel", "K"],
    "pressure": ["Pa", "kPa", "MPa", "bar"],
    "time": ["s", "min", "h", "ms", "us", "ns"],
    "percent": ["%"],
    "irradiance": ["mW/cm2", "W/cm2"],
    "dose": ["mJ/cm2", "J/cm2", "mJ/cm3"],
    "energy": ["uJ", "mJ", "J"],
    "power": ["mW", "W"],
    "voltage": ["V", "kV"],
    "frequency": ["Hz", "kHz", "1/min"],
    "velocity": ["m/s", "mm/s", "mm/min", "um/s"],
    "volume": ["pL", "nL", "uL", "mL", "L"],
    "wavelength": ["nm", "um"],
    "count": ["1"],
    "density": ["/mL", "/uL", "/g"],
    "volume_rate": ["uL/min", "mL/min", "uL/h", "mL/h", "L/min"],
    "area": ["um2", "mm2", "cm2"],
}
PARAM_DIMENSION = {
    "nozzle_inner_diameter": "length", "nozzle_orifice_diameter": "length",
    "nozzle_length": "length", "layer_height": "length", "layer_thickness": "length",
    "strand_spacing": "length", "standoff_height": "length", "standoff_distance": "length",
    "spot_size": "length", "donor_film_thickness": "length", "donor_receiver_gap": "length",
    "receiver_coating_thickness": "length", "absorbing_layer_thickness": "length",
    "collector_distance": "length", "vial_diameter": "length", "fibre_diameter": "length",
    "core_inner_diameter": "length", "shell_inner_diameter": "length",
    "filament_width": "length", "wall_thickness": "length", "z_hop": "length",
    "max_stable_height": "length", "deflection_at_gap": "length", "pore_area": "area",
    "deflection_angle": "count", "normalized_pore_number": "percent",
    "shape_fidelity_index": "count", "aspect_ratio": "count",
    "wall_thickness_ratio": "count", "layers_before_collapse": "count",
    "bath_particle_diameter": "length", "cure_depth_Cd": "length",
    "penetration_depth_Dp": "length", "xy_pixel_pitch": "length",
    "build_temp": "temperature", "cartridge_temp": "temperature", "bed_temp": "temperature",
    "bath_temp": "temperature", "nozzle_temp": "temperature", "heater_temp": "temperature",
    "chamber_temp": "temperature", "incubator_temp": "temperature",
    "temp_of_measurement": "temperature", "reaction_temp": "temperature",
    "flushing_temp": "temperature", "release_temp": "temperature",
    "extrusion_pressure": "pressure", "feed_pressure": "pressure",
    "yield_stress": "pressure", "bath_yield_stress": "pressure",
    "wall_shear_stress_max": "pressure",
    "print_duration": "time", "exposure_time_per_layer": "time", "bottom_exposure": "time",
    "pulse_duration": "time", "reaction_time": "time", "release_time": "time",
    "residence_time_in_nozzle": "time", "time_out_of_incubator": "time",
    "cell_viability_post_print": "percent", "chamber_RH": "percent",
    "ambient_RH": "percent", "atmosphere_CO2": "percent", "atmosphere_O2": "percent",
    "irradiance": "irradiance",
    "total_light_dose": "dose", "critical_energy_Ec": "dose", "laser_fluence": "dose",
    "post_cure_dose": "dose",
    "pulse_energy": "energy",
    "optical_power": "power", "average_power": "power",
    "applied_voltage": "voltage", "collector_voltage": "voltage",
    "jetting_frequency": "frequency", "repetition_rate": "frequency",
    "rotation_speed": "frequency",
    "print_speed": "velocity", "droplet_velocity": "velocity", "scan_speed": "velocity",
    "collector_speed": "velocity", "critical_translation_speed": "velocity",
    "droplet_volume": "volume",
    "flow_rate": "volume_rate", "cycles_per_day": "count", "strain_amplitude": "percent",
    "stimulation_frequency": "frequency", "wall_shear_stress": "pressure",
    "pressure_amplitude": "pressure", "field_strength": "voltage",
    "stimulation_duration": "time", "pulse_width": "time",
    "core_shell_ratio": "count", "perimeter_count": "count", "raster_angle": "count",
    "printability_Pr": "count", "screw_speed": "frequency",
    "light_wavelength": "wavelength", "laser_wavelength": "wavelength",
    "number_of_projections": "count", "passage_at_print": "count", "flow_index_n": "count",
    "resin_refractive_index": "count", "Z_number": "count", "Weber_number": "count",
    "speed_ratio": "count", "cells_per_droplet": "count",
}
# (low, high, unit) - deliberately generous. A bound that fires on legitimate work is worse
# than no bound, so these reject only the physically impossible or the plainly mistyped.
BOUNDS = {
    "printability_Pr": (0, 5, "1"),
    "shape_fidelity_index": (0, 3, "1"),
    "normalized_pore_number": (0, 200, "%"),
    "deflection_angle": (0, 90, "1"),
    "wall_thickness_ratio": (0, 5, "1"),
    "strain_amplitude": (0, 100, "%"),
    "cycles_per_day": (0, 10000000, "1"),
    "core_shell_ratio": (0, 100, "1"),
    "raster_angle": (-360, 360, "1"),
    "cell_viability_post_print": (0, 100, "%"),
    "chamber_RH": (0, 100, "%"), "ambient_RH": (0, 100, "%"),
    "atmosphere_CO2": (0, 100, "%"), "atmosphere_O2": (0, 100, "%"),
    "purity": (0, 100, "%"),
    "passage_at_print": (0, 100, "1"),
    "initial_pH": (0, 14, "1"),
    "reaction_pH": (0, 14, "1"),
    "resin_refractive_index": (1.0, 3.0, "1"),
    "flow_index_n": (0, 2, "1"),
    "light_wavelength": (100, 2000, "nm"), "laser_wavelength": (100, 2000, "nm"),
    "build_temp": (-200, 500, "Cel"), "incubator_temp": (0, 100, "Cel"),
    "cartridge_temp": (-200, 500, "Cel"), "temp_of_measurement": (-200, 500, "Cel"),
}
NONNEGATIVE = ("density", "conc", "diameter", "thickness", "duration", "time", "power",
               "energy", "dose", "volume", "pressure", "speed", "frequency", "count")

REGULATED_USE = ("clinical-investigation", "implantable", "preclinical", "veterinary")


def _num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def check_plausibility(model):
    """U1-U3: dimension and physical-bound sanity. Catches transcription and unit errors."""
    for p in model.iter(B("param")):
        name, unit = p.get("name"), p.get("unit")
        dim = PARAM_DIMENSION.get(name)
        if dim and unit and unit not in DIMENSION[dim]:
            err("U1", f"param {name!r} is a {dim} quantity but carries unit {unit!r}; "
                      f"expected one of {DIMENSION[dim]}", p)
        for attr in ("setpoint", "measured"):
            v = _num(p.get(attr))
            if v is None:
                continue
            if name in BOUNDS:
                lo, hi, u = BOUNDS[name]
                if not (lo <= v <= hi):
                    err("U2", f"param {name!r} {attr}={v} is outside the physically possible "
                              f"range [{lo}, {hi}] {u}", p)
            elif v < 0 and any(k in name for k in NONNEGATIVE):
                err("U2", f"param {name!r} {attr}={v} is negative", p)

    for cl in model.iter(B("cellload")):
        v = _num(cl.get("density"))
        if v is not None and v < 0:
            err("U2", f"cell density {v} is negative", cl)

    # Field ranges: a graded quantity's declared span must itself be possible.
    NONNEG_QUANTITY = ("cell_density", "stiffness_target", "photoinitiator_conc",
                       "polymer_conc", "porosity", "mineral_fraction",
                       "growth_factor_conc", "crosslink_density", "oxygen_tension")
    for fb in model.iter(B("fieldbinding")):
        rng = fb.find(B("range"))
        if rng is None:
            continue
        lo, hi, fb_ = _num(rng.get("min")), _num(rng.get("max")), _num(rng.get("fallback"))
        q = fb.get("quantity")
        if lo is not None and hi is not None and lo > hi:
            err("U4", f"field range min={lo} exceeds max={hi}", fb)
        if q in NONNEG_QUANTITY:
            for label, v in (("min", lo), ("max", hi), ("fallback", fb_)):
                if v is not None and v < 0:
                    err("U4", f"field {label}={v} is negative for quantity {q!r}", fb)
        if fb_ is not None and lo is not None and hi is not None and not (lo <= fb_ <= hi):
            warn("U4", f"field fallback={fb_} lies outside the declared range "
                       f"[{lo}, {hi}]", fb)
        if q == "porosity" and hi is not None and hi > 100 and rng.get("max"):
            warn("U4", f"porosity max={hi} exceeds 100", fb)

    for p in model.iter(B("param")):
        sp, ms = _num(p.get("setpoint")), _num(p.get("measured"))
        if sp is not None and ms is not None and sp != 0:
            ratio = abs(ms - sp) / abs(sp)
            if ratio > 0.5:
                warn("U3", f"param {p.get('name')!r} measured={ms} differs from setpoint={sp} "
                           f"by {ratio * 100:.0f}%; confirm this is real and not a unit error", p)


def check_dates(model):
    """D1-D2: dates that cannot be true."""
    today = datetime.date.today()
    for el in model.iter():
        if not isinstance(el.tag, str) or not el.tag.startswith(f"{{{BIO}}}"):
            continue
        for attr in ("performed", "date", "raised", "resolved", "calibrationdate",
                     "determineddate"):
            v = el.get(attr)
            if not v:
                continue
            try:
                d = datetime.date.fromisoformat(v)
            except ValueError:
                err("D1", f"{attr}={v!r} is not a valid ISO date", el)
                continue
            if d > today:
                err("D2", f"{attr}={v} is in the future", el)
    for it in model.iter(B("openitem")):
        r, res = it.get("raised"), it.get("resolved")
        if r and res:
            try:
                if datetime.date.fromisoformat(res) < datetime.date.fromisoformat(r):
                    err("D2", f"open item {it.get('key')!r} was resolved before it was raised",
                        it)
            except ValueError:
                pass


def check_authentication_results(model):
    """C7: an authentication record that reports a failure is not a satisfied requirement."""
    BAD = ("positive", "fail", "failed", "mismatch", "contaminated", "not match", "no match")
    for c in model.iter(B("cellpopulation")):
        for a in c.findall(B("authentication")):
            res = (a.get("result") or "").strip().lower()
            assay = (a.get("assay") or "").lower()
            if not res:
                warn("C8", f"authentication {assay!r} records no result", c)
                continue
            hit = any(b in res for b in BAD)
            if assay == "mycoplasma" and hit:
                err("C7", f"mycoplasma authentication result is {a.get('result')!r}. A "
                          f"contaminated population invalidates the biological record; this "
                          f"is not a satisfiable requirement by recording it", c)
            elif hit:
                warn("C7", f"authentication {assay!r} result {a.get('result')!r} appears to "
                           f"report a failure", c)


def check_checksums(model, root_dir):
    """T4: a recorded hash that nobody checks is decoration."""
    for tp in model.iter(B("toolpath")):
        raw = (tp.get("checksum") or "").strip()
        path = tp.get("path") or ""
        if not raw or ":" not in raw:
            continue
        algo, _, digest = raw.partition(":")
        algo = algo.lower()
        if algo not in hashlib.algorithms_available:
            warn("T4", f"toolpath checksum algorithm {algo!r} is not recognised", tp)
            continue
        fs = os.path.join(root_dir, path.lstrip("/"))
        if not os.path.exists(fs):
            continue  # O2 reports the missing part
        h = hashlib.new(algo)
        with open(fs, "rb") as fh:
            for chunk in iter(lambda: fh.read(65536), b""):
                h.update(chunk)
        actual = h.hexdigest()
        if actual != digest.lower():
            err("T4", f"toolpath checksum does not match {path}: recorded {digest[:16]}..., "
                      f"actual {actual[:16]}...", tp)


def check_online(model, enabled):
    """W1-W2: identifier resolution. Off by default; needs network."""
    if not enabled:
        return
    try:
        import urllib.request
    except ImportError:
        return
    seen = set()
    for r in model.iter(B("reference")):
        doi = r.get("doi")
        if not doi or doi in seen:
            continue
        seen.add(doi)
        try:
            req = urllib.request.Request(f"https://doi.org/api/handles/{doi}",
                                         headers={"User-Agent": "3mf-bio-validator"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                if json.load(resp).get("responseCode") != 1:
                    err("W1", f"DOI {doi} does not resolve", r)
        except Exception as e:
            warn("W1", f"could not verify DOI {doi}: {e}", r)
    for o in model.iter(B("origin")):
        rrid = o.get("rrid") or ""
        if not rrid:
            continue
        try:
            req = urllib.request.Request(
                f"https://api.cellosaurus.org/cell-line/{rrid}?format=json",
                headers={"User-Agent": "3mf-bio-validator"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                resp.read(1)
        except Exception as e:
            warn("W2", f"could not verify RRID {rrid}: {e}", o)


def _iso_days(tp):
    """Crude ISO 8601 duration ordering. Good enough to sort timepoints."""
    if not tp or not tp.startswith("P"):
        return None
    import re as _re
    m = _re.match(r"P(?:(\d+)Y)?(?:(\d+)M)?(?:(\d+)W)?(?:(\d+)D)?"
                  r"(?:T(?:(\d+)H)?(?:(\d+)M)?(?:([\d.]+)S)?)?$", tp)
    if not m:
        return None
    y, mo, w, d, h, mi, sec = [float(x) if x else 0 for x in m.groups()]
    return y * 365 + mo * 30 + w * 7 + d + h / 24 + mi / 1440 + sec / 86400


# A stimulation regime is only interpretable if magnitude, rate and duration are all
# present. The perfusion-bioreactor literature notes that circuit parameters "as a group"
# are routinely omitted, which is precisely why this is a rule and not a suggestion.
STIMULATION_REQUIRED = {
    "fluid-shear":          ["flow_rate", "wall_shear_stress", "stimulation_duration"],
    "cyclic-tension":       ["strain_amplitude", "stimulation_frequency", "cycles_per_day"],
    "cyclic-compression":   ["strain_amplitude", "stimulation_frequency", "cycles_per_day"],
    "hydrostatic-pressure": ["pressure_amplitude", "stimulation_frequency", "stimulation_duration"],
    "electrical":           ["field_strength", "stimulation_frequency", "pulse_width"],
    "electromagnetic":      ["field_strength", "stimulation_frequency", "stimulation_duration"],
    "ultrasound":           ["intensity", "stimulation_frequency", "stimulation_duration"],
}


def check_maturation(model, ids):
    """Q1-Q6: what happens to the construct after the print.

    A printed construct is not the product. The matured construct is. A format that stops
    at the print records the least biologically consequential half of the work.
    """
    for mat in model.iter(B("maturation")):
        tid = mat.get("targetid") or ""
        if tid and tid not in ids:
            err("Q1", f"maturation targetid={tid} does not resolve to a resource", mat)

        stages = mat.findall(B("stage"))
        prev_to = None
        for st in stages:
            frm, to = st.get("from"), st.get("to")
            a, b_ = _iso_days(frm), _iso_days(to)
            if a is not None and b_ is not None and b_ < a:
                err("Q2", f"maturation stage {st.get('name')!r} ends ({to}) before it "
                          f"begins ({frm})", mat)
            if prev_to is not None and a is not None and a < prev_to:
                warn("Q2", f"maturation stage {st.get('name')!r} starts at {frm}, before the "
                           f"previous stage ended; overlapping stages need a note", mat)
            if b_ is not None:
                prev_to = b_

            fmt = st.get("culture")
            br = st.find(B("bioreactor"))
            brparams = {p.get("name") for p in br.findall(B("param"))} if br is not None else set()

            if fmt == "perfusion":
                if br is None:
                    err("Q3", f"stage {st.get('name')!r} is perfusion culture but describes no "
                              f"bioreactor", mat)
                elif "flow_rate" not in brparams:
                    err("Q3", f"perfusion stage {st.get('name')!r} records no flow_rate. Flow "
                              f"rate is the parameter that sets wall shear stress at the "
                              f"construct, and shear drives differentiation", mat)
            if br is not None and br.get("kind") not in (None, "", "none") and fmt == "static":
                warn("Q4", f"stage {st.get('name')!r} declares culture='static' but names a "
                           f"{br.get('kind')!r} bioreactor", mat)

            for stim in st.findall(B("stimulation")):
                mode = stim.get("mode")
                names = {p.get("name") for p in stim.findall(B("param"))}
                for need in STIMULATION_REQUIRED.get(mode, []):
                    if need not in names:
                        err("Q5", f"stimulation mode {mode!r} in stage {st.get('name')!r} "
                                  f"records no {need!r}. Magnitude, rate and duration are only "
                                  f"interpretable together", mat)

            for med in st.findall(B("medium")):
                if not (med.get("exchangeinterval") or ""):
                    warn("Q6", f"medium {med.get('name')!r} in stage {st.get('name')!r} "
                               f"records no exchange interval", mat)
                serum = med.get("serum") or ""
                if serum not in ("", "0") and not (med.get("serumlot") or ""):
                    warn("Q6", f"medium {med.get('name')!r} uses serum but records no lot", mat)


def check_characterization(model, ids):
    """Q7-Q11: assays over time, and the timecourse a single result cannot express."""
    for ch in model.iter(B("characterization")):
        tid = ch.get("targetid") or ""
        if tid and tid not in ids:
            err("Q7", f"characterization targetid={tid} does not resolve", ch)

        for a in ch.findall(B("assay")):
            readings = a.findall(B("reading"))
            if not a.get("method"):
                err("Q8", f"assay {a.get('name')!r} names no method. An endpoint without a "
                          f"method is not a measurement", ch)
            tps = [r.get("timepoint") for r in readings]
            dupes = {t for t in tps if tps.count(t) > 1}
            if dupes:
                err("Q9", f"assay {a.get('name')!r} has more than one reading at timepoint(s) "
                          f"{sorted(dupes)}; use n and sd for replicates", ch)
            if a.get("destructive") == "true" and len(readings) > 1:
                warn("Q10", f"assay {a.get('name')!r} is destructive but has "
                            f"{len(readings)} timepoints; each requires its own specimen, "
                            f"which should be recorded as separate test-coupon objects", ch)
            for r in readings:
                if r.get("provenance") == "measured" and not (r.get("value") or ""):
                    err("Q11", f"reading at {r.get('timepoint')} in assay {a.get('name')!r} is "
                               f"provenance='measured' but carries no value", ch)
                if a.get("acceptance") and (r.get("value") or "") and not r.get("outcome"):
                    warn("Q11", f"assay {a.get('name')!r} has an acceptance criterion and a "
                                f"value at {r.get('timepoint')} but records no outcome", ch)
                n = r.get("n")
                if n in (None, "", "0", "1") and (r.get("sd") or ""):
                    warn("Q11", f"reading at {r.get('timepoint')} reports a standard deviation "
                                f"with n={n!r}", ch)

    # a package with maturation but no characterization has recorded a process with no result
    if model.find(f".//{B('maturation')}") is not None \
            and model.find(f".//{B('characterization')}") is None:
        warn("Q12", "package records a maturation regime but no characterization; the effect "
                    "of the regime is therefore unrecorded")


def check_calibration(model, ids):
    """K1-K6: calibration as a dated, evidenced event."""
    cals = {c.get("id"): c for c in model.iter(B("calibration"))}
    objects = {o.get("id") for o in model.iter(C("object"))}

    for c in cals.values():
        if not (c.get("performed") or ""):
            err("K1", "calibration record without a performed date; a calibration is an event, "
                      "not a machine attribute", c)
        for t in c.findall(B("test")):
            if not t.get("acceptance"):
                err("K2", f"calibration test {t.get('name')!r} has no acceptance criterion", c)
            if t.get("outcome") == "pass" and t.get("measured") in (None, ""):
                err("K3", f"calibration test {t.get('name')!r} is marked pass but records no "
                          f"measured value", c)
            aid = t.get("artifactobjectid") or ""
            if aid and aid not in objects:
                err("K4", f"calibration test {t.get('name')!r} references artifact object "
                          f"{aid}, which does not exist", c)
            if t.get("outcome") == "fail":
                warn("K5", f"calibration test {t.get('name')!r} FAILED; builds using this "
                           f"process are out of specification", c)

    for pr in model.iter(B("process")):
        cid = pr.get("calibrationid") or ""
        mod = pr.get("modality", "")
        if not cid:
            warn("K6", f"process {pr.get('id')} declares no calibration record", pr)
            continue
        if cid not in cals:
            err("K4", f"process calibrationid={cid} does not resolve to a <b:calibration>", pr)
            continue
        cal = cals[cid]
        if cal.get("modality") != mod:
            err("K7", f"process modality {mod!r} does not match the calibration record's "
                      f"modality {cal.get('modality')!r}", pr)
        names = {t.get("name") for t in cal.findall(B("test"))}
        for want in CALIBRATION_EXPECTED.get(mod, []):
            if want in names or (names & CALIBRATION_ALIASES.get(want, set())):
                continue
            hint = ""
            if want == "layer_stacking_test":
                hint = (" - a bridge test and a grid test both assess one layer; an ink can "
                        "pass both and still slump under the weight of twenty")
            warn("K8", f"modality {mod!r} has no calibration test named {want!r}{hint}", pr)


def check_regulatory(model, ids):
    """R4-R9: regulatory determination is recorded, not assumed."""
    regs = {r.get("id"): r for r in model.iter(B("regulatory"))}
    openkeys = {o.get("key") for o in model.iter(B("openitem"))}

    for r in regs.values():
        use = r.get("intendeduse")
        js = r.findall(B("jurisdiction"))
        if not js:
            err("R4", "regulatory resource with no jurisdiction", r)
        for j in js:
            if j.get("determination") == "undetermined":
                note = j.get("note") or ""
                if not any(f"'{k}'" in note for k in openkeys):
                    err("R5", f"jurisdiction {j.get('region')!r} is undetermined but points at "
                              f"no open item; an undetermined status must be tracked", r)
            if use in REGULATED_USE and j.get("determination") == "self-assessed":
                warn("R6", f"intended use {use!r} in region {j.get('region')!r} rests on "
                           f"self-assessment; confirm with the authority", r)
        if use in ("clinical-investigation", "implantable"):
            stds = {sr.get("stdno") for sr in r.findall(B("standardref"))}
            if not any(str(x).startswith("ISO 10993") for x in stds):
                err("R7", f"intended use {use!r} requires an ISO 10993 standardref", r)
            if not (r.get("contactduration") and r.get("contactnature")):
                err("R8", f"intended use {use!r} requires contactduration and contactnature; "
                          f"they are the inputs to ISO 10993 categorisation", r)
        for ob in r.iter(B("obligation")):
            if ob.get("status") in ("not-met", "unknown") and not (ob.get("openitemid") or
                                                                   ob.get("note")):
                warn("R9", f"obligation {ob.get('ref')!r} is {ob.get('status')!r} with no "
                           f"open item or note", r)

    for pr in model.iter(B("process")):
        rid = pr.get("regulatoryid") or ""
        if rid and rid not in regs:
            err("R4", f"process regulatoryid={rid} does not resolve to a <b:regulatory>", pr)


def check_openitems(model, ids):
    """J1-J6: open items are the record of what is not known."""
    items = list(model.iter(B("openitem")))
    keys = {}
    for it in items:
        k = it.get("key")
        if k in keys:
            err("J1", f"duplicate open item key {k!r}", it)
        keys[k] = it
        st = it.get("status")
        if st == "resolved" and not (it.get("resolution") or ""):
            err("J2", f"open item {k!r} is resolved but records no resolution", it)
        if st == "resolved" and not (it.get("resolved") or ""):
            err("J2", f"open item {k!r} is resolved but records no resolution date", it)
        if st in ("open", "in-progress") and not (it.get("action") or ""):
            err("J3", f"open item {k!r} states no action that would close it", it)
        for a in it.findall(B("affects")):
            tid = a.get("targetid")
            if tid not in ids:
                err("J4", f"open item {k!r} affects target {tid}, which is not a resource", it)

    # Anything estimated or empty should be accounted for by an open item.
    covered = set()
    for it in items:
        for a in it.findall(B("affects")):
            pn = a.get("paramname")
            if pn:
                covered.add((a.get("targetid"), pn))
            # A resource-wide <affects> (no paramname) refers to the resource's own
            # attributes -- machine serial, donor metadata -- and deliberately does NOT
            # excuse individual estimated params inside it. An open item about a missing
            # firmware version should not silently account for an unmeasured light dose.

    def owning_resource(el):
        cur = el
        while cur is not None:
            if cur.get("id") and cur.tag.startswith(f"{{{BIO}}}"):
                return cur.get("id")
            cur = parents.get(id(cur))
        return None

    parents = {id(ch): p for p in model.iter() for ch in p}
    uncovered = []
    for p in model.iter(B("param")):
        if p.get("provenance") != "estimated":
            continue
        rid = owning_resource(p)
        if rid is None:
            continue
        if (rid, p.get("name")) in covered:
            continue
        uncovered.append((rid, p.get("name")))
    for rid, name in uncovered:
        warn("J5", f"param {name!r} in resource {rid} is provenance='estimated' but no open "
                   f"item accounts for it")

    blocking = [i for i in items if i.get("severity") == "blocking"
                and i.get("status") in ("open", "in-progress")]
    if blocking:
        warn("J6", f"{len(blocking)} blocking open item(s) unresolved: "
                   f"{sorted(i.get('key') for i in blocking)}")


def check_iso52900(model):
    for pr in model.iter(B("process")):
        mod, cat = pr.get("modality", ""), pr.get("iso52900")
        expect = ISO52900.get(mod)
        if cat and expect and cat != expect:
            err("N1", f"modality {mod!r} maps to ISO/ASTM 52900 category {expect!r}, not "
                      f"{cat!r}", pr)
        if expect and not cat:
            warn("N2", f"process declares no iso52900 category (expected {expect!r})", pr)



def check_fields(model, ids):
    """F1-F6: the bio/volumetric binding."""
    bindings = {fb.get("id"): fb for fb in model.iter(B("fieldbinding"))}
    volumes = {v.get("id"): v for v in model.iter(V("volumedata"))}

    if bindings and model.find(f".//{V('volumedata')}") is None:
        warn("F5", "field bindings are present but no <v:volumedata> resource was found; is "
                   "the volumetric extension namespace declared?")

    for fb in bindings.values():
        vid = fb.get("volumeid")
        vol = volumes.get(vid)
        if vol is None:
            err("F1", f"fieldbinding volumeid={vid} does not resolve to a <v:volumedata> "
                      f"resource", fb)
        else:
            names = {pr.get("name") for pr in vol.findall(V("property"))}
            if fb.get("property") not in names:
                err("F2", f"fieldbinding names property {fb.get('property')!r}, which is not a "
                          f"<v:property> of volumedata {vid} (has: {sorted(n for n in names if n)})",
                    fb)
        if fb.get("provenance") in ("cited", "derived") and not fb.get("method") \
                and not fb.get("evid"):
            err("F7", "field binding carries neither evidence nor a method; the evidence rule "
                      "applies to graded quantities too", fb)
        mp = fb.find(B("maps"))
        if mp is not None:
            bid = mp.get("bioinkid")
            grp = ids.get(bid)
            if grp is None or grp.tag != B("bioinkgroup"):
                err("F8", f"maps bioinkid={bid} does not resolve to a <b:bioinkgroup>", fb)
            elif int(mp.get("bioinkindex", -1)) >= len(grp.findall(B("bioink"))):
                err("F8", "maps bioinkindex is out of range", fb)
        rng = fb.find(B("range"))
        if rng is None:
            warn("F9", "field binding without a <b:range>; the field's admissible span is "
                       "undeclared", fb)

    for cl in model.iter(B("cellload")):
        fid = cl.get("fieldid") or ""
        if fid and fid not in bindings:
            err("F4", f"cellload fieldid={fid} does not resolve to a <b:fieldbinding>", cl)
        elif fid:
            q = bindings[fid].get("quantity")
            if q not in BIO_QUANTITY_NEEDS_CELLS:
                err("F6", f"cellload binds field {fid} whose quantity is {q!r}; a cell load "
                          f"must bind a cell_density field", cl)

    for fb in bindings.values():
        if fb.get("quantity") == "cell_density":
            mp = fb.find(B("maps"))
            if mp is not None:
                grp = ids.get(mp.get("bioinkid"))
                if grp is not None and grp.tag == B("bioinkgroup"):
                    inks = grp.findall(B("bioink"))
                    idx = int(mp.get("bioinkindex", -1))
                    if 0 <= idx < len(inks) and inks[idx].get("class") == "biomaterial-ink":
                        err("F6", "a cell_density field is mapped to a biomaterial-ink, which "
                                  "by definition contains no cells", fb)


# Embedded extrusion is still extrusion: it inherits the base set and adds the bath.
# Defining it as a separate flat list once let the Python table, the Schematron and the
# specification prose disagree about whether print_speed was required. Inheritance makes
# that class of drift impossible.
# Extrusion is the dominant modality and gets the deepest treatment.
#
# nozzle_length is REQUIRED, not optional: the wall shear stress relation is tau_w =
# dP*R/(2L). Without a length there is no derivable shear stress, and shear is the
# quantity the whole cell-damage literature turns on.
#
# The controlled variable differs by drive. A pneumatic system commands a pressure; a
# piston commands a displacement rate; a screw commands a rotation. Demanding
# extrusion_pressure from a piston system is a category error, so the sets diverge.
_EXTRUSION_BASE = ["nozzle_inner_diameter", "nozzle_geometry", "nozzle_length",
                   "print_speed", "cartridge_temp", "layer_height", "strand_spacing"]
_PNEUMATIC = ["extrusion_pressure"]
_DISPLACEMENT = ["volumetric_flow_rate"]
_BATH = ["bath_composition", "bath_particle_diameter", "bath_yield_stress", "bath_temp"]
_COAXIAL = ["core_flow_rate", "shell_flow_rate", "core_shell_ratio",
            "core_inner_diameter", "shell_inner_diameter"]

REQUIRED = {
    "extrusion-pneumatic": _EXTRUSION_BASE + _PNEUMATIC,
    "extrusion-piston":    _EXTRUSION_BASE + _DISPLACEMENT,
    "extrusion-screw":     _EXTRUSION_BASE + _DISPLACEMENT + ["screw_speed"],
    "extrusion-embedded":  _EXTRUSION_BASE + _BATH,
    "extrusion-coaxial":   _EXTRUSION_BASE + _COAXIAL,
    "inkjet-piezo":        ["droplet_volume", "droplet_velocity", "jetting_frequency",
                            "nozzle_orifice_diameter"],
    "inkjet-thermal":      ["droplet_volume", "droplet_velocity", "jetting_frequency",
                            "nozzle_orifice_diameter", "heater_temp"],
    "microvalve":          ["droplet_volume", "droplet_velocity", "jetting_frequency"],
    "laser-lift":          ["laser_wavelength", "pulse_duration", "pulse_energy", "laser_fluence",
                            "spot_size", "absorbing_layer_material", "absorbing_layer_thickness",
                            "donor_film_thickness", "donor_receiver_gap",
                            "receiver_coating_thickness"],
    "vat-dlp":             ["light_wavelength", "irradiance", "exposure_time_per_layer",
                            "layer_thickness", "photoinitiator_conc", "photoabsorber_identity",
                            "photoabsorber_conc"],
    "vat-sla":             ["light_wavelength", "irradiance", "exposure_time_per_layer",
                            "layer_thickness", "photoinitiator_conc"],
    "vat-2pp":             ["laser_wavelength", "pulse_duration", "average_power", "NA",
                            "scan_speed"],
    "volumetric-tomographic": ["light_wavelength", "optical_power", "total_light_dose",
                               "print_duration", "rotation_speed", "number_of_projections"],
    "melt-electrowriting": ["nozzle_temp", "applied_voltage", "collector_distance",
                            "collector_speed", "critical_translation_speed"],
    "electrospinning":     ["nozzle_temp", "applied_voltage", "collector_distance"],
}
COMMON = ["build_temp", "print_duration", "sterility_method", "cell_viability_post_print"]
EHD = ("melt-electrowriting", "electrospinning")
DERIVED_ONLY = ("wall_shear_stress_max", "Z_number", "Weber_number", "penetration_depth_Dp",
                "speed_ratio", "total_light_dose", "residence_time_in_nozzle",
                "critical_energy_Ec")


def check_shear_derivation(model, ids):
    """X1: a derived shear stress must have its inputs present, or it is a guess.

    tau_w = dP * R / (2L) for pressure-driven flow, with the rheology model supplying the
    velocity profile. A package that reports wall_shear_stress_max without a nozzle length,
    a radius, a driving term and a fitted rheology model has not derived anything.
    """
    inkgroups = {g.get("id"): g for g in model.iter(B("bioinkgroup"))}
    for pr in model.iter(B("process")):
        pel = pr.find(B("parameters"))
        if pel is None:
            continue
        params = {p.get("name"): p for p in pel.findall(B("param"))}
        shear = params.get("wall_shear_stress_max")
        if shear is None:
            continue
        missing = [n for n in ("nozzle_inner_diameter", "nozzle_length") if n not in params]
        if not ({"extrusion_pressure", "volumetric_flow_rate"} & set(params)):
            missing.append("extrusion_pressure or volumetric_flow_rate")
        # a fitted rheology model must exist on some ink in the package
        has_rheology = any(ink.find(B("rheology")) is not None
                           for g in inkgroups.values() for ink in g.findall(B("bioink")))
        if not has_rheology:
            missing.append("a fitted <b:rheology> on the ink")
        if missing:
            err("X1", f"wall_shear_stress_max is declared but its inputs are absent: "
                      f"{missing}. Shear stress is computed from geometry, driving term and "
                      f"rheology; without them the value is not derived", pr)


def check_printheads(model, ids):
    """H1-H6: deposition heads, nozzles and coaxial channels."""
    groups = {g.get("id"): g for g in model.iter(B("printheads"))}
    inkgroups = {g.get("id"): g for g in model.iter(B("bioinkgroup"))}

    for g in groups.values():
        tools = []
        for h in g.findall(B("printhead")):
            noz = h.find(B("nozzle"))
            drive = h.get("drive")
            geom = noz.get("geometry") if noz is not None else None
            if h.get("tool"):
                tools.append(h.get("tool"))

            if noz is not None and not (noz.get("length") or ""):
                warn("H1", f"printhead {h.get('name')!r} nozzle records no length; wall shear "
                           f"stress cannot be derived without it", g)
            cox = h.find(B("coaxial"))
            if geom in ("coaxial", "triaxial") and cox is None:
                err("H2", f"printhead {h.get('name')!r} declares a {geom} nozzle but has no "
                          f"<b:coaxial> channel description", g)
            if cox is not None:
                roles = [c.get("role") for c in cox.findall(B("channel"))]
                if "core" not in roles or not ({"shell", "sheath"} & set(roles)):
                    err("H2", f"coaxial head {h.get('name')!r} must describe a core and at "
                              f"least one shell or sheath channel; found {roles}", g)
                contents = {c.get("role"): c.get("content")
                            for c in cox.findall(B("channel"))}
                product = cox.get("product")
                if product == "hollow-tube" and contents.get("core") == "bioink":
                    err("H4", f"coaxial head {h.get('name')!r} claims product 'hollow-tube' but "
                              f"the core carries bioink. A hollow tube requires a sacrificial, "
                              f"crosslinker or mist core", g)
                if product == "solid-fibre" and contents.get("core") in ("sacrificial",
                                                                        "crosslinker-mist"):
                    err("H4", f"coaxial head {h.get('name')!r} claims product 'solid-fibre' but "
                              f"the core is {contents.get('core')!r}", g)
                for c in cox.findall(B("channel")):
                    if c.get("content") == "bioink" and not (c.get("bioinkid") or ""):
                        err("H5", f"coaxial channel {c.get('role')!r} carries bioink but names "
                                  f"no bioinkid", g)
            # drive and geometry sanity
            if drive == "thermoplastic-filament" and geom in ("coaxial", "microfluidic"):
                warn("H6", f"printhead {h.get('name')!r}: drive {drive!r} with a {geom!r} "
                           f"nozzle is unusual; confirm", g)
        dupes = {t for t in tools if tools.count(t) > 1}
        if dupes:
            err("H1", f"duplicate tool identifier(s) {sorted(dupes)} in printhead group "
                      f"{g.get('id')}", g)

    # object -> head, and head/ink consistency
    for obj in model.iter(C("object")):
        hid = obj.get(B("printheadid")) or ""
        if not hid:
            continue
        g = groups.get(hid)
        if g is None:
            err("H3", f"object printheadid={hid} does not resolve to a <b:printheads> "
                      f"resource", obj)
            continue
        heads = g.findall(B("printhead"))
        hidx = obj.get(B("printheadindex"))
        if hidx is None or int(hidx) >= len(heads):
            err("H3", f"object printheadindex={hidx!r} is missing or out of range "
                      f"({len(heads)} heads)", obj)
            continue
        head = heads[int(hidx)]
        hb, hbi = head.get("bioinkid") or "", head.get("bioinkindex") or ""
        ob, obi = obj.get("pid") or "", obj.get("pindex") or ""
        if hb and ob and ob in inkgroups and (hb, hbi) != (ob, obi):
            err("H3", f"object selects bioink {ob}/{obi} but is printed by head "
                      f"{head.get('name')!r}, which is loaded with {hb}/{hbi}", obj)

    for pr in model.iter(B("process")):
        pid = pr.get("printheadsid") or ""
        if pid and pid not in groups:
            err("H3", f"process printheadsid={pid} does not resolve", pr)
        if not pid and pr.get("modality", "").startswith("extrusion-"):
            warn("H7", f"extrusion process {pr.get('id')} declares no printhead group; the "
                       f"nozzle and drive are then only implicit in parameters", pr)


def check_processes(model):
    for pr in model.iter(B("process")):
        mod = pr.get("modality", "")
        pel = pr.find(B("parameters"))
        params = {p.get("name"): p for p in pel.findall(B("param"))} if pel is not None else {}
        for need in COMMON + REQUIRED.get(mod, []):
            if need not in params:
                err("P0", f"modality {mod!r} requires parameter {need!r}", pr)
        if mod == "melt-electrowriting":
            cts = params.get("critical_translation_speed")
            if cts is not None and cts.get("provenance") != "measured":
                err("P1", "critical_translation_speed must be measured, not cited: CTS drifts "
                          "with ambient conditions and is session-specific", pr)
        if mod in EHD:
            env = pr.find(B("environment"))
            enames = {p.get("name") for p in env.findall(B("param"))} if env is not None else set()
            for need in ("chamber_temp", "chamber_RH"):
                if need not in enames:
                    err("P2", f"electrohydrodynamic modality requires {need!r}", pr)
        for dname in DERIVED_ONLY:
            p = params.get(dname)
            if p is not None and p.get("provenance") != "derived":
                err("P3", f"{dname!r} is a derived quantity and must not be presented as "
                          f"provenance={p.get('provenance')!r}", pr)
        if mod.startswith("x-"):
            warn("P4", f"modality {mod!r} is vendor-specific and not interoperable", pr)
        tp = pr.find(B("toolpath"))
        if tp is not None:
            if not tp.get("checksum"):
                err("T1", "toolpath without checksum: dossier claims are unbound to the "
                          "executed file", pr)
            if tp.find(B("commandmap")) is None:
                warn("T2", "toolpath without a commandmap; bio-relevant codes are unmapped", pr)
            layer_names = {p.get("name") for le in tp.findall(B("layerevent"))
                           for p in le.findall(B("param"))}
            clash = sorted(layer_names & set(params))
            if clash:
                warn("T3", f"parameters {clash} appear in both <parameters> and a "
                           f"<layerevent>; the layer event wins, but verify this is intended", pr)


def check_geometry(model, ids):
    inkgroups = {k for k, v in ids.items() if v.tag == B("bioinkgroup")}
    processes = {k for k, v in ids.items() if v.tag == B("process")}
    seen_ink = False
    for obj in model.iter(C("object")):
        pid = obj.get("pid")
        if pid in inkgroups:
            seen_ink = True
            grp = ids[pid]
            n = len(grp.findall(B("bioink")))
            pindex = obj.get("pindex")
            if pindex is None or int(pindex) >= n:
                err("G1", f"object pid={pid} selects a bioink group but pindex={pindex!r} "
                          f"is missing or out of range ({n} bioinks)", obj)
        procid = obj.get(B("processid"))
        if procid is not None and procid not in processes:
            err("G2", f"object processid={procid} does not resolve to a <process> resource", obj)
        elif procid is None and pid in inkgroups:
            warn("G3", "object is assigned a bioink but no process; the build modality is "
                       "undetermined", obj)
        role = obj.get(B("regionrole"))
        if role is None and pid in inkgroups:
            warn("G4", "bio object without regionrole; role is not recoverable from geometry",
                 obj)
    for item in model.iter(C("item")):
        procid = item.get(B("processid"))
        if procid is not None and procid not in processes:
            err("G2", f"build item processid={procid} does not resolve to a <process>", item)
    if not seen_ink and model.find(f".//{B('bioinkgroup')}") is not None:
        warn("G5", "a bioinkgroup is defined but no object references it via pid/pindex")


def check_results(model, ids):
    endpoints = set()
    for grp in model.iter(B("results")):
        for r in grp.findall(B("result")):
            endpoints.add(r.get("endpoint"))
            if not r.get("acceptance"):
                warn("R1", f"result {r.get('endpoint')!r} has no acceptance criterion", r)
            tid = r.get("targetid")
            if tid and tid not in ids:
                err("R3", f"result targetid={tid} does not resolve to any resource", r)
    has_cells = model.find(f".//{B('cellload')}") is not None
    if has_cells:
        proc_names = {p.get("name") for pr in model.iter(B("process"))
                      for pel in pr.findall(B("parameters"))
                      for p in pel.findall(B("param"))}
        if "cell_viability_post_print" not in endpoints | proc_names:
            warn("R2", "package contains cell-laden material but records no post-print viability")


def check_parts(root_dir, model):
    """Every ST_UriReference MUST exist and MUST be a relationship target from the model part."""
    rels_path = os.path.join(root_dir, "3D", "_rels", "3dmodel.model.rels")
    targets = set()
    if os.path.exists(rels_path):
        for rel in ET.parse(rels_path).getroot():
            targets.add(rel.get("Target"))
    else:
        warn("O1", "no /3D/_rels/3dmodel.model.rels part found")

    referenced = set()
    for attr in ("path", "coa", "report"):
        for el in model.iter():
            v = el.get(attr)
            if v:
                referenced.add(v)
    for uri in sorted(referenced):
        fs = os.path.join(root_dir, uri.lstrip("/"))
        if not os.path.exists(fs):
            err("O2", f"referenced part {uri} is not present in the package")
        if uri not in targets:
            err("O3", f"referenced part {uri} is not the target of a relationship from the "
                      f"3D Model part")

    ct = os.path.join(root_dir, "[Content_Types].xml")
    if not os.path.exists(ct):
        err("O4", "package has no [Content_Types].xml")
    else:
        exts = {d.get("Extension") for d in ET.parse(ct).getroot()}
        for uri in referenced:
            e = uri.rsplit(".", 1)[-1].lower()
            if e not in exts:
                warn("O5", f"no content type declared for extension .{e} (part {uri})")


def check_bibliography_part(root_dir, model):
    for ev in model.iter(B("evidence")):
        path = ev.get("path")
        if not path:
            warn("E3", f"evidence resource {ev.get('id')} has no CSL-JSON path", ev)
            continue
        fs = os.path.join(root_dir, path.lstrip("/"))
        if not os.path.exists(fs):
            continue  # O2 already reported it
        try:
            csl = json.load(open(fs))
        except Exception as e:
            err("E4", f"bibliography {path} is not valid JSON: {e}", ev)
            continue
        csl_ids = {entry.get("id") for entry in csl}
        for r in ev.findall(B("reference")):
            if r.get("key") not in csl_ids:
                err("E5", f"reference key {r.get('key')!r} has no matching entry in {path}", ev)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags = {a for a in sys.argv[1:] if a.startswith("--")}
    if not args:
        print(__doc__)
        return 1

    target = args[0]
    tmp = None
    if zipfile.is_zipfile(target):
        tmp = tempfile.mkdtemp()
        with zipfile.ZipFile(target) as z:
            z.extractall(tmp)
        root_dir = tmp
    else:
        root_dir = target

    model_path = os.path.join(root_dir, "3D", "3dmodel.model")
    if not os.path.exists(model_path):
        print(f"ERROR   no /3D/3dmodel.model in {root_dir}")
        return 1
    model = ET.parse(model_path).getroot()

    check_version(model)
    check_declaration(model)
    ids = collect_resource_ids(model)
    ev_index = build_evidence_index(model)
    check_params(model, ev_index)
    check_substances(model, ev_index)
    check_cells(model)
    check_inks(model, ids)
    check_plausibility(model)
    check_dates(model)
    check_authentication_results(model)
    check_checksums(model, root_dir)
    check_fields(model, ids)
    check_maturation(model, ids)
    check_characterization(model, ids)
    check_printheads(model, ids)
    check_shear_derivation(model, ids)
    check_calibration(model, ids)
    check_regulatory(model, ids)
    check_openitems(model, ids)
    check_iso52900(model)
    check_processes(model)
    check_online(model, "--online" in flags)
    check_geometry(model, ids)
    check_results(model, ids)
    check_parts(root_dir, model)
    check_bibliography_part(root_dir, model)

    if "--release" in flags:
        for p in model.iter(B("param")):
            if p.get("provenance") == "estimated":
                err("REL", f"param {p.get('name')!r} is provenance='estimated' in a "
                           f"manufacturing release", p)

    for e in errors:
        print("ERROR  ", e)
    for w in warnings:
        print("WARN   ", w)
    print(f"\n{len(errors)} error(s), {len(warnings)} warning(s)")

    if errors:
        return 1
    if warnings and "--strict" in flags:
        return 1
    return 2 if warnings else 0


if __name__ == "__main__":
    sys.exit(main())
