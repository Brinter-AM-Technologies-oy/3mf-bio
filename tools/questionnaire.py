#!/usr/bin/env python3
"""
Generate the integrator questionnaire FROM the rules, not alongside them.

Design decision worth stating: the question set is derived from the same Python tables the
validator enforces -- REQUIRED, CALIBRATION_EXPECTED, STIMULATION_REQUIRED, PARAM_DIMENSION,
BOUNDS. It is not a hand-written form.

A hand-written form drifts. Someone adds a required parameter to the validator, forgets the
form, and the tool starts producing packages that fail their own validation. Deriving the
form means that cannot happen: add a rule, and the question appears.

The second design decision: **the questionnaire never blocks.** Every question may be
answered with "unknown", and every unknown becomes a <b:openitem> with the action that would
close it. A tool that demands forty fields before it emits anything does not get used, and
the format's whole position is that a recorded gap beats a fabricated value.

Usage:
    python3 tools/questionnaire.py --modality extrusion-pneumatic
    python3 tools/questionnaire.py --profile brinter --head pneuma-pro
    python3 tools/questionnaire.py --modality vat-dlp --format json > answers.json
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "spec"))

from validate_bio import (REQUIRED, COMMON, CALIBRATION_EXPECTED, STIMULATION_REQUIRED,
                          PARAM_DIMENSION, DIMENSION, BOUNDS, DERIVED_ONLY, ISO52900)

PREFERRED_UNIT = {
    "length": "um", "temperature": "Cel", "pressure": "kPa", "time": "s", "percent": "%",
    "irradiance": "mW/cm2", "dose": "mJ/cm2", "energy": "uJ", "power": "mW", "voltage": "kV",
    "frequency": "Hz", "velocity": "mm/s", "volume": "pL", "wavelength": "nm", "count": "1",
    "density": "/mL", "volume_rate": "uL/min",
}
FALLBACK_UNIT = {
    "nozzle_geometry": "1", "sterility_method": "1", "bath_composition": "1",
    "absorbing_layer_material": "1", "photoabsorber_identity": "1",
    "volumetric_flow_rate": "uL/min", "screw_speed": "1/min", "infill_pattern": "1",
    "NA": "1", "core_shell_ratio": "1", "raster_angle": "1", "perimeter_count": "1",
}

# Why each question is asked. Absent entries fall back to the rule that requires them.
WHY = {
    "nozzle_length": "The wall shear relation is tau_w = dP*R/(2L). Without a length no shear "
                     "stress can be derived, and shear is what the cell-damage literature "
                     "turns on.",
    "nozzle_geometry": "Peak shear is lowest in a cylindrical nozzle but persists over a "
                       "longer stretch at lower flow, which has been associated with worse "
                       "viability than conical. Bore alone does not determine the answer.",
    "strand_spacing": "Set it visually until strands just overlap, then hold that overlap "
                      "percentage. This is what makes mechanical results reproducible.",
    "cartridge_temp": "Nozzle and chamber temperature control has been reported to move "
                      "viability from around 56% to around 90%.",
    "passage_at_print": "Passage number is a process parameter, not cell metadata.",
    "atmosphere_O2": "Normoxia is a choice, not a default. Record it either way.",
    "total_light_dose": "Derived: power x time / area. It must carry provenance='derived' and "
                        "name the model; it is not a measurement.",
    "resin_refractive_index": "Scattering raises dose next to the target volume and its mean "
                              "free path depends on cell density, so this is cell-density "
                              "dependent.",
    "critical_translation_speed": "Must be measured this session, never cited. CTS drifts "
                                  "daily with polymer and environment.",
    "core_shell_ratio": "Printability of a multimaterial filament depends on the core-to-shell "
                        "ratio, not only the target outer diameter.",
    "bath_particle_diameter": "Bath particle size, not the nozzle, sets your resolution floor.",
    "flow_rate": "Flow rate sets wall shear stress at the construct, and shear is a "
                 "differentiation cue rather than a plumbing detail.",
    "temp_of_measurement": "A viscosity without a temperature is not a measurement.",
    "antibiotics": "State it explicitly, including the value 'none'.",
}


def unit_for(name):
    d = PARAM_DIMENSION.get(name)
    return PREFERRED_UNIT[d] if d else FALLBACK_UNIT.get(name, "1")


def q(key, prompt, kind="text", unit=None, why=None, rule=None, options=None,
      allow_unknown=True, group="process"):
    item = {"key": key, "prompt": prompt, "kind": kind, "group": group,
            "allow_unknown": allow_unknown}
    if unit:
        item["unit"] = unit
    if why:
        item["why"] = why
    if rule:
        item["rule"] = rule
    if options:
        item["options"] = options
    if key in BOUNDS:
        lo, hi, u = BOUNDS[key]
        item["bounds"] = {"min": lo, "max": hi, "unit": u}
    return item


def build(modality, profile=None, head=None, with_maturation=True):
    qs = []

    # --- identity -----------------------------------------------------------------
    qs += [
        q("title", "What is this build called?", group="identity", allow_unknown=False),
        q("intendeduse", "What is this for?", kind="choice", group="identity",
          allow_unknown=False,
          options=["research-only", "in-vitro-model", "drug-screening", "preclinical",
                   "clinical-investigation", "implantable", "veterinary", "education"],
          why="Drives which regulatory questions are asked. It does not determine compliance; "
              "it decides which fields your own audit will want filled."),
        q("machine_vendor", "Printer vendor", group="identity"),
        q("machine_model", "Printer model", group="identity"),
        q("machine_serial", "Serial number", group="identity",
          why="Without it the process cannot be attributed to a specific instrument."),
        q("machine_calibrationdate", "Date the machine was last calibrated", kind="date",
          group="identity"),
    ]

    # --- geometry -----------------------------------------------------------------
    qs += [
        q("mesh_files", "Which STL or OBJ files make up this build?", kind="files",
          group="geometry", allow_unknown=False),
        q("regionrole", "For each mesh: what is it?", kind="choice-per-mesh", group="geometry",
          options=["parenchyma", "vasculature", "interface", "sacrificial", "support",
                   "fiducial", "test-coupon"],
          why="Two meshes of identical shape may be parenchyma and sacrificial template. The "
              "role is not recoverable from geometry."),
        q("mesh_units", "What units is the mesh in?", kind="choice", group="geometry",
          options=["millimeter", "micron", "centimeter", "inch"], allow_unknown=False),
    ]

    # --- materials and cells ------------------------------------------------------
    qs += [
        q("substances", "List each substance: name, role, and CAS number if it has one",
          kind="table", group="material", allow_unknown=False,
          why="A substance with no CAS and no synthesis record is unidentifiable. Mixtures "
              "without a CAS need supplier and lot instead.",
          rule="S1/S1a/S2"),
        q("synthesised_in_house", "Did you make or modify any of these yourself?",
          kind="bool", group="material",
          why="If so, the format needs the route, the conditions, the yield, and the assay "
              "that verified it. An unmeasured yield is recorded as unmeasured, not omitted.",
          rule="S2/S3/S4"),
        q("bioink_name", "What is the formulation called?", group="material"),
        q("bioink_class", "Does it contain cells at the point of printing?", kind="choice",
          group="material", allow_unknown=False,
          options=["bioink", "biomaterial-ink", "bioresin", "support-bath", "fugitive",
                   "sacrificial"],
          why="A formulation containing cells and one that does not are different objects "
              "both in process terms and regulatorily.",
          rule="I1"),
        q("rheology_model", "Which rheological model was fitted?", kind="choice",
          group="material",
          options=["Herschel-Bulkley", "power-law", "Carreau-Yasuda", "Cross", "Bingham",
                   "newtonian", "not measured"],
          why="Power-law cannot represent a yield stress. Herschel-Bulkley is generally better "
              "for shape-fidelity work. Neither captures thixotropy."),
        q("temp_of_measurement", "At what temperature was the rheology measured?",
          unit="Cel", group="material", why=WHY["temp_of_measurement"], rule="I2"),
        q("cell_name", "Which cells?", group="cells"),
        q("cell_kind", "What kind of population?", kind="choice", group="cells",
          options=["primary", "line", "iPSC-derived", "ESC-derived", "organoid", "spheroid",
                   "co-culture"]),
        q("rrid", "Cellosaurus RRID (required for a cell line)", group="cells", rule="C1",
          why="A name is not an identifier. Cell-line misidentification is one of the two "
              "best-documented reproducibility failures in cell work."),
        q("mycoplasma_result", "Mycoplasma test result and date", group="cells",
          allow_unknown=False, rule="C2",
          why="Required for every population. A positive result is recorded as positive and "
              "the validator will reject the package -- that is the point."),
        q("passage_at_print", "Passage number at the time of printing", unit="1",
          group="cells", why=WHY["passage_at_print"], rule="C3"),
        q("antibiotics", "Antibiotics in the culture medium", group="cells",
          allow_unknown=False, why=WHY["antibiotics"], rule="C4"),
        q("serum", "Serum percentage and lot", group="cells"),
        q("cell_density", "Cell density in the formulation", unit="/mL", group="cells"),
        q("ethicsref", "Ethics or IRB approval reference", group="cells"),
    ]

    # --- process, derived from REQUIRED -------------------------------------------
    names = list(dict.fromkeys(COMMON + REQUIRED.get(modality, [])))
    for n in names:
        if n in DERIVED_ONLY:
            qs.append(q(n, f"{n.replace('_', ' ')} -- how was it derived?",
                        unit=unit_for(n), group="process", rule="P3",
                        why=WHY.get(n, "A derived quantity. Name the model or equation; do not "
                                       "present it as a measurement.")))
        else:
            qs.append(q(n, n.replace("_", " "), unit=unit_for(n), group="process", rule="P0",
                        why=WHY.get(n)))

    if modality.startswith("extrusion-"):
        for n in ("infill_pattern", "raster_angle", "perimeter_count", "standoff_height"):
            qs.append(q(n, n.replace("_", " "), unit=unit_for(n), group="process",
                        why=WHY.get(n)))
        qs.append(q("wall_shear_stress_max",
                    "Wall shear stress -- derived, or leave unknown", unit="kPa",
                    group="process", rule="X1",
                    why="Requires nozzle bore, nozzle length, a driving term and a fitted "
                        "rheology. If any is missing the value is a guess, and the validator "
                        "will say so."))

    if modality in ("melt-electrowriting", "electrospinning"):
        qs += [q("chamber_temp", "Chamber temperature", unit="Cel", group="process", rule="P2"),
               q("chamber_RH", "Chamber relative humidity", unit="%", group="process",
                 rule="P2")]

    # --- calibration, derived from CALIBRATION_EXPECTED ---------------------------
    for t in CALIBRATION_EXPECTED.get(modality, []):
        qs.append(q(f"cal_{t}", f"Calibration: {t.replace('_', ' ')} -- result and date",
                    group="calibration", rule="K2/K3",
                    why="Every calibration test needs an acceptance criterion that YOU set. "
                        "This project asserts no thresholds. A test marked pass must carry a "
                        "measured value."))
    qs.append(q("calibration_performed", "Date this calibration set was performed", kind="date",
                group="calibration", rule="K1",
                why="Calibration is a dated event with an operator, not a machine attribute."))

    # --- maturation ---------------------------------------------------------------
    if with_maturation:
        qs += [
            q("maturation_stages",
              "After printing, list the culture stages: name, format, from, to",
              kind="table", group="maturation",
              why="A printed construct is not the product. Everything before this describes "
                  "about a day of work."),
            q("bioreactor_kind", "Bioreactor, if any", kind="choice", group="maturation",
              options=["none", "perfusion", "spinner-flask", "rotating-wall",
                       "hydrostatic-pressure", "uniaxial-tension", "compression",
                       "multi-modal", "organ-on-chip"]),
            q("stimulation_mode", "Stimulation applied, if any", kind="choice",
              group="maturation",
              options=["none"] + sorted(STIMULATION_REQUIRED),
              why="Whichever mode you pick, the format asks for magnitude, rate AND duration. "
                  "The perfusion literature notes these are 'as a group often overlooked', "
                  "which is why all three are required together.",
              rule="Q5"),
        ]
        for mode, needs in STIMULATION_REQUIRED.items():
            for n in needs:
                qs.append(q(f"stim_{mode}_{n}", f"[{mode}] {n.replace('_', ' ')}",
                            unit=unit_for(n), group="maturation", rule="Q5",
                            why=WHY.get(n), allow_unknown=True))
        qs.append(q("medium_exchange", "Medium exchange interval and volume",
                    group="maturation", rule="Q6"))

    # --- characterization ---------------------------------------------------------
    qs += [
        q("assays", "Which assays, at which timepoints?", kind="table",
          group="characterization",
          why="Readings form a timecourse. 92% viability at day 1 and 74% at day 21 is a "
              "different construct from one holding 90% throughout, and a single value "
              "cannot say so."),
        q("assay_methods", "For each assay: the method",
          group="characterization", rule="Q8", allow_unknown=False,
          why="An endpoint without a method is not a measurement. Unconfined compression and "
              "nanoindentation both report 'compressive modulus' and are not comparable."),
        q("acceptance", "For each assay: your acceptance criterion",
          group="characterization",
          why="This project asserts no thresholds anywhere. State your own and be held to it."),
    ]

    # --- evidence and regulatory --------------------------------------------------
    qs += [
        q("references", "DOIs or standard numbers for anything you are citing",
          kind="table", group="evidence", rule="V1",
          why="Any parameter you mark 'cited' must resolve to one of these."),
        q("regulatory_regions", "Which jurisdictions do you need to consider?",
          kind="multi", group="regulatory",
          options=["US", "EU", "UK", "AU", "CA", "JP", "CN", "none"],
          why="The format records that you considered them and how you reached a view. It "
              "does not determine anything, and filling these fields is not compliance."),
        q("determination", "How was that view reached?", kind="choice", group="regulatory",
          options=["confirmed-by-authority", "advice-sought", "self-assessed", "undetermined",
                   "not-applicable"],
          why="The contested part of a regulatory record is rarely the classification. It is "
              "how the classification was reached and whether anyone with authority agreed.",
          rule="R5/R6"),
    ]

    meta = {
        "modality": modality,
        "iso52900": ISO52900.get(modality),
        "generated_from": "spec/validate_bio.py rule tables",
        "question_count": len(qs),
        "note": "Every question may be answered 'unknown'. Each unknown becomes a "
                "<b:openitem> with the action that would close it. Nothing here blocks.",
    }
    if profile:
        meta["profile"] = profile.get("vendor")
        meta["platform"] = profile.get("platform")
        if head:
            meta["head"] = head
    return {"meta": meta, "questions": qs}


def load_profile(name):
    p = os.path.join(HERE, "machine_profiles", f"{name}.json")
    if not os.path.exists(p):
        sys.exit(f"no machine profile '{name}' in tools/machine_profiles/")
    return json.load(open(p))


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--modality")
    ap.add_argument("--profile", help="machine profile name, e.g. brinter")
    ap.add_argument("--head", help="printhead key within the profile")
    ap.add_argument("--format", choices=["text", "json", "template"], default="text")
    ap.add_argument("--no-maturation", action="store_true")
    a = ap.parse_args()

    profile = load_profile(a.profile) if a.profile else None
    modality, headinfo = a.modality, None

    if profile and a.head:
        heads = {h["key"]: h for h in profile["printheads"]}
        if a.head not in heads:
            sys.exit(f"profile '{a.profile}' has no head '{a.head}'. "
                     f"Available: {', '.join(heads)}")
        headinfo = heads[a.head]
        modality = modality or headinfo["modality"]
    if not modality:
        if profile:
            print(f"{profile['vendor']} {profile['platform']} printheads:\n")
            for h in profile["printheads"]:
                print(f"  {h['key']:<14} {h['name']:<32} {h['modality']}")
                print(f"  {'':<14} {h['principle']}")
                if h.get("suits"):
                    print(f"  {'':<14} suits: {h['suits']}")
                print()
            print("Pick one with --head, or give --modality directly.")
            return 0
        sys.exit("give --modality, or --profile with --head")

    if modality not in REQUIRED and not modality.startswith("x-"):
        print(f"note: modality '{modality}' has no required-parameter set defined; "
              f"only the common questions will be generated.\n", file=sys.stderr)

    out = build(modality, profile, headinfo, with_maturation=not a.no_maturation)

    if a.format == "json":
        print(json.dumps(out, indent=2))
        return 0
    if a.format == "template":
        ans = {"_modality": modality, "_note": "Replace null with a value, or leave null and "
                                               "it becomes a tracked open item."}
        if headinfo:
            ans["_head"] = headinfo["key"]
        for q_ in out["questions"]:
            ans[q_["key"]] = None
        print(json.dumps(ans, indent=2))
        return 0

    m = out["meta"]
    print(f"Questionnaire for modality: {m['modality']}")
    if m.get("profile"):
        print(f"Machine: {m['profile']} {m.get('platform', '')}")
    if headinfo:
        print(f"Head:    {headinfo['name']} -- {headinfo['principle']}")
        print(f"         controlled variable: {headinfo['controlled_variable']}")
        for p in headinfo.get("prompts", []):
            print(f"         ! {p}")
    print(f"{m['question_count']} questions, generated from {m['generated_from']}")
    print(f"\n{m['note']}\n")

    last = None
    for q_ in out["questions"]:
        if q_["group"] != last:
            last = q_["group"]
            print(f"\n--- {last.upper()} " + "-" * (60 - len(last)))
        req = "" if q_["allow_unknown"] else "  [required]"
        unit = f"  ({q_['unit']})" if q_.get("unit") else ""
        rule = f"  [{q_['rule']}]" if q_.get("rule") else ""
        print(f"\n  {q_['prompt']}{unit}{req}{rule}")
        if q_.get("options"):
            print(f"      one of: {', '.join(q_['options'])}")
        if q_.get("bounds"):
            b = q_["bounds"]
            print(f"      must lie in [{b['min']}, {b['max']}] {b['unit']}")
        if q_.get("why"):
            for line in _wrap(q_["why"], 72):
                print(f"      {line}")
    return 0


def _wrap(text, width):
    words, line, out = text.split(), "", []
    for w in words:
        if len(line) + len(w) + 1 > width:
            out.append(line)
            line = w
        else:
            line = f"{line} {w}".strip()
    if line:
        out.append(line)
    return out


if __name__ == "__main__":
    sys.exit(main())
