import re
from dataclasses import dataclass
from typing import List, Tuple, Literal, Optional
from geometry.geometry_types import Segment, Path
Point = Tuple[float, float]

SegmentType = Literal["line", "quadratic_bezier", "cubic_bezier"]

@dataclass
class Segment:
    type: SegmentType
    p0: Point
    p1: Optional[Point] = None
    p2: Optional[Point] = None
    p3: Optional[Point] = None

@dataclass
class Path:
    segments: List[Segment]
    closed: bool = False

def _is_number(s):
    try:
        float(s)
        return True
    except:
        return False
    
def parse_polygon_points(points_str):
   
    if not points_str:
        return []

    nums = list(map(float, re.findall(r"-?\d+(?:\.\d+)?", points_str)))

    if len(nums) % 2 != 0:
        raise ValueError(f"Invalid polygon points: {points_str}")

    return [(nums[i], nums[i + 1]) for i in range(0, len(nums), 2)]


def clean_path(path, tol=1e-3):
    cleaned = []

    for seg in path.segments:

        # ===== 1. 去零长度 =====
        if seg.type == "line":
            dx = abs(seg.p0[0] - seg.p1[0])
            dy = abs(seg.p0[1] - seg.p1[1])
            if dx < tol and dy < tol:
                continue

        cleaned.append(seg)

    # ===== 2. 去“回到起点的微小段” =====
    if path.closed and len(cleaned) >= 2:
        first = cleaned[0].p0
        last = cleaned[-1].p1

        dx = abs(first[0] - last[0])
        dy = abs(first[1] - last[1])

        if dx < tol and dy < tol:
            # 已经闭合，不需要最后一段
            cleaned.pop()

    path.segments = cleaned
    return path





# ====== 精度控制 ======
def round_point(p, ndigits=3):
    return (round(p[0], ndigits), round(p[1], ndigits))


def make_point(x, y):
    return round_point((x, y))


def parse_path_d_multi(d):

    tokens = re.findall(r"""[MLCQZHVmlcqzhv]|[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?""", d, re.VERBOSE)

    paths = []
    current_segments = []

    x = y = 0.0
    start = None
    i = 0
    cmd = None

    # ====== 安全加线（去零长度） ======
    def add_line(p0, p1):
        if p0 == p1:
            return
        current_segments.append(
            Segment(type="line", p0=p0, p1=p1)
        )

    while i < len(tokens):
        t = tokens[i]

        # ====== Z ======
        if t in ("Z", "z"):
            if current_segments and start is not None:
                p0 = make_point(x, y)

                if p0 != start:
                    add_line(p0, start)

                paths.append(
                    Path(
                        segments=current_segments,
                        closed=True
                    )
                )

                current_segments = []
                start = None

            i += 1
            continue

        # ====== 命令 ======
        if t in "MLCQHVmlcqhv":
            cmd = t
            i += 1
            continue

        # ====== Move ======
        if cmd == "M":
            if current_segments:
                paths.append(Path(segments=current_segments, closed=False))
            current_segments = []

            x, y = float(tokens[i]), float(tokens[i+1])
            x, y = make_point(x, y)
            start = (x, y)

            i += 2

        elif cmd == "m":
            if current_segments:
                paths.append(Path(segments=current_segments, closed=False))
            current_segments = []

            x += float(tokens[i])
            y += float(tokens[i+1])
            x, y = make_point(x, y)
            start = (x, y)

            i += 2

        # ====== L ======
        elif cmd in ("L", "l"):
            while i + 1 < len(tokens) and _is_number(tokens[i]):
                p0 = make_point(x, y)

                if cmd == "L":
                    x, y = float(tokens[i]), float(tokens[i+1])
                else:
                    x += float(tokens[i])
                    y += float(tokens[i+1])

                x, y = make_point(x, y)
                p1 = (x, y)

                add_line(p0, p1)

                i += 2

        # ====== H ======
        elif cmd in ("H", "h"):
            while i < len(tokens) and _is_number(tokens[i]):
                p0 = make_point(x, y)

                if cmd == "H":
                    x = float(tokens[i])
                else:
                    x += float(tokens[i])

                x, y = make_point(x, y)
                p1 = (x, y)

                add_line(p0, p1)

                i += 1

        # ====== V ======
        elif cmd in ("V", "v"):
            while i < len(tokens) and _is_number(tokens[i]):
                p0 = make_point(x, y)

                if cmd == "V":
                    y = float(tokens[i])
                else:
                    y += float(tokens[i])

                x, y = make_point(x, y)
                p1 = (x, y)

                add_line(p0, p1)

                i += 1

        # ====== Quadratic ======
        elif cmd in ("Q", "q"):
            while i + 3 < len(tokens) and _is_number(tokens[i]):
                p0 = make_point(x, y)

                if cmd == "Q":
                    p1 = make_point(float(tokens[i]), float(tokens[i+1]))
                    p2 = make_point(float(tokens[i+2]), float(tokens[i+3]))
                else:
                    p1 = make_point(x + float(tokens[i]), y + float(tokens[i+1]))
                    p2 = make_point(x + float(tokens[i+2]), y + float(tokens[i+3]))

                current_segments.append(
                    Segment(
                        type="quadratic_bezier",
                        p0=p0,
                        p1=p1,
                        p2=p2
                    )
                )

                x, y = p2
                i += 4

        # ====== Cubic ======
        elif cmd in ("C", "c"):
            while i + 5 < len(tokens) and _is_number(tokens[i]):
                p0 = make_point(x, y)

                if cmd == "C":
                    p1 = make_point(float(tokens[i]), float(tokens[i+1]))
                    p2 = make_point(float(tokens[i+2]), float(tokens[i+3]))
                    p3 = make_point(float(tokens[i+4]), float(tokens[i+5]))
                else:
                    p1 = make_point(x + float(tokens[i]), y + float(tokens[i+1]))
                    p2 = make_point(x + float(tokens[i+2]), y + float(tokens[i+3]))
                    p3 = make_point(x + float(tokens[i+4]), y + float(tokens[i+5]))

                current_segments.append(
                    Segment(
                        type="cubic_bezier",
                        p0=p0,
                        p1=p1,
                        p2=p2,
                        p3=p3
                    )
                )

                x, y = p3
                i += 6

        else:
            i += 1

    # ====== open path ======
    if current_segments:
        paths.append(
            Path(
                segments=current_segments,
                closed=False
            )
        )

    return paths








