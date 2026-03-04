import math


def normalize(vx, vy):
    l = math.hypot(vx, vy)
    if l < 1e-9:
        return 0.0, 0.0
    return vx / l, vy / l


def edge_normal(p0, p1):
    dx = p1[0] - p0[0]
    dy = p1[1] - p0[1]
    return normalize(-dy, dx)  # 左法线


def line_intersection(p1, d1, p2, d2, eps=1e-9):
    cross = d1[0] * d2[1] - d1[1] * d2[0]
    if abs(cross) < eps:
        return None
    t = ((p2[0] - p1[0]) * d2[1] - (p2[1] - p1[1]) * d2[0]) / cross
    return (p1[0] + t * d1[0], p1[1] + t * d1[1])


def expand_polyline_by_stroke(points, stroke_width):
    if len(points) < 2:
        return []

    d = stroke_width * 0.5
    n = len(points)

    left = []
    right = []

    # ---------- left offset ----------
    for i in range(n):
        if i == 0:
            n0 = edge_normal(points[0], points[1])
            left.append((
                points[0][0] + n0[0] * d,
                points[0][1] + n0[1] * d,
            ))
        elif i == n - 1:
            n0 = edge_normal(points[-2], points[-1])
            left.append((
                points[-1][0] + n0[0] * d,
                points[-1][1] + n0[1] * d,
            ))
        else:
            p0, p1, p2 = points[i - 1], points[i], points[i + 1]
            n1 = edge_normal(p0, p1)
            n2 = edge_normal(p1, p2)

            a1 = (p0[0] + n1[0] * d, p0[1] + n1[1] * d)
            d1 = (p1[0] - p0[0], p1[1] - p0[1])

            a2 = (p1[0] + n2[0] * d, p1[1] + n2[1] * d)
            d2 = (p2[0] - p1[0], p2[1] - p1[1])

            ip = line_intersection(a1, d1, a2, d2)
            if ip is None:
                ip = (p1[0] + n1[0] * d, p1[1] + n1[1] * d)
            left.append(ip)

    # ---------- right offset ----------
    for i in range(n):
        if i == 0:
            n0 = edge_normal(points[0], points[1])
            right.append((
                points[0][0] - n0[0] * d,
                points[0][1] - n0[1] * d,
            ))
        elif i == n - 1:
            n0 = edge_normal(points[-2], points[-1])
            right.append((
                points[-1][0] - n0[0] * d,
                points[-1][1] - n0[1] * d,
            ))
        else:
            p0, p1, p2 = points[i - 1], points[i], points[i + 1]
            n1 = edge_normal(p0, p1)
            n2 = edge_normal(p1, p2)

            a1 = (p0[0] - n1[0] * d, p0[1] - n1[1] * d)
            d1 = (p1[0] - p0[0], p1[1] - p0[1])

            a2 = (p1[0] - n2[0] * d, p1[1] - n2[1] * d)
            d2 = (p2[0] - p1[0], p2[1] - p1[1])

            ip = line_intersection(a1, d1, a2, d2)
            if ip is None:
                ip = (p1[0] - n1[0] * d, p1[1] - n1[1] * d)
            right.append(ip)

    # ---------- 正确的端帽（关键） ----------
    # 起点 cap
    nx0, ny0 = edge_normal(points[0], points[1])
    start_cap = (
        points[0][0] - nx0 * d,
        points[0][1] - ny0 * d,
    )

    # 终点 cap
    nx1, ny1 = edge_normal(points[-2], points[-1])
    end_cap = (
        points[-1][0] - nx1 * d,
        points[-1][1] - ny1 * d,
    )

    # ---------- 拼成真正闭合 polygon ----------
    polygon = []

    # 1️⃣ 左边：起点 → 终点
    polygon.extend(left)

    # 2️⃣ 终点端帽：left[-1] → right[-1]
    polygon.append(right[-1])

    # 3️⃣ 右边：终点 → 起点
    polygon.extend(reversed(right))

    # 4️⃣ 起点端帽：right[0] → left[0]
    polygon.append(left[0])

    # 5️⃣ 闭合
    polygon.append(polygon[0])

    return [polygon]
