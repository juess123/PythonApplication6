from geometry.bezier import quad_bezier,cubic_bezier
import re
# 这些函数做的事只有一件：
# 把不同 SVG 图元（polygon / rect / polyline / line）
# 统一转换成“contours（点序列）”这种内部几何表示。
def vec(a, b):
    return (b[0] - a[0], b[1] - a[1])

def dot(a, b):
    return a[0]*b[0] + a[1]*b[1]

def length(v):
    return (v[0]**2 + v[1]**2) ** 0.5


def is_rectangle(points, eps=1e-3):
    if len(points) != 4:
        return False

    # 👉 保证顺序一致（很重要）
    points = sort_points_clockwise(points)

    # ===== 1️⃣ 判断四个角都是直角 =====
    for i in range(4):
        a = points[i]
        b = points[(i + 1) % 4]
        c = points[(i + 2) % 4]

        ab = vec(a, b)
        bc = vec(b, c)

        if abs(dot(ab, bc)) > eps * (length(ab) * length(bc)):
            return False

    # ===== 2️⃣ 对边长度相等 =====
    d0 = length(vec(points[0], points[1]))
    d1 = length(vec(points[1], points[2]))
    d2 = length(vec(points[2], points[3]))
    d3 = length(vec(points[3], points[0]))

    if abs(d0 - d2) > eps or abs(d1 - d3) > eps:
        return False

    return True


def sort_points_clockwise(points):
    cx = sum(p[0] for p in points) / len(points)
    cy = sum(p[1] for p in points) / len(points)

    def angle(p):
        import math
        return math.atan2(p[1] - cy, p[0] - cx)

    return sorted(points, key=angle)

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