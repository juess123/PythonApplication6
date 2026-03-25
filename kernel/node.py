
from geometry.bbox import contour_to_bbox, intersect_bbox
from geometry.parse import parse_path_d_multi,clean_path
from geometry.polygon import is_rectangle
from svg_model.geometry_builder import rect_to_contours, parse_points
from svg_model.node_utils import resolve_clip_id
from svg_model.geometry_builder import paths_to_contours
from kernel.writer import draw_paths,draw_rect_contours,draw_polygon_contours,draw_geometries
from kernel.RenderStrategyLayer import resolve_render_strategy,draw_occlusion
from clip.dispatcher import needs_clipping
from kernel.normalize import normalize_contours
from geometry.bbox import path_is_closed
from stroke.stroke_dispatch import expand_contours_by_stroke

def process_path_node(node, doc, msp, clip_ctx, svg_to_mm, color=7):
    d = node.attrib.get("d", "")
    paths = parse_path_d_multi(d)
    paths = [clean_path(p) for p in paths]
    contours = paths_to_contours(paths)
    #contours = expand_contours_by_stroke(node, contours, doc)
    # ===== 🎯 渲染策略 =====
    strategy = resolve_render_strategy(node, doc)
    if not strategy["use_fill"] and not strategy["has_stroke"]:
        return
    # ===== 🔥 判断是否需要裁剪 =====
    if not needs_clipping(node, contours, clip_ctx):
        # 👉 fill → 先遮蔽
        if strategy["use_fill"]:
            geoms = [{
                "type": "polygon",
                "points": c
            } for c in contours]

            #draw_occlusion(geoms, msp, svg_to_mm)
        # 👉 保留高级语义
        draw_paths(paths, msp, svg_to_mm, color)
        return
    # ===== ✂️ 需要裁剪 =====
    geoms = normalize_contours(node,contours,clip_ctx,is_closed=path_is_closed(d))
    # 👉 fill → 先遮蔽
    if strategy["use_fill"]:
        pass
        #draw_occlusion(geoms, msp, svg_to_mm)
    # 👉 再画
    draw_geometries(geoms, msp, svg_to_mm)
    

    # print("====== PATH DEBUG ======")
    # print("num paths:", len(paths))
    # for i, path in enumerate(paths):
    #     print(f"\n--- Path {i} ---")
    #     print("closed:", path.closed)
    #     print("num segments:", len(path.segments))
    #     for j, seg in enumerate(path.segments):
    #         print(f"  seg {j}: type={seg.type}, p0={seg.p0}, p1={seg.p1}, p2={seg.p2}, p3={seg.p3}")




def process_rect_node(node, doc, msp, clip_ctx, svg_to_mm, color):
    
    contours = rect_to_contours(node)

    # ===== 🎯 渲染策略 =====
    strategy = resolve_render_strategy(node, doc)
    if not strategy["use_fill"] and not strategy["has_stroke"]:
        return
    # ===== 🔥 转成统一结构 =====
    geoms = []
    for c in contours:
        if len(c) >= 3:
            geoms.append({
                "type": "polygon",
                "points": c
            })
    # ===== 🔥 遮蔽 =====
    if strategy["use_fill"]:
        draw_occlusion(geoms, msp, svg_to_mm)

    # ===== 🎨 绘制 =====
    draw_rect_contours(contours, msp, svg_to_mm, color)
    


def process_polygon_node(node, doc, msp, clip_ctx, svg_to_mm, color):
    points_str = node.attrib.get("points", "")
    if not points_str:
        return
    # ===== 解析 =====
    points = parse_points(points_str)
    contours = [points]

    # ===== clip 判断 =====
    if not needs_clipping(node, contours, clip_ctx):
        # ===== 矩形 =====
        if is_rectangle(points):
            print("🔥 polygon -> rect")
            contour = points + [points[0]]  # 闭合
            strategy = resolve_render_strategy(node, doc)
            if strategy["use_fill"]:
                geoms = [{
                    "type": "polygon",
                    "points": contour
                }]
                draw_occlusion(geoms, msp, svg_to_mm)
            draw_rect_contours([contour], msp, svg_to_mm, color)
        # ===== 普通 polygon =====
        else:
            draw_polygon_contours(contours, msp, svg_to_mm, color)
    geoms = normalize_contours(node,contours,clip_ctx,is_closed=True)
    draw_geometries(geoms, msp, svg_to_mm)

    

    
    


def process_polyline_node(node, doc, msp, clip_ctx, svg_to_mm, color=7):
    points_str = node.attrib.get("points", "")
    # 👉 解析 points
    points = parse_points(points_str)

    strategy = resolve_render_strategy(node, doc)
    if not strategy["use_fill"] and not strategy["has_stroke"]:
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
