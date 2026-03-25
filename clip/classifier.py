from geometry.bbox import point_in_bbox,point_in_polygon,contour_to_bbox, point_in_bbox, is_bbox_clip
def classify_contours_by_clip(contours, clip):
    inside = False
    outside = False
    is_bbox = isinstance(clip, tuple) and len(clip) == 4
    for contour in contours:
        for p in contour:
            if is_bbox:
                in_clip = point_in_bbox(p, clip)
            else:
                in_clip = point_in_polygon(p, clip)

            if in_clip:
                inside = True
            else:
                outside = True

    if inside and not outside:
        return "inside"

    if outside and not inside:
        return "outside"

    return "partial"


def fast_partial_break_bbox_only(
    contours,
    clip,
    *,
    max_segments=50,
):
    """
    真正 O(N) 且极轻的熔断判断：
    - 只用 bbox
    - 不调用 point_in_polygon
    - 不调用 polygon 相交
    """
    # 统一拿 bbox
    if is_bbox_clip(clip):
        clip_bbox = clip
    else:
        clip_bbox = contour_to_bbox(clip)

    clipped = 0

    for contour in contours:
        n = len(contour)
        if n < 2:
            continue

        for i in range(n - 1):
            p0 = contour[i]
            p1 = contour[i + 1]

            in0 = point_in_bbox(p0, clip_bbox)
            in1 = point_in_bbox(p1, clip_bbox)

            # 一内一外 → bbox 层面已足够说明“可能被裁剪”
            if in0 != in1:
                clipped += 1
                if clipped >= max_segments:
                    return True

    return False