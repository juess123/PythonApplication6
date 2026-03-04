
from stroke.stroke_info import get_stroke_info
from stroke.stroke_rect import expand_rect_by_stroke
from stroke.stroke_path import expand_closed_path_by_stroke, contour_is_closed
from stroke.stroke_polygon import expand_polygon_by_stroke
from stroke.stroke_polyline import expand_polyline_by_stroke
def path_is_closed(d):
    return 'z' in d.lower()

def expand_contours_by_stroke(node, contours, doc):
    stroke = get_stroke_info(node, doc)
    if not stroke:
        return contours

    # —— 核心分发：基于 SVG 语义，而不是几何猜测 ——
    if node.tag == "rect":
        out = []
        for contour in contours:
            out.extend(expand_rect_by_stroke(contour, stroke["width"]))
        return out
    
    if node.tag == "polygon":
        out = []
        for contour in contours:
            out.extend(expand_polygon_by_stroke(contour, stroke["width"]))
        return out

    if node.tag == "polyline":
        out = []
        for contour in contours:
            out.extend(expand_polyline_by_stroke(contour,stroke["width"]))
        return out
    if node.tag == "line":
        out = []
        for contour in contours:
            out.extend(expand_polyline_by_stroke(contour, stroke["width"]))
        return out
    if node.tag == "path":
        out = []
        for contour in contours:
            if contour_is_closed(contour):
                out.extend(expand_closed_path_by_stroke(contour,stroke["width"]))
            else:
                out.extend(expand_polyline_by_stroke(contour, stroke["width"]))
        return out
    return contours