import math


# ---------- 基础几何 ----------

def polygon_area(contour):
    s = 0.0
    n = len(contour)
    for i in range(n):
        x1, y1 = contour[i]
        x2, y2 = contour[(i + 1) % n]
        s += (x1 * y2 - x2 * y1)
    return 0.5 * s


def ensure_ccw(contour):
    if polygon_area(contour) < 0:
        return list(reversed(contour))
    return contour


def normalize(vx, vy):
    l = math.hypot(vx, vy)
    if l < 1e-12:
        return 0.0, 0.0
    return vx / l, vy / l


def edge_normal(p0, p1):
    dx = p1[0] - p0[0]
    dy = p1[1] - p0[1]
    # CCW polygon: 左法线 = 外法线
    return normalize(-dy, dx)


def line_intersection(p1, d1, p2, d2, eps=1e-9):
    cross = d1[0] * d2[1] - d1[1] * d2[0]
    if abs(cross) < eps:
        return None

    t = ((p2[0] - p1[0]) * d2[1] - (p2[1] - p1[1]) * d2[0]) / cross
    return (p1[0] + t * d1[0], p1[1] + t * d1[1])


# ---------- Polygon Offset ----------

def offset_polygon(contour, offset):
    """
    contour: CCW, 不带重复闭合点
    offset: >0 外扩，<0 内缩
    """
    n = len(contour)
    if n < 3:
        return []

    MITER_LIMIT = abs(offset) * 4.0
    out = []

    for i in range(n):
        p0 = contour[(i - 1) % n]
        p1 = contour[i]
        p2 = contour[(i + 1) % n]

        n1 = edge_normal(p0, p1)
        n2 = edge_normal(p1, p2)

        # 偏移线 1
        a1 = (p0[0] + n1[0] * offset, p0[1] + n1[1] * offset)
        d1 = (p1[0] - p0[0], p1[1] - p0[1])

        # 偏移线 2
        a2 = (p1[0] + n2[0] * offset, p1[1] + n2[1] * offset)
        d2 = (p2[0] - p1[0], p2[1] - p1[1])

        ip = line_intersection(a1, d1, a2, d2)

        if ip is not None:
            dx = ip[0] - p1[0]
            dy = ip[1] - p1[1]
            if math.hypot(dx, dy) > MITER_LIMIT:
                ip = None

        if ip is None:
            # bevel fallback
            ip = (
                p1[0] + n1[0] * offset,
                p1[1] + n1[1] * offset,
            )

        out.append(ip)

    return out


# ---------- SVG stroke 扩展 ----------

def expand_polygon_by_stroke(contour, stroke_width):
    d = stroke_width * 0.5

    # 去掉重复闭合点
    if contour[0] == contour[-1]:
        base = contour[:-1]
    else:
        base = contour

    base = ensure_ccw(base)

    outer = offset_polygon(base, +d)
    inner = offset_polygon(base, -d)

    rings = []

    if outer and len(outer) >= 3:
        rings.append(outer + [outer[0]])

    if inner and len(inner) >= 3:
        rings.append(inner + [inner[0]])

    if not rings:
        return []

    # —— 关键：按面积从大到小排序 ——
    rings.sort(
        key=lambda r: abs(polygon_area(r)),
        reverse=True
    )

    return rings

