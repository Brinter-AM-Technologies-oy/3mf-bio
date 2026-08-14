# Calibration Dossier — what to test, per modality

Companion to `spec/3MF Bio Extension.md` Chapter 9. Reference keys (R…, K…) resolve in
`dossier/References.md`.

**The distinction this file rests on.** A *parameter* is what you set. A *calibration test*
is the independent measurement that tells you the setting means what you think it means. A
package can be full of exact parameters and still be unreproducible, because the numbers
were never tied to a machine whose behaviour was checked.

`<b:calibration>` therefore records a dated event with an operator, a per-test acceptance
criterion, and a pass/fail outcome — not a machine attribute. Rule K1 enforces the date;
K3 forbids marking a test `pass` without a measured value.

---

## 0. The standards baseline for calibration

| Standard | What it gives | Use here |
|---|---|---|
| **ISO/ASTM 52902:2023** | Test artefacts — geometric capability assessment of AM systems. Supersedes the 2019 edition. Describes a suite of benchmark test geometries and prescribes the quantities and qualities to be measured, without dictating measurement methods. Explicitly serves **two** purposes: capability assessment **and calibration** of the AM system (K1) | The `geometric` test kind. Bind the artefact to a real printed `<object>` via `artifactobjectid` |
| **ASTM F2971** | Reporting data for test specimens produced by AM. 52902 explicitly defers specimen procedure and machine settings to it (K1) | What a `<b:calibration>` record is for |
| **ISO/ASTM 52900:2021** | Fundamentals and vocabulary. Seven process categories with abbreviations, and a normative Annex A for identifying processes within a category (K2) | The `iso52900` attribute on `<b:process>` |
| **ASTM F3659-24** | Standard Guide for Bioinks. Pre-print, print and post-print considerations including post-printing viability (R1) | The `biological` test kind |

52902 does not dictate measurement methods, and does not cover bioprinting-specific
behaviour at all. Everything in §2–§8 below is drawn from the biofabrication literature
instead, and is labelled with its source.

---

## 1. Calibration test kinds

`<b:test kind=…>` is a closed vocabulary:

| Kind | Answers |
|---|---|
| `geometric` | Does the machine put material where the file says? |
| `dosimetric` | Is the delivered energy what the setting claims? |
| `optical` | Is the light what the setting claims, at the build plane? |
| `flow` | Is the delivered volume what the setting claims? |
| `rheological` | Is the ink in the state the process assumes? |
| `printability` | Does this ink, on this machine, produce the intended shape? |
| `thermal` | Is the temperature at the material what the controller reports? |
| `biological` | Do cells survive the calibrated process? |
| `sterility` | Is the fluid path clean? |

**Why `printability` is separate from `geometric`.** 52902's artefacts assess the *machine*.
A bioink is a co-determinant of fidelity, so the same machine passing 52902 can still print
an unusable construct with a different ink. Printability tests are ink×machine, and must be
repeated per formulation.

---

## 2. Extrusion (`extrusion-pneumatic` / `-piston` / `-screw`)

| `name` | kind | Metric | Notes and source |
|---|---|---|---|
| **`filament_width`** | printability | µm | Measured strand width vs nozzle inner diameter at the intended pressure and speed. The base measurement everything else calibrates against. *Aliases: `strand_width`, `line_width`* |
| **`grid_test`** | printability | several, below | Print a lattice and measure the pores. *Aliases: `printability_Pr`, `lattice_test`* |
| **`bridge_test`** | printability | deflection angle | Print filaments spanning pillars at increasing gap. *Aliases: `filament_collapse`, `overhang_test`* |
| **`layer_stacking_test`** | printability | height, wall ratio | Stack until it slumps. *Aliases: `stackability`, `cylinder_test`* |
| `filament_fusion` | printability | fused length / thickness | Print parallel filaments at decreasing separation and measure fused length, filament distance and filament thickness. Higher-entanglement inks show less swelling and less coalescence (K5, K6) |
| `flow_rate_check` | flow | µL/min | Extrude to a tared vessel for a fixed time. Flow rate rises highly non-linearly with pressure for shear-thinning inks, so flow cannot be inferred from pressure (R10) |
| `nozzle_temp_at_tip` | thermal | °C | Controller setpoint vs a probe at the tip. Nozzle and chamber temperature control has been reported to move viability from ~56% to ~90% (R7) |
| `geometric_capability` | geometric | µm | 52902 artefact, printed in the build material (K1) |
| `post_print_viability` | biological | % | Coupon printed in the same run; F3659 addresses post-printing viability (R1) |

### The three shape-fidelity tests, and why they are three

They are not variations on one measurement. Each applies a **different load** to the ink, and
an ink can pass one and fail another. Running only the easy one is the commonest way a
formulation looks printable in a paper and is not printable in a lab.

| Test | Load applied | Fails when |
|---|---|---|
| **Grid test** | none beyond surface tension and gravity on a supported strand | the ink spreads, swells or merges in-plane |
| **Bridge test** | gravity on an *unsupported* span | the ink cannot hold itself over a gap |
| **Layer stacking test** | the **weight of the layers above** | the ink holds one layer and slumps at twenty |

#### `grid_test` — in-plane fidelity

Print a lattice of interconnected pores. One print yields several independent metrics, which
is why the format treats the grid as a test and the numbers as its outputs rather than
conflating them:

| Metric | Meaning |
|---|---|
| `printability_Pr` | Derived from the circularity of the enclosed pore; **Pr = 1** for a perfect square pore, i.e. ideal gelation. Under-gelation gives extrudate swell, filament swelling and rounded pores; over-gelation gives irregular, lumpy filaments and unpredictable pore geometry (K3, K4) |
| `normalized_pore_number` | Printed open pores as a percentage of designed. One alginate/gelatin study reported **98%** for 3% w/v gelatin in 4% alginate, alongside >90% viability at five days (K8) |
| `pore_area` | Absolute pore area against the design |
| `shape_fidelity_index` | Printed dimension as a fraction of the designed dimension. **Indices below 1 indicate filament merging or collapse; an index of 1 indicates high fidelity and optimal layer stacking** (K9) |

#### `bridge_test` — out-of-plane fidelity

Print filaments spanning supports at increasing gap distance and measure the deflection
angle against half-gap distance. A model based on the equilibrium between the gravitational
force on the filament and its resistance to deformation predicts the curve (K5, K6).

Two things worth recording that are usually not:

- **Time.** Collapse is not instantaneous. One study observed overhanging deformation *over
  time*, at two different ambient temperatures, and fitted a model estimating Young's modulus
  and collapse as a function of time (K8). A deflection measured immediately and one measured
  at ten minutes are different numbers. Record which you took.
- **Model disagreement.** In that study the model **overestimated** the deflection angle,
  although the slope of the fitted lines followed the experimental trend (K8). If you report
  a predicted deflection, say so and say by how much it missed.

#### `layer_stacking_test` — the one people skip

The load that collapses a tall construct is **the weight of the layers above it**, and no
single-layer test applies that load. Stacking is treated in the printability literature as
its own evaluation, distinct from filament formation and from planar orientation (K9).

The documented procedure is a **cylinder print to a fixed layer count**, then compare wall
thickness near the base against wall thickness near the top. In one worked example a bioink
was printed through a 400 µm tip to a 100-layer, 2 cm cylinder with a 200 µm target layer
height and 500 µm extrusion width; wall thickness in the lowest five layers showed no
significant difference from the highest five, and height and aspect ratio (20 = 2 cm / 1 mm)
matched the CAD model within 1 mm (K10).

| Metric | Meaning |
|---|---|
| `layers_before_collapse` | Where it stops being printable |
| `max_stable_height` | The same, in length |
| `wall_thickness_ratio` | Base wall thickness ÷ top wall thickness. **1.0 means no spreading under load**; above 1 means the base is squashing |
| `aspect_ratio` | Height ÷ width, against the design |

Report the layer height and extrusion width you used. A stacking result at 200 µm layers does
not transfer to 400 µm layers, and the number is meaningless without them.

**Recommended frequency.** `filament_width`, `grid_test`, `bridge_test` and
`layer_stacking_test` per ink lot — they are ink × machine, so a new formulation invalidates
all four. `flow_rate_check` per session; `geometric_capability` monthly;
`post_print_viability` per build.

### `extrusion-coaxial` additionally

| `name` | kind | Metric | Notes and source |
|---|---|---|---|
| **`core_shell_concentricity`** | geometric | µm | Cross-section a deposited filament; measure core offset from the shell centroid. An eccentric core gives a wall that is thin on one side and will burst under perfusion |
| **`wall_thickness`** | geometric | µm | Wall thickness and lumen diameter respond to core pressure and sheath flow rate (R60) |
| `lumen_patency` | printability | pass/fail | Perfuse the printed lumen and check for leakage and blockage |
| `flow_ratio_check` | flow | — | Verify both supplies independently before printing. Core and shell are separately controlled, so a single flow check is not sufficient (R57) |

Note the frequency: core–shell geometry is `per-session`, because two independent supplies
drift independently.

### `extrusion-embedded` additionally

| `name` | kind | Metric | Notes and source |
|---|---|---|---|
| **`bath_rheology`** | rheological | Pa | Bath yield stress at the printing temperature. The bath behaves as a Bingham plastic when cold and a viscous liquid above ~37 °C; that transition is what holds the filament (R12) |
| `bath_particle_size` | rheological | µm | Sets the resolution floor: minimum perfusable channel must be several particles wide because of random packing and pre-gelation filament diffusion. ~55 µm in original FRESH; coacervation reduced this to ~25 µm, enabling ~20 µm features (R12, R13) |
| `release_completeness` | geometric | % mass | Bath fully melted out without construct damage |

Record `bath_particle_size` and you can predict your resolution floor before printing. Skip
it and the failure looks like a machine problem.

---

## 3. Droplet: `inkjet-piezo`, `inkjet-thermal`, `microvalve`

| `name` | kind | Metric | Notes and source |
|---|---|---|---|
| **`droplet_volume`** | flow | pL | Gravimetric over n drops, or stroboscopic imaging |
| **`droplet_velocity`** | flow | m/s | Stroboscopic. Waveform voltage, rise/dwell/fall/echo times, nozzle diameter and air gap all significantly affect droplet velocity and volume (R17) |
| `satellite_check` | printability | count | Satellite-drop onset bounds the usable window; the stable regime has been described jointly in (Z, We) space with an upper We bound set by satellite onset (R19) |
| `Z_number_check` | rheological | dimensionless | Compute Z = 1/Oh from density, viscosity and surface tension **measured at the jetting temperature**. A Z computed from a vendor sheet at 25 °C and applied at 37 °C is a common silent error |
| `nozzle_dropout` | flow | nozzles firing / total | Multi-nozzle heads only |
| `cells_per_droplet` | biological | count | Cell distribution within droplets is highly non-uniform and propagates into the construct (R18) |
| `post_print_viability` | biological | % | Thermal DOD collapses a vapour bubble to eject, which can damage cells; piezo is generally preferred (R18) |

---

## 4. `laser-lift`

| `name` | kind | Metric | Notes and source |
|---|---|---|---|
| **`fluence_threshold`** | dosimetric | mJ/cm² | Find the boundaries of the three regimes with increasing fluence: subthreshold, jetting, plume (R22). Only the jetting regime is usable |
| **`spot_size`** | optical | µm | Beam profiler or burn pattern |
| `droplet_size_vs_fluence` | dosimetric | µm per mJ/cm² | In the jetting regime, droplet size and volume rose approximately linearly with fluence (R23) |
| `donor_film_thickness` | geometric | µm | **Re-measure within the session.** Under ambient conditions (20 °C, 50% RH) the hydrogel donor layer thinned at ~8 µm/min by drying, so transfer parameters drift as you print (R23) |
| `ambient_temp_stability` | thermal | °C | Holding ±2 °C was sufficient to neglect temperature-induced viscosity change (R23) |
| `receiver_cushion_check` | biological | % activity | Increasing a buffering coating from 20 to 40 µm raised printed-cell activity from ~50% to >95%; with no buffering layer, ~5% (R21) |

The donor-thinning rate is the reason LIFT calibration is `per-session` and arguably
per-slide, not monthly.

---

## 5. Vat: `vat-sla`, `vat-dlp`, `vat-2pp`

| `name` | kind | Metric | Notes and source |
|---|---|---|---|
| **`working_curve`** | dosimetric | Dp (µm), Ec (mJ/cm²) | Cure depth vs exposure, fitted per Jacobs with Beer–Lambert attenuation (R25, R52). **The single most transferable artifact in a vat dossier** — it lets another lab hit your geometry with a different lamp. Publish the curve, not just your exposure time |
| **`irradiance_uniformity`** | optical | % across build area | Radiometer at the build plane at several positions, not the vendor figure |
| `cure_depth_check` | dosimetric | µm | Cure depth exceeding layer thickness over-crosslinks the out-of-focus plane and destroys axial accuracy; photoabsorbers reduce and tighten it (R27) |
| `wavelength_match` | optical | nm | Photoinitiator absorption vs projector output. Mismatch between wide ink absorption bands and projector wavelength degrades printability; LAP absorbs around 350–400 nm and at 400 nm (R26, R44) |
| `xy_resolution` | geometric | µm | Resolution artefact at the build plane |
| `geometric_capability` | geometric | µm | 52902 artefact (K1) |

For `vat-2pp`, substitute `voxel_size` (measured voxel dimensions vs scan speed and average
power) for `working_curve`.

---

## 6. `volumetric-tomographic`

| `name` | kind | Metric | Notes and source |
|---|---|---|---|
| **`dose_threshold`** | dosimetric | mJ/cm² | Per resin lot. Irradiate spots into a cuvette of solidified resin over varying exposure time and average power; exposure of 2–64 s at varying power is the documented procedure (R29) |
| **`optical_power_at_vial`** | optical | mW | Power meter at the vial position at the printing setpoint |
| `rotation_sync` | geometric | ° | Projection index vs actual vial angle |
| `resin_transmittance` | optical | OD | At the printing wavelength. **Cell-density dependent**: scattering blurs projections and raises dose adjacent to but outside the target, causing off-target polymerisation, and the scattering mean free path is inversely related to cell density (R31) |
| `refractive_index_match` | optical | n | RI matching of intracellular components reduces scattering (R31) |
| `geometric_capability` | geometric | µm | 52902 artefact printed in the build resin |

**The trap.** A dose calibration performed on cell-free resin does not transfer to the same
resin at 8 × 10⁶ cells/mL. Record the cell density at which the dose test was run, or the
calibration is describing a different material.

---

## 7. `melt-electrowriting` / `electrospinning`

| `name` | kind | Metric | Notes and source |
|---|---|---|---|
| **`critical_translation_speed`** | flow | mm/min | **Must be measured, never cited** (spec Rule P1). Straight fibres are written when collector speed exceeds CTS, the speed matching jet velocity (R35). One published setup reported CTS of 180–230 mm/min varying daily with polymer and environment, re-measured each session after ≥5 min of jet stabilisation, with translation then set at 1.25 × CTS (R36) |
| **`fibre_diameter`** | geometric | µm | The output, not an input. Melt flow rate was the most influential of six factors; applied voltage the least (R34) |
| `jet_stability_time` | flow | min | Time to stable jetting before the session begins; ≥5 min in R36 |
| `ambient_log` | thermal | °C, %RH | 19–22 °C and 35–42% RH logged in R36. Required by spec Rule P2 |
| `placement_accuracy` | geometric | µm | Highest accuracy just above CTS (R37) |

MEW is the modality where "same parameters, different result" is most common. Published
fibre diameters span 8–138 µm across a systematic sweep (R37). None of those numbers
transfer between labs. The *practice* does: measure CTS, print at a stated multiple of it,
log ambient.

---

## 8. Cross-cutting

Run regardless of modality, before a build is called reproducible:

1. **`post_print_viability`** — on a coupon from the same build, bound via
   `b:regionrole="test-coupon"`, so the QC is traceable to the run that produced it.
2. **`sterility`** — fluid path and chamber.
3. **`geometric_capability`** — 52902 artefact, in the build material, not in a
   calibration plastic.
4. **Radiometer / power meter / thermocouple calibration dates** — a calibration performed
   with an uncalibrated instrument measures nothing. Record the instrument's own
   calibration date in `method`.

---

## 9. What this dossier deliberately does not say

No acceptance *thresholds* are asserted here. A Pr window, a viability floor, a dimensional
tolerance — all are application-specific, and asserting a number would be exactly the
invention this format exists to prevent. `acceptance` is a required attribute on
`<b:test>` precisely so that each laboratory states its own and is held to it.

The one exception is structural: Rule K3 forbids marking a test `pass` without a measured
value, whatever the threshold.
