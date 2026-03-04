from geometry.bbox import point_in_bbox, point_in_polygon,is_bbox_clip

#polygon 精裁剪层
def clip_segment_to_polygon(p0, p1, polygon):
    """
    返回：
      - None
      - (q0, q1)
    """
    inside0 = point_in_polygon(p0, polygon)
    inside1 = point_in_polygon(p1, polygon)

    if inside0 and inside1:
        return p0, p1

    intersections = segment_polygon_intersections(p0, p1, polygon)

    if inside0 and intersections:
        return p0, intersections[0]

    if inside1 and intersections:
        return intersections[0], p1

    if len(intersections) >= 2:
        return intersections[0], intersections[1]

    return None
def segment_polygon_intersections(p0, p1, polygon):
    """
    返回线段 p0-p1 与 polygon 边界的交点列表
    """
    intersections = []

    n = len(polygon)
    if n < 3:
        return intersections

    # 遍历多边形每一条边
    for i in range(n):
        a = polygon[i]
        b = polygon[(i + 1) % n]

        ip = segment_intersection(p0, p1, a, b)
        if ip is not None:
            intersections.append(ip)

    # ---- 去重（防止顶点被算两次）----
    uniq = []
    eps = 1e-6
    for p in intersections:
        if not any(abs(p[0]-q[0]) < eps and abs(p[1]-q[1]) < eps for q in uniq):
            uniq.append(p)

    # ---- 按 p0 -> p1 方向排序 ----
    def t_of(p):
        dx = p1[0] - p0[0]
        dy = p1[1] - p0[1]
        if abs(dx) >= abs(dy):
            return (p[0] - p0[0]) / (dx if dx != 0 else 1)
        else:
            return (p[1] - p0[1]) / (dy if dy != 0 else 1)

    uniq.sort(key=t_of)
    return uniq
def segment_intersection(p0, p1, p2, p3, eps=1e-9):
    """
    判断线段 p0-p1 与 p2-p3 是否相交
    返回：
      - None
      - (x, y) 交点
    """
    x1, y1 = p0
    x2, y2 = p1
    x3, y3 = p2
    x4, y4 = p3

    # 1️⃣ 计算行列式（判断是否平行）
    denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if abs(denom) < eps:
        return None  # 平行或共线（当前阶段直接忽略）

    # 2️⃣ 求无限直线的交点
    px = (
        (x1 * y2 - y1 * x2) * (x3 - x4) -
        (x1 - x2) * (x3 * y4 - y3 * x4)
    ) / denom

    py = (
        (x1 * y2 - y1 * x2) * (y3 - y4) -
        (y1 - y2) * (x3 * y4 - y3 * x4)
    ) / denom

    # 3️⃣ 判断交点是否在线段范围内
    def on_segment(x, y, xa, ya, xb, yb):
        return (
            min(xa, xb) - eps <= x <= max(xa, xb) + eps and
            min(ya, yb) - eps <= y <= max(ya, yb) + eps
        )

    if (
        on_segment(px, py, x1, y1, x2, y2) and
        on_segment(px, py, x3, y3, x4, y4)
    ):
        return (px, py)

    return None
def clip_contours_to_polygon_segments(contours, polygon):
    segments = []

    for contour in contours:
        if len(contour) < 2:
            continue

        for i in range(len(contour) - 1):
            p0 = contour[i]
            p1 = contour[i + 1]

            clipped = clip_segment_to_polygon(p0, p1, polygon)
            if clipped is None:
                continue

            q0, q1 = clipped
            segments.append((q0, q1))

    return segments
#入口函数 
def clip_contours_to_segments(contours, clip):
    """
    clip:
      - bbox: (xmin, ymin, xmax, ymax)
      - polygon: [(x,y), ...]
    """
    if is_bbox_clip(clip):
        return clip_contours_to_bbox_segments(contours, clip)
    else:
        return clip_contours_to_polygon_segments(contours, clip)
def classify_contours_by_clip(contours, clip):
    """
    返回：
    - "inside"
    - "partial"
    - "outside"
    clip:
      - bbox: (xmin, ymin, xmax, ymax)
      - polygon: [(x, y), ...]
    """
    inside = False
    outside = False

    is_bbox = (
        isinstance(clip, tuple)
        and len(clip) == 4
    )
   
    for contour in contours:
        for p in contour:
            if is_bbox:
                in_clip = point_in_bbox(p, clip)
            else:
                in_clip = point_in_polygon(p, clip)

            if in_clip:
                inside = True
            else:
                outside = True

    if inside and not outside:
        return "inside"
    if inside and outside:
        return "partial"
    return "outside"
#bbox 快裁剪层
def clip_segment_to_bbox(p0, p1, bbox):
    """
    Liang-Barsky line clipping
    返回：
      None                 → 线段完全在 bbox 外
      (q0, q1)             → 裁剪后的线段（两个点）
    """
    x0, y0 = p0
    x1, y1 = p1
    xmin, ymin, xmax, ymax = bbox

    dx = x1 - x0
    dy = y1 - y0

    p = [-dx, dx, -dy, dy]
    q = [x0 - xmin, xmax - x0, y0 - ymin, ymax - y0]

    u1, u2 = 0.0, 1.0

    for pi, qi in zip(p, q):
        if pi == 0:
            if qi < 0:
                return None
        else:
            t = qi / pi
            if pi < 0:
                if t > u2:
                    return None
                if t > u1:
                    u1 = t
            else:
                if t < u1:
                    return None
                if t < u2:
                    u2 = t

    if u1 > u2:
        return None

    cx0 = x0 + u1 * dx
    cy0 = y0 + u1 * dy
    cx1 = x0 + u2 * dx
    cy1 = y0 + u2 * dy

    return (cx0, cy0), (cx1, cy1)
def clip_contours_to_bbox_segments(contours, bbox):
    """
    对 contours 里的每一条线段做 bbox 裁剪
    返回：List[ (p0, p1) ]
    """
    segments = []

    for contour in contours:
        if len(contour) < 2:
            continue

        for i in range(len(contour) - 1):
            p0 = contour[i]
            p1 = contour[i + 1]

            clipped = clip_segment_to_bbox(p0, p1, bbox)
            if clipped is None:
                continue

            q0, q1 = clipped
            segments.append((q0, q1))

    return segments



