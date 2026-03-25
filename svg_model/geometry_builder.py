from geometry.parse import parse_path_d_multi
from geometry.bezier import quad_bezier, cubic_bezier
import re
# clipPath → 几何轮廓字典
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

                # ===== path =====
                if child.tag == "path":
                    d = child.attrib.get("d")
                    if not d:
                        continue

                    paths = parse_path_d_multi(d)

                    for path in paths:
                        contour = path_to_contour(path)

                        if len(contour) < 3:
                            continue

                        contour_r = [
                            (round(x, ndigits), round(y, ndigits))
                            for x, y in contour
                        ]

                        contours_all.append(contour_r)

                # ===== rect =====
                elif child.tag == "rect":
                    contour = rect_to_contour(child)
                    contours_all.append(contour)

            if contours_all:
                clip_geoms[clip_id] = contours_all

    return clip_geoms











# 把 <rect> 转成一个轮廓（contour）
# 输入（SVG）<rect width="100" height="50" transform="..."/>
# [
#     (x0, y0),
#     (x1, y1),
#     (x2, y2),
#     (x3, y3)
# ]
def rect_to_contour(node, ndigits=6):
    w = float(node.attrib.get("width", 0))
    h = float(node.attrib.get("height", 0))

    # 👉 默认局部坐标
    pts = [
        (0, 0),
        (w, 0),
        (w, h),
        (0, h),
    ]
    transform = node.attrib.get("transform")

    if transform and "matrix" in transform:
        import re

        nums = list(map(float, re.findall(r"[-\d.]+", transform)))
        a, b, c, d, e, f = nums

        def apply(p):
            x, y = p
            x_new = a*x + c*y + e
            y_new = b*x + d*y + f
            return (round(x_new, ndigits), round(y_new, ndigits))

        pts = [apply(p) for p in pts]

    return pts

# 把一个 path（贝塞尔/直线）转成“点”
def paths_to_contours(paths, sample_n=10):
    return [path_to_contour(p, sample_n) for p in paths]

def path_to_contour(path, sample_n=10):
    pts = []
    for i, seg in enumerate(path.segments):

        if i == 0:
            pts.append(seg.p0)

        if seg.type == "line":
            pts.append(seg.p1)

        elif seg.type == "cubic_bezier":
            curve = cubic_bezier(
                seg.p0, seg.p1, seg.p2, seg.p3, sample_n
            )
            pts.extend(curve[1:])

        elif seg.type == "quadratic_bezier":
            curve = quad_bezier(
                seg.p0, seg.p1, seg.p2, sample_n
            )
            pts.extend(curve[1:])

    # ===== 闭合处理 =====
    if path.closed and pts and pts[0] != pts[-1]:
        pts.append(pts[0])

    return pts






def parse_points(points_str):
    """
    SVG: "x1,y1 x2,y2 ..."
    → [(x1,y1), (x2,y2), ...]
    """
    pts = []
    for item in points_str.strip().split():
        if not item:
            continue
        x, y = item.split(",")
        pts.append((float(x), float(y)))

    # 🔥 有些 SVG 最后会重复第一个点（闭合）
    if len(pts) >= 2 and pts[0] == pts[-1]:
        pts.pop()

    return pts

def polygon_to_contours(node, eps=1e-6):
    points_str = node.attrib.get("points")
    if not points_str:
        return []

    contour = parse_points(points_str)

    # ===== 去重连续点 =====
    cleaned = []
    for p in contour:
        if not cleaned:
            cleaned.append(p)
        else:
            last = cleaned[-1]
            if abs(p[0]-last[0]) > eps or abs(p[1]-last[1]) > eps:
                cleaned.append(p)

    contour = cleaned

    if len(contour) < 3:
        return []

    # ===== 闭合（带容差）=====
    p0 = contour[0]
    p1 = contour[-1]

    if abs(p0[0]-p1[0]) > eps or abs(p0[1]-p1[1]) > eps:
        contour.append(p0)
    return [contour]



def rect_to_contours(node):
    try:
        x = float(node.attrib.get("x", 0))
        y = float(node.attrib.get("y", 0))
        w = float(node.attrib.get("width", 0))
        h = float(node.attrib.get("height", 0))
    except Exception:
        
        return []

    if w <= 0 or h <= 0:
        return []

    contour = [
        (x, y),
        (x + w, y),
        (x + w, y + h),
        (x, y + h),
        (x, y),
    ]
    return [contour]
def polyline_to_contours(node):
    points_str = node.attrib.get("points", "")
    if not points_str:
        return []

    # SVG points ֧�֣�x,y x,y �� x y x y
    tokens = points_str.replace(",", " ").split()
    if len(tokens) < 4 or len(tokens) % 2 != 0:
        return []

    pts = []
    try:
        for i in range(0, len(tokens), 2):
            x = float(tokens[i])
            y = float(tokens[i + 1])
            pts.append((x, y))
    except ValueError:
        return []

    if len(pts) < 2:
        return []

    return [pts]   
def line_to_contours(node):
    """
    SVG <line> �� contours
    ����һ�� contour��[ (x1,y1), (x2,y2) ]
    """
    x1 = float(node.attrib.get("x1", 0.0))
    y1 = float(node.attrib.get("y1", 0.0))
    x2 = float(node.attrib.get("x2", 0.0))
    y2 = float(node.attrib.get("y2", 0.0))

    return [[(x1, y1), (x2, y2)]]


def _is_number(s: str) -> bool:
    try:
        float(s)
        return True
    except ValueError:
        return False
def _require_numbers(tokens, i, n, d, cmd):
    for k in range(n):
        if i + k >= len(tokens) or not _is_number(tokens[i + k]):
            raise RuntimeError(
                f"[SVG PATH PARSE ERROR]\n"
                f" d = {d}\n"
                f" cmd = {cmd}\n"
                f" i = {i}\n"
                f" expect number at tokens[{i + k}]\n"
                f" token = {tokens[i + k] if i + k < len(tokens) else 'EOF'}\n"
                f" tokens = {tokens}\n"
            )




def parse_path_d_multi_to_contours(d):
    """
    解析 SVG path 的 d 属性
    返回：
        paths: List[List[(x, y)]]
    规则：
        - 只有遇到 Z/z 才真正闭合
        - open path 绝不偷偷首尾相连
    """
    tokens = re.findall(r"[MLCQZHVmlcqzhv]|-?\d+\.?\d*", d)
    paths = []
    current = []

    x = y = 0.0
    start = None
    i = 0
    cmd = None

    while i < len(tokens):
        t = tokens[i]
        
        # ====== 关键修复：立即处理 Z / z ======
        if t in ("Z", "z"):
            if current and start is not None:
                # 只在 Z 时闭合
                current.append(start)
                paths.append(current)
                current = []
                start = None
            i += 1
            continue
        # =====================================

        # 命令切换
        if t in "MLCQHVmlcqhv":
            cmd = t
            i += 1
            continue
        if cmd in ("M", "m", "L", "l", "Q", "q", "C", "c"):
            if not _is_number(tokens[i]):
                raise RuntimeError(
                    f"[SVG PATH PARSE ERROR]\n"
                    f" d = {d}\n"
                    f" cmd = {cmd}\n"
                    f" i = {i}\n"
                    f" token = {tokens[i]}\n"
                    f" tokens = {tokens}\n"
                )
        # ====== Move ======
        if cmd == "M":
            if current:
                paths.append(current)
                current = []
            _require_numbers(tokens, i, 2, d, cmd)
            x, y = float(tokens[i]), float(tokens[i + 1])
            start = (x, y)
            current.append((x, y))
            i += 2

        elif cmd == "m":
            if current:
                paths.append(current)
                current = []
            _require_numbers(tokens, i, 2, d, cmd)
            x += float(tokens[i])
            y += float(tokens[i + 1])
            start = (x, y)
            current.append((x, y))
            i += 2

        # ====== Line ======
        elif cmd == "L":
            _require_numbers(tokens, i, 2, d, cmd)
            x, y = float(tokens[i]), float(tokens[i + 1])
            current.append((x, y))
            i += 2
            
        elif cmd == "l":
            _require_numbers(tokens, i, 2, d, cmd)
            x += float(tokens[i])
            y += float(tokens[i + 1])
            current.append((x, y))
            i += 2

        # ====== Quadratic Bezier ======
        elif cmd == "Q":
            _require_numbers(tokens, i, 4, d, cmd)
            p1 = (float(tokens[i]), float(tokens[i + 1]))
            p2 = (float(tokens[i + 2]), float(tokens[i + 3]))

            
            curve = quad_bezier((x, y), p1, p2)
            

            current.extend(curve[1:])  # ⚠️ 不重复起点
            x, y = p2
            i += 4

        elif cmd == "q":
            _require_numbers(tokens, i, 4, d, cmd)
            p1 = (x + float(tokens[i]),     y + float(tokens[i + 1]))
            p2 = (x + float(tokens[i + 2]), y + float(tokens[i + 3]))

           
            curve = quad_bezier((x, y), p1, p2)
            
            
  
            current.extend(curve[1:])
            x, y = p2
            i += 4

        # ====== Cubic Bezier ======
        elif cmd == "C":
            _require_numbers(tokens, i, 6, d, cmd)
            p1 = (float(tokens[i]),     float(tokens[i + 1]))
            p2 = (float(tokens[i + 2]), float(tokens[i + 3]))
            p3 = (float(tokens[i + 4]), float(tokens[i + 5]))
            curve = cubic_bezier((x, y), p1, p2, p3)
            current.extend(curve[1:])
            x, y = p3
            i += 6

        elif cmd == "c":
            _require_numbers(tokens, i, 6, d, cmd)
            p1 = (x + float(tokens[i]),     y + float(tokens[i + 1]))
            p2 = (x + float(tokens[i + 2]), y + float(tokens[i + 3]))
            p3 = (x + float(tokens[i + 4]), y + float(tokens[i + 5]))
            curve = cubic_bezier((x, y), p1, p2, p3)
            current.extend(curve[1:])
            x, y = p3
            i += 6
        elif cmd == "H":
            _require_numbers(tokens, i, 1, d, cmd)
            x = float(tokens[i])
            current.append((x, y))
            i += 1


        elif cmd == "h":
            _require_numbers(tokens, i, 1, d, cmd)
            x += float(tokens[i])
            current.append((x, y))
            i += 1


        elif cmd == "V":
            _require_numbers(tokens, i, 1, d, cmd)
            y = float(tokens[i])
            current.append((x, y))
            i += 1


        elif cmd == "v":
            _require_numbers(tokens, i, 1, d, cmd)
            y += float(tokens[i])
            current.append((x, y))
            i += 1
        else:
            i += 1

    # ====== open path 收尾（不闭合） ======
    if current:
        paths.append(current)
    return paths
# SVG
#  ├── rect  ─────────────→ rect_to_contour
#  ├── path  ─────────────→ path_to_contour
#  │                         ↓
#  │                   paths_to_contours
#  │
#  └── defs/clipPath ───→ find_clip_geometries_from_defs
#                              ↓
#                       {clip_id: contours}