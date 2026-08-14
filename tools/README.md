# Tools: integrator and viewer

Two programs, one purpose: make the format usable by someone who has a mesh and a bench,
not a schema editor.

```
questionnaire.py   generates the question set FROM the rules
integrate.py       STL/OBJ + answers  ->  validating .3mf package
viewer.html        .3mf  ->  run sheet, open items, dossier, maturation, geometry
machine_profiles/  vendor profiles; brinter.json is the first
test_tools.py      round-trip tests
```

## Try it in three commands

```bash
python3 tools/questionnaire.py --profile brinter                    # see the printheads
python3 tools/questionnaire.py --profile brinter --head pneuma-pro --format template > answers.json
# fill in what you know; leave the rest null
python3 tools/integrate.py answers.json --mesh part.stl --out mybuild/ --zip mybuild.3mf
python3 spec/validate_bio.py mybuild/
```

Then open `tools/viewer.html` in a browser and drop `mybuild.3mf` on it.

## Three design decisions worth arguing with

**The questionnaire is generated from the rules, not written alongside them.**
`questionnaire.py` imports `REQUIRED`, `CALIBRATION_EXPECTED`, `STIMULATION_REQUIRED`,
`PARAM_DIMENSION` and `BOUNDS` from the validator. A hand-written form drifts: someone adds
a required parameter, forgets the form, and the tool starts producing packages that fail
their own validation. Deriving it makes that impossible — add a rule, the question appears.

**The integrator never refuses to emit, and never fabricates to fill a shape.**
Any answer left `null` becomes a `<b:openitem>` naming the action that would close it. A tool
demanding forty fields before producing output does not get used, and a recorded gap beats an
invented number.

The second half of that sentence took three fixes to get right. Early versions emitted a
calibration record with no date, and a placeholder substance named "TODO". Both satisfied the
*shape* of a valid record while asserting something false — that a dated calibration event
occurred, that a material existed. Now: **if it wasn't supplied, it isn't emitted.** No
substances means no formulation, which means objects carry no `pid`. That is a geometry
package with a dossier skeleton, and it is an honest intermediate state.

The contract is tested both ways in `test_tools.py`: empty answers must still produce a
package that validates with **zero errors**, and a positive mycoplasma result must still be
emitted and must then be **rejected** by the validator.

**The viewer leads with the run sheet, not the 3D preview.**
Plenty of things render a mesh. The problem this solves is that a package carries
instructions and constraints, and the person receiving it has to follow them. So the default
tab is an ordered operator checklist assembled from the package, with the open items and
acceptance criteria attached to the steps where they bite: a contaminated mycoplasma result
appears at *prepare cells* and says do not proceed; unset parameters appear at *print* and
say you cannot follow this run sheet.

Without a standards body, the viewer is the enforcement mechanism. A package showing
"6 blocking open items" in red is the social pressure that a committee would otherwise apply.

## Privacy

`viewer.html` is one file with no build step and no server. `JSZip` and `three.js` load from
a CDN; the package itself is read with `FileReader` and never leaves the machine. CI asserts
the file contains no `fetch(`, `XMLHttpRequest`, `sendBeacon` or `action=`.

Open it from disk, or host it anywhere static.

## Machine profiles

A profile pre-answers the machine-dependent questions and adds head-specific prompts. The
Brinter profile is compiled from published product material and press coverage; it records
**drive principles and modalities**, and deliberately omits bore sizes, pressure ranges and
speeds, which are configuration-dependent and were not published in a form worth copying.
The questionnaire asks for those; the profile does not assume them.

Adding a vendor is a JSON file. The useful part is `prompts` — head-specific things a user
would otherwise get wrong. For example, the Visco heads are progressive-cavity drives
delivering constant volume per revolution, so the controlled variable is a volume rate and a
screw speed, **not a pressure**; the profile says so, and rule P0 then asks for the right
parameter.

## Not yet built

- A browser front end for the questionnaire. It is CLI plus JSON today, which suits someone
  scripting a batch but not a bench scientist filling one in by hand.
- Writing edits back from the viewer. It is read-only, so closing an open item means editing
  the package.
- Slicer integration. Brinter's own workflow is STL into a browser slicer, out as G-code;
  the natural next step is emitting the `.3mf` alongside that G-code with the toolpath
  checksum already populated.
