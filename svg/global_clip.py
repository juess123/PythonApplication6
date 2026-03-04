def find_global_clip_bbox(doc):
    """
    Global clip bbox is strictly defined by SVG viewBox
    """
    if not doc.root or not doc.root.viewbox:
        raise RuntimeError("SvgRoot.viewbox not initialized")

    minx, miny, w, h = doc.root.viewbox
    return (minx, miny, minx + w, miny + h)

