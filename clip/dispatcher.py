from clip.collector import collect_clip_geometries
from clip.classifier import classify_contours_by_clip,fast_partial_break_bbox_only
from clip.clipper import clip_contours_to_segments
def needs_clipping(node, contours, clip_ctx):
    # 👉 收集所有 clip（全局 + 局部）
    clips = [clip_ctx.global_clip] + collect_clip_geometries(node, clip_ctx.clip_geoms)
    for clip in clips:
        state = classify_contours_by_clip(contours, clip)
        if state != "inside":
            return True   # ❗只要有一个不完全 inside，就必须裁剪
    return False
def dispatch_by_clip_state(contours,clip_bbox,*,on_inside,on_partial,):
    geoms = []
    # ---------- fast 熔断 ----------
    total_seg = sum(len(c) - 1 for c in contours if len(c) >= 2)
    if total_seg >= 50:
        if fast_partial_break_bbox_only(contours, clip_bbox, max_segments=50):
            return []
    # ---------- classify ----------
    state = classify_contours_by_clip(contours, clip_bbox)
    # ---------- outside ----------
    if state == "outside":
        
        return geoms

    # ---------- inside ----------
    if state == "inside":
        out = on_inside(contours)
        return out
    # ---------- partial ----------
    if state == "partial":
        segments = clip_contours_to_segments(contours, clip_bbox)
        for p0, p1 in segments:
            geoms.append(on_partial(p0, p1))
        return geoms

    return geoms