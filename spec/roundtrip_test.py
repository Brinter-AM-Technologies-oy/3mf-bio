#!/usr/bin/env python3
"""
Round-trip preservation test.

Chapter 7 states normatively: "Consumers MUST NOT silently discard b: elements or
attributes they do not recognise... Loss of a process parameter is a safety event."

That rule had no test. This simulates a naive consumer -- one that understands 3MF core
and a subset of the bio extension, parses a package, and re-exports it -- then checks
whether anything was lost. It also injects content from a hypothetical FUTURE version of
the extension, which today's consumer cannot possibly understand, and checks that it
survives.

A consumer that fails this test will silently drop a light dose or a shear stress on
re-export, and the resulting file will still validate.
"""
import copy
import os
import sys
from xml.etree import ElementTree as ET

CORE = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
BIO = "https://3mfbio.com/ns/bio/2026/07"
FUTURE = "urn:3mf-bio:2099-01"

ET.register_namespace("", CORE)
ET.register_namespace("b", BIO)
ET.register_namespace("bf", FUTURE)


def inventory(root):
    """Every bio element and attribute, as a comparable set."""
    els, attrs = [], []
    for el in root.iter():
        if not isinstance(el.tag, str):
            continue
        if el.tag.startswith(f"{{{BIO}}}") or el.tag.startswith(f"{{{FUTURE}}}"):
            els.append(el.tag)
        for k, v in el.attrib.items():
            if k.startswith(f"{{{BIO}}}") or k.startswith(f"{{{FUTURE}}}"):
                attrs.append((k, v))
            elif el.tag.startswith(f"{{{BIO}}}") or el.tag.startswith(f"{{{FUTURE}}}"):
                attrs.append((el.tag, k, v))
    return sorted(els), sorted(map(str, attrs))


def naive_consumer(root):
    """A consumer that understands core plus a few bio elements, and re-exports.

    This is the CORRECT implementation: it deep-copies the tree, touching only what it
    understands. The elements it does not recognise ride along untouched.
    """
    out = copy.deepcopy(root)
    for obj in out.iter(f"{{{CORE}}}object"):
        obj.set("name", (obj.get("name") or "") + "")  # a no-op edit
    return out


def lossy_consumer(root):
    """The failure mode this test exists to catch: rebuild only what is understood."""
    out = copy.deepcopy(root)
    known = {f"{{{BIO}}}{t}" for t in
             ("evidence", "reference", "substances", "substance", "identity", "grade",
              "bioinkgroup", "bioink", "component", "process", "machine", "parameters",
              "param")}
    for parent in list(out.iter()):
        for child in list(parent):
            if isinstance(child.tag, str) and child.tag.startswith(f"{{{BIO}}}") \
                    and child.tag not in known:
                parent.remove(child)
    return out


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "examples/3D/3dmodel.model"
    tree = ET.parse(path)
    root = tree.getroot()

    # Inject content from a hypothetical future version of this extension. Today's consumer
    # cannot know what it means; the rule says it must survive anyway.
    res = root.find(f"{{{CORE}}}resources")
    future = ET.SubElement(res, f"{{{FUTURE}}}timeseries")
    future.set("id", "9001")
    future.set("property", "cell_density")
    pt = ET.SubElement(future, f"{{{FUTURE}}}point")
    pt.set("day", "7")
    pt.set("value", "4.2e6")
    for pr in root.iter(f"{{{BIO}}}process"):
        pr.set(f"{{{FUTURE}}}oxygenprofile", "9001")

    before = inventory(root)

    ok = True
    good = inventory(naive_consumer(root))
    if good == before:
        print("PASS  preserving consumer: all bio and future-version content survives")
    else:
        ok = False
        print("FAIL  preserving consumer lost content")

    bad = inventory(lossy_consumer(root))
    lost_els = set(before[0]) - set(bad[0])
    if lost_els:
        print(f"PASS  lossy consumer detected: dropped {len(lost_els)} element type(s)")
        for e in sorted(lost_els)[:6]:
            print(f"        {e.split('}')[-1]}")
        print("      A consumer behaving this way silently discards process parameters,")
        print("      and the re-exported file still validates. This is the failure mode")
        print("      Chapter 7 forbids.")
    else:
        ok = False
        print("FAIL  the lossy consumer was not detected; this test is not testing anything")

    lost_attrs = set(before[1]) - set(bad[1])
    print(f"\n      elements before: {len(before[0])}  after lossy re-export: {len(bad[0])}")
    print(f"      attributes lost to the lossy consumer: {len(lost_attrs)}")
    return 0 if ok else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except BrokenPipeError:
        # tolerate being piped into head/tail
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
        sys.exit(0)
