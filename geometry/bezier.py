def quad_bezier(p0, p1, p2, steps=20):
    """二次贝塞尔曲线离散采样（优化版）"""
    pts = []

    p0x, p0y = p0
    p1x, p1y = p1
    p2x, p2y = p2

    inv_steps = 1.0 / steps

    for i in range(1, steps + 1):
        t = i * inv_steps
        omt = 1.0 - t
        omt2 = omt * omt
        t2 = t * t

        x = omt2 * p0x + 2.0 * omt * t * p1x + t2 * p2x
        y = omt2 * p0y + 2.0 * omt * t * p1y + t2 * p2y

        pts.append((x, y))

    return pts


def cubic_bezier(p0, p1, p2, p3, steps=30):
    """三次贝塞尔曲线离散采样（优化版）"""
    pts = []

    p0x, p0y = p0
    p1x, p1y = p1
    p2x, p2y = p2
    p3x, p3y = p3

    inv_steps = 1.0 / steps

    for i in range(1, steps + 1):
        t = i * inv_steps
        omt = 1.0 - t

        omt2 = omt * omt
        omt3 = omt2 * omt
        t2 = t * t
        t3 = t2 * t

        x = (
            omt3 * p0x
            + 3.0 * omt2 * t * p1x
            + 3.0 * omt * t2 * p2x
            + t3 * p3x
        )
        y = (
            omt3 * p0y
            + 3.0 * omt2 * t * p1y
            + 3.0 * omt * t2 * p2y
            + t3 * p3y
        )

        pts.append((x, y))

    return pts