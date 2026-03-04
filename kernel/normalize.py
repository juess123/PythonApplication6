
def remove_fake_closure(contour, eps=1e-6):
    if len(contour) < 2:
        return contour
    x0, y0 = contour[0]
    x1, y1 = contour[-1]
    if abs(x0 - x1) < eps and abs(y0 - y1) < eps:
        return contour[:-1]
    return contour
def normalize_contours(node, contours, clip_ctx, is_closed):
    def on_partial(p0, p1):
        return {
            "type": "line",
            "p0": p0,
            "p1": p1,
        }

    def on_inside(contours):
        out = []
        if is_closed:
            for c in contours:
                if len(c) >= 3:
                    out.append({
                        "type": "polygon",
                        "points": c,
                    })
        else:
            for c in contours:
                c2 = remove_fake_closure(c)
                if len(c2) >= 2:
                    out.append({
                        "type": "polyline",
                        "points": c2,
                        "closed": False,
                    })
        return out

    return clip_ctx.apply(node, contours, on_inside, on_partial)
