from clip.dispatcher import dispatch_by_clip_state
from clip.collector import collect_clip_geometries
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
    def __init__(self):
        # 模拟 ClipContext 必要属性，防止 AttributeError
        self.global_clip = []   # 空列表表示没有全局裁剪
        self.clip_geoms = []    # 没有父 clip-path

    def apply(self, node, contours, on_inside, on_partial):
        # 不裁剪，直接返回 contours 作为 inside
        return on_inside(contours)