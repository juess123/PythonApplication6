
from geometry.bbox import polygon_has_area

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
def draw_geometries(geoms, msp, svg_to_mm, color=7):
    for g in geoms:
        gtype = g["type"]

        if gtype == "line":
            x0, y0 = svg_to_mm(g["p0"])
            x1, y1 = svg_to_mm(g["p1"])
            msp.add_line(
                (x0, y0),
                (x1, y1),
                dxfattribs={"color": color},
            )

        elif gtype == "polyline":
            pts_mm = [svg_to_mm(pt) for pt in g["points"]]
            msp.add_lwpolyline(
                pts_mm,
                dxfattribs={
                    "closed": g.get("closed", False),
                    "color": color,
                },
            )

        # elif gtype == "polygon":
        #     contour_mm = [svg_to_mm(pt) for pt in g["points"]]

        #     if len(contour_mm) < 3:
        #         return

        #     # 强制闭合
        #     if contour_mm[0] != contour_mm[-1]:
        #         contour_mm = contour_mm + [contour_mm[0]]

        #     # 🚨 核心：只有“有面积的面”才能 WIPEOUT
        #     if polygon_has_area(contour_mm):
        #         msp.add_wipeout(contour_mm)


        #     # 轮廓线永远可以画
        #     add_contour_outlines(
        #         msp,
        #         [contour_mm],
        #         color=color
        #     )
        elif gtype == "polygon":
            contour_mm = [svg_to_mm(pt) for pt in g["points"]]
            if len(contour_mm) < 3:
                continue
            # 强制闭合
            if contour_mm[0] != contour_mm[-1]:
                contour_mm = contour_mm + [contour_mm[0]]
            # 只画轮廓
            add_contour_outlines(
                msp,
                [contour_mm],
                color=color
            )

        else:
            raise RuntimeError(f"Unknown geometry type: {gtype}")
def draw_global_clip_bbox(global_clip, msp, svg_to_mm, color=1):
    """
    在 CAD 中绘制 SVG 的全局裁剪框（viewBox）

    global_clip: (xmin, ymin, xmax, ymax)  —— SVG 坐标
    msp: ezdxf modelspace
    svg_to_mm: 坐标变换函数
    color: CAD 颜色（默认 1 = 红色，调试友好）
    """

    xmin, ymin, xmax, ymax = global_clip

    # SVG 坐标系下的四个角（逆时针）
    pts_svg = [
        (xmin, ymin),
        (xmax, ymin),
        (xmax, ymax),
        (xmin, ymax),
        (xmin, ymin),  # 闭合
    ]

    # 转成 CAD mm 坐标
    pts_mm = [svg_to_mm(p) for p in pts_svg]

    # 画一个闭合 polyline
    msp.add_lwpolyline(
        pts_mm,
        close=True,
        dxfattribs={
            "color": color,
            "lineweight": 25,  # 可选：稍微粗一点，方便看
        }
    )
def draw_bbox(bbox, msp, svg_to_mm, color=5):
    xmin, ymin, xmax, ymax = bbox
    pts_svg = [
        (xmin, ymin),
        (xmax, ymin),
        (xmax, ymax),
        (xmin, ymax),
    ]

    pts = [svg_to_mm((x, y)) for x, y in pts_svg]
    pts.append(pts[0])

    msp.add_lwpolyline(
        pts,
        dxfattribs={"color": color}
    )
def draw_clip_contour(contour, msp, svg_to_mm, color=1, close=True):
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

