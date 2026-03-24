def has_hline(horizontal, y, x1, x2, eps):
    for hy, hx1, hx2 in horizontal:
        if abs(hy - y) < eps:
            if hx1 <= x1 + eps and hx2 >= x2 - eps:
                return True
    return False


def has_vline(vertical, x, y1, y2, eps):
    for vx, vy1, vy2 in vertical:
        if abs(vx - x) < eps:
            if vy1 <= y1 + eps and vy2 >= y2 - eps:
                return True
    return False
def build_rectangles_from_lines(segments, eps=0.5):
    horizontal = []
    vertical = []


    # 1️⃣ 分类
    for x0, y0, x1, y1 in segments:
        if abs(y0 - y1) < eps:
            y = (y0 + y1) / 2
            horizontal.append((y, min(x0, x1), max(x0, x1)))

        elif abs(x0 - x1) < eps:
            x = (x0 + x1) / 2
            vertical.append((x, min(y0, y1), max(y0, y1)))

    if len(horizontal) < 2 or len(vertical) < 2:
        return []

    # 2️⃣ 聚类（🔥关键）
    def cluster(vals):
        vals = sorted(vals)
        groups = []

        for v in vals:
            if not groups or abs(groups[-1][-1] - v) > eps:
                groups.append([v])
            else:
                groups[-1].append(v)

        return [sum(g)/len(g) for g in groups]

    ys = cluster([h[0] for h in horizontal])
    xs = cluster([v[0] for v in vertical])

    rects = []

    # 3️⃣ 尝试组合
    for i in range(len(ys)):
        for j in range(i + 1, len(ys)):
            y1 = ys[i]
            y2 = ys[j]

            for k in range(len(xs)):
                for l in range(k + 1, len(xs)):
                    x1 = xs[k]
                    x2 = xs[l]

                    if (
                        has_hline(horizontal, y1, x1, x2, eps)
                        and has_hline(horizontal, y2, x1, x2, eps)
                        and has_vline(vertical, x1, y1, y2, eps)
                        and has_vline(vertical, x2, y1, y2, eps)
                    ):
                        rects.append((x1, y1, x2, y2))

    return rects
def lines_dect_rects(geoms, eps=0.5):

    # 🔥 直接从 geoms 里找 line
    lines = [
        g for g in geoms
        if isinstance(g, dict) and g.get("type") == "line"
    ]

    # print("\n=== ALL LINES ===")
    # for l in lines:
    #     print(f"LINE: {l['p0']} -> {l['p1']}")

    if len(lines) < 4:
        return geoms

    segments = []
    for l in lines:
        x0, y0 = l["p0"]
        x1, y1 = l["p1"]
        segments.append((x0, y0, x1, y1))

    rects = build_rectangles_from_lines(segments, eps)

    if not rects:
        return geoms

    out = []

    for r in rects:
        x_min, y_min, x_max, y_max = r

        cx = (x_min + x_max) / 2
        cy = (y_min + y_max) / 2
        width = x_max - x_min
        height = y_max - y_min

        rect = {
            "center": (cx, cy),
            "width": width,
            "height": height,
            "angle": 0
        }

        g = {
            "type": "rect",
            "semantic": "rect",
            "role": "line_to_rect",
            "rect": rect
        }

        out.append(g)

    return out