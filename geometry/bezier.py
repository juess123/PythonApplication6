def quad_bezier(p0, p1, p2, steps=20):
    pts = []
    for i in range(steps + 1):
        t = i / steps
        x = (1 - t)**2 * p0[0] + 2*(1 - t)*t*p1[0] + t**2 * p2[0]
        y = (1 - t)**2 * p0[1] + 2*(1 - t)*t*p1[1] + t**2 * p2[1]
        pts.append((x, y))
    return pts


def cubic_bezier(p0, p1, p2, p3, steps=20):
    pts = []
    for i in range(steps + 1):
        t = i / steps
        x = (1 - t)**3 * p0[0] + 3*(1 - t)**2*t*p1[0] + 3*(1 - t)*t**2*p2[0] + t**3*p3[0]
        y = (1 - t)**3 * p0[1] + 3*(1 - t)**2*t*p1[1] + 3*(1 - t)*t**2*p2[1] + t**3*p3[1]
        pts.append((x, y))
    return pts