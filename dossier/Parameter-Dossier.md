# Bio Parameter Dossier — what to record, per modality

Companion to `spec/3MF-Bio-Extension-v0.1.md`. Reference keys (R1…) resolve in
`dossier/References.md`.

**How to read this.** Each table lists the parameter, its UCUM unit, whether the spec
requires it, and the source that establishes it as process-relevant. The *source column
justifies the parameter, not a value.* Numeric values belong in your own package with
`provenance="measured"`. Where a specific published value is quoted below, it is labelled
with its source and its context — it is an example of what a real record looks like, not a
recommended setting for your machine.

---

## 0. The standards baseline

| Standard | Scope | Relevance here |
|---|---|---|
| ASTM F3659-24 | Standard Guide for Bioinks Used in Bioprinting | The only bioink-specific consensus guide. Extrusion is its primary focus; it also acknowledges electrospinning, electrospray, droplet/inkjet and laser-assisted modalities. Covers pre-printing and printing considerations, post-print stabilisation, sterility and cytocompatibility including post-printing viability. 20 pp., published 2024, developed over ~6 years by ~35 contributors including FDA and NIST participants. (R1) |
| ASTM F2150 | Standard guide for characterisation of scaffolds | General scaffold characterisation, referenced by F3659 |
| ASTM F2027 | Standard guide for source materials | Material characterisation, referenced by F3659 |
| ISO 10993 series | Biological evaluation of medical devices | Cytotoxicity/biocompatibility, referenced by F3659 |
| GCCP 2.0 | Good Cell and Tissue Culture Practice | Six principles: characterisation and maintenance of essential characteristics, quality management, documentation and reporting, safety, education and training, ethics. Drives the `<b:cellpopulation>` rules. (R14) |

ASTM's scaffold-related standards already cover porosity, permeability, pore size and
uniformity; viscoelasticity, stiffness, swelling ratio and polymerisation kinetics; and
viability, morphology, differentiation, proliferation and distribution — but extrusion
bioprinting imposes printability considerations that these do not yet cover, and a general
guideline for them does not exist (R3). That gap is what §1 below is for.

An early systematic study of process standardisation recommended optimising line
dimensions via feedrate, pressure, nozzle dimension and printing height; determining line
spacing visually until overlap occurs; investigating percentage line overlap for
reproducible mechanical properties; performing tensile testing to ISO/ASTM protocols and
reporting which stress/strain convention was used; evaluating sterilisation and storage
effects on mechanical properties; and running viability for a minimum period plus
proliferation and protein-synthesis assays (R4). Those recommendations map directly onto
`<b:process>`, `<b:result>` and `<b:protocol>`.

---

## 1. Extrusion and deposition — the dominant modality

Extrusion is the most widely used biofabrication modality, and this extension gives it the
deepest treatment: five sub-modalities, a printhead resource, and the only fully specified
derivation chain in the format.

**Three things distinguish extrusion from the other modalities here.**

*The controlled variable differs by drive.* A pneumatic system commands a **pressure**; a
piston or screw commands a **displacement or rotation**. Requiring `extrusion_pressure` from
a piston system is a category error, so `<b:process modality>` splits and the required
parameter sets diverge. `extrusion-pneumatic` requires `extrusion_pressure`;
`extrusion-piston` and `extrusion-screw` require `volumetric_flow_rate`; screw additionally
requires `screw_speed`.

*The machine has heads, plural.* Multi-head deposition is normal — a cell-laden parenchymal
ink in one head, a fugitive support in another, a coaxial vascular head in a third. The
`<b:printhead>` resource carries the nozzle and drive, and names the formulation the head is
loaded with, so a consumer can check that an object's ink and its depositing head agree.
That contradiction is invisible in a flat parameter list.

*Shear stress is the quantity everything turns on, and it is derived, not measured.*
Section 1.3 specifies its inputs and the format enforces their presence.

## 1.0 Sub-modalities

| `modality` | Drive | Controlled variable | Additionally required |
|---|---|---|---|
| `extrusion-pneumatic` | Compressed air | Pressure | `extrusion_pressure` |
| `extrusion-piston` | Mechanical displacement | Volume rate | `volumetric_flow_rate` |
| `extrusion-screw` | Auger rotation | Volume rate + rotation | `volumetric_flow_rate`, `screw_speed` |
| `extrusion-embedded` | Any, into a support bath | As above | bath composition, particle size, yield stress, temperature |
| `extrusion-coaxial` | Two or more independent supplies | Per-channel flow | `core_flow_rate`, `shell_flow_rate`, `core_shell_ratio`, channel bores |

All five inherit a base set: `nozzle_inner_diameter`, `nozzle_geometry`, **`nozzle_length`**,
`print_speed`, `cartridge_temp`, `layer_height`, `strand_spacing`.

`nozzle_length` is **required**, not optional, and this is a deliberate strengthening. The
wall shear relation is τ_w = ΔP·R/(2L). Without a length there is no derivable shear stress,
and the entire cell-damage literature for this modality is expressed in shear.

## 1 Extrusion (`extrusion-pneumatic` / `-piston` / `-screw`)

### 1.1 Machine level

| `name` | Unit | Req | Source / rationale |
|---|---|---|---|
| `nozzle_inner_diameter` | `um` | MUST | Smaller diameter → higher velocity gradient → higher shear → more cell damage (R7) |
| `nozzle_geometry` | — | MUST | `cylindrical` vs `conical`/`tapered`. Conical gives higher flow at equal pressure, so lower pressure for equal flow; one comparison reported viability in cylindrical nozzles an order of magnitude worse than conical (R7, R8) |
| `nozzle_length` | `mm` | SHOULD | Enters both shear and residence-time terms (R9) |
| `extrusion_pressure` | `kPa` | MUST* | *one of pressure or flow rate. Flow rate rises highly non-linearly with pressure for shear-thinning inks, which is why one cannot be inferred from the other (R10) |
| `volumetric_flow_rate` | `uL/min` | MUST* | see above |
| `print_speed` | `mm/s` | MUST | With flow rate sets strand width |
| `layer_height` | `um` | SHOULD | |
| `strand_spacing` | `um` | SHOULD | Line spacing / overlap drives reproducible mechanical properties (R4) |
| `standoff_height` | `um` | SHOULD | First-layer geometry |
| `cartridge_temp` | `Cel` | MUST | Controlling nozzle and chamber temperature has been reported to move viability from ~56% to ~90% (R7) |
| `bed_temp` | `Cel` | SHOULD | |
| `print_duration` | `min` | MUST | Long print time reduces post-extrusion viability (R7) |

### 1.1a Path and layer strategy

Frequently omitted, and the reason two labs with identical inks and pressures get different
mechanics.

| `name` | Unit | Req | Source / rationale |
|---|---|---|---|
| `layer_height` | `um` | MUST | |
| `strand_spacing` | `um` | MUST | Determine visually until strands just overlap, then hold the overlap percentage; percentage line overlap drives reproducible mechanical properties (R4) |
| `infill_pattern` | — | SHOULD | e.g. `0-90 rectilinear`, `60 degree offset`, `concentric` |
| `raster_angle` | `1` | SHOULD | Per-layer deposition angle |
| `perimeter_count` | `1` | SHOULD | |
| `layer_offset` | `um` | SHOULD | Shifting alternate layers changes pore topology at constant spacing |
| `standoff_height` | `um` | SHOULD | First-layer geometry; part of the line-optimisation sweep (R4) |
| `preflow_delay` / `postflow_delay` | `ms` | SHOULD | Pneumatic systems have a compressibility lag; the commanded pressure is not the delivered flow at the instant of the command |
| `retraction` / `z_hop` | `um` | SHOULD | Travel-move artefacts |

**Recommended procedure**, per the process-standardisation study (R4): optimise line
dimensions via feedrate, pressure, nozzle dimension and printing height; determine line
spacing visually until overlap occurs; investigate percentage line overlap for reproducible
mechanics.

### 1.2 Derived (`provenance="derived"`, `method` names the model)

| `name` | Unit | Model |
|---|---|---|
| `wall_shear_stress_max` | `Pa` | Power-law or Herschel–Bulkley wall shear. Shear stress is zero at the nozzle centre and maximal at the wall; the linear distribution known for Newtonian pipe flow also holds for shear-thinning fluids (R10). Cells nearer the wall are more likely to be damaged (R9) |
| `residence_time_in_nozzle` | `s` | Flow rate, nozzle radius and length. Viability falls with increasing flow rate, increasing bioink viscosity, increasing nozzle length, or decreasing nozzle radius — via shear stress *or* residence time (R9) |

### The derivation chain, and why the format enforces it

τ_w = ΔP·R/(2L), maximal at the wall and decreasing toward the centreline, where L is the
nozzle length and R the nozzle radius (R53). The rheology model supplies the velocity
profile; the geometry and the driving term supply the rest.

**Rule X1** therefore requires that a package declaring `wall_shear_stress_max` also carries
`nozzle_inner_diameter`, `nozzle_length`, a pressure or flow rate, and a fitted
`<b:rheology>` on the ink. Without all four, the value is not derived — it is a guess with a
`provenance="derived"` label, which is worse than an honest estimate.

Do not record shear stress as `measured`. It is not directly measurable during printing
(R11); it is computed from rheology plus geometry plus flow. The spec forces this
distinction because conflating the two is the single most common overclaim in extrusion
bioprinting reporting.

**Reported thresholds, for context and not as acceptance criteria.** A synthesis of hydrogel
extrusion rheology places viability near 91% at shear stresses around 5–10 kPa, falling
toward roughly 76% above 10 kPa, with operating envelopes linking pressure and shear history
to survival targets between 76% and 96% (R53). Record your own acceptance criterion; these
figures describe particular inks and cells.

### The counter-intuitive nozzle-geometry result

Maximum wall shear stress is **lowest** in a cylindrical nozzle — but that stress condition
persists over a longer portion of the nozzle, and at equal inlet pressure and bore the mass
flow rate is lower, which has been associated with **lower** cell viability than conical or
tapered-conical geometries (R11). Peak stress and integrated exposure are different
quantities, and optimising for one can worsen the other. This is why the format requires
`nozzle_geometry` and `nozzle_length` rather than diameter alone.

### Modelling caveats worth recording in `note`

- The **power-law model cannot represent a yield stress** and becomes unphysical near zero
  and at very high shear rates. For yield-stress plus shear-thinning inks use
  Herschel–Bulkley; for shape-fidelity optimisation Herschel–Bulkley is better suited, while
  power-law may suffice for parameter prediction where only high shear rates matter
  (R54, R55).
- **Neither captures thixotropy.** Time-dependent viscosity needs a structural-parameter
  model (R54).
- The usual **no-slip wall condition may not hold**: viscoplastic materials can slide below
  the critical shear rate, so wall slip is a real source of disagreement between predicted
  and measured pressure (R55).
- Predicted versus experimental pressures agree well but not perfectly: for alginate/CaCl₂
  through a 0.25 mm plastic conical nozzle, calculated 30–80 kPa against an experimental
  35–70 kPa, with near-zero error for a 0.41 mm tapered nozzle (R56).

### 1.3 Ink level

`<b:rheology model="Herschel-Bulkley">` with `yield_stress`, `consistency_K`,
`flow_index_n`, plus mandatory `temp_of_measurement`. Power-law constants spanning
roughly 0.086–0.505 have been used in published CFD parameter sweeps of extrusion
bioprinting; nozzle geometries compared were conical, tapered-conical and cylindrical over
0.1–0.5 mm diameters and 0.025–0.25 MPa inlet pressure (R11). Record shear-thinning and
shear-recovery behaviour explicitly (R4).

### 1.4 `extrusion-coaxial` (core–shell) — additional

Coaxial extrusion is the principal route to perfusable vasculature in a single deposition
step, because crosslinking happens inline at the moment of deposition rather than afterwards.

| `name` | Unit | Req | Source / rationale |
|---|---|---|---|
| **`core_inner_diameter`** | `um` | MUST | An inner nozzle diameter of 210 µm has been reported as a practical lower limit for a HUVEC-laden vascular network (R57) |
| **`shell_inner_diameter`** | `um` | MUST | |
| `outer_diameter` | `um` | SHOULD | One documented nozzle: core 514 µm, mantle 819 µm, outer 3200 µm (R58) |
| **`core_flow_rate`** | `uL/min` | MUST | Core and shell are independently controlled, commonly by separate pneumatic supplies, allowing different flow rates (R57) |
| **`shell_flow_rate`** | `uL/min` | MUST | Larger shell flow rate gives thicker fibres (R57) |
| **`core_shell_ratio`** | `1` | MUST | Printability of a multimaterial filament depends on the core-to-shell ratio, not only the target outer diameter (R59) |
| `core_pressure` | `kPa` | SHOULD | For mist-based cores, core pressure and sheath flow rate together govern uniformity, lumen diameter and wall thickness (R60) |

**Channel content determines the product, and the format checks the two agree.**
`<b:coaxial product>` is one of `hollow-tube`, `solid-fibre` or `core-shell`, and Rule H4
rejects the combinations that cannot happen:

| Configuration | Product |
|---|---|
| Bioink in shell, crosslinker in core | **Hollow tube.** Core removed or diffuses out, leaving a lumen (R57) |
| Bioink in core, crosslinker in sheath | **Solid fibre**, gelled from the outside (R61) |
| Sacrificial core, bioink shell | **Hollow tube** after the core is flushed (R57) |
| Crosslinker mist as core flow | **Hollow tube** without liquid crosslinker or sacrificial ink, and without extra post-processing (R60) |
| Two cell-laden inks | **Core–shell**, e.g. co-culture in defined layers (R59) |

A package claiming `hollow-tube` while the core carries bioink is describing something that
does not exist, and Rule H4 says so.

**Worked parameter set from the literature**, as an illustration of a complete record rather
than a recommendation: 1.3% w/v high-molecular-weight HA-tyramine with 5.5 U/mL HRP as the
inner core bioink, 27.5% w/v Pluronic F-127 with 0.1% H₂O₂ as the outer sacrificial shell,
45 kPa core and 80 kPa shell pressure, 300 mm/min print speed, 30 °C bed — with enzymatic
gelation by diffusion of hydrogen peroxide into the core (R61).

**Additional calibration**, beyond the base extrusion set: `core_shell_concentricity`
(core offset from the shell centroid on a cross-section) and `wall_thickness`.

### 1.5 `extrusion-embedded` (FRESH / suspended-bath) — additional

| `name` | Unit | Req | Source |
|---|---|---|---|
| `bath_composition` | — | MUST | Gelatin microparticle slurry; FRESH v2.0 used 2% w/v gelatin with 0.25% w/v Pluronic and 0.1% w/v gum arabic (R12) |
| `bath_particle_diameter` | `um` | MUST | ~55 µm in original FRESH; coacervation reduced this to ~25 µm, enabling ~20 µm print resolution; the bath particle size, not the nozzle or stage, is the resolution limit (R12, R13) |
| `bath_yield_stress` | `Pa` | MUST | Bath behaves as a Bingham plastic at low temperature; this is what immobilises the filament where deposited (R12, R13) |
| `bath_temp` | `Cel` | MUST | Thermo-reversible: Bingham-plastic when cold, viscous liquid above ~37 °C (R12) |
| `bath_crosslink_trigger` | — | SHOULD | The aqueous phase can be tuned to drive gelation of the extruded ink — e.g. pH-driven collagen gelation at pH 7.4 (R12) |
| `release_temp` / `release_time` | `Cel` / `min` | MUST | Bath melted out to free the construct |

Note the resolution logic: minimum perfusable channel diameter must be several particles
wide because of random packing and filament diffusion before gelation (R13). If you
record `bath_particle_diameter` you can predict your resolution floor; if you don't, you
can't.

---

## 2. Droplet: `inkjet-piezo`, `inkjet-thermal`, `microvalve`, `acoustic-droplet`

| `name` | Unit | Req | Source |
|---|---|---|---|
| `nozzle_orifice_diameter` | `um` | MUST | |
| `waveform.voltage` | `V` | MUST | Published sweeps have covered 20–150 V (R16) |
| `waveform.pulse_width` | `us` | MUST | 20–200 µs in the same sweep (R16) |
| `waveform.rise_time` / `dwell_time` / `fall_time` / `echo_time` | `us` | SHOULD | The standard piezo waveform decomposition; these plus nozzle speed, nozzle diameter and air gap significantly affect droplet velocity and volume (R17) |
| `jetting_frequency` | `Hz` | MUST | 50–1000 Hz in R16 |
| `droplet_volume` | `pL` | MUST | |
| `droplet_velocity` | `m/s` | MUST | |
| `standoff_distance` | `mm` | SHOULD | |
| `heater_temp` | `Cel` | MUST (thermal) | Thermal DOD vaporises a fluid pocket; the vapour bubble's collapse ejects the drop, and this can damage cells — piezo is generally preferred for cells (R18) |
| `cells_per_droplet` | `1` | SHOULD | Cell distribution within droplets is highly non-uniform and this propagates into the construct (R18) |

### Derived

| `name` | Model |
|---|---|
| `Z_number` | Z = 1/Oh, where Oh = √We / Re. Z identifies ink printability; a commonly cited stable-drop window is Z between 1 and 10 (R15) — note other work bounds the regime jointly in (Z, We) space with 2 < We_jet < 25, the lower bound set by capillary forces preventing ejection and the upper by satellite-drop onset (R19) |
| `Weber_number` | For Oh ≈ 0.1, We governs whether the drop detaches with positive tip velocity or falls back toward the nozzle (R20) |

Record both `Z_number` and `Weber_number` as `derived`, with `method` naming the fluid
properties used (density, viscosity, surface tension) and the temperature at which they
were measured. A Z number computed from vendor-sheet viscosity at 25 °C and used to
justify jetting at 37 °C is a common silent error.

---

## 3. `laser-lift` (LIFT / LAB / BA-LIFT)

Critical parameters, per two independent reviews (R21, R22):

| `name` | Unit | Req | Note |
|---|---|---|---|
| `laser_wavelength` | `nm` | MUST | UV is common (R23) |
| `pulse_duration` | `ns` | MUST | Sets whether loading is stress-confined |
| `pulse_energy` | `uJ` | MUST | |
| `spot_size` | `um` | MUST | |
| `laser_fluence` | `mJ/cm2` | MUST | ∝ pulse energy / spot area. Three regimes with increasing fluence: **subthreshold**, **jetting**, **plume** (R22). In the jetting regime, droplet size and volume rose approximately linearly with fluence (R23) |
| `absorbing_layer_material` | — | MUST | Metal DRL, or polyimide for blister-actuated LIFT where the laser partially ablates an intermediate layer and the blister ejects the drop (R24) |
| `absorbing_layer_thickness` | `nm` | MUST | |
| `donor_film_thickness` | `um` | MUST | Under ambient conditions (20 °C, 50% RH) the hydrogel layer thinned at ~8 µm/min from drying, so transfer parameters drift within a session (R23) |
| `donor_receiver_gap` | `um` | MUST | |
| `receiver_coating_thickness` | `um` | MUST | Increasing a buffering coating from 20 to 40 µm raised printed-cell activity from ~50% to >95%; with no buffering layer at all, activity was ~5% (R21) |
| `donor_viscosity` | `mPa.s` | SHOULD | Fluence alone does not determine the regime: high viscosity needs more fluence to trigger jetting, low viscosity tends to splash (R22) |
| `repetition_rate` | `Hz` | SHOULD | |
| `jetting_regime` | — | SHOULD | `subthreshold` / `jetting` / `plume` |

Cell-specific caveat to record in `note`: printing with cells typically requires higher
laser energy than cell-free ink, produces slower jets and smaller spots, and cell
aggregation can produce non-straight jets or non-straight trajectories (R21). Also record
ambient temperature stability — holding ±2 °C was sufficient to neglect temperature-induced
viscosity change (R23).

---

## 4. Vat photopolymerisation: `vat-sla`, `vat-dlp`, `vat-2pp`

| `name` | Unit | Req | Source |
|---|---|---|---|
| `light_wavelength` | `nm` | MUST | Must be matched to the photoinitiator's absorption; LAP absorbs UV/blue ~350–400 nm and at 400 nm, and mismatch between ink absorption and projector wavelength degrades printability (R26) |
| `irradiance` | `mW/cm2` | MUST | Measure at the build plane with a radiometer, not from the vendor spec |
| `exposure_time_per_layer` | `s` | MUST | |
| `bottom_exposure` | `s` | SHOULD | |
| `layer_thickness` | `um` | MUST | |
| `photoinitiator_conc` | `%{w/v}` | MUST | |
| `photoabsorber_identity` | — | MUST | UV: benzotriazole derivatives, brilliant blue, quinoline yellow. Visible: food dyes — tartrazine, curcumin, anthocyanin, acid red, phenol red (R27); Ponceau 4R has been used where absorbance spans visible wavelengths (R28) |
| `photoabsorber_conc` | `%{w/v}` | MUST | |
| `cure_depth_Cd` | `um` | SHOULD | Also called light-penetration depth. If cure depth exceeds layer thickness the out-of-focus plane over-crosslinks and axial accuracy is lost; photoabsorbers reduce and tighten it (R27) |
| `xy_pixel_pitch` | `um` | SHOULD | |
| `lift_speed` | `mm/s` | SHOULD | |

### Derived — the Jacobs working curve

`penetration_depth_Dp` (`um`) and `critical_energy_Ec` (`mJ/cm2`) are fitted from
cure depth vs exposure, with light attenuation following Beer–Lambert (R25). Record both
as `derived` with `method="Jacobs working curve"` and attach the raw fit data as a
`<b:result>` pointing at a CSV in `/bio/results/`.

The working curve is the single most transferable thing in a vat dossier: it lets another
lab hit your geometry with a different lamp. Publish it, not just your exposure time.

For `vat-2pp` record instead: `average_power`, `NA`, `scan_speed`, `hatch_distance`,
`slicing_distance`, `voxel_dimensions`.

---

## 5. `volumetric-tomographic`

| `name` | Unit | Req | Source |
|---|---|---|---|
| `light_wavelength` | `nm` | MUST | 405 nm laser in a widely used commercial prototype/production system (R29) |
| `optical_power` | `mW` | MUST | |
| `total_light_dose` | `mJ/cm3` or `mJ/cm2` | MUST | Dose tests are run per resin: spots irradiated into a cuvette of solidified resin over varying exposure times and average powers (R29) |
| `print_duration` | `s` | MUST | Constructs have been printed in ~20–30 s (R5, R30) |
| `rotation_speed` | `1/min` | MUST | |
| `number_of_projections` | `1` | MUST | |
| `vial_diameter` | `mm` | SHOULD | Bounds addressable construct size |
| `resin_refractive_index` | `1` | SHOULD | Scattering blurs projections and raises dose in regions adjacent to but outside the target, causing off-target polymerisation and loss of resolution; scattering mean free path is inversely related to cell density, so this is a *cell-density-dependent* optical parameter. RI matching of intracellular components reduced it (R31) |
| `scattering_correction` | — | SHOULD | |
| `post_cure_dose` | `mJ/cm2` | SHOULD | |
| `flushing_temp` | `Cel` | SHOULD | Unpolymerised resin washed out |

**Worked example of a real record** (illustrating format, not prescribing settings): a
bioresin of 5% GelMA with 0.05% LAP was identified as optimal for volumetric printing of
complex perfusable constructs in ~30 s at >90% viability, after screening GelMA and LAP
concentrations for photo-reactivity, printability and cell compatibility, targeting a soft
(<5 kPa) matrix for bone tissue engineering with hMSCs and endothelial co-culture (R30).
Separately, 5% w/v GelMA with 0.1% w/v LAP was used for liver-organoid and HepG2 volumetric
printing (R31), and 5% GelMA with 0.1% LAP plus poly-aspartic acid for mineralising
constructs, with pAsp concentration chosen by measuring resin optical density at 405 nm
(R32).

Two things to notice. First, the same nominal material appears at two photoinitiator
concentrations for different targets — which is exactly why `<b:bioink>` must be a distinct
resource from `<b:substance>`. Second, chemistry choice moves the dose budget: a step-growth
norbornene/thiol gelatin system needed a photoinitiator concentration three times lower and
more than 50% less light exposure dose than chain-growth GelMA, with better positive and
negative resolution (R33). Record `crosslink mechanism` (`photo-chain-growth` vs
`photo-step-growth`), not just "photocrosslinked".

---

## 6. `melt-electrowriting` / `electrospinning`

| `name` | Unit | Req | Source |
|---|---|---|---|
| `nozzle_temp` | `Cel` | MUST | One of the four significant factors in an orthogonal design (R34) |
| `applied_voltage` | `kV` | MUST | Least influential of six factors on fibre diameter in R34 — but still required, since it maintains the jet |
| `collector_voltage` | `kV` | SHOULD | Negative collector bias is used in some setups (R36) |
| `collector_distance` | `mm` | MUST | Significant factor (R34) |
| `feed_pressure` or `flow_rate` | `bar` / `uL/h` | MUST | Melt flow rate was the *most* influential factor on fibre diameter (R34). Typical MEW flow rates are far lower than melt extrusion (R36) |
| `collector_speed` | `mm/min` | MUST | Significant factor (R34) |
| `critical_translation_speed` | `mm/min` | MUST, `measured` | Straight fibres are written when collector speed exceeds CTS, the speed matching the jet velocity (R35). CTS varies with daily polymer and environmental conditions — hence the spec forbids citing it |
| `speed_ratio` | `1` | SHOULD, `derived` | collector_speed / CTS. Best placement accuracy is obtained just above CTS (R37) |
| `spinneret_gauge` | — | SHOULD | 23G–30G ranges reported (R37) |
| `ambient_temp` | `Cel` | MUST | |
| `ambient_RH` | `%` | MUST | |
| `fibre_diameter` | `um` | SHOULD, `measured` | The output, not an input |

**Why the spec is strict here.** MEW is the modality where "same parameters, different
result" is most common, and the published record shows why: fibre diameters from 8 to 138 µm
across a systematic sweep of temperature 200–220 °C, pressure 1.0–3.0 bar, voltage 3.0–7.0 kV
and collector distance 3.0–7.0 mm with four spinneret sizes (R37); fibre diameter digitally
controlled by combining mass flow rate with collector speed *without changing voltage*
(R37); and in one setup a CTS of 180–230 mm/min that had to be re-measured each session
after ≥5 min of jet stabilisation, with ambient conditions logged at 19–22 °C and 35–42% RH
(R36). None of those numbers transfer. The *practice* — measure CTS, print at a stated
multiple of it, log ambient — does.

---

## 7. Material record: worked example (GelMA)

This is the template for `<b:synthesis>`: route → conditions → yield → verification.

**Route.** Methacryloylation of gelatin with methacrylic anhydride. Three published route
families are in common use: the original method (Van Den Bulcke et al. 2000), a sequential
method (Lee et al. 2015), and a facile one-pot method (Shirahama et al. 2016), later refined
(R38, R39).

**Conditions (one-pot, optimised).** Low MAA-to-gelatin feed ratio of 0.1 mL/g, 0.25 M
carbonate–bicarbonate buffer at initial pH 9, gelatin at 10–20% w/v, 50 °C — balancing
deprotonation of amino groups against MAA hydrolysis, giving near-complete substitution with
a single one-pot MAA addition (R39). Reaction time matters: Van Den Bulcke used 1 h and
subsequent studies 1–3 h, but with 0.1 M and 0.25 M CB buffer a sharp pH drop to 6.6 was
observed early, indicating the reaction largely completes quickly (R39).

**Feed ratio → target DS.** Molar feed ratios of MAA to gelatin of 1.859:1 and 0.628:1 were
used to target DS of 100% and 60% respectively in a carbonate–bicarbonate one-pot system
across five batches (R40).

**Verification.** DS by `1H-NMR`: integrate the lysine methylene signal (2.87–3.00 ppm) in
GelMA against unmodified gelatin, using phenylalanine (7.1–7.4 ppm) as internal reference;
one report gives DS ≈ 57% by this method (R29). Reported DS generally ranges 30–100% (R41).
Because `1H-NMR` requires the precise amine content to be known, a colourimetric amine assay
(TNBS) is used alongside it (R39, R41). **Record which assay produced the number** — the
spec makes `assay` mandatory on `<b:verification>` for this reason.

**Other grade attributes to record.** Gelatin source and type (Type A porcine skin vs
Type B bovine skin) and bloom number materially change the product and its rheology
(R38, R42); molecular weight is frequently overlooked despite strongly affecting
printability and biological performance (R43). Sterility route: sterile filtration through
0.22 µm followed by lyophilisation is one documented approach (R29). Storage: dissolved
GelMA kept dark at 4 °C to avoid loss of functionality (R29).

**Yield.** Record it. If your process does not measure isolated yield, emit
`<b:yield provenance="estimated" measured="">` rather than omitting the element — see
Rule S3. I have not filled in a yield figure here because I did not find one reported in
the sources consulted, and inventing one would defeat the purpose of the format.

### Photoinitiator identity block

| Field | Value | Source |
|---|---|---|
| `name` | LAP | |
| `casrn` | 85073-19-4 | R44 |
| `iupac` | lithium phenyl-2,4,6-trimethylbenzoylphosphinate | R44 |
| `formula` | C16H16LiO3P | R44 |

Relevant `<b:hazard>`/`note` content: LAP generates free radicals that are potentially
cytotoxic; toxicity assessment is only meaningful *with light exposure*, since the radicals
are highly reactive and short-lived. In one study, 10 min at 9.6 mW/cm² of 405 nm LED light
fully crosslinked 10 wt% GelMA with >3.4 mmol/L LAP, and those conditions were cytotoxic to
M-1 mouse kidney collecting-duct cells while not mutagenic in bacterial reverse-mutation
assays (R45). Record the light condition alongside the concentration — a photoinitiator
concentration on its own does not describe an exposure.

Alternative initiator systems to record with the same rigour: Irgacure 2959,
ruthenium(II)/persulfate, eosin Y, riboflavin (R46).

---

## 8. Biological record

Driven by GCCP 2.0 (R14) and the cell-line reporting literature (R47, R48).

**Required fields** (`<b:cellpopulation>`):

- `kind` — line / primary / iPSC-derived / ESC-derived / organoid / spheroid / co-culture
- `rrid` — Cellosaurus accession, mandatory for `kind="line"`. Misidentification and
  cross-contamination are pervasive and long-documented; naming a line is not identifying it (R47, R48)
- STR authentication result and date, for lines
- **mycoplasma test, always** — contamination may remain undetectable without a specific
  test yet still affects data (R14)
- `antibiotics` — explicitly, including `none`. GCCP 2.0 treats routine antibiotic use as
  something to avoid except in well-justified cases (protecting rare/unique tissue,
  disinfecting heavily contaminated primary or organ culture, selecting recombinant clones),
  because it masks contamination; adequate aseptic technique should make it unnecessary (R14)
- `passage_at_print`
- medium, basal medium, serum % **and serum lot**
- substrate / matrix: Matrigel, vitronectin, fibronectin, laminin, collagen and similar
  extracts are a recorded variable, not a background detail (R14)
- atmosphere: CO₂ **and O₂**. Record 21% explicitly rather than leaving normoxia implicit
- `cell_density` at print, with counting method and replicate count

**Post-print biology** goes in `<b:result>` with an `acceptance` criterion:
`cell_viability_post_print` (F3659 addresses post-printing viability measures, R1),
proliferation, protein synthesis, differentiation markers, and — for multi-week culture —
the timepoint. Run viability for a minimum multi-week period alongside proliferation and
protein-synthesis assays (R4).

Two published anchors for what "good" looks like in context: >90% viability at 30 s
volumetric print of 5% GelMA / 0.05% LAP with hMSCs (R30); 99.7% post-print viability for
C2C12 myoblasts in FRESH-printed constructs with active proliferation over seven days (R12).
Both are reported *with* their full process context — which is the point.

---

## 9. Cross-cutting: what almost every dossier omits

These are all `SHOULD` in the spec because their absence is the usual reason a package
cannot be reproduced:

1. **Temperature of rheological measurement.** Mandatory in this spec (Rule I2).
2. **Ambient temperature and humidity** for EHD modalities (Rule P2).
3. **Time out of incubator** — cumulative excursion during printing.
4. **Sterilisation route and its effect on mechanics** — evaluate sterilisation and storage
   effects on mechanical properties (R4).
5. **Serum lot.** Serum is the least controlled reagent in most cell work.
6. **Which stress/strain convention** was used in mechanical testing — global vs local
   strain, Cauchy vs Piola–Kirchhoff stress, and the strain at which a secant modulus was
   taken (R4).
7. **Calibration date** of the machine and of the radiometer.
8. **The negative result.** `<b:result>` with a failing `acceptance` is valid and valuable.
