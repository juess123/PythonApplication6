def get_stroke_info(node, doc):
    """
    返回：
      None
      或
      {
        "width": float,
        "color": str | None,
      }
    """
    class_attr = node.attrib.get("class", "")
    if not class_attr:
        return None

    for cls in class_attr.split():
        style = doc.defs.styles.get(cls)
        if not style:
            continue

        sw = style.get("stroke-width")
        if sw is None:
            continue

        try:
            width = float(sw)
        except ValueError:
            continue

        if width <= 0:
            continue

        return {
            "width": width,
            "color": style.get("stroke"),
        }

    return None