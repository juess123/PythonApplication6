
def init_svg_root_geometry(root_elem, svg_root):


    # ---------- viewBox ----------
    viewbox = root_elem.attrib.get("viewBox")
    if not viewbox:
        raise RuntimeError("SVG missing viewBox")

    vb = viewbox.split()
    if len(vb) != 4:
        raise RuntimeError(f"Invalid viewBox: {viewbox}")

    svg_root.viewbox = tuple(map(float, vb))

    # ---------- width / height ----------
    def to_mm(val: str) -> float:
        val = val.strip().lower()

        if val.endswith("mm"):
            return float(val[:-2])
        if val.endswith("cm"):
            return float(val[:-2]) * 10.0
        if val.endswith("in"):
            return float(val[:-2]) * 25.4
        if val.replace(".", "", 1).isdigit():
            # ���� SVG ֱ�Ӹ���ֵ����Ϊ mm
            return float(val)

        raise RuntimeError(f"Unsupported SVG size unit: {val}")

    w_attr = root_elem.attrib.get("width")
    h_attr = root_elem.attrib.get("height")

    if not w_attr or not h_attr:
        raise RuntimeError("SVG missing width/height attributes")

    svg_root.width_mm = to_mm(w_attr)
    svg_root.height_mm = to_mm(h_attr)