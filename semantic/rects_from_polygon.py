from geometry.bbox import is_rectangle
import math

import math

def extract_rect_info(pts):
    import math

    # 计算4条边
    edges = []
    for i in range(4):
        p0 = pts[i]
        p1 = pts[i+1]
        dx = p1[0] - p0[0]
        dy = p1[1] - p0[1]
        length = math.hypot(dx, dy)
        edges.append((length, dx, dy))

    # 所有长度
    lengths = sorted([e[0] for e in edges])

    # 最短 & 最长
    height = lengths[0]
    width = lengths[-1]

    # center（对角线）
    p0, p2 = pts[0], pts[2]
    center = (
        (p0[0] + p2[0]) / 2,
        (p0[1] + p2[1]) / 2
    )

    # angle（最长边方向）
    longest_edge = max(edges, key=lambda e: e[0])
    angle = math.atan2(longest_edge[2], longest_edge[1])

    return {
        "center": center,
        "width": width,
        "height": height,
        "angle": angle
    }
def polygon_detect_rectangles(geoms):
    for g in geoms:
        if g["type"] != "polygon":
            continue
        pts = g["points"]
        # 1️⃣ 确保闭合
        if pts[0] != pts[-1]:
            pts = pts + [pts[0]]
            g["points"] = pts
        # 2️⃣ 判断是否矩形
        if not is_rectangle(pts):
            continue
        # 3️⃣ 标记语义
        g["semantic"] = "rect"
        g["role"] = "general"
        g["rect"] = extract_rect_info(pts)

    return geoms