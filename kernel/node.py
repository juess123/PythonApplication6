from kernel.process_node_common import process_node_common
from geometry.bbox import contour_to_bbox, intersect_bbox
from geometry.parse import parse_path_d_multi
from geometry.adapters import polygon_to_contours, rect_to_contours,polyline_to_contours, line_to_contours
from svg.path import path_is_closed
from svg.clip_geoms import resolve_clip_id
def process_path_node(node, doc, msp, clip_ctx, svg_to_mm, color=7):
    d = node.attrib.get("d", "")
    process_node_common(
        node,
        doc,
        msp,
        clip_ctx,
        svg_to_mm,
        get_contours=lambda _: parse_path_d_multi(d),
        is_closed=path_is_closed(d),
        color=color,
    )


def process_rect_node(node, doc, msp, clip_ctx, svg_to_mm, color=7):
    process_node_common(
        node,
        doc,
        msp,
        clip_ctx,
        svg_to_mm,
        get_contours=rect_to_contours,
        is_closed=True,
        color=color,
    )


def process_polygon_node(node, doc, msp, clip_ctx, svg_to_mm, color=7):
    process_node_common(
        node,
        doc,
        msp,
        clip_ctx,
        svg_to_mm,
        get_contours=polygon_to_contours,
        is_closed=True,
        color=color,
    )


def process_polyline_node(node, doc, msp, clip_ctx, svg_to_mm, color=7):
    process_node_common(
        node,
        doc,
        msp,
        clip_ctx,
        svg_to_mm,
        get_contours=polyline_to_contours,
        is_closed=False,
        color=color,
    )


def process_line_node(node, doc, msp, clip_ctx, svg_to_mm, color=7):
    process_node_common(
        node,
        doc,
        msp,
        clip_ctx,
        svg_to_mm,
        get_contours=line_to_contours,
        is_closed=False,
        color=color,
    )

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