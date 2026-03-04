from geometry.clip import clip_contours_to_segments,classify_contours_by_clip
from svg_model.style import parse_clip_id_from_style
from kernel.logger import log
from kernel.clip_stats import stat_inc
from geometry.bbox import contour_to_bbox, point_in_bbox, is_bbox_clip
import time
def collect_clip_geometries(node, clip_geoms):
    """
    从当前 node 向上，收集所有 clip-path 对应的几何
    返回：
      List[ contour ]，顺序：由外到内
    """
    clips = []

    cur = node.parent
    while cur:
        style = cur.attrib.get("style")
        clip_id = parse_clip_id_from_style(style)
        if clip_id and clip_id in clip_geoms:
            # 一个 clipPath 可能有多个 contour
            clips.extend(clip_geoms[clip_id])
        cur = cur.parent

    # SVG 语义：外层先裁，内层后裁
    clips.reverse()
    return clips
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
def dispatch_by_clip_state(contours,clip_bbox,*,on_inside,on_partial,):
    t_enter = time.perf_counter()
    geoms = []
    # ---------- fast 熔断 ----------
    total_seg = sum(len(c) - 1 for c in contours if len(c) >= 2)
    if total_seg >= 50:
        t0 = time.perf_counter()
        if fast_partial_break_bbox_only(contours, clip_bbox, max_segments=50):
            dt = time.perf_counter() - t0
            stat_inc("fast_break", dt)
            log(
                f"FAST_BREAK contours={len(contours)} seg={total_seg}",
                tag="FAST"
            )
            return []
        stat_inc("fast_check", time.perf_counter() - t0)

    # ---------- classify ----------
    t0 = time.perf_counter()
    state = classify_contours_by_clip(contours, clip_bbox)
    dt_classify = time.perf_counter() - t0
    stat_inc("classify", dt_classify)

    # ---------- outside ----------
    if state == "outside":
        stat_inc("outside", time.perf_counter() - t_enter)
        return geoms

    # ---------- inside ----------
    if state == "inside":
        t0 = time.perf_counter()
        out = on_inside(contours)
        dt = time.perf_counter() - t0
        stat_inc("inside", dt)
        return out

    # ---------- partial ----------
    if state == "partial":
        t0 = time.perf_counter()

        segments = clip_contours_to_segments(contours, clip_bbox)
        for p0, p1 in segments:
            geoms.append(on_partial(p0, p1))

        dt = time.perf_counter() - t0
        stat_inc("partial", dt)

        log(
            f"PARTIAL contours={len(contours)} "
            f"segments_out={len(geoms)}",
            tag="CLIP"
        )
        return geoms

    return geoms

class ClipContext:
    def __init__(self, global_clip, clip_geoms):
        """
        global_clip: bbox 或 polygon（全局裁剪）
        clip_geoms: find_clip_geometries_from_defs(doc) 的结果
        """
        self.global_clip = global_clip
        self.clip_geoms = clip_geoms

    def apply(self, node, contours, on_inside, on_partial):
        """
        对 contours 依次应用：
          1️⃣ 全局裁剪
          2️⃣ 所有父 clip-path 裁剪
        """
        # 1️⃣ 全局裁剪
        geoms = dispatch_by_clip_state(
            contours,
            self.global_clip,
            on_inside=on_inside,
            on_partial=on_partial,
        )
        # geoms → 重新转回 contours（关键）
        contours = self._geoms_to_contours(geoms)
        if not contours:
            return []
        # 2️⃣ clip-path 裁剪
        clips = collect_clip_geometries(node, self.clip_geoms)
        for clip in clips:
            geoms = dispatch_by_clip_state(
                contours,
                clip,
                on_inside=on_inside,
                on_partial=on_partial,
            )
            contours = self._geoms_to_contours(geoms)
            if not contours:
                return []
        return geoms
    def _geoms_to_contours(self, geoms):
        """
        把 dispatch 输出的 geoms 再变回 contours
        （为下一轮裁剪服务）
        """
        contours = []
        for g in geoms:
            if g["type"] == "polygon":
                contours.append(g["points"])
            elif g["type"] == "polyline":
                contours.append(g["points"])
            elif g["type"] == "line":
                contours.append([g["p0"], g["p1"]])
        return contours



class NoClipContext:
    def apply(self, node, contours, on_inside, on_partial):
    # 🚫 不裁剪，直接认为全部 inside
        return on_inside(contours)

