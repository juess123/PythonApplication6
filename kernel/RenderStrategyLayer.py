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

        if stroke:
            has_stroke = True

        if fill:
            if fill.strip().lower() == "none":
                has_fill_none = True
            else:
                has_fill = True

                if opacity:
                    try:
                        op = float(opacity)
                        if op < 1.0:
                            has_transparent_fill = True
                    except:
                        pass

    # -------- 决策逻辑 --------

    # ① fill:none
    if has_fill_none:
        return False, 7  # 不遮蔽 + 主色
    # ② 半透明
    if has_transparent_fill:
        print("浅色")
        return False, 1  # 不遮蔽 + 浅色
    # ③ 实色填充
    if has_fill:
        return True, 7   # 遮蔽 + 主色
    # ④ 纯描边
    if has_stroke:
        return False, 7  # 不遮蔽 + 主色
    # ⑤ 默认
    return False, 7

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