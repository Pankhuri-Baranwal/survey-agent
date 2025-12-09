from typing import Dict, List, Optional
import xml.etree.ElementTree as ET
from xml.dom import minidom

TYPE_MAP = {
    "single_select": "radio",
    "multi_select": "checkbox",
    "open_text": "open",
    "matrix": "grid",
}

def _safe_label(base: str, idx: Optional[int] = None) -> str:
    """
    Build a stable XML label: alphanumerics + underscores.
    """
    clean = "".join(ch if ch.isalnum() else "_" for ch in base)
    return f"{clean}_{idx}" if idx is not None else clean

def _add_title(parent: ET.Element, text: str) -> None:
    t = ET.SubElement(parent, "title")
    t.text = text

def _add_rows(parent: ET.Element, qid: str, options: List[str]) -> None:
    for i, opt in enumerate(options, start=1):
        r = ET.SubElement(parent, "row")
        r.set("label", _safe_label(qid, i))
        r.text = opt

def build_decipher_xml(survey_json: Dict) -> str:
    """
    Convert canonical survey JSON into Decipher-style XML.
    """
    root = ET.Element("survey")
    root.set("title", survey_json.get("title", "Untitled Survey"))
    root.set("language", survey_json.get("language", "en"))

    # Optional block wrapper for grouping questions
    block = ET.SubElement(root, "block")
    block.set("label", "b1")

    for q in survey_json.get("questions", []):
        qtype = q.get("type", "single_select")
        tag = TYPE_MAP.get(qtype, "radio")  # default to radio if unknown

        q_elem = ET.SubElement(block, tag)
        q_elem.set("label", _safe_label(q["id"]))
        _add_title(q_elem, q.get("text", q["id"]))

        # Options/rows for selectable types
        if tag in ("radio", "checkbox"):
            options = q.get("options") or []
            _add_rows(q_elem, q["id"], options)

        # Open text can include an optional <validate> or attributes if needed
        if tag == "open":
            # Example of optional attributes; adjust to your needs
            q_elem.set("size", "medium")

        # Matrix/grid handling placeholder (rows/cols depending on your schema)
        if tag == "grid":
            # If your JSON includes nested rows/columns, map them here.
            # Example structure:
            # q["rows"] -> <row> elements
            # q["cols"] -> <col> elements
            pass

    # Pretty print
    rough = ET.tostring(root, encoding="utf-8")
    pretty = minidom.parseString(rough).toprettyxml(indent="  ", encoding="utf-8")
    return pretty.decode("utf-8")
