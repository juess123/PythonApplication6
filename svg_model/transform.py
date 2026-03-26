def make_svg_to_mm_transform(root):
    """
    root: SvgRoot
    构造 SVG user space → CAD mm space 的坐标变换函数

    返回:
        svg_to_mm(pt) -> (x_mm, y_mm)
    """

    # -------- viewBox（user space）--------
    if root.viewbox is None:
        raise RuntimeError("SvgRoot.viewbox is None")

    vb_minx, vb_miny, vb_w, vb_h = root.viewbox
    if vb_w <= 0 or vb_h <= 0:
        raise RuntimeError(f"Invalid viewBox size: {root.viewbox}")

    # -------- physical size（mm）--------
    if root.width_mm is None or root.height_mm is None:
        raise RuntimeError("SvgRoot physical size not resolved")

    svg_w_mm = root.width_mm
    svg_h_mm = root.height_mm

    # -------- scale --------
    sx = svg_w_mm / vb_w
    sy = svg_h_mm / vb_h

    if abs(sx - sy) > 1e-2:
        # 记录一下，不要直接炸
        print(f"[WARN] Non-uniform scaling: sx={sx}, sy={sy}, use avg")
        s = (sx + sy) / 2
        sx = sy = s

    # -------- transform function --------
    def svg_to_mm(pt):
        x, y = pt

        # X: 平移 + 缩放
        x_mm = (x - vb_minx) * sx

        # Y: SVG 向下 → CAD 向上（翻转 + 缩放）
        y_mm = (vb_h - (y - vb_miny)) * sy

        return (x_mm, y_mm)

    return svg_to_mm
