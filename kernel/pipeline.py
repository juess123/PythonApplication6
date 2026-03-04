from svg.global_clip import find_global_clip_bbox
from svg.clip_geoms import find_clip_geometries_from_defs
from kernel.clip_context import ClipContext, NoClipContext
from kernel.node import process_path_node, process_polygon_node, process_rect_node, process_polyline_node, process_line_node,compute_image_effective_bbox
from kernel.writer import draw_global_clip_bbox, draw_bbox
from collections import defaultdict
from svg.viewport import make_svg_to_mm_transform
from kernel.logger import log
stats = defaultdict(lambda: {"time": 0.0, "count": 0})

def dispatch_from_first_g(doc, msp, color=7):
    # 1️⃣ 找第一个 <g>
    start_index = None
    for i, node in enumerate(doc.nodes):
        if node.tag == "g":
            start_index = i
            break
    if start_index is None:
        raise RuntimeError("No <g> node found")

    # ==============================
    # ⭐ 全局一次性计算（性能关键）
    # ==============================
    global_clip = find_global_clip_bbox(doc)
    clip_geoms = find_clip_geometries_from_defs(doc)
    clip_ctx = ClipContext(global_clip, clip_geoms)
    # clip_ctx = NoClipContext()
    # 坐标变换也是全局常量
    svg_to_mm = make_svg_to_mm_transform(doc.root)

    # （可选）全局框只画一次
    draw_global_clip_bbox(global_clip, msp, svg_to_mm, color=color)
   
    # ==============================
    # 2️⃣ 正式分发
    # ==============================

    for node in doc.nodes[start_index + 1:]:
        tag = node.tag
        if tag == "path":
            process_path_node(node, doc, msp, clip_ctx, svg_to_mm, color)
        elif tag == "polygon":
            process_polygon_node(node, doc, msp, clip_ctx, svg_to_mm, color)
        elif tag == "rect":
            process_rect_node(node, doc, msp, clip_ctx, svg_to_mm, color)
        elif tag == "polyline":
            process_polyline_node(node, doc, msp, clip_ctx, svg_to_mm, color)
        elif tag == "line":
            process_line_node(node, doc, msp, clip_ctx, svg_to_mm, color)
        elif tag == "image":
            effective_bbox = compute_image_effective_bbox(node,clip_geoms,global_clip)
            if not effective_bbox:
                continue
            draw_bbox(effective_bbox,msp,svg_to_mm,color=7) 
        else:
            continue
   