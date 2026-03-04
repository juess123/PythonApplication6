
from geometry.parse import parse_path_d_multi
import re

_CLIP_RE = re.compile(r"url\(#([^)]+)\)")
#下面两个是处理 图片的 加上矩形框 主要是给其他文件使用
def _extract_clip_from_node(node):
    """只从当前节点提取 clip-path，不看父节点"""
    clip = node.attrib.get("clip-path")
    if clip:
        m = _CLIP_RE.search(clip)
        if m:
            return m.group(1)

    style = node.attrib.get("style", "")
    if style:
        m = _CLIP_RE.search(style)
        if m:
            return m.group(1)

    return None
def resolve_clip_id(node):
    """
    clip-path 解析规则（兼容旧版本）：
    1️⃣ 自己有 → 用自己的
    2️⃣ 自己没有 → 向上找最近父节点
    """
    # ① 自身优先
    own = _extract_clip_from_node(node)
    if own:
        return own

    # ② 向上查找（注意：SvgNode 用 parent）
    cur = node.parent
    while cur is not None:
        parent_clip = _extract_clip_from_node(cur)
        if parent_clip:
            return parent_clip
        cur = cur.parent

    return None




#下面两个是处理裁剪框的 
def rect_to_contour(node, ndigits=6):
    x = float(node.attrib.get("x", 0))
    y = float(node.attrib.get("y", 0))
    w = float(node.attrib.get("width", 0))
    h = float(node.attrib.get("height", 0))

    return [
        (round(x, ndigits), round(y, ndigits)),
        (round(x + w, ndigits), round(y, ndigits)),
        (round(x + w, ndigits), round(y + h, ndigits)),
        (round(x, ndigits), round(y + h, ndigits)),
    ]

def find_clip_geometries_from_defs(doc, ndigits=6):
    clip_geoms = {}
    defs_nodes = [n for n in doc.nodes if n.tag == "defs"]
    if not defs_nodes:
        return clip_geoms

    for defs in defs_nodes:
        for node in getattr(defs, "children", []):
            if node.tag != "clipPath":
                continue

            clip_id = node.attrib.get("id")
            if not clip_id:
                continue

            contours_all = []

            for child in getattr(node, "children", []):
                if child.tag == "path":
                    d = child.attrib.get("d")
                    if not d:
                        continue

                    contours = parse_path_d_multi(d)
                    for contour in contours:
                        if len(contour) < 3:
                            continue

                        contour_r = [
                            (round(x, ndigits), round(y, ndigits))
                            for x, y in contour
                        ]
                        contours_all.append(contour_r)

                elif child.tag == "rect":
                    contour = rect_to_contour(child, ndigits)
                    contours_all.append(contour)

            if contours_all:
                clip_geoms[clip_id] = contours_all

    return clip_geoms
