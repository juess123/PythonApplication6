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
#检测线段是否穿越bbox
def segments_intersect(p1, p2, p3, p4):
    def cross(a, b, c):
        return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])

    d1 = cross(p1, p2, p3)
    d2 = cross(p1, p2, p4)
    d3 = cross(p3, p4, p1)
    d4 = cross(p3, p4, p2)

    return (d1 * d2 < 0) and (d3 * d4 < 0)
def segment_intersects_bbox(p0, p1, bbox):
    xmin, ymin, xmax, ymax = bbox

    # ---- 快速排除 ----
    if max(p0[0], p1[0]) < xmin or min(p0[0], p1[0]) > xmax:
        return False
    if max(p0[1], p1[1]) < ymin or min(p0[1], p1[1]) > ymax:
        return False

    # ---- 任一点在 bbox 内 ----
    if point_in_bbox(p0, bbox) or point_in_bbox(p1, bbox):
        return True

    # ---- 与 bbox 边相交 ----
    edges = [
        ((xmin, ymin), (xmax, ymin)),
        ((xmax, ymin), (xmax, ymax)),
        ((xmax, ymax), (xmin, ymax)),
        ((xmin, ymax), (xmin, ymin)),
    ]

    for e0, e1 in edges:
        if segments_intersect(p0, p1, e0, e1):
            return True

    return False

#检测线段是否穿越polygon
def segments_intersect(p1, p2, p3, p4):
    def cross(a, b, c):
        return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])

    d1 = cross(p1, p2, p3)
    d2 = cross(p1, p2, p4)
    d3 = cross(p3, p4, p1)
    d4 = cross(p3, p4, p2)

    return (d1 * d2 < 0) and (d3 * d4 < 0)
def segment_intersects_polygon(p0, p1, polygon):
    n = len(polygon)
    if n < 2:
        return False

    # ===== 1️⃣ 任一点在 polygon 内 =====
    if point_in_polygon(p0, polygon) or point_in_polygon(p1, polygon):
        return True

    # ===== 2️⃣ 与 polygon 边是否相交 =====
    for i in range(n):
        q0 = polygon[i]
        q1 = polygon[(i + 1) % n]

        if segments_intersect(p0, p1, q0, q1):
            return True

    return False








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


#s是否是圆



def sample_cubic_bezier(p0, p1, p2, p3, n=10):
    """
    在三次贝塞尔曲线上均匀采样 n+1 个点
    """
    if n <= 0:
        return [p0, p3]

    pts = []
    for i in range(n + 1):
        t = i / n
        mt = 1 - t

        x = (
            mt**3 * p0[0]
            + 3 * mt**2 * t * p1[0]
            + 3 * mt * t**2 * p2[0]
            + t**3 * p3[0]
        )
        y = (
            mt**3 * p0[1]
            + 3 * mt**2 * t * p1[1]
            + 3 * mt * t**2 * p2[1]
            + t**3 * p3[1]
        )
        pts.append((x, y))
    return pts


def is_circle_path(path,
                   bbox_tol_ratio=0.08,
                   radius_tol_ratio=0.08,
                   sample_per_seg=8,
                   min_radius=1.0):
    """
    判断一个 closed cubic bezier path 是否近似圆

    参数：
    - bbox_tol_ratio: 外接框宽高允许误差比例
    - radius_tol_ratio: 半径波动允许比例
    - sample_per_seg: 每段采样点数
    - min_radius: 最小半径限制，防止极小噪声图元误判
    """
    if not path.closed:
        return False

    segs = path.segments

    if len(segs) not in (4, 8):
        return False

    if not all(s.type == "cubic_bezier" for s in segs):
        return False

    # 1) 采样整条曲线
    pts = []
    for seg in segs:
        sampled = sample_cubic_bezier(seg.p0, seg.p1, seg.p2, seg.p3, n=sample_per_seg)
        if pts:
            sampled = sampled[1:]   # 避免段连接处重复点
        pts.extend(sampled)

    if len(pts) < 8:
        return False

    # 2) 看 bbox 是否接近正方形
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]

    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)

    w = max_x - min_x
    h = max_y - min_y

    if w <= 1e-6 or h <= 1e-6:
        return False

    wh_avg = (w + h) / 2.0
    if abs(w - h) / wh_avg > bbox_tol_ratio:
        return False

    # 3) 用采样点平均值求中心，比 bbox 中心更稳一点
    cx = sum(xs) / len(xs)
    cy = sum(ys) / len(ys)

    # 4) 所有采样点到中心的距离
    rs = [math.hypot(x - cx, y - cy) for x, y in pts]
    r_avg = sum(rs) / len(rs)

    if r_avg < min_radius:
        return False

    r_min = min(rs)
    r_max = max(rs)

    # 半径波动不能太大
    if (r_max - r_min) / r_avg > radius_tol_ratio:
        return False

    # 5) 再加一个兜底：平均半径应接近 bbox 推导出的半径
    bbox_r = (w + h) / 4.0
    if abs(r_avg - bbox_r) / max(r_avg, 1e-6) > 0.1:
        return False

    return True
# 提取圆参数
def get_circle_from_path(path):
    pts = []
    for s in path.segments:
        pts.append(s.p0)
        pts.append(s.p3)

    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]

    cx = (min(xs) + max(xs)) / 2
    cy = (min(ys) + max(ys)) / 2

    rs = [math.hypot(x - cx, y - cy) for x, y in pts]
    r = sum(rs) / len(rs)

    return (cx, cy), r

def path_is_closed(d):
    return 'z' in d.lower()
