import re
_CLIP_RE = re.compile(r"url\(#([^)]+)\)")
#下面两个是处理 图片的 加上矩形框 主要是给其他文件使用
#从当前 node 提取 clip id（不看父节点）
def _extract_clip_from_node(node):
    """只从当前节点提取 clip-path，不看父节点"""
    clip = node.attrib.get("clip-path")
    if clip:
        m = _CLIP_RE.search(clip)
        if m:
            return m.group(1)

    style = node.attrib.get("style", "")
    if style:
        m = _CLIP_RE.search(style)
        if m:
            return m.group(1)
    return None

#自己没有 → 向上找父节点
def resolve_clip_id(node):
    """
    clip-path 解析规则（兼容旧版本）：
    1️⃣ 自己有 → 用自己的
    2️⃣ 自己没有 → 向上找最近父节点
    """
    # ① 自身优先
    own = _extract_clip_from_node(node)
    if own:
        return own

    # ② 向上查找（注意：SvgNode 用 parent）
    cur = node.parent
    while cur is not None:
        parent_clip = _extract_clip_from_node(cur)
        if parent_clip:
            return parent_clip
        cur = cur.parent

    return None