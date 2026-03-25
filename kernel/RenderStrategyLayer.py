from geometry.bbox import polygon_has_area
def resolve_render_strategy(node, doc):
    styles = doc.defs.styles
    class_attr = node.attrib.get("class", "")
    class_list = class_attr.split()

    has_fill = False
    has_fill_none = False
    has_transparent_fill = False
    has_stroke = False

    for cls in class_list:
        props = styles.get(cls)
        if not props:
            continue

        fill = props.get("fill")
        stroke = props.get("stroke")
        opacity = props.get("fill-opacity")

        if stroke and stroke != "none":
            has_stroke = True

        if fill:
            if fill.strip().lower() == "none":
                has_fill_none = True
            else:
                has_fill = True

                if opacity:
                    try:
                        if float(opacity) < 1.0:
                            has_transparent_fill = True
                    except:
                        pass

    # ===== 🎯 统一输出 =====
    return {
        "use_fill": has_fill and not has_transparent_fill,
        "has_stroke": has_stroke,
        "color": 7 if not has_transparent_fill else 1,
        "is_fill_none": has_fill_none,
        "is_transparent": has_transparent_fill,
    }

def draw_occlusion(geoms, msp, svg_to_mm):
    for g in geoms:
        if g["type"] != "polygon":
            continue
        contour_mm = [svg_to_mm(pt) for pt in g["points"]]
        if len(contour_mm) < 3:
            continue
        if contour_mm[0] != contour_mm[-1]:
            contour_mm = contour_mm + [contour_mm[0]]
        if polygon_has_area(contour_mm):
            msp.add_wipeout(contour_mm)