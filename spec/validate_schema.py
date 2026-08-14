#!/usr/bin/env python3
"""
XSD structural validation for the bio subtrees of a 3MF model part.

A 3MF extension schema cannot validate a whole model part on its own: it redefines
CT_Resources and depends on the core schema, which is not redistributed here. What IS
directly checkable is each bio resource subtree, because every bio element is declared
globally in bio.xsd. This script lifts each top-level bio resource out of <resources>
and validates it against its global declaration.

Usage:  python3 validate_schema.py <package-dir> [schema.xsd]
"""
import copy, os, sys
from lxml import etree

BIO = "https://3mfbio.com/ns/bio/2026/07"
CORE = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
TOP = ("evidence", "substances", "cellpopulations", "bioinkgroup",
       "process", "protocol", "results", "fieldbinding",
       "calibration", "regulatory", "openitems")


def main():
    pkg = sys.argv[1] if len(sys.argv) > 1 else "examples"
    xsd = sys.argv[2] if len(sys.argv) > 2 else os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "bio.libxml.xsd")
    schema = etree.XMLSchema(etree.parse(xsd))
    model = etree.parse(os.path.join(pkg, "3D", "3dmodel.model"))
    res = model.getroot().find(f"{{{CORE}}}resources")

    checked = bad = 0
    for el in res:
        if not isinstance(el.tag, str) or not el.tag.startswith(f"{{{BIO}}}"):
            continue  # skip comments and non-bio resources
        tag = el.tag.split("}", 1)[1]
        if tag not in TOP:
            continue
        checked += 1
        doc = etree.ElementTree(copy.deepcopy(el))
        if not schema.validate(doc):
            bad += 1
            print(f"INVALID  <b:{tag} id={el.get('id')}>")
            for e in schema.error_log:
                print("        ", e.message)
        else:
            print(f"valid    <b:{tag} id={el.get('id')}>")
    print(f"\n{checked} bio resource(s) checked, {bad} invalid")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
