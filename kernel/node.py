from kernel.process_node_common import process_node_common
from geometry.bbox import contour_to_bbox, intersect_bbox
from geometry.parse import parse_path_d_multi,clean_path
from geometry.adapters import polygon_to_contours, rect_to_contours,polyline_to_contours, parse_points,is_rectangle
from svg.clip_geoms import resolve_clip_id
from kernel.writer import draw_paths,draw_rect_contours,draw_polygon_contours

def process_path_node(node, doc, msp, clip_ctx, svg_to_mm, color=7):
    d = node.attrib.get("d", "")
    get_paths = lambda _: parse_path_d_multi(d)
    paths = get_paths(node)                 
    paths = [clean_path(p) for p in paths]

    draw_paths(paths, msp, svg_to_mm, color)

    # print("====== PATH DEBUG ======")
    # print("num paths:", len(paths))
    # for i, path in enumerate(paths):
    #     print(f"\n--- Path {i} ---")
    #     print("closed:", path.closed)
    #     print("num segments:", len(path.segments))

    #     for j, seg in enumerate(path.segments):
    #         print(f"  seg {j}: type={seg.type}, p0={seg.p0}, p1={seg.p1}, p2={seg.p2}, p3={seg.p3}")




def process_rect_node(node, doc, msp, clip_ctx, svg_to_mm, color=7):

    contours = rect_to_contours(node)
    if not contours:
        return
    # 👉 绘制
    draw_rect_contours(contours, msp, svg_to_mm, color)
    


def process_polygon_node(node, doc, msp, clip_ctx, svg_to_mm, color=7):
    points_str = node.attrib.get("points", "")
    if not points_str:
        return

    points = parse_points(points_str)
    if is_rectangle(points):
        contour = points + [points[0]]
        contours = [contour]
        draw_rect_contours(contours, msp, svg_to_mm, color)

    else:
        contours = polygon_to_contours(node)
        draw_polygon_contours(contours, msp, svg_to_mm, color)

    
    


def process_polyline_node(node, doc, msp, clip_ctx, svg_to_mm, color=7):
    points_str = node.attrib.get("points", "")
    if not points_str:
        return
    # 👉 解析 points
    points = parse_points(points_str)
    if len(points) < 2:
        return
    # 👉 逐段画线（核心逻辑）
    for i in range(len(points) - 1):
        x1, y1 = points[i]
        x2, y2 = points[i + 1]
        # 坐标转换
        p0 = svg_to_mm((x1, y1))
        p1 = svg_to_mm((x2, y2))
        # 画线
        msp.add_line(p0, p1, dxfattribs={"color": color})
   


def process_line_node(node, doc, msp, clip_ctx, svg_to_mm, color=7):
    try:
        x1 = float(node.attrib.get("x1", 0))
        y1 = float(node.attrib.get("y1", 0))
        x2 = float(node.attrib.get("x2", 0))
        y2 = float(node.attrib.get("y2", 0))
    except Exception:
        return

    # 👉 坐标转换（你现在是函数方式）
    p0 = svg_to_mm((x1, y1))
    p1 = svg_to_mm((x2, y2))
    # 👉 画线
    msp.add_line(p0, p1, dxfattribs={"color": color})



    
def compute_image_effective_bbox(
    node,
    clip_geoms,
    global_clip_bbox,
):

    clip_id = resolve_clip_id(node)
    if not clip_id:
        return None

    contours = clip_geoms.get(clip_id)
    
    if not contours:
        return None
    # image 的 clipPath 通常只有一个 contour
    for contour in contours:
        image_bbox = contour_to_bbox(contour)
        effective_bbox = intersect_bbox(image_bbox, global_clip_bbox)
        if effective_bbox:
            return effective_bbox
    return None
