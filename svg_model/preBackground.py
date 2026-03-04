from lxml import etree
from geometry.element_bbox import get_element_bbox
from geometry.bbox import is_simple_path
def iter_last_graphic_elements(root_elem, max_check=10):
    graphics = []

    for elem in root_elem.iter():
        tag = etree.QName(elem).localname
        if tag in ("rect", "path", "polygon"):
            graphics.append(elem)

    return graphics[-max_check:]

def is_global_like_bbox(
    bbox,
    ref_bbox,
    *,
    area_ratio=0.95,
    margin_ratio=0.02,
    width_ratio=0.8,   # ⭐ 新增
):
    x1, y1, x2, y2 = bbox
    w = x2 - x1
    h = y2 - y1

    rx1, ry1, rx2, ry2 = ref_bbox
    rw = rx2 - rx1
    rh = ry2 - ry1

    # ===============================
    # ⭐ 规则 B：宽度接近即可
    # ===============================
    if rw > 0 and (w / rw) >= width_ratio:
        return True

    # ===============================
    # 规则 A：完整 bbox 接近
    # ===============================
    if w * h < rw * rh * area_ratio:
        return False

    mx = rw * margin_ratio
    my = rh * margin_ratio

    if abs(x1 - rx1) > mx:
        return False
    if abs(y1 - ry1) > my:
        return False
    if abs(x2 - rx2) > mx:
        return False
    if abs(y2 - ry2) > my:
        return False

    return True


def remove_tail_global_like_elements(
    root_elem,
    svg_root,
    *,
    max_check=10,
    area_ratio=0.95,
    margin_ratio=0.02,
):
    from lxml import etree

    tail = iter_last_graphic_elements(root_elem, max_check=max_check)
    ref_bbox = get_global_reference_bbox(root_elem, svg_root)

    for elem in reversed(tail):
        tag = etree.QName(elem).localname

        bbox = get_element_bbox(elem)
        if not bbox:
            continue

        # ---------- 类型过滤 ----------
        if tag == "rect":
            allow = True

        elif tag == "path":
            # 只允许“极其简单”的 path
            d = elem.attrib.get("d", "")
            if is_simple_path(d):
                allow = True
            else:
                allow = False
        else:
            allow = False

        if not allow:
            continue
        # --------------------------------

        if is_global_like_bbox(
            bbox,
            ref_bbox,
            area_ratio=area_ratio,
            margin_ratio=margin_ratio,
        ):
            parent = elem.getparent()
            if parent is not None:
                cls = elem.attrib.get("class", "")
                print(f"[REMOVE] <{tag} class=\"{cls}\"> bbox={bbox}")
                parent.remove(elem)


def get_global_reference_bbox(root_elem, svg_root):
    """
    获取全局参考 bbox：
    优先使用第一个 <g> 的第一个图形元素，
    否则退回到 svg viewBox
    """
    # ① 尝试从第一个 g 里取
    for elem in root_elem:
        if etree.QName(elem).localname == "g":
            for child in elem.iter():
                tag = etree.QName(child).localname
                if tag in ("rect", "path", "polygon"):
                    bbox = get_element_bbox(child)
                    if bbox:
                        return bbox
            break  # 只看第一个 g

    # ② fallback：viewBox
    vb_x, vb_y, vb_w, vb_h = svg_root.viewbox
    return (vb_x, vb_y, vb_x + vb_w, vb_y + vb_h)
