from dataclasses import dataclass
from typing import List, Tuple, Literal, Optional
# ====== 基础类型 ======
Point = Tuple[float, float]
SegmentType = Literal[
    "line",
    "quadratic_bezier",
    "cubic_bezier",
    "arc",
]

# ====== Segment ======

@dataclass
class Segment:
    type: SegmentType

    # 起点（必须）
    p0: Point

    # 终点（必须）
    p1: Optional[Point] = None

    # 二次贝塞尔
    p2: Optional[Point] = None

    # 三次贝塞尔
    p3: Optional[Point] = None

    # arc 预留
    radius: Optional[Tuple[float, float]] = None
    rotation: Optional[float] = None
    large_arc: Optional[bool] = None
    sweep: Optional[bool] = None


# ====== Path ======

@dataclass
class Path:
    segments: List[Segment]
    closed: bool = False


# ====== Geometry（可选，用于统一接口） ======

@dataclass
class Geometry:
    paths: List[Path]