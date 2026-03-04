class SvgRoot:
    __slots__ = (
        "width_mm",
        "height_mm",
        "viewbox",
        "namespaces",
        "raw_attrib",
    )

    def __init__(self, raw_attrib: dict):
        self.raw_attrib = raw_attrib      # 原始 <svg> 属性

        self.width_mm = None
        self.height_mm = None
        self.viewbox = None               # (x, y, w, h)

        
class SvgDefs:
    __slots__ = (
        "styles",
        "gradients",
        "symbols",
        "raw_elements",
    )

    def __init__(self):
        self.styles = {}        # class -> style dict
        self.gradients = {}     # id -> gradient info
        self.symbols = {}       # symbol / use
        self.raw_elements = []  # 原始 defs 子节点

class SvgNode:
    __slots__ = (
        "id",
        "tag",          # path / rect / g / defs / svg ...
        "attrib",       # 原始属性 dict
        "style",        # 解析后的 style dict（可选）

        "parent",       # SvgNode | None
        "children",     # list[SvgNode]

        "order",        # 全局 DFS 顺序
    )

    def __init__(self, id: int, tag: str, attrib: dict):
        self.id = id
        self.tag = tag
        self.attrib = attrib
        self.style = None
        self.parent = None
        self.children = []
        self.order = -1

class SvgDocument:
    __slots__ = (
        "root",
        "defs",
        "nodes",        # 所有 SvgNode（平铺）
    )

    def __init__(self):
        self.root: SvgRoot | None = None
        self.defs: SvgDefs | None = None
        self.nodes: list[SvgNode] = []

