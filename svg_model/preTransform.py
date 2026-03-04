import re
from lxml import etree
_MATRIX_RE = re.compile(r"matrix\(([^)]+)\)")

def parse_matrix(tf: str):
    """
    matrix(a b c d e f)
    """
    m = _MATRIX_RE.search(tf)
    if not m:
        return None

    nums = [float(x) for x in m.group(1).replace(",", " ").split()]
    if len(nums) != 6:
        return None

    return nums  # a,b,c,d,e,f
def apply_matrix_to_point(x, y, a, b, c, d, e, f):
    nx = a * x + c * y + e
    ny = b * x + d * y + f
    return nx, ny
def flatten_rotated_rect(elem):
    tf = elem.attrib.get("transform")
    mat = parse_matrix(tf)
    if not mat:
        return False

    try:
        w = float(elem.attrib.get("width"))
        h = float(elem.attrib.get("height"))
    except Exception:
        return False

    a, b, c, d, e, f = mat

    pts = [
        apply_matrix_to_point(0, 0, a, b, c, d, e, f),
        apply_matrix_to_point(w, 0, a, b, c, d, e, f),
        apply_matrix_to_point(w, h, a, b, c, d, e, f),
        apply_matrix_to_point(0, h, a, b, c, d, e, f),
    ]

    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]

    x1, y1 = min(xs), min(ys)
    x2, y2 = max(xs), max(ys)

    # ✨ 重写 rect
    elem.attrib.pop("transform", None)
    elem.attrib["x"] = f"{x1:.6f}"
    elem.attrib["y"] = f"{y1:.6f}"
    elem.attrib["width"] = f"{(x2 - x1):.6f}"
    elem.attrib["height"] = f"{(y2 - y1):.6f}"

    return True
def flatten_rotated_rects(root_elem):
    fixed = 0

    for elem in root_elem.iter():
        if etree.QName(elem).localname != "rect":
            continue

        tf = elem.attrib.get("transform")
        if not tf or "matrix" not in tf:
            continue

        if flatten_rotated_rect(elem):
            fixed += 1

    if fixed:
        print(f"[CLEAN] flattened rotated rects = {fixed}")
