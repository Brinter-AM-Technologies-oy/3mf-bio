<?xml version="1.0" encoding="UTF-8"?>
<!--
  3MF Bio Extension - ISO Schematron companion, working draft v0.3

  WHAT THIS COVERS, AND WHAT IT CANNOT

  Schematron validates one XML document. It therefore expresses every INTRA-DOCUMENT rule
  of this extension: the evidence rule, resource integrity, the chemistry and biology
  requirements, modality-dispatched parameters, and the volumetric field binding.

  It cannot express the CROSS-PART rules, because they are not about this document:
    O2/O3  referenced parts exist and are OPC relationship targets
    E5     every reference key matches an entry in the CSL-JSON bibliography
    T4     a toolpath checksum matches the bytes of the referenced part
    REL    the release gate over a whole package
  Nor D2 (a date lies in the future), because XPath 1.0 has no current-date() function.
  That arrived in XPath 2.0, and the reference runner compiles to XSLT 1.0. For the same
  reason Q2 (a maturation stage that ends before it begins) is out of scope: comparing two
  ISO 8601 durations needs xs:duration arithmetic, which is also XPath 2.0.
  These remain in spec/validate_bio.py. The split is principled, not a shortcut: an
  OPC relationship graph and a JSON payload are outside any single XML document.

  XPath 1.0 LIMITATION. The reference implementation (lxml.isoschematron) compiles to
  XSLT 1.0, so there is no tokenize() or matches(). Bounds-checking a whitespace-separated
  evindices list is therefore only performed for the single-index case; multi-index lists
  are checked for resolvability of @evid but not for per-index range. validate_bio.py
  checks every index. This is stated rather than hidden because a rule that silently
  half-fires is worse than one that declares its scope.

  PHASES
    structural  X, G, I3/I4 - resource and reference integrity
    evidence    V, E        - the provenance rule
    chemistry   S           - substances and synthesis
    biology     C, I1, I2   - cells and formulations
    process     P, T        - modality parameters and toolpaths
    fields      F           - volumetric field bindings
    all         everything
-->
<sch:schema xmlns:sch="http://purl.oclc.org/dsdl/schematron" queryBinding="xslt">

  <sch:title>3MF Bio Extension conformance rules</sch:title>

  <sch:ns prefix="core" uri="http://schemas.microsoft.com/3dmanufacturing/core/2015/02"/>
  <sch:ns prefix="b"    uri="https://3mfbio.com/ns/bio/2026/07"/>
  <sch:ns prefix="v"    uri="http://schemas.3mf.io/3dmanufacturing/volumetric/2022/01"/>

  <sch:phase id="structural">
    <sch:active pattern="resource-integrity"/>
    <sch:active pattern="geometry-binding"/>
    <sch:active pattern="geometry-process"/>
    <sch:active pattern="ink-references"/>
  </sch:phase>
  <sch:phase id="evidence">
    <sch:active pattern="provenance"/>
    <sch:active pattern="param-provenance"/>
    <sch:active pattern="evidence-resources"/>
  </sch:phase>
  <sch:phase id="chemistry">
    <sch:active pattern="substances"/>
  </sch:phase>
  <sch:phase id="biology">
    <sch:active pattern="cells"/>
    <sch:active pattern="formulations"/>
  </sch:phase>
  <sch:phase id="process">
    <sch:active pattern="process-common"/>
    <sch:active pattern="process-extrusion"/>
    <sch:active pattern="process-vat"/>
    <sch:active pattern="process-volumetric"/>
    <sch:active pattern="process-mew"/>
    <sch:active pattern="process-lift"/>
    <sch:active pattern="derived-quantities"/>
    <sch:active pattern="toolpaths"/>
  </sch:phase>
  <sch:phase id="fields">
    <sch:active pattern="field-bindings"/>
  </sch:phase>
  <sch:phase id="deposition">
    <sch:active pattern="printheads"/>
    <sch:active pattern="coaxial-channels"/>
    <sch:active pattern="shear-derivation"/>
  </sch:phase>
  <sch:phase id="maturation">
    <sch:active pattern="maturation-stages"/>
    <sch:active pattern="stimulation-regimes"/>
    <sch:active pattern="characterization-assays"/>
  </sch:phase>
  <sch:phase id="calibration">
    <sch:active pattern="calibration-records"/>
    <sch:active pattern="calibration-binding"/>
  </sch:phase>
  <sch:phase id="regulatory">
    <sch:active pattern="regulatory-context"/>
  </sch:phase>
  <sch:phase id="plausibility">
    <sch:active pattern="unit-dimensions"/>
    <sch:active pattern="physical-bounds"/>
  </sch:phase>
  <sch:phase id="openitems">
    <sch:active pattern="open-items"/>
    <sch:active pattern="open-item-coverage"/>
  </sch:phase>

  <!-- ================= X: model and resource integrity ================= -->

  <sch:pattern id="resource-integrity">
    <sch:rule context="core:model">
      <sch:assert test="core:metadata[@name = 'b:SpecVersion']"
        >[M1] Package declares no b:SpecVersion metadata. A consumer cannot tell which draft
        it is reading; this extension is pre-1.0 and changing.</sch:assert>
      <sch:assert test="not(.//b:cellload) or contains(concat(' ', normalize-space(@requiredextensions), ' '), ' b ')"
        >[X1] A package encoding cell-laden material MUST list the bio prefix in
        requiredextensions.</sch:assert>
    </sch:rule>

    <sch:rule context="core:resources/*[@id]">
      <sch:assert test="count(../*[@id = current()/@id]) = 1"
        >[X3] Resource id <sch:value-of select="@id"/> is not unique. 3MF resource ids MUST be
        unique across core and all extensions.</sch:assert>
    </sch:rule>
  </sch:pattern>

  <!-- ================= V/E: the evidence rule ================= -->

  <sch:pattern id="provenance">
    <sch:rule context="b:param | b:yield | b:verification | b:component | b:cellload | b:fieldbinding">
      <sch:assert test="not(@provenance = 'cited') or (@evid and //b:evidence[@id = current()/@evid])"
        >[V1] provenance='cited' MUST resolve to a b:evidence resource
        (<sch:name/><sch:value-of select="concat(' ', @name, @endpoint, @quantity)"/>).</sch:assert>

      <sch:assert test="not(@evid) or //b:evidence[@id = current()/@evid]"
        >[V1] evid=<sch:value-of select="@evid"/> does not resolve to a b:evidence
        resource.</sch:assert>

      <!-- single-index bounds check only; see the header note on XPath 1.0 -->
      <sch:assert test="not(@evindices) or contains(normalize-space(@evindices), ' ')
                        or not(//b:evidence[@id = current()/@evid])
                        or number(normalize-space(@evindices)) &lt; count(//b:evidence[@id = current()/@evid]/b:reference)"
        >[V1] evindices <sch:value-of select="@evindices"/> is out of range for evidence group
        <sch:value-of select="@evid"/>.</sch:assert>
    </sch:rule>

  </sch:pattern>

  <!-- Separate pattern: within a pattern only the first matching rule fires, and b:param
       already matches the shared evidence rule above. -->
  <sch:pattern id="param-provenance">
    <sch:rule context="b:param">
      <sch:assert test="not(@provenance = 'measured') or @measured"
        >[V2] param '<sch:value-of select="@name"/>' is provenance='measured' but carries no
        measured value.</sch:assert>
      <sch:assert test="not(@provenance = 'derived') or (@method and string-length(normalize-space(@method)) &gt; 0)"
        >[V3] param '<sch:value-of select="@name"/>' is provenance='derived' but names no model
        in @method.</sch:assert>
      <sch:report test="not(@setpoint) and not(@measured)" role="warning"
        >[V4] param '<sch:value-of select="@name"/>' carries neither setpoint nor
        measured.</sch:report>
    </sch:rule>
  </sch:pattern>

  <sch:pattern id="evidence-resources">
    <sch:rule context="b:reference">
      <sch:report test="not(@doi) and not(@stdno) and not(@url)" role="warning"
        >[E2] reference '<sch:value-of select="@key"/>' has no resolvable
        identifier.</sch:report>
    </sch:rule>
    <sch:rule context="b:evidence">
      <sch:report test="not(@path)" role="warning"
        >[E3] evidence resource <sch:value-of select="@id"/> declares no CSL-JSON
        path.</sch:report>
    </sch:rule>
  </sch:pattern>

  <!-- ================= S: substances ================= -->

  <sch:pattern id="substances">
    <sch:rule context="b:substance">
      <sch:assert test="b:identity/@casrn[string-length(.) &gt; 0]
                        or b:synthesis
                        or (b:identity/@kind = 'mixture'
                            and b:grade/@supplier[string-length(.) &gt; 0]
                            and b:grade/@lot[string-length(.) &gt; 0])"
        >[S1/S1a/S2] Substance '<sch:value-of select="@name"/>' has no CAS number, no synthesis
        record, and is not a mixture traced by supplier and lot: it is
        unidentifiable.</sch:assert>
    </sch:rule>

    <sch:rule context="b:synthesis">
      <sch:assert test="b:yield"
        >[S3] A synthesis record MUST contain b:yield. If the yield is unmeasured, emit it with
        provenance='estimated' and an empty value: an absent yield and an unmeasured yield are
        different claims.</sch:assert>
      <sch:assert test="b:verification"
        >[S4] A synthesis record MUST contain at least one b:verification. A synthesis with no
        verification assay is not a characterised material.</sch:assert>
    </sch:rule>

    <sch:rule context="b:verification">
      <sch:assert test="@assay and string-length(normalize-space(@assay)) &gt; 0"
        >[S4] b:verification MUST name the assay. Different assays do not return the same value
        for the same batch.</sch:assert>
    </sch:rule>
  </sch:pattern>

  <!-- ================= C: cells ================= -->

  <sch:pattern id="cells">
    <sch:rule context="b:cellpopulation">
      <sch:assert test="not(b:origin/@kind = 'line') or b:origin/@rrid[string-length(.) &gt; 0]"
        >[C1] A cell line MUST carry a Cellosaurus RRID. A name is not an
        identifier.</sch:assert>
      <sch:assert test="b:authentication[@assay = 'mycoplasma']"
        >[C2] Every cell population MUST carry a mycoplasma authentication record.</sch:assert>
      <sch:assert test="b:culture/b:param[@name = 'passage_at_print']"
        >[C3] passage_at_print MUST be present: passage number is a process
        parameter.</sch:assert>
      <sch:assert test="b:culture/@antibiotics and string-length(b:culture/@antibiotics) &gt; 0"
        >[C4] antibiotics MUST be stated explicitly, including the value 'none'.</sch:assert>
      <sch:assert test="not(b:authentication[@assay = 'mycoplasma'][
                          contains(translate(@result, 'POSITIVEFAL', 'positivefal'), 'positive')
                          or contains(translate(@result, 'FAILED', 'failed'), 'fail')
                          or contains(translate(@result, 'CONTAMIED', 'contamied'), 'contamin')])"
        >[C7] A mycoplasma authentication reports contamination. A contaminated population
        does not satisfy the requirement for a mycoplasma record; it invalidates the
        biological data.</sch:assert>
      <sch:report test="b:origin/@kind = 'line' and not(b:authentication[@assay = 'STR'])" role="warning"
        >[C1b] Cell line without an STR authentication record.</sch:report>
      <sch:report test="not(b:culture/b:param[@name = 'atmosphere_O2'])" role="warning"
        >[C5] atmosphere_O2 not recorded; normoxia is a choice, not a default.</sch:report>
      <sch:report test="b:culture/@serum[. != ''][. != '0'] and not(b:culture/@serumlot[string-length(.) &gt; 0])" role="warning"
        >[C6] Serum used but serumlot not recorded.</sch:report>
    </sch:rule>
  </sch:pattern>

  <!-- ================= I: formulations ================= -->

  <sch:pattern id="formulations">
    <sch:rule context="b:bioink">
      <sch:assert test="not(@class = 'bioink') or b:cellload"
        >[I1] class='bioink' requires at least one b:cellload. A formulation with no cells is a
        biomaterial-ink.</sch:assert>
      <sch:assert test="not(b:rheology) or b:rheology/b:param[@name = 'temp_of_measurement']"
        >[I2] b:rheology MUST record temp_of_measurement. A viscosity without a temperature is
        not a measurement.</sch:assert>
    </sch:rule>
  </sch:pattern>

  <sch:pattern id="ink-references">
    <sch:rule context="b:component">
      <sch:assert test="//b:substances[@id = current()/@substanceid]"
        >[I3] substanceid=<sch:value-of select="@substanceid"/> does not resolve to a
        b:substances resource.</sch:assert>
      <sch:assert test="not(//b:substances[@id = current()/@substanceid])
                        or number(@substanceindex) &lt; count(//b:substances[@id = current()/@substanceid]/b:substance)"
        >[I3] substanceindex <sch:value-of select="@substanceindex"/> is out of
        range.</sch:assert>
    </sch:rule>

    <sch:rule context="b:cellload">
      <sch:assert test="//b:cellpopulations[@id = current()/@cellpopid]"
        >[I4] cellpopid=<sch:value-of select="@cellpopid"/> does not resolve to a
        b:cellpopulations resource.</sch:assert>
      <sch:assert test="not(//b:cellpopulations[@id = current()/@cellpopid])
                        or number(@cellpopindex) &lt; count(//b:cellpopulations[@id = current()/@cellpopid]/b:cellpopulation)"
        >[I4] cellpopindex <sch:value-of select="@cellpopindex"/> is out of range.</sch:assert>
    </sch:rule>
  </sch:pattern>

  <!-- ================= P/T: process ================= -->

  <sch:pattern id="process-common">
    <sch:rule context="b:process">
      <sch:assert test="b:parameters/b:param[@name = 'build_temp']"
        >[P0] Every process MUST record build_temp.</sch:assert>
      <sch:assert test="b:parameters/b:param[@name = 'print_duration']"
        >[P0] Every process MUST record print_duration.</sch:assert>
      <sch:assert test="b:parameters/b:param[@name = 'sterility_method']"
        >[P0] Every process MUST record sterility_method.</sch:assert>
      <sch:assert test="b:parameters/b:param[@name = 'cell_viability_post_print']"
        >[P0] Every process MUST record cell_viability_post_print.</sch:assert>
      <sch:report test="starts-with(@modality, 'x-')" role="warning"
        >[P4] modality '<sch:value-of select="@modality"/>' is vendor-specific and not
        interoperable.</sch:report>
    </sch:rule>
  </sch:pattern>

  <sch:pattern id="process-extrusion">
    <sch:rule context="b:process[starts-with(@modality, 'extrusion-')]">
      <sch:assert test="b:parameters/b:param[@name = 'nozzle_inner_diameter']"
        >[P0] Extrusion MUST record nozzle_inner_diameter.</sch:assert>
      <sch:assert test="b:parameters/b:param[@name = 'print_speed']"
        >[P0] Extrusion MUST record print_speed.</sch:assert>
      <sch:assert test="b:parameters/b:param[@name = 'nozzle_geometry']"
        >[P0] Extrusion MUST record nozzle_geometry.</sch:assert>
      <sch:assert test="b:parameters/b:param[@name = 'cartridge_temp']"
        >[P0] Extrusion MUST record cartridge_temp.</sch:assert>
      <sch:assert test="b:parameters/b:param[@name = 'nozzle_length']"
        >[P0] Extrusion MUST record nozzle_length. Without it the wall shear stress is not
        derivable, and shear is the quantity the cell-damage literature turns on.</sch:assert>
      <sch:assert test="b:parameters/b:param[@name = 'layer_height']
                        and b:parameters/b:param[@name = 'strand_spacing']"
        >[P0] Extrusion MUST record layer_height and strand_spacing.</sch:assert>
      <sch:assert test="not(@modality = 'extrusion-pneumatic')
                        or b:parameters/b:param[@name = 'extrusion_pressure']"
        >[P0] A pneumatic drive commands a pressure; extrusion_pressure is
        required.</sch:assert>
      <sch:assert test="not(@modality = 'extrusion-piston' or @modality = 'extrusion-screw')
                        or b:parameters/b:param[@name = 'volumetric_flow_rate']"
        >[P0] A displacement drive commands a volume rate, not a pressure;
        volumetric_flow_rate is required.</sch:assert>
      <sch:assert test="not(@modality = 'extrusion-screw')
                        or b:parameters/b:param[@name = 'screw_speed']"
        >[P0] Screw extrusion MUST record screw_speed.</sch:assert>
      <sch:assert test="not(@modality = 'extrusion-coaxial')
                        or (b:parameters/b:param[@name = 'core_flow_rate']
                            and b:parameters/b:param[@name = 'shell_flow_rate']
                            and b:parameters/b:param[@name = 'core_shell_ratio'])"
        >[P0] Coaxial extrusion MUST record core_flow_rate, shell_flow_rate and
        core_shell_ratio. These, not the nozzle bore alone, set lumen diameter and wall
        thickness.</sch:assert>
      <sch:assert test="not(@modality = 'extrusion-embedded')
                        or (b:parameters/b:param[@name = 'bath_composition']
                            and b:parameters/b:param[@name = 'bath_particle_diameter']
                            and b:parameters/b:param[@name = 'bath_yield_stress']
                            and b:parameters/b:param[@name = 'bath_temp'])"
        >[P0] Embedded extrusion MUST record bath_composition, bath_particle_diameter,
        bath_yield_stress and bath_temp. Bath particle size, not the nozzle, sets the
        resolution floor.</sch:assert>
    </sch:rule>
  </sch:pattern>

  <sch:pattern id="process-vat">
    <sch:rule context="b:process[@modality = 'vat-dlp' or @modality = 'vat-sla']">
      <sch:assert test="b:parameters/b:param[@name = 'light_wavelength']"
        >[P0] Vat photopolymerisation MUST record light_wavelength.</sch:assert>
      <sch:assert test="b:parameters/b:param[@name = 'irradiance']"
        >[P0] Vat photopolymerisation MUST record irradiance.</sch:assert>
      <sch:assert test="b:parameters/b:param[@name = 'exposure_time_per_layer']"
        >[P0] Vat photopolymerisation MUST record exposure_time_per_layer.</sch:assert>
      <sch:assert test="b:parameters/b:param[@name = 'layer_thickness']"
        >[P0] Vat photopolymerisation MUST record layer_thickness.</sch:assert>
      <sch:assert test="b:parameters/b:param[@name = 'photoinitiator_conc']"
        >[P0] Vat photopolymerisation MUST record photoinitiator_conc.</sch:assert>
      <sch:assert test="not(@modality = 'vat-dlp')
                        or (b:parameters/b:param[@name = 'photoabsorber_identity']
                            and b:parameters/b:param[@name = 'photoabsorber_conc'])"
        >[P0] DLP MUST record photoabsorber_identity and photoabsorber_conc.</sch:assert>
    </sch:rule>
  </sch:pattern>

  <sch:pattern id="process-volumetric">
    <sch:rule context="b:process[@modality = 'volumetric-tomographic']">
      <sch:assert test="b:parameters/b:param[@name = 'light_wavelength']"
        >[P0] Volumetric printing MUST record light_wavelength.</sch:assert>
      <sch:assert test="b:parameters/b:param[@name = 'optical_power']"
        >[P0] Volumetric printing MUST record optical_power.</sch:assert>
      <sch:assert test="b:parameters/b:param[@name = 'total_light_dose']"
        >[P0] Volumetric printing MUST record total_light_dose.</sch:assert>
      <sch:assert test="b:parameters/b:param[@name = 'rotation_speed']"
        >[P0] Volumetric printing MUST record rotation_speed.</sch:assert>
      <sch:assert test="b:parameters/b:param[@name = 'number_of_projections']"
        >[P0] Volumetric printing MUST record number_of_projections.</sch:assert>
      <sch:report test="not(b:parameters/b:param[@name = 'resin_refractive_index'])" role="warning"
        >[P5] resin_refractive_index not recorded. Scattering raises dose outside the target
        volume and its mean free path depends on cell density.</sch:report>
    </sch:rule>
  </sch:pattern>

  <sch:pattern id="process-mew">
    <sch:rule context="b:process[@modality = 'melt-electrowriting']">
      <sch:assert test="b:parameters/b:param[@name = 'critical_translation_speed']"
        >[P0] Melt electrowriting MUST record critical_translation_speed.</sch:assert>
      <sch:assert test="not(b:parameters/b:param[@name = 'critical_translation_speed'])
                        or b:parameters/b:param[@name = 'critical_translation_speed']/@provenance = 'measured'"
        >[P1] critical_translation_speed MUST be measured, never cited. CTS drifts with ambient
        conditions and is session-specific.</sch:assert>
      <sch:assert test="b:parameters/b:param[@name = 'applied_voltage']
                        and b:parameters/b:param[@name = 'collector_distance']
                        and b:parameters/b:param[@name = 'collector_speed']
                        and b:parameters/b:param[@name = 'nozzle_temp']"
        >[P0] Melt electrowriting MUST record nozzle_temp, applied_voltage, collector_distance
        and collector_speed.</sch:assert>
    </sch:rule>

    <sch:rule context="b:process[@modality = 'melt-electrowriting' or @modality = 'electrospinning']">
      <sch:assert test="b:environment/b:param[@name = 'chamber_temp']
                        and b:environment/b:param[@name = 'chamber_RH']"
        >[P2] Electrohydrodynamic modalities MUST record chamber_temp and
        chamber_RH.</sch:assert>
    </sch:rule>
  </sch:pattern>

  <sch:pattern id="process-lift">
    <sch:rule context="b:process[@modality = 'laser-lift']">
      <sch:assert test="b:parameters/b:param[@name = 'laser_fluence']
                        and b:parameters/b:param[@name = 'spot_size']
                        and b:parameters/b:param[@name = 'pulse_energy']
                        and b:parameters/b:param[@name = 'pulse_duration']
                        and b:parameters/b:param[@name = 'laser_wavelength']"
        >[P0] LIFT MUST record laser_wavelength, pulse_duration, pulse_energy, laser_fluence and
        spot_size.</sch:assert>
      <sch:assert test="b:parameters/b:param[@name = 'absorbing_layer_material']
                        and b:parameters/b:param[@name = 'absorbing_layer_thickness']
                        and b:parameters/b:param[@name = 'donor_film_thickness']
                        and b:parameters/b:param[@name = 'donor_receiver_gap']
                        and b:parameters/b:param[@name = 'receiver_coating_thickness']"
        >[P0] LIFT MUST record the donor and receiver geometry: absorbing layer material and
        thickness, donor film thickness, donor-receiver gap, receiver coating
        thickness.</sch:assert>
    </sch:rule>
  </sch:pattern>

  <sch:pattern id="derived-quantities">
    <sch:rule context="b:param[@name = 'wall_shear_stress_max'
                            or @name = 'residence_time_in_nozzle'
                            or @name = 'Z_number'
                            or @name = 'Weber_number'
                            or @name = 'penetration_depth_Dp'
                            or @name = 'critical_energy_Ec'
                            or @name = 'speed_ratio'
                            or @name = 'total_light_dose']">
      <sch:assert test="@provenance = 'derived'"
        >[P3] '<sch:value-of select="@name"/>' is computed from rheology, geometry and flow. It
        MUST carry provenance='derived' and MUST NOT be presented as a
        measurement.</sch:assert>
    </sch:rule>
  </sch:pattern>

  <sch:pattern id="toolpaths">
    <sch:rule context="b:toolpath">
      <sch:assert test="@checksum and string-length(normalize-space(@checksum)) &gt; 0"
        >[T1] A toolpath MUST carry a checksum. Otherwise the dossier's process claims are not
        bound to the file that was executed.</sch:assert>
      <sch:report test="not(b:commandmap)" role="warning"
        >[T2] Toolpath without a commandmap; bio-relevant codes are unmapped. M106 is a fan on
        one machine and a crosslinking lamp on another.</sch:report>
    </sch:rule>

    <sch:rule context="b:layerevent/b:param">
      <sch:report test="ancestor::b:process/b:parameters/b:param[@name = current()/@name]" role="warning"
        >[T3] '<sch:value-of select="@name"/>' appears in both b:parameters and a b:layerevent.
        The layer event governs that layer; confirm this is intended.</sch:report>
    </sch:rule>
  </sch:pattern>

  <!-- ================= G: geometry binding ================= -->

  <sch:pattern id="geometry-binding">
    <sch:rule context="core:object[//b:bioinkgroup[@id = current()/@pid]]">
      <sch:assert test="@pindex and number(@pindex) &lt; count(//b:bioinkgroup[@id = current()/@pid]/b:bioink)"
        >[G1] Object selects bioink group <sch:value-of select="@pid"/> but pindex is missing or
        out of range.</sch:assert>
      <sch:report test="not(@b:processid)" role="warning"
        >[G3] Object is assigned a bioink but no process; the build modality is
        undetermined.</sch:report>
      <sch:report test="not(@b:regionrole)" role="warning"
        >[G4] Bio object without regionrole. Two meshes of identical shape may be parenchyma and
        sacrificial template; the role is not recoverable from geometry.</sch:report>
    </sch:rule>

  </sch:pattern>

  <sch:pattern id="geometry-process">
    <sch:rule context="core:object[@b:processid] | core:item[@b:processid]">
      <sch:assert test="//b:process[@id = current()/@b:processid]"
        >[G2] processid=<sch:value-of select="@b:processid"/> does not resolve to a b:process
        resource.</sch:assert>
    </sch:rule>
  </sch:pattern>

  <!-- ================= F: volumetric field bindings ================= -->

  <sch:pattern id="field-bindings">
    <sch:rule context="b:fieldbinding">
      <sch:assert test="//v:volumedata[@id = current()/@volumeid]"
        >[F1] volumeid=<sch:value-of select="@volumeid"/> does not resolve to a v:volumedata
        resource.</sch:assert>
      <sch:assert test="not(//v:volumedata[@id = current()/@volumeid])
                        or //v:volumedata[@id = current()/@volumeid]/v:property[@name = current()/@property]"
        >[F2] Property '<sch:value-of select="@property"/>' is not a v:property of volumedata
        <sch:value-of select="@volumeid"/>.</sch:assert>
      <sch:assert test="not(@provenance = 'cited' or @provenance = 'derived')
                        or @evid or @method"
        >[F7] A field binding MUST carry evidence or a method. The evidence rule applies to
        graded quantities too.</sch:assert>
      <sch:assert test="not(b:maps) or //b:bioinkgroup[@id = current()/b:maps/@bioinkid]"
        >[F8] maps bioinkid does not resolve to a b:bioinkgroup.</sch:assert>
      <sch:assert test="not(@quantity = 'cell_density')
                        or not(b:maps)
                        or not(//b:bioinkgroup[@id = current()/b:maps/@bioinkid])
                        or not(//b:bioinkgroup[@id = current()/b:maps/@bioinkid]/b:bioink[position() = current()/b:maps/@bioinkindex + 1][@class = 'biomaterial-ink'])"
        >[F6] A cell_density field is mapped to a biomaterial-ink, which by definition contains
        no cells.</sch:assert>
      <sch:assert test="not(b:range/@min) or not(b:range/@max)
                        or number(b:range/@min) &lt;= number(b:range/@max)"
        >[U4] Field range min exceeds max.</sch:assert>
      <sch:assert test="not(@quantity = 'cell_density' or @quantity = 'porosity'
                            or @quantity = 'polymer_conc' or @quantity = 'photoinitiator_conc')
                        or not(b:range/@min) or number(b:range/@min) &gt;= 0"
        >[U4] Field range min is negative for a quantity that cannot be
        negative.</sch:assert>
      <sch:report test="not(b:range)" role="warning"
        >[F9] Field binding without a b:range; the admissible span of the field is
        undeclared.</sch:report>
    </sch:rule>

    <sch:rule context="b:cellload">
      <sch:assert test="not(@density and @fieldid[string-length(.) &gt; 0])"
        >[F3] A cell load declares both a scalar density and a fieldid. A load is either
        uniform or graded, not both.</sch:assert>
      <sch:assert test="@density or @fieldid[string-length(.) &gt; 0]"
        >[F3] A cell load declares neither density nor fieldid.</sch:assert>
      <sch:assert test="not(@density) or @unit"
        >[F3] A scalar cell load density requires a unit.</sch:assert>
      <sch:assert test="not(@fieldid[string-length(.) &gt; 0])
                        or //b:fieldbinding[@id = current()/@fieldid]"
        >[F4] fieldid=<sch:value-of select="@fieldid"/> does not resolve to a
        b:fieldbinding.</sch:assert>
      <sch:assert test="not(@fieldid[string-length(.) &gt; 0])
                        or not(//b:fieldbinding[@id = current()/@fieldid])
                        or //b:fieldbinding[@id = current()/@fieldid]/@quantity = 'cell_density'"
        >[F6] A cell load must bind a cell_density field.</sch:assert>
    </sch:rule>
  </sch:pattern>

  <!-- ================= U: plausibility ================= -->

  <sch:pattern id="unit-dimensions">
    <!-- U1: a parameter's unit must belong to the dimension of the quantity it names.
         Catches transcription and unit-conversion errors, not dishonesty. -->
    <sch:rule context="b:param[@name = 'build_temp' or @name = 'cartridge_temp'
                            or @name = 'bed_temp' or @name = 'bath_temp'
                            or @name = 'nozzle_temp' or @name = 'chamber_temp'
                            or @name = 'incubator_temp' or @name = 'temp_of_measurement'
                            or @name = 'reaction_temp'][@unit]">
      <sch:assert test="@unit = 'Cel' or @unit = 'K'"
        >[U1] '<sch:value-of select="@name"/>' is a temperature but carries unit
        '<sch:value-of select="@unit"/>'.</sch:assert>
    </sch:rule>

    <sch:rule context="b:param[@name = 'light_wavelength' or @name = 'laser_wavelength'][@unit]">
      <sch:assert test="@unit = 'nm' or @unit = 'um'"
        >[U1] '<sch:value-of select="@name"/>' is a wavelength but carries unit
        '<sch:value-of select="@unit"/>'.</sch:assert>
    </sch:rule>

    <sch:rule context="b:param[@name = 'total_light_dose' or @name = 'laser_fluence'
                            or @name = 'critical_energy_Ec' or @name = 'post_cure_dose'][@unit]">
      <sch:assert test="@unit = 'mJ/cm2' or @unit = 'J/cm2' or @unit = 'mJ/cm3'"
        >[U1] '<sch:value-of select="@name"/>' is a dose but carries unit
        '<sch:value-of select="@unit"/>'.</sch:assert>
    </sch:rule>

    <sch:rule context="b:param[@name = 'extrusion_pressure' or @name = 'yield_stress'
                            or @name = 'bath_yield_stress'
                            or @name = 'wall_shear_stress_max'][@unit]">
      <sch:assert test="@unit = 'Pa' or @unit = 'kPa' or @unit = 'MPa' or @unit = 'bar'"
        >[U1] '<sch:value-of select="@name"/>' is a pressure or stress but carries unit
        '<sch:value-of select="@unit"/>'.</sch:assert>
    </sch:rule>

    <sch:rule context="b:param[@name = 'cell_viability_post_print' or @name = 'chamber_RH'
                            or @name = 'ambient_RH' or @name = 'atmosphere_CO2'
                            or @name = 'atmosphere_O2'][@unit]">
      <sch:assert test="@unit = '%'"
        >[U1] '<sch:value-of select="@name"/>' is a percentage but carries unit
        '<sch:value-of select="@unit"/>'.</sch:assert>
    </sch:rule>
  </sch:pattern>

  <sch:pattern id="physical-bounds">
    <!-- U2: deliberately generous. A bound that fires on legitimate work is worse than no
         bound, so these reject only the impossible or the plainly mistyped. -->
    <sch:rule context="b:param[@name = 'cell_viability_post_print' or @name = 'chamber_RH'
                            or @name = 'ambient_RH' or @name = 'atmosphere_CO2'
                            or @name = 'atmosphere_O2']">
      <sch:assert test="not(@measured) or @measured = ''
                        or (number(@measured) &gt;= 0 and number(@measured) &lt;= 100)"
        >[U2] '<sch:value-of select="@name"/>' measured='<sch:value-of select="@measured"/>'
        is outside 0-100 %.</sch:assert>
      <sch:assert test="not(@setpoint) or @setpoint = ''
                        or (number(@setpoint) &gt;= 0 and number(@setpoint) &lt;= 100)"
        >[U2] '<sch:value-of select="@name"/>' setpoint='<sch:value-of select="@setpoint"/>'
        is outside 0-100 %.</sch:assert>
    </sch:rule>

    <sch:rule context="b:param[@name = 'passage_at_print']">
      <sch:assert test="not(@measured) or @measured = ''
                        or (number(@measured) &gt;= 0 and number(@measured) &lt;= 100)"
        >[U2] passage_at_print='<sch:value-of select="@measured"/>' is outside a plausible
        range.</sch:assert>
    </sch:rule>

    <sch:rule context="b:param[@name = 'initial_pH' or @name = 'reaction_pH']">
      <sch:assert test="not(@setpoint) or @setpoint = ''
                        or (number(@setpoint) &gt;= 0 and number(@setpoint) &lt;= 14)"
        >[U2] pH '<sch:value-of select="@setpoint"/>' is outside 0-14.</sch:assert>
    </sch:rule>

    <sch:rule context="b:param[@name = 'light_wavelength' or @name = 'laser_wavelength']">
      <sch:assert test="not(@setpoint) or @setpoint = ''
                        or (number(@setpoint) &gt;= 100 and number(@setpoint) &lt;= 2000)"
        >[U2] wavelength '<sch:value-of select="@setpoint"/>' nm is outside a plausible
        range.</sch:assert>
    </sch:rule>
  </sch:pattern>

  <!-- ================= Q: maturation and characterization ================= -->

  <sch:pattern id="maturation-stages">
    <sch:rule context="b:stage">
      <sch:assert test="not(@culture = 'perfusion') or b:bioreactor"
        >[Q3] Stage '<sch:value-of select="@name"/>' is perfusion culture but describes no
        bioreactor.</sch:assert>
      <sch:assert test="not(@culture = 'perfusion') or not(b:bioreactor)
                        or b:bioreactor/b:param[@name = 'flow_rate']"
        >[Q3] Perfusion stage '<sch:value-of select="@name"/>' records no flow_rate. Flow rate
        sets the wall shear stress at the construct, and shear drives
        differentiation.</sch:assert>
      <sch:report test="@culture = 'static' and b:bioreactor[@kind != 'none']" role="warning"
        >[Q4] Stage '<sch:value-of select="@name"/>' declares static culture but names a
        bioreactor.</sch:report>
      <sch:report test="b:medium[not(@exchangeinterval)]" role="warning"
        >[Q6] A medium in stage '<sch:value-of select="@name"/>' records no exchange
        interval.</sch:report>
    </sch:rule>
  </sch:pattern>

  <sch:pattern id="stimulation-regimes">
    <!-- Q5: magnitude, rate and duration are only interpretable together. The perfusion
         literature specifically notes that these circuit parameters, as a group, are
         routinely omitted from reporting. -->
    <sch:rule context="b:stimulation[@mode = 'fluid-shear']">
      <sch:assert test="b:param[@name = 'flow_rate']
                        and b:param[@name = 'wall_shear_stress']
                        and b:param[@name = 'stimulation_duration']"
        >[Q5] Fluid-shear stimulation MUST record flow_rate, wall_shear_stress and
        stimulation_duration.</sch:assert>
    </sch:rule>

    <sch:rule context="b:stimulation[@mode = 'cyclic-tension' or @mode = 'cyclic-compression']">
      <sch:assert test="b:param[@name = 'strain_amplitude']
                        and b:param[@name = 'stimulation_frequency']
                        and b:param[@name = 'cycles_per_day']"
        >[Q5] Cyclic loading MUST record strain_amplitude, stimulation_frequency and
        cycles_per_day.</sch:assert>
    </sch:rule>

    <sch:rule context="b:stimulation[@mode = 'electrical' or @mode = 'electromagnetic']">
      <sch:assert test="b:param[@name = 'field_strength']
                        and b:param[@name = 'stimulation_frequency']"
        >[Q5] Electrical and electromagnetic stimulation MUST record field_strength and
        stimulation_frequency.</sch:assert>
    </sch:rule>
  </sch:pattern>

  <sch:pattern id="characterization-assays">
    <sch:rule context="b:assay">
      <sch:assert test="@method and string-length(normalize-space(@method)) &gt; 0"
        >[Q8] Assay '<sch:value-of select="@name"/>' names no method. An endpoint without a
        method is not a measurement.</sch:assert>
      <sch:report test="@destructive = 'true' and count(b:reading) &gt; 1" role="warning"
        >[Q10] Assay '<sch:value-of select="@name"/>' is destructive across
        <sch:value-of select="count(b:reading)"/> timepoints; each needs its own
        specimen.</sch:report>
    </sch:rule>

    <sch:rule context="b:reading">
      <sch:assert test="count(../b:reading[@timepoint = current()/@timepoint]) = 1"
        >[Q9] Assay '<sch:value-of select="../@name"/>' has more than one reading at timepoint
        <sch:value-of select="@timepoint"/>; use n and sd for replicates.</sch:assert>
      <sch:assert test="not(@provenance = 'measured')
                        or (@value and string-length(normalize-space(@value)) &gt; 0)"
        >[Q11] Reading at <sch:value-of select="@timepoint"/> is provenance='measured' but
        carries no value.</sch:assert>
    </sch:rule>
  </sch:pattern>

  <!-- ================= H: deposition heads ================= -->

  <sch:pattern id="printheads">
    <sch:rule context="b:printhead">
      <sch:assert test="count(//b:printhead[@tool = current()/@tool]) = 1 or not(@tool)"
        >[H1] Duplicate tool identifier '<sch:value-of select="@tool"/>'.</sch:assert>
      <sch:assert test="not(b:nozzle/@geometry = 'coaxial' or b:nozzle/@geometry = 'triaxial')
                        or b:coaxial"
        >[H2] Printhead '<sch:value-of select="@name"/>' declares a
        <sch:value-of select="b:nozzle/@geometry"/> nozzle but describes no channels.</sch:assert>
      <sch:report test="not(b:nozzle/@length[string-length(.) &gt; 0])" role="warning"
        >[H1] Printhead '<sch:value-of select="@name"/>' nozzle records no length; wall shear
        stress cannot be derived without it.</sch:report>
    </sch:rule>

    <sch:rule context="core:object[@b:printheadid]">
      <sch:assert test="//b:printheads[@id = current()/@b:printheadid]"
        >[H3] printheadid=<sch:value-of select="@b:printheadid"/> does not resolve to a
        b:printheads resource.</sch:assert>
      <sch:assert test="not(//b:printheads[@id = current()/@b:printheadid])
                        or (@b:printheadindex
                            and number(@b:printheadindex) &lt;
                                count(//b:printheads[@id = current()/@b:printheadid]/b:printhead))"
        >[H3] printheadindex is missing or out of range.</sch:assert>
      <!-- The head is loaded with one formulation. An object claiming a different one is a
           contradiction that no amount of parameter detail would reveal. -->
      <sch:assert test="not(@pid) or not(@b:printheadindex)
                        or not(//b:printheads[@id = current()/@b:printheadid])
                        or not(//b:printheads[@id = current()/@b:printheadid]/b:printhead[
                                 position() = current()/@b:printheadindex + 1]/@bioinkid[string-length(.) &gt; 0])
                        or (//b:printheads[@id = current()/@b:printheadid]/b:printhead[
                              position() = current()/@b:printheadindex + 1]/@bioinkid = current()/@pid
                            and //b:printheads[@id = current()/@b:printheadid]/b:printhead[
                              position() = current()/@b:printheadindex + 1]/@bioinkindex = current()/@pindex)"
        >[H3] This object selects a bioink that the head depositing it is not loaded
        with.</sch:assert>
    </sch:rule>

    <sch:rule context="b:process[@printheadsid]">
      <sch:assert test="//b:printheads[@id = current()/@printheadsid]"
        >[H3] printheadsid=<sch:value-of select="@printheadsid"/> does not resolve.</sch:assert>
    </sch:rule>
  </sch:pattern>

  <sch:pattern id="coaxial-channels">
    <sch:rule context="b:coaxial">
      <sch:assert test="b:channel[@role = 'core']"
        >[H2] A coaxial nozzle MUST describe a core channel.</sch:assert>
      <sch:assert test="b:channel[@role = 'shell'] or b:channel[@role = 'sheath']"
        >[H2] A coaxial nozzle MUST describe a shell or sheath channel.</sch:assert>
      <!-- The product claimed and the core contents must agree: a hollow tube requires a
           core that is removed or that only crosslinks, not one carrying cells. -->
      <sch:assert test="not(@product = 'hollow-tube')
                        or not(b:channel[@role = 'core']/@content = 'bioink')"
        >[H4] Product 'hollow-tube' is claimed but the core carries bioink. A hollow tube
        requires a sacrificial, crosslinker or mist core.</sch:assert>
      <sch:assert test="not(@product = 'solid-fibre')
                        or not(b:channel[@role = 'core']/@content = 'sacrificial'
                               or b:channel[@role = 'core']/@content = 'crosslinker-mist')"
        >[H4] Product 'solid-fibre' is claimed but the core is sacrificial or mist.</sch:assert>
    </sch:rule>

    <sch:rule context="b:channel[@content = 'bioink']">
      <sch:assert test="@bioinkid[string-length(.) &gt; 0]"
        >[H5] Channel '<sch:value-of select="@role"/>' carries bioink but names no
        bioinkid.</sch:assert>
    </sch:rule>
  </sch:pattern>

  <sch:pattern id="shear-derivation">
    <!-- X1: shear stress is computed from geometry, driving term and rheology. A package
         that reports it without those has not derived anything. -->
    <sch:rule context="b:param[@name = 'wall_shear_stress_max']">
      <sch:assert test="ancestor::b:process/b:parameters/b:param[@name = 'nozzle_inner_diameter']"
        >[X1] wall_shear_stress_max is declared but nozzle_inner_diameter is
        absent.</sch:assert>
      <sch:assert test="ancestor::b:process/b:parameters/b:param[@name = 'nozzle_length']"
        >[X1] wall_shear_stress_max is declared but nozzle_length is absent. The wall shear
        relation is tau_w = dP*R/(2L); without L there is nothing to derive.</sch:assert>
      <sch:assert test="ancestor::b:process/b:parameters/b:param[@name = 'extrusion_pressure']
                        or ancestor::b:process/b:parameters/b:param[@name = 'volumetric_flow_rate']"
        >[X1] wall_shear_stress_max is declared but neither a pressure nor a flow rate is
        recorded.</sch:assert>
      <sch:assert test="//b:rheology"
        >[X1] wall_shear_stress_max is declared but no ink carries a fitted
        rheology model.</sch:assert>
    </sch:rule>
  </sch:pattern>

  <!-- ================= K: calibration ================= -->

  <sch:pattern id="calibration-records">
    <sch:rule context="b:calibration">
      <sch:assert test="@performed and string-length(normalize-space(@performed)) &gt; 0"
        >[K1] A calibration record MUST carry a performed date. Calibration is a dated event,
        not a machine attribute.</sch:assert>
    </sch:rule>

    <sch:rule context="b:test">
      <sch:assert test="@acceptance and string-length(normalize-space(@acceptance)) &gt; 0"
        >[K2] Calibration test '<sch:value-of select="@name"/>' has no acceptance
        criterion.</sch:assert>
      <sch:assert test="not(@outcome = 'pass') or (@measured and string-length(normalize-space(@measured)) &gt; 0)"
        >[K3] Calibration test '<sch:value-of select="@name"/>' is marked pass but records no
        measured value.</sch:assert>
      <sch:assert test="not(@artifactobjectid[string-length(.) &gt; 0])
                        or //core:object[@id = current()/@artifactobjectid]"
        >[K4] Calibration test '<sch:value-of select="@name"/>' references artifact object
        <sch:value-of select="@artifactobjectid"/>, which does not exist.</sch:assert>
      <sch:report test="@outcome = 'fail'" role="warning"
        >[K5] Calibration test '<sch:value-of select="@name"/>' FAILED; builds using this
        process are out of specification.</sch:report>
    </sch:rule>
  </sch:pattern>

  <sch:pattern id="calibration-binding">
    <sch:rule context="b:process">
      <sch:assert test="not(@calibrationid[string-length(.) &gt; 0])
                        or //b:calibration[@id = current()/@calibrationid]"
        >[K4] calibrationid=<sch:value-of select="@calibrationid"/> does not resolve to a
        b:calibration resource.</sch:assert>
      <sch:assert test="not(@calibrationid[string-length(.) &gt; 0])
                        or not(//b:calibration[@id = current()/@calibrationid])
                        or //b:calibration[@id = current()/@calibrationid]/@modality = current()/@modality"
        >[K7] The calibration record's modality does not match this process's modality
        '<sch:value-of select="@modality"/>'.</sch:assert>
      <sch:assert test="not(@regulatoryid[string-length(.) &gt; 0])
                        or //b:regulatory[@id = current()/@regulatoryid]"
        >[R4] regulatoryid=<sch:value-of select="@regulatoryid"/> does not resolve to a
        b:regulatory resource.</sch:assert>
      <sch:report test="not(@calibrationid[string-length(.) &gt; 0])" role="warning"
        >[K6] Process declares no calibration record.</sch:report>

      <!-- K8: the three shape-fidelity tests load the ink differently and do not substitute
           for one another. A grid test and a bridge test both assess ONE layer; only the
           stacking test applies the weight of the layers above. -->
      <sch:report test="starts-with(@modality, 'extrusion-')
                        and @calibrationid[string-length(.) &gt; 0]
                        and //b:calibration[@id = current()/@calibrationid]
                        and not(//b:calibration[@id = current()/@calibrationid]/b:test[
                                  @name = 'layer_stacking_test' or @name = 'stackability'
                                  or @name = 'stacking_test' or @name = 'cylinder_test'])"
        role="warning"
        >[K8] Extrusion process has no layer stacking test. A bridge test and a grid test both
        load a single layer; an ink can pass both and still slump under the weight of
        twenty.</sch:report>
      <sch:report test="starts-with(@modality, 'extrusion-')
                        and @calibrationid[string-length(.) &gt; 0]
                        and //b:calibration[@id = current()/@calibrationid]
                        and not(//b:calibration[@id = current()/@calibrationid]/b:test[
                                  @name = 'bridge_test' or @name = 'filament_collapse'
                                  or @name = 'overhang_test'])"
        role="warning"
        >[K8] Extrusion process has no bridge test; out-of-plane fidelity is
        unassessed.</sch:report>
      <sch:report test="starts-with(@modality, 'extrusion-')
                        and @calibrationid[string-length(.) &gt; 0]
                        and //b:calibration[@id = current()/@calibrationid]
                        and not(//b:calibration[@id = current()/@calibrationid]/b:test[
                                  @name = 'grid_test' or @name = 'printability_Pr'
                                  or @name = 'lattice_test' or @name = 'pore_test'])"
        role="warning"
        >[K8] Extrusion process has no grid test; in-plane fidelity is
        unassessed.</sch:report>

      <!-- N1: ISO/ASTM 52900 crosswalk. Only unambiguous mappings are asserted. -->
      <sch:assert test="not(@iso52900) or not(starts-with(@modality, 'extrusion-')) or @iso52900 = 'MEX'"
        >[N1] Extrusion modalities map to ISO/ASTM 52900 category MEX.</sch:assert>
      <sch:assert test="not(@iso52900)
                        or not(starts-with(@modality, 'vat-') or @modality = 'volumetric-tomographic'
                               or @modality = 'stereolithography-continuous')
                        or @iso52900 = 'VPP'"
        >[N1] Vat and volumetric modalities map to ISO/ASTM 52900 category VPP.</sch:assert>
      <sch:assert test="not(@iso52900)
                        or not(starts-with(@modality, 'inkjet-') or @modality = 'microvalve'
                               or @modality = 'acoustic-droplet' or @modality = 'laser-lift')
                        or @iso52900 = 'MJT'"
        >[N1] Droplet and laser-transfer modalities map to ISO/ASTM 52900 category
        MJT.</sch:assert>
    </sch:rule>
  </sch:pattern>

  <!-- ================= R: regulatory ================= -->

  <sch:pattern id="regulatory-context">
    <sch:rule context="b:regulatory">
      <sch:assert test="b:jurisdiction"
        >[R4] A regulatory resource MUST declare at least one jurisdiction.</sch:assert>
      <sch:assert test="not(@intendeduse = 'implantable' or @intendeduse = 'clinical-investigation')
                        or b:standardref[starts-with(@stdno, 'ISO 10993')]"
        >[R7] Intended use '<sch:value-of select="@intendeduse"/>' requires an ISO 10993
        standardref.</sch:assert>
      <sch:assert test="not(@intendeduse = 'implantable' or @intendeduse = 'clinical-investigation')
                        or (@contactduration and @contactnature)"
        >[R8] Intended use '<sch:value-of select="@intendeduse"/>' requires contactduration and
        contactnature; they are the inputs to ISO 10993 categorisation.</sch:assert>
      <sch:report test="(@intendeduse = 'implantable' or @intendeduse = 'clinical-investigation'
                         or @intendeduse = 'preclinical' or @intendeduse = 'veterinary')
                        and b:jurisdiction[@determination = 'self-assessed']" role="warning"
        >[R6] A regulated intended use rests on self-assessment in at least one jurisdiction;
        confirm with the authority.</sch:report>
    </sch:rule>

    <sch:rule context="b:jurisdiction[@determination = 'undetermined']">
      <sch:assert test="@note and contains(@note, 'openitem')"
        >[R5] Jurisdiction '<sch:value-of select="@region"/>' is undetermined but points at no
        open item. An undetermined regulatory status must be tracked, not left
        silent.</sch:assert>
    </sch:rule>

    <sch:rule context="b:obligation[@status = 'not-met' or @status = 'unknown']">
      <sch:report test="not(@openitemid[string-length(.) &gt; 0]) and not(@note)" role="warning"
        >[R9] Obligation '<sch:value-of select="@ref"/>' is
        '<sch:value-of select="@status"/>' with no open item or note.</sch:report>
    </sch:rule>
  </sch:pattern>

  <!-- ================= J: open items ================= -->

  <sch:pattern id="open-items">
    <sch:rule context="b:openitem">
      <sch:assert test="count(//b:openitem[@key = current()/@key]) = 1"
        >[J1] Duplicate open item key '<sch:value-of select="@key"/>'.</sch:assert>
      <sch:assert test="not(@status = 'resolved')
                        or (@resolution and string-length(normalize-space(@resolution)) &gt; 0)"
        >[J2] Open item '<sch:value-of select="@key"/>' is resolved but records no
        resolution.</sch:assert>
      <sch:assert test="not(@status = 'resolved')
                        or (@resolved and string-length(normalize-space(@resolved)) &gt; 0)"
        >[J2] Open item '<sch:value-of select="@key"/>' is resolved but records no resolution
        date.</sch:assert>
      <sch:assert test="not(@status = 'open' or @status = 'in-progress')
                        or (@action and string-length(normalize-space(@action)) &gt; 0)"
        >[J3] Open item '<sch:value-of select="@key"/>' states no action that would close
        it.</sch:assert>
      <sch:report test="@severity = 'blocking' and (@status = 'open' or @status = 'in-progress')"
        role="warning"
        >[J6] Blocking open item '<sch:value-of select="@key"/>' is
        unresolved.</sch:report>
    </sch:rule>

    <sch:rule context="b:affects">
      <sch:assert test="//core:resources/*[@id = current()/@targetid]"
        >[J4] Open item affects target <sch:value-of select="@targetid"/>, which is not a
        resource.</sch:assert>
    </sch:rule>
  </sch:pattern>

  <sch:pattern id="open-item-coverage">
    <!-- J5: an estimated parameter is an admission of a gap, so something must own it.
         Coverage is by exact param name: a resource-wide affects refers to the resource's own
         attributes and does not excuse individual estimated parameters inside it. -->
    <sch:rule context="b:param[@provenance = 'estimated']">
      <sch:report test="not(//b:affects[@paramname = current()/@name])" role="warning"
        >[J5] Param '<sch:value-of select="@name"/>' is provenance='estimated' but no open item
        accounts for it.</sch:report>
    </sch:rule>
  </sch:pattern>

</sch:schema>
