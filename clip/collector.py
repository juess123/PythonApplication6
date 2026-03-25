from svg_model.style import get_clip_id_from_node
def collect_clip_geometries(node, clip_geoms):
    """
    从当前 node 向上，收集所有 clip-path 对应的几何
    返回：
      List[ contour ]，顺序：由外到内
    """
    clips = []

    cur = node.parent
    while cur:
        clip_id = get_clip_id_from_node(cur)
        if clip_id and clip_id in clip_geoms:
            # 一个 clipPath 可能有多个 contour
            clips.extend(clip_geoms[clip_id])
        cur = cur.parent
    # SVG 语义：外层先裁，内层后裁
    clips.reverse()
    return clips