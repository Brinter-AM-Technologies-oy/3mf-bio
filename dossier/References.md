# References

Every claim in `Parameter-Dossier.md` and every normative rationale in the spec traces to
an entry here. Nothing in this dossier is asserted from memory: if a number is not
attributable to an entry below, it is either marked `TODO-VERIFY` or absent.

**Grades** (per spec §3): A consensus standard / systematic review · B peer-reviewed
primary, parameters explicitly reported · C peer-reviewed, parameters inferred ·
D preprint / abstract · E vendor or aggregator documentation · F internal.

**Verification note.** DOIs below were observed in the retrieved records. Where a DOI was
not observed, a stable URL or PMC identifier is given instead rather than a reconstructed
DOI. Two entries (R19, R44) carry explicit caveats about what could not be confirmed.

---

## Standards and definitions

**R1** — ASTM F3659-24, *Standard Guide for Bioinks Used in Bioprinting*. ASTM
International, 2024. 20 pp. Committee F04.42. — Grade A.
Supports: the standards baseline; scope covering bioinks and biomaterial inks with or
without encapsulated cells; the acknowledgement of electrospinning, electrospray,
droplet/inkjet and laser-assisted modalities alongside its extrusion focus; pre-print,
print and post-print stabilisation considerations; sterility, cytocompatibility and
post-printing viability assessment. Cross-references Guide F2150, Guide F2027 and the
ISO 10993 series.

**R2** — Groll J, Burdick JA, Cho D-W, Derby B, Gelinsky M, Heilshorn SC, Jüngst T, Malda J,
Mironov VA, Nakayama K, Ovsianikov A, Sun W, Takeuchi S, Yoo JJ, Woodfield TBF.
*A definition of bioinks and their distinction from biomaterial inks.* Biofabrication
2019;11(1):013001. DOI: 10.1088/1758-5090/aaec52 — Grade A.
Supports: the `class` distinction in `<b:bioink>`. A bioink is defined as a formulation of
cells suitable for processing by an automated biofabrication technology, which may also
contain biologically active components and biomaterials; a biomaterial ink is a biomaterial
used for printing where cell contact occurs post-fabrication.

**R4** — *Guidelines for standardization of bioprinting: a systematic study of process
parameters and their effect on bioprinted structures.* Bioinspired, Biomimetic and
Nanobiomaterials / De Gruyter, 2016. DOI: 10.1515/bnm-2016-0004 — Grade B.
Supports: line-dimension optimisation via feedrate, pressure, nozzle dimension and printing
height; visual determination of line spacing to overlap; percentage line overlap for
reproducible mechanics; tensile testing per ISO/ASTM with explicit reporting of the
stress/strain convention and secant-modulus strain; evaluation of sterilisation and storage
effects on mechanics; multi-week viability plus proliferation and protein-synthesis assays.

**R6** — Perin et al. *Bioprinted Constructs in the Regulatory Landscape: Current State and
Future Perspectives.* Advanced Materials, 2026. DOI: 10.1002/adma.202504037 — Grade B.
Supports: the observation that regulation of novel biofabrication techniques is still
developing while ISO/ASTM standards exist for common hydrogels. Context for the
regulatory annex deferred to v0.2.

**R14** — *Guidance document on Good Cell and Tissue Culture Practice 2.0 (GCCP 2.0).*
ALTEX, 2021/2022. PubMed: 34882777 — Grade A.
Supports: the six principles (characterisation and maintenance of essential
characteristics; quality management; documentation and reporting; safety; education and
training; ethics); mycoplasma contamination remaining undetectable without a specific test
while still affecting data; the position that routine antibiotic and antifungal use should
be avoided except in well-justified cases (rare/unique tissue, heavily contaminated primary
or organ culture, selection of recombinant clones) and that aseptic technique should make
it unnecessary; matrix/substrate (Matrigel, vitronectin, fibronectin, laminin, collagens)
as a recorded culture variable.

**R47** — *Research reporting guidelines for cell lines: more than just a recommendation.*
Annals of Translational Medicine, 2023. PMC: PMC10777224 — Grade B.
Supports: the persistence of misidentified and cross-contaminated lines; the case for
minimal reporting requirements on continuous cell lines; the failure of peer review alone
to catch falsely designated lines.

**R48** — ATCC, *Cell Line Authentication Test Recommendations.* atcc.org — Grade E.
Supports: STR profiling as the identity assay for human lines; mycoplasma testing;
providing verification benchmarks in publication.

**R50** — 3MF Consortium specifications: Core, Materials and Properties, Production, Beam
Lattice, Slice, Secure Content, Volumetric (pre-release); machine toolpath extension under
consortium review. github.com/3MFConsortium — Grade A (de facto industry spec).
Supports: the package model this extension attaches to, and the statement that none of the
existing extensions carry biological or process-biological semantics.

**R51** — 3MF Volumetric Extension specification. github.com/3MFConsortium/spec_volumetric
— Grade A.
Supports: `<b:field>` binding; the requirement/recommendation model this extension mirrors
(a producer using level sets must mark the extension required; consumers must interpret the
data as exact).

---

## Extrusion

**R3** — *Key parameters and applications of extrusion-based bioprinting.* Bioprinting
(Elsevier), 2021. sciencedirect.com/science/article/abs/pii/S2405886621000294 — Grade B.
Supports: existing ASTM scaffold standards cover porosity, permeability, pore size and
uniformity, viscoelasticity, stiffness, swelling ratio, polymerisation kinetics, viability,
morphology, differentiation, proliferation and distribution — while extrusion bioprinting
imposes printability considerations for which no general guideline yet exists.

**R7** — *Printability and Cell Viability in Extrusion-Based Bioprinting from Experimental,
Computational, and Machine Learning Views.* PMC: PMC9036289 — Grade B.
Supports: smaller nozzle diameter → higher velocity gradient → higher shear → higher cell
damage; tapered vs cylindrical needle flow and pressure behaviour; a report of viability in
cylindrical nozzles an order of magnitude below conical; nozzle/chamber temperature control
moving viability from 55.52% to 90%; long print duration reducing post-extrusion viability.

**R8** — *An overview of extrusion-based bioprinting with a focus on induced shear stress
and its effect on cell viability.* Bioprinting, 2020.
sciencedirect.com/science/article/abs/pii/S2405886620300208 — Grade B.
Supports: maximum velocity gradient and maximum shear stress occurring near the nozzle wall.

**R9** — *Cell viability in extrusion bioprinting: the impact of process parameters, bioink
rheology, and cell mechanics.* Rheologica Acta, 2025. DOI: 10.1007/s00397-025-01504-z
— Grade B.
Supports: shear stress zero at nozzle centre, maximal at wall; cells nearer the wall more
likely to be damaged; viability decreasing with increasing flow rate, increasing bioink
viscosity, increasing nozzle length or decreasing nozzle radius, mediated by shear stress
or residence time; power-law and Herschel–Bulkley fits as the rheological inputs.

**R10** — *Flow and hydrodynamic shear stress inside a printing needle during
biofabrication.* PLOS ONE, 2020. DOI: 10.1371/journal.pone.0236371 — Grade B.
Supports: the linear shear-stress distribution of Newtonian pipe flow also holding for
shear-thinning fluids; the highly non-linear rise of flow rate with pressure that makes
optimal parameters hard to predict; calculated shear stress as a proxy for mechanical load
correlated with post-printing viability.

**R11** — *Computational Fluid Dynamics Assessment of the Effect of Bioprinting Parameters
in Extrusion Bioprinting.* International Journal of Bioprinting, 2022.
DOI: 10.18063/ijb.v8i2.545 — Grade B.
Supports: wall shear stress as the critical determinant of viability and not directly
measurable; the parameter space swept (conical / tapered-conical / cylindrical nozzles,
0.1–0.5 mm diameter, 0.025–0.25 MPa inlet pressure, non-Newtonian power law with constants
0.0863–0.5050).

---

## Extrusion — shear modelling and coaxial

**R53** — *Flow and hydrodynamic shear stress inside a printing needle during biofabrication*
(synthesis and citing literature). DOI: 10.1371/journal.pone.0236371 and associated review
coverage — Grade B.
Supports: the wall shear relation with maximum at the wall decreasing toward the centre, in
terms of pressure drop, nozzle radius and nozzle length; the Herschel–Bulkley law converting
pressure and nozzle geometry to shear-rate histories; reported viability near 91% at shear
around 5–10 kPa falling toward ~76% above 10 kPa; operating envelopes linking pressure and
shear history to survival targets between 76% and 96%.
**Caveat:** the 5–10 kPa and 10 kPa figures are reported in a synthesis rather than a single
primary measurement, and are ink- and cell-specific. They are context, not thresholds.

**R54** — *Biomaterial flow modeling beyond the nozzle: a rheological perspective.* Applied
Physics Letters, 2026. pubs.aip.org/aip/apl/article/128/25/252702 — Grade B.
Supports: the power-law model's inability to represent yield stress and its unphysical
behaviour near zero and at extreme shear rates; Herschel–Bulkley for combined yield stress
and shear-thinning or shear-thickening; neither model capturing thixotropy, requiring a
structural-parameter formulation.

**R55** — *Exploiting nozzle geometry to predict resolution in extrusion-based bioprinting:
mathematical modelling of a power-law fluid.* Royal Society Open Science, 2025.
royalsocietypublishing.org/rsos/article/12/11/250504 — Grade B.
Supports: power-law sufficiency for parameter prediction where only higher shear rates
matter, versus Herschel–Bulkley for shape-fidelity optimisation; the caveat that viscoplastic
materials can slide below the critical shear rate, so the no-slip wall condition may need
relaxing.

**R56** — *Bridging rheology and bioprinting: a predictive framework for safe and precise
extrusion bioprinting parameters.* Bioprinting, 2026.
sciencedirect.com/science/article/pii/S2405886626000175 — Grade B.
Supports: the printability window bounded by a minimum pressure to initiate flow and a
maximum for continuous extrusion; the wall shear stress equation in terms of pressure, nozzle
length and radius; smaller nozzles requiring higher pressure; calculated 30–80 kPa versus
experimental 35–70 kPa for alginate/CaCl₂ through a 0.25 mm plastic conical nozzle, with
near-zero error for a 0.41 mm tapered nozzle.

**R57** — *3D coaxial bioprinting: process mechanisms, bioinks and applications.* Progress in
Biomedical Engineering, 2022. DOI: 10.1088/2516-1091/ac631c — Grade B.
Supports: an inner nozzle diameter of 210 µm reported for a HUVEC-laden vascular network as a
potential lower limit; core and shell independently controlled by separate pneumatic
processes allowing different flow rates; larger shell flow rates giving thicker fibres; the
core–shell configuration for hollow tubes, where a stable shell is crosslinked around a
liquid core that is removed post-processing.

**R58** — *Automated devices, systems, and methods for the fabrication of tissue*
(US 9,315,043) — Grade E.
Supports: a documented coaxial nozzle specification — core bore 514 µm, mantle bore 819 µm,
outer diameter 3200 µm; calcium chloride extruded through the centre sufficing to crosslink
an alginate–gelatin outer shell; a resulting cell-laden hollow tube of inner diameter 820 µm
and outer 2300 µm.

**R59** — CELLINK, *Coaxial bioprinting enables more complex biofabricating* — Grade E.
Supports: the point that printability of a multimaterial filament depends on the core-to-shell
ratio and not only the target filament diameter; coaxial co-deposition of two cell-laden
materials in defined layers for co-culture.

**R60** — *A mist-based crosslinking technique for coaxial bioprinting of hollow hydrogel
fibers.* Bioprinting, 2023. sciencedirect.com/science/article/abs/pii/S2405886623000519
— Grade B.
Supports: mist as a core flow providing adequate pressure and sufficient crosslinking to
maintain a tubular shape, eliminating liquid crosslinker and sacrificial inks and requiring
no additional post-processing; core pressure and sheath flow rate as the parameters governing
uniformity, diameter and wall thickness.

**R61** — *Coaxial bioprinting of enzymatically crosslinkable hyaluronic acid-tyramine
bioinks for tissue regeneration.* PMC: PMC11398246 — Grade B.
Supports: the worked parameter set — 1.3% w/v HMW HA-TA with 5.5 U/mL HRP as inner core,
27.5% w/v Pluronic F-127 with 0.1% H₂O₂ as outer shell, 45 kPa core and 80 kPa shell, 300
mm/min print speed, 30 °C bed; near-instantaneous gelation by diffusion of hydrogen peroxide
into the core; seven-day culture of bovine primary chondrocytes and 3T3 fibroblasts.

**R62** — *Process optimization for coaxial extrusion-based bioprinting: a comprehensive
analysis of material behavior, structural precision, and cell viability.* Additive
Manufacturing, 2025. sciencedirect.com/science/article/abs/pii/S2214860425000466 — Grade B.
Supports: power-law analysis of flow inside a coaxial nozzle validated against CFD; feed flow
rates, printing gaps and deposition velocities as the influences on core–shell structure;
evaluation criteria of encapsulated cell viability, print fidelity and precision, core–shell
dimensions, and structural integrity and uniformity.

## Embedded / suspended-bath

**R12** — *Embedded 3D bioprinting — an emerging strategy to fabricate biomimetic and large
vascularized tissue constructs.* Bioactive Materials, 2023. PMC: PMC10618244 — Grade B.
Supports: FRESH origin (Feinberg, CMU) and commercialisation; support bath of gelatin
microparticles ~55.3 ± 2 µm; FRESH v2.0 with 2% w/v gelatin plus 0.25% w/v Pluronic and
0.1% w/v gum arabic, ~25 µm particles, ~20 µm resolution; pH-driven collagen gelation at
pH 7.4; C2C12 myoblast viability 99.7% post-print with proliferation over 7 days; bath
behaving as a Bingham plastic at 4 °C.

**R13** — *3D bioprinting of collagen-based high-resolution internally perfusable scaffolds
for engineering fully biologic tissue systems.* Science Advances, 2025.
DOI: 10.1126/sciadv.adu5905 — Grade B.
Supports: resolution limited by average bath microparticle size (~25 µm), not by printer
(200 nm) or needle (down to 20 µm); minimum perfusable channel several particles wide due
to random packing and pre-gelation filament diffusion; coacervation tunable to ~10 µm
particles; Bingham-plastic bath rheology performing filament immobilisation and gelation
triggering.

---

## Droplet / inkjet

**R15** — *Drop-on-Demand Inkjets* (Elsevier ScienceDirect Topics reference entry) — Grade E.
Supports: Z as the inverse Ohnesorge number identifying ink printability, with a stated
stable-drop window of Z between 1 and 10.
**Caveat:** this is an aggregator entry, and the numeric window is source-dependent — see
R19 for a jointly bounded (Z, We) formulation. Record which convention you used.

**R16** — *Inkjet printing of mammalian cells — theory and applications.* Bioprinting, 2021.
sciencedirect.com/science/article/pii/S2405886621000300 — Grade B.
Supports: a 32-setting study across voltage 20–150 V, pulse width 20–200 µs and droplet
frequency 50–1000 Hz; controlled cell number per droplet.

**R17** — *Predictive Modeling of Droplet Formation Processes in Inkjet-Based Bioprinting.*
ASME (author copy: mae.ucf.edu) — Grade B.
Supports: the process-parameter set — excitation waveform (voltage, rise, dwell, fall, echo
times, frequency), nozzle speed, nozzle diameter, air gap — and its significant effect on
droplet velocity and volume.

**R18** — *Effects of printing conditions on cell distribution within microspheres during
inkjet-based bioprinting.* AIP Advances 9:095055, 2019.
pubs.aip.org/aip/adv/article/9/9/095055 — Grade B.
Supports: thermal DOD mechanism (microheater vaporises fluid, bubble collapse ejects drop)
and its risk to cells; piezo preferred for cells; highly non-uniform cell distribution
within droplets propagating into constructs.

**R19** — *Control of Droplet Formation in Inkjet Printing Using Ohnesorge Number* — Grade C.
Supports: the (Z, We_jet) phase diagram with stable generation bounded by a parallelogram,
2 < We_jet < 25; lower bound where capillary forces prevent ejection, upper bound at
satellite-drop onset; for Z < 50 the critical We_jet rises as Z falls due to viscous
dissipation.
**Caveat:** retrieved via a secondary index; full author/venue attribution was not confirmed
in the sources consulted. Verify before citing formally.

**R20** — *Physicochemical parameters that underlie inkjet printing for medical
applications.* PMC: PMC10903396 — Grade B.
Supports: Reynolds, Weber and Ohnesorge numbers as the printability descriptors; for
Oh ≈ 0.1, Weber number regulating ejection into three regimes (suspended/oscillating,
ejected with negative tip velocity, and proper DOD formation with positive tip velocity).

---

## Laser-induced forward transfer

**R21** — *Laser-induced forward transfer based laser bioprinting in biomedical
applications.* PMC: PMC10475545 — Grade B.
Supports: pulse energy, beam size and fluence as key parameters; cell-laden ink typically
requiring higher laser energy with slower jets and smaller spots than cell-free ink; cell
aggregation causing non-straight jets and non-straight trajectories; receiver coating
thickness 20 → 40 µm raising printed-cell activity from ~50% to >95%, versus ~5% with no
buffering substance.

**R22** — *Laser-Induced Forward Transfer on Regenerative Medicine Applications.* Biomedical
Materials & Devices, 2022. DOI: 10.1007/s44174-022-00040-1 — Grade B.
Supports: the six critical parameters (laser fluence, laser spot size, absorbing-layer
thickness, biomaterial physical properties, biomaterial thickness, donor–receiver distance);
three jet regimes with increasing fluence — subthreshold, jetting, plume; viscosity as
co-determinant (high viscosity needs more fluence, low viscosity splashes); the need for a
shock-absorbing receiver substrate, and alginate raising viscosity to improve viability.

**R23** — *Laser-induced Forward Transfer Hydrogel Printing: A Defined Route for Highly
Controlled Process.* International Journal of Bioprinting, 2020. DOI: 10.18063/ijb.v6i3.271
— Grade B.
Supports: near-linear increase of transferred droplet size and volume with laser fluence in
the optimal single-droplet jetting regime; temperature stability of ±2 °C sufficient to
neglect temperature-induced viscosity change; hydrogel donor layer thinning at ~8 µm/min by
drying at 20 °C and 50% RH, causing temporal drift of transfer parameters; the tunable set
being pulse energy, spot size, donor–acceptor distance and donor hydrogel thickness.

**R24** — *Blister-Actuated LIFT Printing for Multiparametric Functionalization of
Paper-Like Biosensors.* PMC: PMC6523816 — Grade B.
Supports: the BA-LIFT variant with an intermediate polyimide layer partially ablated by the
pulse, gaseous ablation products forming blisters that eject droplets from the subjacent
viscous layer.

---

## Vat photopolymerisation

**R25** — *Theoretical prediction and experimental validation of the digital light
processing (DLP) working curve for photocurable materials.* Additive Manufacturing, 2020.
sciencedirect.com/science/article/abs/pii/S2214860420310885 — Grade B.
Supports: the Jacobs working curve as the relationship between absorbed light energy and
cured thickness, and its role in obtaining accurate parameters for a given photocurable
material.

**R52** — *High-precision digital light processing (DLP) printing of microstructures for
microfluidics applications based on a machine learning approach.* Virtual and Physical
Prototyping, 2024. DOI: 10.1080/17452759.2024.2318774 — Grade B.
Supports: the Jacobs working-curve formulation in terms of light intensity and exposure
time, penetration depth and critical exposure, with light penetration following
Beer–Lambert.

**R26** — *Improving Printability of Digital-Light-Processing 3D Bioprinting via
Photoabsorber Pigment Adjustment.* PMC: PMC9143265 — Grade B.
Supports: LAP absorbing UV and blue light around 350–400 nm; UV range negatively affecting
cell behaviour and generating excess heat; mismatch between wide bioink absorption bands
and the projector's wavelength degrading printability; photorheology as a quantitative route
to exposure-time optimisation.

**R27** — *Stereolithography apparatus and digital light processing-based 3D bioprinting for
tissue fabrication.* iScience, 2023.
sciencedirect.com/science/article/pii/S2589004223001165 — Grade B.
Supports: cure depth / light-penetration depth definition and its effect on vertical
resolution; over-crosslinking of the out-of-focus plane when cure depth exceeds layer
thickness; photoabsorbers reducing and tightly controlling cure depth; UV absorbers
(benzotriazole derivatives, brilliant blue, quinoline yellow) and visible-light food dyes
(tartrazine, curcumin, anthocyanin, acid red, phenol red).

**R28** — *Molecularly cleavable bioinks facilitate high-performance digital light
processing-based bioprinting of functional volumetric soft tissues.* Nature Communications,
2022. DOI: 10.1038/s41467-022-31002-2 — Grade B.
Supports: photoabsorber use to attenuate excess light and tune polymerisation kinetics for
a target layer thickness; Ponceau 4R selected for a visible-light system on absorbance-range
grounds; the working curve as a rapid estimator of printing settings.

Additional DLP context (not separately numbered): a top-down multi-material DLP study
reporting 30% w/v PEGDA with 0.1% w/v LAP and 0.05% w/v tartrazine at 21.5 mW/cm²,
5 s exposure and 100 µm layers — Biofabrication, DOI: 10.1088/1758-5090/ae55cc.

---

## Volumetric (tomographic)

**R5** — Bernal PN, Delrot P, Loterie D, Li Y, Malda J, Moser C, Levato R. *Volumetric
Bioprinting of Complex Living-Tissue Constructs within Seconds.* Advanced Materials
2019;31:1904209. DOI: 10.1002/adma.201904209 — Grade B.
Supports: optical-tomography-inspired visible-light projection printing; >85% viability;
GelMA in PBS with LAP (gelRESIN); a printed human auricle model at 22.7 s; free-form
structures including trabecular bone models and meniscal grafts.

**R29** — Gehlen J et al. *Tomographic Volumetric Bioprinting of Heterocellular Bone-like
Tissues in Seconds.* bioRxiv preprint, DOI: 10.1101/2021.11.14.468504 — Grade D
(preprint of R30).
Supports: GelMA DS ≈ 57% by ¹H-NMR (Bruker 400 MHz, D₂O; lysine methylene 2.87–3.00 ppm vs
gelatin, phenylalanine 7.1–7.4 ppm internal reference) with the DS equation; sterile
filtration and lyophilisation through 0.22 µm PTFE; LAP 0.03–0.08% w/v; storage of dissolved
GelMA dark at 4 °C; Readily3D prototype and Tomolite v1.0 with Apparite software; laser dose
tests at λ = 405 nm with exposure 2–64 s at varying average power.

**R30** — Gehlen J et al. *Tomographic volumetric bioprinting of heterocellular bone-like
tissues in seconds.* Acta Biomaterialia, 2022.
sciencedirect.com/science/article/pii/S1742706122003580 — Grade B (published version of R29).
Supports: bioresins screened across GelMA and LAP concentrations for photo-reactivity,
printability and cell compatibility; 5% GelMA with 0.05% LAP identified as optimal for
complex perfusable constructs in ~30 s at >90% viability; soft (<5 kPa) matrix with hMSC and
3D endothelial co-culture.

**R31** — Bernal PN et al. *Volumetric Bioprinting of Organoids and Optically Tuned Hydrogels
to Build Liver-Like Metabolic Biofactories.* Advanced Materials, 2022.
DOI: 10.1002/adma.202110054 — Grade B.
Supports: scattering blurring tomographic projections and raising dose adjacent to but
outside the target volume, causing off-target polymerisation and resolution loss;
scattering mean free path inversely related to cell density; ballistic attenuation limiting
addressable construct size; 5% w/v GelMA with 0.1% w/v LAP carrying HepG2 or human
liver-derived epithelial organoids; refractive-index matching of intracellular components
to reduce scattering.

**R32** — *Volumetric Bioprinting of Bone-like Mineralizing Hydrogel Constructs in the
Presence of High Cell Densities and Mineral Precursors.* bioRxiv, 2025.
DOI: 10.1101/2025.07.03.662947 — Grade D.
Supports: 5% GelMA with 0.1% LAP plus poly-aspartic acid for PILP-induced mineralisation;
pAsp concentration determined by resin optical density at λ = 405 nm; 5% GelMA chosen for
permissive cell spreading.

**R33** — *Volumetric bioprinting of the osteoid niche.* PubMed: 39819878 — Grade B.
Supports: step-growth norbornene-norbornene gelatin with thiolated gelatin (GelNB–NBSH)
outperforming chain-growth GelMA, requiring a photoinitiator concentration three times lower
and more than 50% less light exposure dose, with improved positive and negative resolution;
Li-TPO-L post-curing at 1 vs 10 mg/mL with the lower concentration selected on elasticity
and biocompatibility grounds (>95% with HT1080).

**R43** — Ribezzi D, Zegwaart J-P, Van Gansbeke T, Tejo-Otero A, Florczak S, Aerts J,
Delrot P, Hierholzer A, Fussenegger M, Malda J, Levato R et al. *Multi-material volumetric
bioprinting and plug-and-play suspension bath biofabrication via bioresin molecular weight
tuning and multiwavelength optics.* bioRxiv 2024, DOI: 10.1101/2024.09.21.614231; published
version PMC: PMC11962684 — Grade D/B.
Supports: gelatin and GelMA as de facto standard bioprinting materials on availability,
biocompatibility, RGD content and support for adhesion/proliferation grounds; molecular
weight being mostly overlooked despite strongly shaping bioresin characteristics,
printability and biological performance; 520 nm alignment light chosen away from LAP
excitation to avoid unwanted crosslinking; Embedded extrusion Volumetric Printing (EmVP).

---

## Melt electrowriting / electrospinning

**R34** — *Effects of Six Processing Parameters on the Size of PCL Fibers Prepared by Melt
Electrospinning Writing.* Micromachines 2023;14(7):1437. PMC: PMC10385759 — Grade B.
Supports: an orthogonal design (six factors, three levels) over melt temperature, collector
speed, tip-to-collector distance, melt flow rate, voltage and needle gauge; fibre diameters
10.30–20.02 µm; melt flow rate the most influential factor and voltage the least; melt
temperature, collector velocity, tip-to-collector distance and melt flow rate all
statistically significant.

**R35** — Hrynevich A et al. *Dimension-Based Design of Melt Electrowritten Scaffolds.*
Small, 2018. DOI: 10.1002/smll.201800232 — Grade B.
Supports: the critical translation speed concept — straight fibres are direct-written when
collector speed exceeds the CTS, which corresponds to the velocity of both jet and
collector; applied voltage preventing Rayleigh–Plateau instability; the continuous jetting
state depending on both polymeric and processing parameters.

**R36** — Liashenko I, Hrynevich A, Dalton PD. *Designing Outside the Box: Unlocking the
Geometric Freedom of Melt Electrowriting using Microscale Layer Shifting.* Advanced
Materials, 2020. DOI: 10.1002/adma.202001874 — Grade B.
Supports: MEW flow rates typically 0.5–20 µL/h giving fibre diameters typically 2–50 µm;
a worked parameter set (87 °C, 1.2 bar, 22 G nozzle protruding ~0.7 mm, 3.5 mm collector
distance, +5.75 kV nozzle / −1.5 kV collector) yielding a CTS of 180–230 mm/min that varies
daily with polymer and environment (19–22 °C, 35–42% RH); jet stabilisation >5 min before
each session with CTS re-measured and translation set at 1.25 × CTS.

**R37** — *Effects of scaffold design parameters on the printing accuracy for melt
electrowriting.* (Retrieved via secondary index) — Grade C.
Supports: a systematic sweep of heating temperature 200–220 °C, feeding pressure 1.0–3.0 bar,
accelerating voltage 3.0–7.0 kV and collector distance 3.0–7.0 mm across 23 G / 25 G / 27 G /
30 G spinnerets, giving fibre diameters adjustable from 8 to 138 µm; digital control of
fibre diameter by combining mass flow rate with collector speed without changing applied
voltage; highest placement accuracy when collector speed is maintained slightly above the
critical translation speed; a full spectrum of discrete diameters 2–50 µm from a single
nozzle.

**R49** — *A detailed guide to melt electro-writing for tissue engineering applications.*
Biofabrication, 2025. DOI: 10.1088/1758-5090/adfbc4 — Grade B.
Supports: general MEW process guidance; thermal-processing-window considerations for
polymers of differing melting point and for blends; the bridging/deposition failure mode at
very small pore sizes; reported high-resolution parameter sets.

---

## GelMA and photoinitiators

**R38** — *GelMA synthesis and sources comparison for 3D multimaterial bioprinting.*
Frontiers in Bioengineering and Biotechnology, 2024. DOI: 10.3389/fbioe.2024.1383010
— Grade B.
Supports: the three route families (Van Den Bulcke conventional, sequential, one-pot) and
their comparison; gelatin source effects (Type A porcine skin vs Type B bovine skin);
pre-filtration step; degree-of-functionalisation effects on rheology.

**R39** — Shirahama H, Lee BH, Tan LP, Cho N-J. *Precise Tuning of Facile One-Pot Gelatin
Methacryloyl (GelMA) Synthesis.* Scientific Reports 2016;6:31036. DOI: 10.1038/srep31036
— Grade B.
Supports: systematic examination of CB buffer molarity, initial pH, MAA concentration,
gelatin concentration, reaction temperature and reaction time; optimal conditions of
0.1 mL/g MAA-to-gelatin feed ratio, 0.25 M CB buffer at pH 9, 10–20% gelatin, 50 °C, giving
near-complete substitution in one pot; DS by TNBS assay and ¹H-NMR peak assignments
(acrylic protons of methacrylamide grafts on lysine and hydroxylysine, methylene protons of
unreacted lysine, methyl protons of the graft); Van Den Bulcke's 1 h reaction time and
subsequent 1–3 h use; the sharp pH drop to 6.6 early in the reaction.

**R40** — *Gelatin methacryloyl and its hydrogels with an exceptional degree of
controllability and batch-to-batch consistency.* Scientific Reports, 2019.
DOI: 10.1038/s41598-019-42186-x — Grade B.
Supports: molar MAA-to-gelatin feed ratios of 1.859:1 (target DS 100%) and 0.628:1 (target
DS 60%) in a carbonate–bicarbonate one-pot system across five batches; assessment by degree
of methacryloylation, secondary structure, enzymatic degradation, mechanical properties and
cell viability; the proposal that these methods serve as a QC guideline extensible to other
amino/hydroxyl-bearing biopolymers.

**R41** — *An insight into synthesis, properties and applications of gelatin methacryloyl
hydrogel for 3D bioprinting.* Materials Advances, 2023. DOI: 10.1039/D3MA00715D — Grade B.
Supports: general DS range of 30–100%; DS by ¹H-NMR via spectral peak integration against
unmodified gelatin, expressed as moles of methacrylic group per gram of protein; the
limitation that ¹H-NMR requires precise knowledge of amine content, motivating a
complementary colourimetric amine assay.

**R42** — *The effect of the synthetic route on the biophysiochemical properties of
methacrylated gelatin (GelMA) based hydrogel for development of GelMA-based bioinks for 3D
bioprinting applications.* 2022.
sciencedirect.com/science/article/abs/pii/S2589152922002241 — Grade B.
Supports: comparison of conventional, sequential and one-pot routes with varied
methacrylation pH, and their effect on physical, chemical and rheological properties,
printability and biological response.

**R44** — LAP identity: CAS Registry Number **85073-19-4**; IUPAC lithium
phenyl-2,4,6-trimethylbenzoylphosphinate; linear formula C₁₆H₁₆LiO₃P. Sources: Sigma-Aldrich
product 900889; Cayman Chemical 43424; ChemicalBook CB23041806 — Grade E.
Supports: the identity block in `<b:substance>`; LAP's preference over Irgacure 2959 for
biological use on water solubility, polymerisation rate at 365 nm and absorbance at 400 nm
grounds, enabling encapsulation at lower initiator concentration and longer wavelength.
**RESOLVED 2026-07-30.** The InChIKey is now recorded as `JUYQFRXNMVWASF-UHFFFAOYSA-M`,
computed from the isomeric SMILES of PubChem CID 68384915 and cross-checked: the resulting
InChI string matches two independent registry listings character-for-character. The key
widely reproduced by aggregators, `CVDUWYDMNPODNA-UHFFFAOYSA-N`, is the **neutral** species
(suffix -N, composition C16H17O3P.Li.H) and does not correspond to the salt formula those
same vendors state. Also confirmed: PubChem CID 68384915, MW 294.21. See
`dossier/Fact-Check.md` §1.

**R45** — Nguyen AK, Goering PL, Elespuru RK, Sarkar Das S, Narayan RJ. *The Photoinitiator
Lithium Phenyl (2,4,6-Trimethylbenzoyl) Phosphinate with Exposure to 405 nm Light Is
Cytotoxic to Mammalian Cells but Not Mutagenic in Bacterial Reverse Mutation Assays.*
Polymers 2020;12(7):1489. DOI: 10.3390/polym12071489 — Grade B.
Supports: the requirement to assess photoinitiator toxicity *with* light exposure because
the radicals are highly reactive and short-lived; photorheology showing 10 min at
9.6 mW/cm² of 405 nm LED fully crosslinked 10 wt% GelMA with >3.4 mmol/L LAP; cytotoxicity
to M-1 mouse kidney collecting-duct cells under those conditions; no mutagenicity in
bacterial reverse-mutation assays; the observation that literature toxicity results are hard
to compare because studies are usually demonstrations of a specific apparatus or process.

**R46** — *Photocrosslinkable natural polymers in tissue engineering.* Frontiers in
Bioengineering and Biotechnology, 2023. DOI: 10.3389/fbioe.2023.1127757 — Grade B.
Supports: the common photoinitiator set — Irgacure 2959, LAP, ruthenium(II)/persulfate,
eosin Y, riboflavin; methacryloyl substitution routes via methacrylic anhydride, glycidyl
methacrylate and 2-aminoethyl methacrylate.

---

## Calibration and standards

**K1** — ISO/ASTM 52902:2023, *Additive manufacturing — Test artefacts — Geometric
capability assessment of additive manufacturing systems*. Supersedes the 2019 edition.
ISO record: iso.org/standard/79683.html — Grade A.
Supports: benchmark artefact geometries with prescribed quantities and qualities to measure
but no dictated measurement method; the explicit statement that the assessment serves two
purposes, capability assessment **and calibration** of the AM system; deferral of specimen
procedure and machine settings to ASTM F2971.

**K2** — ISO/ASTM 52900:2021, *Additive manufacturing — General principles — Fundamentals
and vocabulary*, 2nd edition. ISO OBP: iso.org/obp/ui/#iso:std:iso-astm:52900:ed-2:v1:en
— Grade A.
Supports: seven process categories with abbreviations; normative Annex A for identifying
processes within a category; the definitions used for the `iso52900` crosswalk — vat
photopolymerization (VPP), powder bed fusion (PBF), sheet lamination (SHL), material
jetting, material extrusion, binder jetting, directed energy deposition.

**K3** — Ouyang L. et al., printability (Pr) index. *Biofabrication* 10, 014102 (2017).
— Grade B.
Supports: Pr quantified from the circularity of the area enclosed by grid holes, equal to 1
for a perfect square pore representing ideal gelation; the under-gelation and over-gelation
failure signatures.

**K4** — *Printability assessment of modified filament deposition modelling 3D bioprinter
using polymeric formulations.* sciencedirect.com/science/article/pii/S2667099223000130
— Grade B.
Supports: the Pr formulation restated; the test battery of physical gelling, crosslinking
ability, filament deposition accuracy and consistency, hydrogel stability, stackability and
filament fusion.

**K5** — Ribeiro A. et al., *Assessing bioink shape fidelity to aid material development in
3D bioprinting.* PubMed: 28976364 — Grade B.
Supports: the filament fusion test measurands (filament distance fd, filament thickness ft,
fused filament length fs); the filament collapse test and its theoretical model based on
equilibrium between gravitational force on the filament and its resistance to deformation.

**K6** — *Potential of Laponite incorporated oxidized alginate-gelatin composite hydrogels
for extrusion bioprinting* (filament collapse and fusion data) — Grade C.
Supports: deflection angle as a function of half-gap distance; the failure of low-viscosity
composite inks to form hanging filaments over larger gaps.

**K7** — ASTM F2971, *Standard Practice for Reporting Data for Test Specimens Prepared by
Additive Manufacturing* — Grade A.
Supports: the reporting obligation that ISO/ASTM 52902 defers to.

**K8** — *Shape Fidelity Evaluation of Alginate-Based Hydrogels through Extrusion-Based
Bioprinting.* PMC: PMC9680455 — Grade B.
Supports: filament collapse evaluated by printing over a platform to observe overhanging
deformation **over time** at two ambient temperatures, with a model estimating Young's modulus
and collapse over time; the caveat that the model **overestimated** the deflection angle while
the slope of the fitted lines followed the experimental trend; printability improved by
optimising gelatin concentration and analysing pore size area; 3% w/v gelatin in 4% alginate
yielding a 98% normalized pore number with >90% viability at five days.

**K9** — *Printability and Shape Fidelity of Bioinks in 3D Bioprinting.* Chemical Reviews
120(19):10850. DOI: 10.1021/acs.chemrev.0c00084 — Grade A.
Supports: the treatment of filament formation, planar orientation and **stacking during
layer-by-layer printing** as three separate evaluations; shape fidelity and integrity indices
computed as printed construct dimensions relative to the designed ones, where indices below 1
indicate filament merging or collapse and an index of 1 indicates high shape fidelity and
optimal layer stacking; the observation that good printability lacks a consensus quantitative
definition.

**K10** — *Nanocomposite ionic-covalent entanglement reinforcement mechanism and hydrogel*
(US 11,414,556) — Grade E.
Supports: the cylinder print test as a stacking procedure — printing to a height of 100 layers
(2 cm) through a 400 µm tip at 200 µm target layer height and 500 µm extrusion width, then
quantifying spreading under the weight of additional layers by comparing wall thickness in the
lowest five against the highest five layers; aspect ratio reported as height over width.

## Regulatory

**G1** — *Combined advanced therapy medicinal products: European regulatory pathways.*
fortrea.com (industry white paper) — Grade E.
Supports: Regulation (EC) No 1394/2007 in force 30 December 2008, defining ATMPs and their
authorisation, supervision and monitoring; the combined-ATMP classification and the
exemption where the cell/tissue component is non-viable and ancillary to the device;
supporting instruments Directive 2009/120/EC and Regulation (EC) No 726/2004.

**G2** — *Bespoke Regulation for Bespoke Medicine? A Comparative Analysis of Bioprinting
Regulation in Europe, the USA and Australia.* DOI: 10.2217/3dp-2021-0011 — Grade B.
Supports: CDRH for devices and CBER for biologics; regulation of more-than-minimally-
manipulated HCT/Ps via the biologics system through PHS Act §351 and 21 CFR Part 1271;
"minimal manipulation" for cells or nonstructural tissues meaning processing that does not
alter biological characteristics.

**G3** — FDA, *Regulation of Human Cells, Tissues, and Cellular and Tissue-Based Products —
Small Entity Compliance Guide.* fda.gov/media/70689/download — Grade A.
Supports: 21 CFR 1271 enforcement provisions; definitions at 21 CFR 1271.3; the registration
obligation attaching to processing steps.

**G4** — *FDA's Regulatory Scheme for Human Tissue: A Brief Overview.* hpm.com — Grade E.
Supports: 21 CFR Part 1271 resting on PHS Act §361 communicable-disease authority; the split
between HCT/Ps eligible for regulation solely under Part 1271 and those regulated under Part
1271 plus premarket and postmarket device, drug or biologics regulation; the Request for
Designation route.

**G5** — *Current Good Tissue Practice for Human Cell, Tissue, and Cellular and Tissue-Based
Product Establishments; Inspection and Enforcement*, Final Rule, 69 FR 68612, 24 November
2004 — Grade A.
Supports: cGTP governing methods, facilities and controls used in HCT/P manufacture,
recordkeeping, and the establishment of a quality programme.

**G6** — *A 3D Bioprinting Exemplar of the Consequences of the Regulatory Requirements on
Customized Processes.* DOI: 10.2217/rme.15.52 — Grade B.
Supports: the worked classification of a substantially manipulated chondrocyte product with
integral scaffold as a tissue-engineered combined ATMP under Article 2(1)(d) of Regulation
(EC) No 1394/2007; the observation that a manufacturer may lack data to substantiate the
principal mode of action early in development and therefore cannot yet identify the
candidate ATMP classification.

**G7** — ISO/IEC 25422:2025, *Information technology — 3D Manufacturing Format (3MF)
specification suite*, first edition, June 2025, Published — Grade A.
Supports: 3MF Core and its extensions now constituting an ISO/IEC International Standard.

## Gaps

Explicitly *not* covered by any source consulted here, and therefore left unpopulated in
the schema rather than filled in. **Each is now also carried as a structured
`<b:openitem>` in the example package, so it is counted and filterable rather than
prose-only.**

1. **Isolated yield figures for GelMA synthesis.** Widely performed, rarely reported.
2. **Acoustic droplet ejection and magnetic levitation parameter sets.** Modality
   enumerations exist in the schema; the evidence base was not assembled.
3. **Bioassembly of spheroids/organoids** (Kenzan-type and scaffold-free) parameters.
4. **In-situ / intraoperative printing** parameters.
5. **Endotoxin limits** for bioprinting-grade polymers — the `endotoxin` attribute exists;
   the acceptance threshold is application- and jurisdiction-specific and is not asserted.
6. **Cellosaurus RRIDs** for specific lines — the attribute is mandatory for `kind="line"`,
   but no specific accession is asserted anywhere in this draft.
7. ~~**A crosswalk to ISO/ASTM 52900 terminology** for the AM process categories.~~
   **RESOLVED 2026-07-30** — see K2 above and the `iso52900` attribute on `<b:process>`.
   The mapping is many-to-one and informative; modalities whose category is genuinely
   arguable (melt electrowriting, electrospinning, magnetic levitation, spheroid
   bioassembly) are deliberately left unmapped rather than forced.
