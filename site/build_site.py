#!/usr/bin/env python3
"""
Build the static site for 3mfbio.com.

No framework, no JS build step. Markdown in, HTML out, plus a copy of the viewer and the
downloadable artifacts.

One thing this does that most doc sites skip: the namespace URI
https://3mfbio.com/ns/bio/2026/07 is resolvable, so the site actually SERVES something
there. A namespace that 404s is a broken promise to anyone who pastes it into a browser to
find out what it means. The namespace document links the schema, the Schematron and the
specification.

Usage:
    python3 site/build_site.py            # -> site/_build/
    python3 site/build_site.py --serve    # build, then serve on :8000
"""
import argparse
import http.server
import os
import re
import shutil
import socketserver
import sys

import markdown

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(HERE, "_build")
DOMAIN = "3mfbio.com"
NS = f"https://{DOMAIN}/ns/bio/2026/07"

NAV = [("/", "Home"), ("/spec/", "Specification"), ("/dossier/", "Dossiers"),
       ("/tools/", "Tools"), ("/review/", "Review"), ("/viewer/", "Viewer"), ("/download/", "Download")]

MD_EXT = ["extra", "toc", "sane_lists", "admonition"]


def shell(title, body, path="/", desc="", toc=""):
    nav = "".join(
        f'<a href="{h}"{" class=\'on\'" if h == path else ""}>{t}</a>' for h, t in NAV)
    return f"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc or 'An open schema for recording biofabrication end to end.'}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc or 'An open schema for recording biofabrication end to end.'}">
<meta property="og:type" content="website">
<link rel="stylesheet" href="/assets/style.css">
</head><body>
<header>
  <a class="brand" href="/"><span class="mark">3MF</span>Bio</a>
  <nav>{nav}</nav>
  <a class="gh" href="https://github.com/Brinter-AM-Technologies-oy/3mf-bio">GitHub</a>
</header>
<main>{toc}{body}</main>
<footer>
  <div>
    <strong>Not a standard. Certifies nothing.</strong> This schema supplies fields; what goes
    in them, and whether that satisfies your auditor, is your judgement. Not affiliated with
    the 3MF Consortium.
  </div>
  <div class="fine">
    Code BSD-2 &middot; schema files CC0 &middot; documentation CC BY 4.0 &middot;
    <a href="/download/">artifacts</a> &middot;
    <a href="https://github.com/Brinter-AM-Technologies-oy/3mf-bio">source</a>
  </div>
</footer>
</body></html>"""


def render_md(src, title=None, path="/", with_toc=False, section=""):
    text = open(src, encoding="utf-8").read()
    md = markdown.Markdown(extensions=MD_EXT)
    html = md.convert(text)
    # first heading becomes the title
    if not title:
        m = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.S)
        title = re.sub(r"<[^>]+>", "", m.group(1)).strip() if m else "3MF Bio"
    # rewrite intra-repo links to site paths
    # Relative .md links resolve within the section the file lives in, otherwise a link
    # from review/README.md to REGULATORY-REVIEW.md lands at /regulatory-review/ instead of
    # /review/regulatory-review/.
    html = re.sub(r'href="([A-Za-z0-9_\-/]+)\.md"',
                  lambda m: f'href="/{_slug(section + m.group(1))}/"', html)
    toc = ""
    if with_toc and getattr(md, "toc", "").count("<li>") > 3:
        toc = f'<aside class="toc"><div class="toc-h">On this page</div>{md.toc}</aside>'
    return title, html, toc


def _slug(p):
    p = p.strip("./").replace("dossier/", "dossier/").replace(".md", "")
    return p.lower()


def write(relpath, content):
    full = os.path.join(OUT, relpath.lstrip("/"))
    os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, "w", encoding="utf-8").write(content)


def copy(src, relpath):
    dst = os.path.join(OUT, relpath.lstrip("/"))
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy(src, dst)


# --------------------------------------------------------------------------- pages

def home():
    return """
<section class="hero">
  <h1>Record a bioprint so someone else can rebuild it.</h1>
  <p class="lead">
    An open schema that carries material synthesis, cell provenance, formulation, print
    process, calibration, maturation and characterization in one file &mdash; with every
    number declaring where it came from.
  </p>
  <p class="lead dim">
    Built on 3MF, so the geometry stays readable by ordinary 3D-printing tools.
  </p>
  <div class="cta">
    <a class="btn primary" href="/viewer/">Open a package in the viewer</a>
    <a class="btn" href="/download/">Download the schema</a>
  </div>
</section>

<section class="claim">
  <p>Engineering formats describe the machine and stop at the material boundary. Life-science
  formats describe the biology and treat fabrication as a black box. A bioprinted construct is
  describable by neither alone, because what decides whether it works is the
  <em>interaction</em> &mdash; nozzle geometry acting on a shear-sensitive cell suspension,
  light dose against scattering that depends on cell density, a perfusion rate that is
  simultaneously mass transport and a differentiation cue.</p>
  <p class="big">This is the only place a CAS number and a G&#8209;code command map sit in the
  same file under the same discipline.</p>
</section>

<section>
  <h2>One rule holds it together</h2>
  <div class="rule">
    <code>provenance</code> is required on every numeric parameter:
    <b>measured</b>, <b>derived</b>, <b>cited</b>, <b>vendor</b>, or <b>estimated</b>.
  </div>
  <p>Making a number up requires labelling it <code>estimated</code>, which a reviewer, a
  release gate or a CI job can filter on. And every estimated value must be owned by an
  <b>open item</b> that names what would close it. Unknowns are data, not comments &mdash;
  a comment is lost on round-trip and cannot be counted, assigned or closed.</p>
</section>

<section>
  <h2>What a package holds</h2>
  <div class="grid">
    <div class="cell"><h3>Materials</h3><p>Identity with CAS, InChIKey, PubChem and ChEBI.
      Synthesis route, conditions, <b>yield</b>, verification assay, grade, hazard.</p></div>
    <div class="cell"><h3>Cells</h3><p>Origin, Cellosaurus RRID, mycoplasma and STR
      authentication, culture, <b>passage at print</b>, differentiation.</p></div>
    <div class="cell"><h3>Process</h3><p>20 modalities. Printheads with drive, nozzle geometry
      and bore, coaxial core&ndash;shell channels. Toolpath with a verified checksum.</p></div>
    <div class="cell"><h3>Calibration</h3><p>Dated events with your own acceptance criteria.
      Grid, bridge and layer&nbsp;stacking tests &mdash; three different loads, and an ink can
      pass two and fail the third.</p></div>
    <div class="cell"><h3>Maturation</h3><p>Staged culture, bioreactors, stimulation regimes,
      media schedules. The print is about a day; this is the three weeks that decide the
      outcome.</p></div>
    <div class="cell"><h3>Characterization</h3><p>What you measured on the construct, and
      when. Readings over a timecourse, because 92% at day&nbsp;1 and 74% at day&nbsp;21 is a
      different construct from one holding 90%.</p></div>
  </div>
</section>

<section>
  <h2>Three commands from an STL</h2>
  <pre><code>python3 tools/questionnaire.py --profile brinter --head pneuma-pro \\
        --format template &gt; answers.json
# fill in what you know, leave the rest null
python3 tools/integrate.py answers.json --mesh part.stl --out mybuild/ --zip mybuild.3mf
python3 spec/validate_bio.py mybuild/</code></pre>
  <p><b>The integrator never refuses to emit</b>, and never fabricates to fill a shape.
  Anything left blank becomes a tracked open item. A tool demanding forty fields before
  producing output does not get used, and a recorded gap beats an invented number.</p>
  <p>Then <a href="/viewer/">drop the package in the viewer</a>, which leads with a
  <b>run sheet</b> &mdash; an ordered operator checklist with constraints attached where they
  bite. A contaminated mycoplasma result appears at <i>prepare cells</i> and says do not
  proceed.</p>
</section>

<section class="honest">
  <h2>What it does not do</h2>
  <ul>
    <li><b>It asserts no thresholds.</b> No viability floor, no endotoxin limit, no
      dimensional tolerance. <code>acceptance</code> is a required attribute so each
      laboratory states its own and is held to it.</li>
    <li><b>It cannot check that a claim is true.</b> Fifteen adversarial packages were built
      that break no rule and are still garbage; six still pass. A real reference cited for an
      unrelated claim will never be caught by a schema. That boundary is
      <a href="/spec/">Chapter&nbsp;12</a>, not a footnote.</li>
    <li><b>No real dataset has been recorded in it yet.</b> That is the honest gap, and it is
      the one thing the authors cannot close alone.</li>
  </ul>
</section>
"""


def download_page():
    return """
<h1>Download</h1>
<p>Everything here is in the <a href="https://github.com/Brinter-AM-Technologies-oy/3mf-bio">repository</a>.
Schema files are CC0 &mdash; take them, change them, embed them, no attribution required.</p>

<h2>Schema and rules</h2>
<table>
<tr><th>File</th><th>What it is</th></tr>
<tr><td><a href="/ns/bio/2026/07/bio.xsd">bio.xsd</a></td>
    <td>Canonical XML Schema</td></tr>
<tr><td><a href="/ns/bio/2026/07/bio.libxml.xsd">bio.libxml.xsd</a></td>
    <td>Generated variant for libxml2 toolchains. libxml2 uses 2<sup>30</sup> as its internal
    UNBOUNDED sentinel and rejects the <code>maxOccurs="2147483647"</code> that 3MF schemas
    use, though it is valid XSD</td></tr>
<tr><td><a href="/ns/bio/2026/07/bio.sch">bio.sch</a></td>
    <td>ISO Schematron &mdash; every intra-document rule, runs in any XSLT toolchain</td></tr>
</table>

<h2>Example packages</h2>
<table>
<tr><th>File</th><th>What it demonstrates</th></tr>
<tr><td><a href="/downloads/examples-package.3mf">examples-package.3mf</a></td>
    <td>Volumetric tomographic print, with a volumetric field binding and a resolved
    chemical-identity correction</td></tr>
<tr><td><a href="/downloads/examples-extrusion-package.3mf">examples-extrusion-package.3mf</a></td>
    <td>Three-head extrusion with a coaxial vascular head, a 21-day perfusion maturation and
    nine assays over a timecourse</td></tr>
</table>
<p class="fine">Both are illustrative. Values marked TEMPLATE or carrying an open item are
placeholders for a laboratory's own data and have not been back-filled from anywhere.
<a href="/viewer/">Open one in the viewer</a> to see what a package looks like from the
receiving end.</p>

<h2>Namespace</h2>
<p>The namespace URI is <code>https://3mfbio.com/ns/bio/2026/07</code>, and it
<a href="/ns/bio/2026/07/">resolves</a>. If you fork this, run
<code>python3 spec/set_namespace.py &lt;your-uri&gt;</code> to move it to a namespace you
control &mdash; one command, rewrites the whole repository.</p>
"""


def ns_page():
    return f"""
<h1>Namespace: <code>{NS}</code></h1>
<p class="lead">This URI identifies the 3MF Bio extension vocabulary. You have probably
arrived here because you pasted it out of an XML file.</p>

<div class="rule">A namespace that returns 404 is a broken promise. This one serves the
schema, the rules and the specification.</div>

<h2>What it means</h2>
<p>An XML document declaring this namespace carries biofabrication data alongside 3MF
geometry: materials and how they were made, cells and their provenance, formulation, print
process, calibration, post-print maturation, and what was measured on the result. Every
numeric value declares its origin.</p>

<h2>Artifacts</h2>
<table>
<tr><td><a href="bio.xsd">bio.xsd</a></td><td>Canonical schema</td></tr>
<tr><td><a href="bio.libxml.xsd">bio.libxml.xsd</a></td><td>libxml2-compatible variant</td></tr>
<tr><td><a href="bio.sch">bio.sch</a></td><td>ISO Schematron rules</td></tr>
<tr><td><a href="/spec/">Specification</a></td><td>Normative document</td></tr>
</table>

<h2>Prefix</h2>
<p>Conventionally <code>b</code>:</p>
<pre><code>&lt;model xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
       xmlns:b="{NS}"
       requiredextensions="b"&gt;</code></pre>

<h2>Status</h2>
<p>Open schema, pre-1.0, published for reuse under CC0. <b>Not a standard and not a 3MF
Consortium extension.</b> It follows their conventions so packages stay readable by ordinary
3MF tools, which is a compatibility decision rather than a claim of affiliation. Packages
declare which draft they were written against in
<code>&lt;metadata name="b:SpecVersion"&gt;</code>.</p>
"""


def index_page(title, blurb, entries):
    rows = "".join(
        f'<a class="card" href="{h}"><h3>{t}</h3><p>{d}</p></a>' for h, t, d in entries)
    return f'<h1>{title}</h1><p class="lead">{blurb}</p><div class="cards">{rows}</div>'


# --------------------------------------------------------------------------- build

def build():
    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)

    write("/index.html", shell("3MF Bio — record a bioprint so someone else can rebuild it",
                               home(), "/",
                               "An open schema carrying material, cells, process, "
                               "calibration, maturation and characterization in one file."))

    # specification
    t, h, toc = render_md(os.path.join(ROOT, "spec", "3MF Bio Extension.md"),
                          path="/spec/", with_toc=True)
    write("/spec/index.html", shell(f"{t} — 3MF Bio", h, "/spec/", toc=toc))

    # dossiers
    dossiers = [
        ("Parameter-Dossier.md", "Parameters",
         "Per-modality parameter sets, with the source establishing why each matters."),
        ("Calibration-Dossier.md", "Calibration",
         "What to test per modality. Grid, bridge and layer stacking apply three different "
         "loads and do not substitute for one another."),
        ("Regulatory-Annex.md", "Regulatory",
         "A map of which instruments exist and which fields exist to record a determination. "
         "Not advice, and not compliance."),
        ("References.md", "References",
         "79 sources graded A–F, each saying what it supports."),
        ("Fact-Check.md", "Fact check",
         "Every claim re-checked, with verdicts and corrections — including a chemical "
         "identifier that is wrong nearly everywhere it is published."),
    ]
    for fn, name, desc in dossiers:
        src = os.path.join(ROOT, "dossier", fn)
        if not os.path.exists(src):
            continue
        slug = fn.replace(".md", "").lower()
        t, h, toc = render_md(src, path="/dossier/", with_toc=True)
        write(f"/dossier/{slug}/index.html", shell(f"{t} — 3MF Bio", h, "/dossier/", desc, toc))
    write("/dossier/index.html", shell("Dossiers — 3MF Bio", index_page(
        "Dossiers",
        "Where the numbers come from. Every parameter in the schema is justified by a source "
        "establishing that it is process-relevant — the source justifies the parameter, not "
        "the value.",
        [(f"/dossier/{fn.replace('.md', '').lower()}/", n, d) for fn, n, d in dossiers]),
        "/dossier/"))

    # repo docs
    for fn, name, desc in [
        ("SCOPE.md", "Scope", "What this is and deliberately is not."),
        ("CONTRIBUTING.md", "Contributing", "Nothing gets a number without a source."),
        ("SUBMISSION.md", "Red team", "The adversarial review and the honest gap list."),
        ("CHANGELOG.md", "Changelog", "What changed, and what broke."),
        ("DISCLAIMER.md", "Disclaimer", "Filling these fields is not compliance."),
        ("SECURITY.md", "Security", "Parsing untrusted packages."),
    ]:
        src = os.path.join(ROOT, fn)
        if os.path.exists(src):
            t, h, toc = render_md(src, path="/tools/", with_toc=True)
            write(f"/{fn.replace('.md', '').lower()}/index.html",
                  shell(f"{name} — 3MF Bio", h, "/", desc, toc))

    # review packs
    for fn, name, desc in [
        ("REGULATORY-REVIEW.md", "Regulatory review",
         "16 numbered claims for a regulatory professional to check."),
        ("DATASET-SHEET.md", "Dataset sheet",
         "Exactly what would turn a template into a real record."),
    ]:
        src = os.path.join(ROOT, "review", fn)
        if os.path.exists(src):
            slug = fn.replace(".md", "").lower()
            t, h, toc = render_md(src, path="/review/", with_toc=True, section="review/")
            write(f"/review/{slug}/index.html", shell(f"{t} — 3MF Bio", h, "/review/", desc, toc))
    src = os.path.join(ROOT, "review", "README.md")
    if os.path.exists(src):
        t, h, toc = render_md(src, path="/review/", with_toc=True, section="review/")
        write("/review/index.html", shell("Review — 3MF Bio", h, "/review/",
                                          "Two things needing outside eyes.", toc))

    # tools
    src = os.path.join(ROOT, "tools", "README.md")
    t, h, toc = render_md(src, path="/tools/", with_toc=True)
    write("/tools/index.html", shell("Tools — 3MF Bio", h, "/tools/",
                                     "Integrator and viewer.", toc))

    # viewer, verbatim
    copy(os.path.join(ROOT, "tools", "viewer.html"), "/viewer/index.html")

    # downloads
    write("/download/index.html", shell("Download — 3MF Bio", download_page(), "/download/"))
    for f in ("examples-package.3mf", "examples-extrusion-package.3mf"):
        p = os.path.join(ROOT, f)
        if os.path.exists(p):
            copy(p, f"/downloads/{f}")

    # the namespace must actually resolve
    write("/ns/bio/2026/07/index.html", shell(f"Namespace {NS}", ns_page(), "/",
                                              "The 3MF Bio extension namespace."))
    for f in ("bio.xsd", "bio.libxml.xsd", "bio.sch"):
        copy(os.path.join(ROOT, "spec", f), f"/ns/bio/2026/07/{f}")

    write("/assets/style.css", CSS)
    write("/CNAME", DOMAIN + "\n")
    write("/.nojekyll", "")
    write("/robots.txt", f"User-agent: *\nAllow: /\nSitemap: https://{DOMAIN}/sitemap.xml\n")

    pages = [p.replace(OUT, "").replace("/index.html", "/").replace("\\", "/")
             for p, _, fs in os.walk(OUT) for f in fs if f == "index.html"
             for p in [os.path.join(p, f)]]
    write("/sitemap.xml",
          '<?xml version="1.0" encoding="UTF-8"?>\n'
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
          "".join(f"  <url><loc>https://{DOMAIN}{u}</loc></url>\n" for u in sorted(pages)) +
          "</urlset>\n")

    n = sum(len(fs) for _, _, fs in os.walk(OUT))
    print(f"built {n} files into {OUT}/")
    return 0


CSS = """
:root{
  --bg:#0f1116; --panel:#161922; --line:#242836; --ink:#e8eaf2; --dim:#98a0b8;
  --accent:#6fd6bd; --accent-dim:#3d8a7a; --warn:#e8b04b; --bad:#e0736a;
  --mono:ui-monospace,"SF Mono",Menlo,Consolas,monospace;
  --w:920px;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--ink);
  font:16px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,sans-serif;
  -webkit-font-smoothing:antialiased}
a{color:var(--accent);text-decoration:none}
a:hover{text-decoration:underline}

header{position:sticky;top:0;z-index:50;background:rgba(15,17,22,.92);
  backdrop-filter:blur(10px);border-bottom:1px solid var(--line);
  display:flex;align-items:center;gap:22px;padding:12px 24px;flex-wrap:wrap}
.brand{font-weight:700;font-size:17px;color:var(--ink);letter-spacing:-.01em}
.brand .mark{color:var(--accent)}
header nav{display:flex;gap:4px;flex-wrap:wrap}
header nav a{color:var(--dim);font-size:14px;padding:5px 11px;border-radius:5px}
header nav a:hover{background:var(--panel);color:var(--ink);text-decoration:none}
header nav a.on{color:var(--accent);background:var(--panel)}
.gh{margin-left:auto;font-size:14px;color:var(--dim);border:1px solid var(--line);
  padding:5px 13px;border-radius:5px}
.gh:hover{border-color:var(--accent);color:var(--accent);text-decoration:none}

main{max-width:var(--w);margin:0 auto;padding:44px 24px 90px}
h1{font-size:32px;line-height:1.22;letter-spacing:-.02em;margin:0 0 18px}
h2{font-size:21px;margin:44px 0 14px;letter-spacing:-.01em}
h3{font-size:16px;margin:24px 0 8px}
p{margin:0 0 15px}
.lead{font-size:18px;color:var(--dim);max-width:64ch}
.dim{color:var(--dim)}
.fine{font-size:13.5px;color:var(--dim)}

.hero{padding:26px 0 10px;border-bottom:1px solid var(--line);margin-bottom:34px}
.hero h1{font-size:40px;max-width:19ch}
.cta{display:flex;gap:11px;margin-top:26px;flex-wrap:wrap}
.btn{display:inline-block;padding:11px 20px;border:1px solid var(--line);border-radius:6px;
  color:var(--ink);font-size:15px}
.btn:hover{border-color:var(--accent);text-decoration:none}
.btn.primary{background:var(--accent);color:#0c0e13;border-color:var(--accent);font-weight:600}
.btn.primary:hover{background:#84e2cb}

.claim{border-left:3px solid var(--accent-dim);padding:4px 0 4px 22px;margin:34px 0}
.claim .big{font-size:19px;color:var(--ink);margin-bottom:0}

.rule{background:var(--panel);border:1px solid var(--line);border-left:3px solid var(--accent);
  border-radius:6px;padding:14px 18px;margin:16px 0;font-size:15.5px}

.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:12px;
  margin-top:16px}
.cell{background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:15px 17px}
.cell h3{margin:0 0 6px;color:var(--accent);font-size:14px;text-transform:uppercase;
  letter-spacing:.07em}
.cell p{margin:0;font-size:14.5px;color:var(--dim)}

.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(270px,1fr));gap:12px;
  margin-top:20px}
.card{background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:17px 19px;
  display:block;color:var(--ink)}
.card:hover{border-color:var(--accent);text-decoration:none}
.card h3{margin:0 0 6px;font-size:16px}
.card p{margin:0;font-size:14px;color:var(--dim)}

.honest{background:var(--panel);border:1px solid var(--line);border-radius:8px;
  padding:6px 22px 18px;margin-top:40px}
.honest ul{padding-left:19px;margin:0}
.honest li{margin-bottom:11px;color:var(--dim);font-size:15px}
.honest li b{color:var(--ink)}

pre{background:var(--panel);border:1px solid var(--line);border-radius:7px;padding:14px 16px;
  overflow-x:auto;font-size:13.5px;line-height:1.55}
code{font-family:var(--mono);font-size:.9em}
p code,li code,td code{background:var(--panel);border:1px solid var(--line);
  padding:1px 5px;border-radius:4px}
pre code{background:none;border:none;padding:0}

table{border-collapse:collapse;width:100%;margin:14px 0;font-size:14.5px;display:block;
  overflow-x:auto}
th,td{text-align:left;padding:9px 14px 9px 0;border-bottom:1px solid var(--line);
  vertical-align:top}
th{color:var(--dim);font-weight:600;font-size:12.5px;text-transform:uppercase;
  letter-spacing:.05em}

blockquote{border-left:3px solid var(--warn);margin:18px 0;padding:2px 0 2px 18px;
  color:var(--dim)}
hr{border:0;border-top:1px solid var(--line);margin:34px 0}
ul,ol{padding-left:22px}
li{margin-bottom:6px}

.toc{background:var(--panel);border:1px solid var(--line);border-radius:8px;
  padding:14px 18px;margin-bottom:30px;font-size:14px}
.toc-h{color:var(--dim);font-size:12px;text-transform:uppercase;letter-spacing:.08em;
  margin-bottom:8px}
.toc ul{padding-left:16px;margin:0}
.toc>ul{padding-left:0;list-style:none}
.toc li{margin-bottom:3px}
.toc a{color:var(--dim)}
.toc a:hover{color:var(--accent)}

footer{border-top:1px solid var(--line);padding:26px 24px 46px;color:var(--dim);
  font-size:14px;max-width:var(--w);margin:0 auto}
footer .fine{margin-top:9px}

@media(max-width:620px){
  main{padding:28px 18px 70px}
  .hero h1{font-size:29px}
  h1{font-size:26px}
  header{padding:10px 16px;gap:12px}
  .gh{display:none}
}
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--serve", action="store_true")
    ap.add_argument("--port", type=int, default=8000)
    a = ap.parse_args()
    rc = build()
    if a.serve and rc == 0:
        os.chdir(OUT)
        class H(http.server.SimpleHTTPRequestHandler):
            def log_message(self, *args):
                pass
        with socketserver.TCPServer(("", a.port), H) as httpd:
            print(f"serving http://localhost:{a.port}/  (ctrl-c to stop)")
            httpd.serve_forever()
    return rc


if __name__ == "__main__":
    sys.exit(main())
