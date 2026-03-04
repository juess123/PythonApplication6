# geometry/stroke/stroke_rect.py

def offset_rect_contour(contour, offset):
    """
    contour: [(x,y), ...]，不含重复闭合点
    offset: 正数向外，负数向内
    """
    xs = [p[0] for p in contour]
    ys = [p[1] for p in contour]

    xmin, xmax = min(xs), max(xs)
    ymin, ymax = min(ys), max(ys)

    return [
        (xmin - offset, ymin - offset),
        (xmax + offset, ymin - offset),
        (xmax + offset, ymax + offset),
        (xmin - offset, ymax + offset),
        (xmin - offset, ymin - offset),
    ]

def expand_rect_by_stroke(contour, stroke_width):
    """
    输入：一个 rect contour
    输出：[outer_contour, inner_contour]
    """
    d = stroke_width / 2.0

    if contour[0] == contour[-1]:
        base = contour[:-1]
    else:
        base = contour

    outer = offset_rect_contour(base, +d)
    inner = offset_rect_contour(base, -d)

    return [outer, inner]
