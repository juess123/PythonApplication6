from lxml import etree
def is_global_background_rect(elem, svg_root, *, area_ratio=0.95, margin_ratio=0.02):

    if etree.QName(elem).localname != "rect":
        return False

    try:
        x = float(elem.attrib.get("x", "0"))
        y = float(elem.attrib.get("y", "0"))
        w = float(elem.attrib["width"])
        h = float(elem.attrib["height"])
    except Exception:
        return False

    vb_x, vb_y, vb_w, vb_h = svg_root.viewbox

    # ����ж�
    rect_area = w * h
    vb_area = vb_w * vb_h
    if rect_area < vb_area * area_ratio:
        return False

    # �߾��ж�
    mx = vb_w * margin_ratio
    my = vb_h * margin_ratio

    return (
        abs(x - vb_x) < mx and
        abs(y - vb_y) < my and
        abs((x + w) - (vb_x + vb_w)) < mx and
        abs((y + h) - (vb_y + vb_h)) < my
    )