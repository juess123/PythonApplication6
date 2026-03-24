import math
import re
#能包住它的最小矩形
def contour_to_bbox(contour):
    """
    contour: [(x, y), (x, y), ...]
    return: (xmin, ymin, xmax, ymax)
    """
    xs = [x for x, y in contour]
    ys = [y for x, y in contour]
    return min(xs), min(ys), max(xs), max(ys)
#点 是否 在矩形框内
def point_in_bbox(p, bbox, eps=1e-6):
    x, y = p
    xmin, ymin, xmax, ymax = bbox
    return (xmin - eps <= x <= xmax + eps) and (ymin - eps <= y <= ymax + eps)
#点 是否 在多线框内
def point_in_polygon(point, polygon):
    x, y = point
    inside = False

    n = len(polygon)
    if n < 3:
        return False

    x0, y0 = polygon[0]
    for i in range(1, n + 1):
        x1, y1 = polygon[i % n]

        if ((y0 > y) != (y1 > y)):
            xinters = (y - y0) * (x1 - x0) / (y1 - y0 + 1e-12) + x0
            if x < xinters:
                inside = not inside

        x0, y0 = x1, y1

    return inside
#如果两个矩形有重叠，那重叠区域的边界在哪里
def intersect_bbox(b1, b2):
    """
    b = (xmin, ymin, xmax, ymax)
    """
    x1 = max(b1[0], b2[0])
    y1 = max(b1[1], b2[1])
    x2 = min(b1[2], b2[2])
    y2 = min(b1[3], b2[3])

    if x1 >= x2 or y1 >= y2:
        return None

    return (x1, y1, x2, y2)
#判断是不是一个 tuple
def is_bbox_clip(clip):
    return isinstance(clip, tuple) and len(clip) == 4
#判断是不是多边形的    
def polygon_has_area(pts, eps=1e-6):
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return (max(xs) - min(xs) > eps) and (max(ys) - min(ys) > eps)
#简单 path 判断函数 
def is_simple_path(d: str) -> bool:
    if not d:
        return False

    # 1️⃣ 长度限制（文字轮廓通常几千字符）
    if len(d) > 200:
        return False

    # 2️⃣ 只允许简单指令
    commands = re.findall(r"[a-zA-Z]", d)

    # 允许的简单矩形类命令
    allowed = set("MmLlHhVvZz")

    if not set(commands).issubset(allowed):
        return False

    # 3️⃣ 命令数量不能太多
    if len(commands) > 20:
        return False

    return True

#判断是否是 矩形
def is_rectangle(pts, angle_tol=1e-2, length_tol=1e-6):
    """
    pts: [(x,y), ...] 必须闭合（5个点）
    angle_tol: 垂直容忍度（越大越宽松）
    length_tol: 长度容忍
    """

    # 1️⃣ 点数检查（闭合）
    if len(pts) != 5:
        return False

    # 2️⃣ 构造4条边向量
    def vec(a, b):
        return (b[0] - a[0], b[1] - a[1])

    v = [vec(pts[i], pts[i+1]) for i in range(4)]

    # 3️⃣ 向量长度
    def length(v):
        return math.hypot(v[0], v[1])

    lengths = [length(e) for e in v]

    # 防止退化边
    if any(l < length_tol for l in lengths):
        return False

    # 4️⃣ 点积（判断垂直）
    def dot(a, b):
        return a[0]*b[0] + a[1]*b[1]

    # 归一化点积（避免尺度影响）
    def is_perpendicular(a, b):
        return abs(dot(a, b)) / (length(a)*length(b)) < angle_tol

    # 5️⃣ 叉积（判断平行）
    def cross(a, b):
        return a[0]*b[1] - a[1]*b[0]

    def is_parallel(a, b):
        return abs(cross(a, b)) / (length(a)*length(b)) < angle_tol

    # 6️⃣ 相邻边垂直
    if not is_perpendicular(v[0], v[1]): return False
    if not is_perpendicular(v[1], v[2]): return False
    if not is_perpendicular(v[2], v[3]): return False
    if not is_perpendicular(v[3], v[0]): return False

    # 7️⃣ 对边平行
    if not is_parallel(v[0], v[2]): return False
    if not is_parallel(v[1], v[3]): return False

    return True