from geometry.bezier import quad_bezier,cubic_bezier
def draw_global_bbox_rect(bbox, msp, svg_to_mm, color):
    xmin, ymin, xmax, ymax = bbox

    # 👉 构造 contour（复用 rect 的“几何表达”）
    contour = [
        (xmin, ymin),
        (xmax, ymin),
        (xmax, ymax),
        (xmin, ymax),
        (xmin, ymin),
    ]

    contours = [contour]

    # 👉 复用 rect 的绘制逻辑（核心复用点）
    draw_rect_contours(contours, msp, svg_to_mm, color)

def add_polyline(msp, points, closed=False, color=7, layer=None):
    """
    在 DXF 中添加一条多段线
    """
    if not points or len(points) < 2:
        return

    attribs = {
        "closed": closed,
        "color": color,
    }

    if layer:
        attribs["layer"] = layer

    msp.add_lwpolyline(points, dxfattribs=attribs)
def add_contour_outlines(msp, contours, color=7):
    """
    绘制轮廓线（不填充）

    contours: List[List[(x_mm, y_mm)]]
    """
    for contour in contours:
        if len(contour) < 2:
            continue

        add_polyline(
            msp,
            contour,
            closed=True,
            color=color
        )



    




def draw_clip_contour(contour, msp, svg_to_mm, color=7, close=True):
    pts = []

    for x, y in contour:
        px, py = svg_to_mm((x, y))   # ⭐ 关键在这里
        pts.append((px, py))

    if close and pts[0] != pts[-1]:
        pts.append(pts[0])

    msp.add_lwpolyline(
        pts,
        dxfattribs={"color": color}
    )





def draw_paths(paths, msp, svg_to_mm=1.0, color=7):
    for path in paths:
        draw_path(path, msp, svg_to_mm, color)

def draw_path(path, msp, svg_to_mm=1.0, color=7):
    for seg in path.segments:
        draw_path_segment(seg, msp, svg_to_mm, color)



def draw_path_segment(seg, msp, svg_to_mm, color=7):

    def to_mm(p):
        return svg_to_mm(p)

    # ====== 直线 ======
    if seg.type == "line":
        msp.add_line(to_mm(seg.p0), to_mm(seg.p1), dxfattribs={"color": color})

    # ====== 二次贝塞尔 ======
    elif seg.type == "quadratic_bezier":
        pts = quad_bezier(seg.p0, seg.p1, seg.p2, steps=8)
        pts = [to_mm(p) for p in pts]

        msp.add_spline(
            fit_points=pts,
            dxfattribs={"color": color}
        )

    # ====== 三次贝塞尔 ======
    elif seg.type == "cubic_bezier":
        pts = cubic_bezier(seg.p0, seg.p1, seg.p2, seg.p3, steps=8)
        pts = [to_mm(p) for p in pts]

        msp.add_spline(
            fit_points=pts,
            dxfattribs={"color": color}
        )



def draw_rect_contours(contours, msp, svg_to_mm, color):
    for contour in contours:
        if len(contour) < 4:
            continue

        # 👉 去掉最后一个重复点（如果闭合了）
        pts = contour[:-1] if contour[0] == contour[-1] else contour

        # 👉 坐标转换
        pts = [svg_to_mm(p) for p in pts]

        # 👉 一次画出闭合矩形
        msp.add_lwpolyline(
            pts,
            dxfattribs={"color": color},
            close=True
        )


def draw_polygon_contours(contours, msp, svg_to_mm, color=7):
    for contour in contours:
        if not contour or len(contour) < 2:
            continue

        is_closed = (contour[0] == contour[-1])

        pts = contour[:-1] if is_closed else contour

        pts = [svg_to_mm(p) for p in pts]

        msp.add_lwpolyline(
            pts,
            dxfattribs={"color": color},
            close=is_closed
        )









def draw_image_rect(bbox, msp, svg_to_mm, role="bbox", color=7):
    if not bbox:
        return

    xmin, ymin, xmax, ymax = bbox

    # 👉 构造四个点（不重复最后一个）
    pts = [
        (xmin, ymin),
        (xmax, ymin),
        (xmax, ymax),
        (xmin, ymax),
    ]

    # 👉 坐标转换（你现在是函数）
    pts = [svg_to_mm(p) for p in pts]

    # 👉 用 polyline 画矩形（CAD友好）
    msp.add_lwpolyline(
        pts,
        dxfattribs={
            "color": color,
            "layer": role
        },
        close=True
    )