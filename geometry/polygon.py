from geometry.vector import vec,length,dot
def sort_points_clockwise(points):
    cx = sum(p[0] for p in points) / len(points)
    cy = sum(p[1] for p in points) / len(points)

    def angle(p):
        import math
        return math.atan2(p[1] - cy, p[0] - cx)

    return sorted(points, key=angle)

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