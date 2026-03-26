
from kernel.normalize import normalize_contours

from stroke.stroke_dispatch import expand_contours_by_stroke
from kernel.RenderStrategyLayer import resolve_render_strategy,draw_occlusion
def is_occlusion_disabled(node):
    cls = node.attrib.get("class", "")
    return "fil2" in cls
def process_node_common(
    node,
    doc,
    msp,
    clip_ctx,          # ⭐ 外部传入
    svg_to_mm,         # ⭐ 外部传入（同样是全局常量）
    *,
    get_contours,
    is_closed,
    color=7,
):
    pass
    # 1️⃣ 解析轮廓
    
    #contours = get_contours(node)
    # 2️⃣ stroke 外扩
    #contours = expand_contours_by_stroke(node, contours, doc)
    
    # 3️⃣ normalize（clip 在这里用 clip_ctx）
    #geoms = normalize_contours(node,contours,clip_ctx,is_closed=is_closed,)
    # 几何语言升级 从多段线 升级为rect矩形
    #geoms = polygon_detect_rectangles(geoms)
    # 几何语言升级 从直线 升级为rect矩形

    #geoms = lines_dect_rects(geoms)

    # # 4 渲染处理  
    # should_occlude, color = resolve_render_strategy(node, doc)

    # if should_occlude and len(contours)<2:
    #     draw_occlusion(geoms, msp, svg_to_mm)
    # 5 画图
    #draw_geometries(geoms, msp, svg_to_mm, color=color)


