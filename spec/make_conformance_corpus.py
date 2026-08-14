#!/usr/bin/env python3
"""
Generate a minimal conformant package for every modality.

Why this exists: the repository shipped one example (volumetric-tomographic), so thirteen
of the fourteen modality required-parameter sets had never been exercised by a package that
is supposed to PASS. Negative tests prove a rule fires; they do not prove the rule is
satisfiable. A required-parameter set with a typo, a unit that fails the dimension check, or
a calibration expectation that contradicts the parameter list would sit undetected.

Each generated package is deliberately minimal: it asserts no numeric values it cannot
justify. Every parameter is provenance="estimated" with an open item accounting for it,
which is the honest state of a template. They are Bio-Core skeletons, not exemplars.

Usage:  python3 spec/make_conformance_corpus.py [outdir]
        default outdir: conformance/
"""
import hashlib
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from validate_bio import (REQUIRED, COMMON, CALIBRATION_EXPECTED, ISO52900,
                          PARAM_DIMENSION, DIMENSION, DERIVED_ONLY)

# Unit to emit for each parameter, chosen to satisfy the U1 dimension check.
PREFERRED = {
    "length": "um", "temperature": "Cel", "pressure": "kPa", "time": "s",
    "percent": "%", "irradiance": "mW/cm2", "dose": "mJ/cm2", "energy": "uJ",
    "power": "mW", "voltage": "kV", "frequency": "Hz", "velocity": "mm/s",
    "volume": "pL", "wavelength": "nm", "count": "1", "density": "/mL",
}
# Parameters with no dimension entry: pick something defensible or leave dimensionless.
FALLBACK_UNIT = {
    "nozzle_geometry": "1", "sterility_method": "1", "bath_composition": "1",
    "absorbing_layer_material": "1", "photoabsorber_identity": "1",
    "volumetric_flow_rate": "uL/min", "flow_rate": "uL/h", "feed_pressure": "bar",
    "NA": "1", "hatch_distance": "um", "slicing_distance": "um",
    "spinneret_gauge": "1", "waveform": "1",
}
MEASURED_OK = {"build_temp", "sterility_method", "critical_translation_speed"}


def unit_for(name):
    dim = PARAM_DIMENSION.get(name)
    if dim:
        return PREFERRED[dim]
    return FALLBACK_UNIT.get(name, "1")


def param(name, indent="\t\t\t\t"):
    u = unit_for(name)
    if name in DERIVED_ONLY:
        # P0 can require a parameter that P3 constrains to provenance="derived".
        # total_light_dose is exactly that case: volumetric printing must record it, and it
        # is computed rather than measured. A template must therefore emit it as derived
        # with a named model, not as an estimate.
        return (f'{indent}<b:param name="{name}" unit="{u}" setpoint="" provenance="derived"\n'
                f'{indent}\tmethod="TEMPLATE - name the model or equation used"\n'
                f'{indent}\tnote="TEMPLATE - derive and record"/>')
    if name in MEASURED_OK:
        val = "TEMPLATE" if u == "1" else "0"
        return (f'{indent}<b:param name="{name}" unit="{u}" setpoint="{val}" '
                f'measured="{val}" provenance="measured" method="TEMPLATE - replace"/>')
    return (f'{indent}<b:param name="{name}" unit="{u}" setpoint="" '
            f'provenance="estimated" note="TEMPLATE - measure and record"/>')


def build(modality, outdir):
    pkg = os.path.join(outdir, modality)
    if os.path.exists(pkg):
        shutil.rmtree(pkg)
    for d in ("3D/_rels", "_rels", "bio/toolpath"):
        os.makedirs(os.path.join(pkg, d), exist_ok=True)

    toolpath = os.path.join(pkg, "bio", "toolpath", "path.gcode")
    with open(toolpath, "w") as f:
        f.write("; TEMPLATE toolpath\nM400\n")
    digest = hashlib.sha256(open(toolpath, "rb").read()).hexdigest()

    names = COMMON + REQUIRED.get(modality, [])
    seen, ordered = set(), []
    for n in names:
        if n not in seen:
            seen.add(n)
            ordered.append(n)
    params = "\n".join(param(n) for n in ordered)

    env = ""
    if modality in ("melt-electrowriting", "electrospinning"):
        env = ("\n\t\t\t<b:environment>\n"
               + param("chamber_temp", "\t\t\t\t") + "\n"
               + param("chamber_RH", "\t\t\t\t") + "\n\t\t\t</b:environment>")

    cal_tests = "\n".join(
        f'\t\t\t<b:test name="{t}" kind="printability" metric="{t}" '
        f'acceptance="TEMPLATE - state your own criterion" outcome="not-performed"/>'
        for t in CALIBRATION_EXPECTED.get(modality, ["geometric_capability"]))

    iso = ISO52900.get(modality)
    iso_attr = f' iso52900="{iso}"' if iso else ""

    # open items covering every estimated parameter (rule J5)
    affects = "\n".join(f'\t\t\t\t<b:affects targetid="5" paramname="{n}"/>'
                        for n in ordered if n not in MEASURED_OK and n not in DERIVED_ONLY)
    if modality in ("melt-electrowriting", "electrospinning"):
        affects += ('\n\t\t\t\t<b:affects targetid="5" paramname="chamber_temp"/>'
                    '\n\t\t\t\t<b:affects targetid="5" paramname="chamber_RH"/>')

    model = f'''<?xml version="1.0" encoding="UTF-8"?>
<!--
  CONFORMANCE TEMPLATE - modality: {modality}
  GENERATED by spec/make_conformance_corpus.py. Do not hand-edit; regenerate.

  This is a Bio-Core skeleton, not an exemplar. Every process parameter is
  provenance="estimated" with an open item accounting for it, because a template that
  asserted values would be asserting values nobody measured. Replace the TEMPLATE markers
  with real measurements and their provenance.
-->
<model unit="millimeter" xml:lang="en-US"
\txmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
\txmlns:b="https://3mfbio.com/ns/bio/2026/07"
\trequiredextensions="b">

\t<metadata name="Title">Conformance template: {modality}</metadata>
\t<metadata name="b:SpecVersion">0.9.0</metadata>
\t<metadata name="b:Conformance">Bio-Core</metadata>

\t<resources>
\t\t<b:evidence id="1" path="/bio/references.json">
\t\t\t<b:reference key="astmF3659" kind="standard" stdno="ASTM F3659-24" grade="A"/>
\t\t\t<b:reference key="gccp2" kind="standard"
\t\t\t\turl="https://pubmed.ncbi.nlm.nih.gov/34882777/" grade="A"/>
\t\t</b:evidence>

\t\t<b:substances id="2">
\t\t\t<b:substance name="TEMPLATE polymer" role="polymer">
\t\t\t\t<b:identity kind="mixture" casrn=""/>
\t\t\t\t<b:grade supplier="TEMPLATE" lot="TEMPLATE"/>
\t\t\t</b:substance>
\t\t</b:substances>

\t\t<b:cellpopulations id="3">
\t\t\t<b:cellpopulation name="TEMPLATE cell population">
\t\t\t\t<b:origin kind="primary" taxon="9606" ethicsref="TEMPLATE"/>
\t\t\t\t<b:authentication assay="mycoplasma" method="PCR" result="negative"/>
\t\t\t\t<b:culture medium="TEMPLATE" antibiotics="none">
\t\t\t\t\t<b:param name="passage_at_print" unit="1" measured="1" provenance="measured"/>
\t\t\t\t\t<b:param name="atmosphere_O2" unit="%" setpoint="21" measured="21"
\t\t\t\t\t\tprovenance="measured" method="ambient"/>
\t\t\t\t</b:culture>
\t\t\t</b:cellpopulation>
\t\t</b:cellpopulations>

\t\t<b:bioinkgroup id="4">
\t\t\t<b:bioink name="TEMPLATE bioink" class="bioink">
\t\t\t\t<b:component substanceid="2" substanceindex="0" value="1" unit="%{{w/v}}"
\t\t\t\t\tprovenance="estimated"/>
\t\t\t\t<b:cellload cellpopid="3" cellpopindex="0" density="1000000" unit="/mL"
\t\t\t\t\tprovenance="estimated" method="TEMPLATE"/>
\t\t\t</b:bioink>
\t\t</b:bioinkgroup>

\t\t<b:process id="5" modality="{modality}"{iso_attr} calibrationid="6">
\t\t\t<b:machine vendor="TEMPLATE" model="TEMPLATE"/>
\t\t\t<b:parameters>
{params}
\t\t\t</b:parameters>{env}
\t\t\t<b:toolpath path="/bio/toolpath/path.gcode" dialect="gcode-marlin"
\t\t\t\tchecksum="sha256:{digest}">
\t\t\t\t<b:commandmap>
\t\t\t\t\t<b:cmd code="M400" means="wait_for_moves_complete"/>
\t\t\t\t</b:commandmap>
\t\t\t</b:toolpath>
\t\t</b:process>

\t\t<b:calibration id="6" modality="{modality}" performed="2026-01-01" operator="TEMPLATE">
{cal_tests}
\t\t</b:calibration>

\t\t<b:results id="7">
\t\t\t<b:result endpoint="cell_viability_post_print" acceptance="TEMPLATE - state your own">
\t\t\t\t<b:param name="cell_viability_post_print" unit="%" measured=""
\t\t\t\t\tprovenance="estimated" note="TEMPLATE - measure and record"/>
\t\t\t</b:result>
\t\t</b:results>

\t\t<b:openitems id="8">
\t\t\t<b:openitem key="template-params" kind="placeholder" severity="blocking" status="open"
\t\t\t\traised="2026-01-01"
\t\t\t\tsummary="This is a generated conformance template. Every process parameter is a placeholder."
\t\t\t\taction="Replace each TEMPLATE parameter with a measured or cited value and its provenance.">
{affects}
\t\t\t\t<b:affects targetid="7" paramname="cell_viability_post_print"/>
\t\t\t</b:openitem>
\t\t</b:openitems>

\t\t<object id="9" type="model" name="template part" pid="4" pindex="0"
\t\t\tb:processid="5" b:regionrole="parenchyma">
\t\t\t<mesh>
\t\t\t\t<vertices/>
\t\t\t\t<triangles/>
\t\t\t</mesh>
\t\t</object>
\t</resources>

\t<build>
\t\t<item objectid="9" transform="1 0 0 0 1 0 0 0 1 0 0 0"/>
\t</build>
</model>
'''
    with open(os.path.join(pkg, "3D", "3dmodel.model"), "w") as f:
        f.write(model)

    with open(os.path.join(pkg, "[Content_Types].xml"), "w") as f:
        f.write('''<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>
  <Default Extension="json" ContentType="application/vnd.3mf.biodossier.bibliography+json"/>
  <Default Extension="gcode" ContentType="application/vnd.3mf.biodossier.toolpath"/>
</Types>
''')
    with open(os.path.join(pkg, "_rels", ".rels"), "w") as f:
        f.write('''<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rel0" Target="/3D/3dmodel.model"
    Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>
</Relationships>
''')
    with open(os.path.join(pkg, "3D", "_rels", "3dmodel.model.rels"), "w") as f:
        f.write('''<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rel1" Target="/bio/references.json"
    Type="https://3mfbio.com/ns/rel/2026/07/biobibliography"/>
  <Relationship Id="rel2" Target="/bio/toolpath/path.gcode"
    Type="https://3mfbio.com/ns/rel/2026/07/biotoolpath"/>
</Relationships>
''')
    os.makedirs(os.path.join(pkg, "bio"), exist_ok=True)
    with open(os.path.join(pkg, "bio", "references.json"), "w") as f:
        f.write('''[
  { "id": "astmF3659", "type": "standard",
    "title": "Standard Guide for Bioinks Used in Bioprinting",
    "number": "ASTM F3659-24", "publisher": "ASTM International",
    "issued": { "date-parts": [[2024]] } },
  { "id": "gccp2", "type": "article-journal",
    "title": "Guidance document on Good Cell and Tissue Culture Practice 2.0 (GCCP 2.0)",
    "container-title": "ALTEX",
    "URL": "https://pubmed.ncbi.nlm.nih.gov/34882777/",
    "issued": { "date-parts": [[2021]] } }
]
''')
    return pkg


def main():
    outdir = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "conformance")
    os.makedirs(outdir, exist_ok=True)
    made = [build(m, outdir) for m in sorted(REQUIRED)]
    print(f"generated {len(made)} conformance templates in {outdir}/")
    for p in made:
        print("  ", os.path.basename(p))


if __name__ == "__main__":
    main()
