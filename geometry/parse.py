import re
from geometry.bezier import quad_bezier, cubic_bezier
def parse_polygon_points(points_str):
   
    if not points_str:
        return []

    nums = list(map(float, re.findall(r"-?\d+(?:\.\d+)?", points_str)))

    if len(nums) % 2 != 0:
        raise ValueError(f"Invalid polygon points: {points_str}")

    return [(nums[i], nums[i + 1]) for i in range(0, len(nums), 2)]

def _is_number(s: str) -> bool:
    try:
        float(s)
        return True
    except ValueError:
        return False
def _require_numbers(tokens, i, n, d, cmd):
    for k in range(n):
        if i + k >= len(tokens) or not _is_number(tokens[i + k]):
            raise RuntimeError(
                f"[SVG PATH PARSE ERROR]\n"
                f" d = {d}\n"
                f" cmd = {cmd}\n"
                f" i = {i}\n"
                f" expect number at tokens[{i + k}]\n"
                f" token = {tokens[i + k] if i + k < len(tokens) else 'EOF'}\n"
                f" tokens = {tokens}\n"
            )
def parse_path_d_multi(d):
    """
    解析 SVG path 的 d 属性
    返回：
        paths: List[List[(x, y)]]
    规则：
        - 只有遇到 Z/z 才真正闭合
        - open path 绝不偷偷首尾相连
    """
    tokens = re.findall(r"[MLCQZHVmlcqzhv]|-?\d+\.?\d*", d)
    paths = []
    current = []

    x = y = 0.0
    start = None
    i = 0
    cmd = None

    while i < len(tokens):
        t = tokens[i]
        
        # ====== 关键修复：立即处理 Z / z ======
        if t in ("Z", "z"):
            if current and start is not None:
                # 只在 Z 时闭合
                current.append(start)
                paths.append(current)
                current = []
                start = None
            i += 1
            continue
        # =====================================

        # 命令切换
        if t in "MLCQHVmlcqhv":
            cmd = t
            i += 1
            continue
        if cmd in ("M", "m", "L", "l", "Q", "q", "C", "c"):
            if not _is_number(tokens[i]):
                raise RuntimeError(
                    f"[SVG PATH PARSE ERROR]\n"
                    f" d = {d}\n"
                    f" cmd = {cmd}\n"
                    f" i = {i}\n"
                    f" token = {tokens[i]}\n"
                    f" tokens = {tokens}\n"
                )
        # ====== Move ======
        if cmd == "M":
            if current:
                paths.append(current)
                current = []
            _require_numbers(tokens, i, 2, d, cmd)
            x, y = float(tokens[i]), float(tokens[i + 1])
            start = (x, y)
            current.append((x, y))
            i += 2

        elif cmd == "m":
            if current:
                paths.append(current)
                current = []
            _require_numbers(tokens, i, 2, d, cmd)
            x += float(tokens[i])
            y += float(tokens[i + 1])
            start = (x, y)
            current.append((x, y))
            i += 2

        # ====== Line ======
        elif cmd == "L":
            _require_numbers(tokens, i, 2, d, cmd)
            x, y = float(tokens[i]), float(tokens[i + 1])
            current.append((x, y))
            i += 2
            
        elif cmd == "l":
            _require_numbers(tokens, i, 2, d, cmd)
            x += float(tokens[i])
            y += float(tokens[i + 1])
            current.append((x, y))
            i += 2

        # ====== Quadratic Bezier ======
        elif cmd == "Q":
            _require_numbers(tokens, i, 4, d, cmd)
            p1 = (float(tokens[i]), float(tokens[i + 1]))
            p2 = (float(tokens[i + 2]), float(tokens[i + 3]))

            
            curve = quad_bezier((x, y), p1, p2)
            

            current.extend(curve[1:])  # ⚠️ 不重复起点
            x, y = p2
            i += 4

        elif cmd == "q":
            _require_numbers(tokens, i, 4, d, cmd)
            p1 = (x + float(tokens[i]),     y + float(tokens[i + 1]))
            p2 = (x + float(tokens[i + 2]), y + float(tokens[i + 3]))

           
            curve = quad_bezier((x, y), p1, p2)
            
            
  
            current.extend(curve[1:])
            x, y = p2
            i += 4

        # ====== Cubic Bezier ======
        elif cmd == "C":
            _require_numbers(tokens, i, 6, d, cmd)
            p1 = (float(tokens[i]),     float(tokens[i + 1]))
            p2 = (float(tokens[i + 2]), float(tokens[i + 3]))
            p3 = (float(tokens[i + 4]), float(tokens[i + 5]))
            curve = cubic_bezier((x, y), p1, p2, p3)
            current.extend(curve[1:])
            x, y = p3
            i += 6

        elif cmd == "c":
            _require_numbers(tokens, i, 6, d, cmd)
            p1 = (x + float(tokens[i]),     y + float(tokens[i + 1]))
            p2 = (x + float(tokens[i + 2]), y + float(tokens[i + 3]))
            p3 = (x + float(tokens[i + 4]), y + float(tokens[i + 5]))
            curve = cubic_bezier((x, y), p1, p2, p3)
            current.extend(curve[1:])
            x, y = p3
            i += 6
        elif cmd == "H":
            _require_numbers(tokens, i, 1, d, cmd)
            x = float(tokens[i])
            current.append((x, y))
            i += 1


        elif cmd == "h":
            _require_numbers(tokens, i, 1, d, cmd)
            x += float(tokens[i])
            current.append((x, y))
            i += 1


        elif cmd == "V":
            _require_numbers(tokens, i, 1, d, cmd)
            y = float(tokens[i])
            current.append((x, y))
            i += 1


        elif cmd == "v":
            _require_numbers(tokens, i, 1, d, cmd)
            y += float(tokens[i])
            current.append((x, y))
            i += 1
        else:
            i += 1

    # ====== open path 收尾（不闭合） ======
    if current:
        paths.append(current)
    return paths