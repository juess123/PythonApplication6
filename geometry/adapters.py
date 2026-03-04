from geometry.parse import parse_polygon_points


# 这些函数做的事只有一件：
# 把不同 SVG 图元（polygon / rect / polyline / line）
# 统一转换成“contours（点序列）”这种内部几何表示。
def polygon_to_contours(node):
    points = node.attrib.get("points")
    if not points:
        return []

    contour = parse_polygon_points(points)
    if len(contour) < 3:
        return []

    # �պ�
    if contour[0] != contour[-1]:
        contour = contour + [contour[0]]

    return [contour]
def rect_to_contours(node):
    try:
        x = float(node.attrib.get("x", 0))
        y = float(node.attrib.get("y", 0))
        w = float(node.attrib.get("width", 0))
        h = float(node.attrib.get("height", 0))
    except Exception:
        return []

    if w <= 0 or h <= 0:
        return []

    contour = [
        (x, y),
        (x + w, y),
        (x + w, y + h),
        (x, y + h),
        (x, y),
    ]
    return [contour]
def polyline_to_contours(node):
    points_str = node.attrib.get("points", "")
    if not points_str:
        return []

    # SVG points ֧�֣�x,y x,y �� x y x y
    tokens = points_str.replace(",", " ").split()
    if len(tokens) < 4 or len(tokens) % 2 != 0:
        return []

    pts = []
    try:
        for i in range(0, len(tokens), 2):
            x = float(tokens[i])
            y = float(tokens[i + 1])
            pts.append((x, y))
    except ValueError:
        return []

    if len(pts) < 2:
        return []

    return [pts]   
def line_to_contours(node):
    """
    SVG <line> �� contours
    ����һ�� contour��[ (x1,y1), (x2,y2) ]
    """
    x1 = float(node.attrib.get("x1", 0.0))
    y1 = float(node.attrib.get("y1", 0.0))
    x2 = float(node.attrib.get("x2", 0.0))
    y2 = float(node.attrib.get("y2", 0.0))

    return [[(x1, y1), (x2, y2)]]