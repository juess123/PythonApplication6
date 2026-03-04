def contour_is_closed(contour, eps=1e-6):
    """
    判断一个 path 轮廓是否闭合（几何级）
    contour: [(x, y), ...]
    """
    if len(contour) < 3:
        return False

    x0, y0 = contour[0]
    x1, y1 = contour[-1]

    return abs(x0 - x1) < eps and abs(y0 - y1) < eps
def compute_centroid(contour):
    """
    简单多边形质心（平均法，工程上足够）
    """
    sx = sy = 0.0
    n = len(contour)
    for x, y in contour:
        sx += x
        sy += y
    return sx / n, sy / n
def scale_contour(contour, center, offset):
    """
    将轮廓相对于中心点做径向缩放
    offset > 0  : 向外
    offset < 0  : 向内
    """
    cx, cy = center
    out = []

    for x, y in contour:
        vx = x - cx
        vy = y - cy

        length = (vx * vx + vy * vy) ** 0.5
        if length == 0:
            out.append((x, y))
            continue

        nx = vx / length
        ny = vy / length

        out.append((
            x + nx * offset,
            y + ny * offset,
        ))

    return out

def expand_closed_path_by_stroke(contour, stroke_width):
    """
    闭合 path 的 stroke 扩展：
    返回 [outer_contour, inner_contour]
    """
    half = stroke_width / 2.0

    center = compute_centroid(contour)

    outer = scale_contour(contour, center, +half)
    inner = scale_contour(contour, center, -half)

    return [outer, inner]
