# geometry/element_bbox.py

from lxml import etree

from geometry.bbox import contour_to_bbox
from geometry.adapters import (
    polygon_to_contours,
    rect_to_contours,
    polyline_to_contours,
    line_to_contours,
)
from geometry.parse import parse_path_d_multi


def get_element_bbox(node):
    tag = etree.QName(node.tag).localname

    contours = []

    # -------- path --------
    if tag == "path":
        d = node.attrib.get("d")
        if not d:
            return None
        contours = parse_path_d_multi(d)

    # -------- rect --------
    elif tag == "rect":
        contours = rect_to_contours(node)

    # -------- polygon --------
    elif tag == "polygon":
        contours = polygon_to_contours(node)

    # -------- polyline --------
    elif tag == "polyline":
        contours = polyline_to_contours(node)

    # -------- line --------
    elif tag == "line":
        contours = line_to_contours(node)

    # -------- image --------
    elif tag == "image":
        try:
            x = float(node.attrib.get("x", 0))
            y = float(node.attrib.get("y", 0))
            w = float(node.attrib.get("width", 0))
            h = float(node.attrib.get("height", 0))
        except Exception:
            return None

        if w <= 0 or h <= 0:
            return None

        return (x, y, x + w, y + h)

    else:
        return None

    # -------- contours �� bbox --------
    if not contours:
        return None

    bboxes = []
    for contour in contours:
        if len(contour) < 2:
            continue
        try:
            bboxes.append(contour_to_bbox(contour))
        except Exception:
            continue

    if not bboxes:
        return None

    xmin = min(b[0] for b in bboxes)
    ymin = min(b[1] for b in bboxes)
    xmax = max(b[2] for b in bboxes)
    ymax = max(b[3] for b in bboxes)

    return (xmin, ymin, xmax, ymax)
