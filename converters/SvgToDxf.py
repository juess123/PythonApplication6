from pathlib import Path
import ezdxf
from svg_model.builder import build_svg_document
from kernel.pipeline import dispatch_from_first_g
from functools import wraps
import threading
def timeout(seconds):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = []
            exception = []

            def target():
                try:
                    res = func(*args, **kwargs)
                    result.append(res)
                except Exception as e:
                    exception.append(e)

            thread = threading.Thread(target=target)
            thread.daemon = True
            thread.start()
            thread.join(timeout=seconds)

            if thread.is_alive():
                raise TimeoutError(f"函数执行超时，超过 {seconds} 秒未完成")
            if exception:
                raise exception[0]
            return result[0] if result else None
        return wrapper
    return decorator
def svg_to_dxf(svg_path: str, dxf_path: str):
    """
    将 SVG 文件转换为 DXF 文件（同步版本）
    包含 60 秒超时控制
    """
    out_dxf = Path(dxf_path)
    doc = build_svg_document(svg_path)
    dxf_doc = ezdxf.new("R2018")
    msp = dxf_doc.modelspace()

    # ✅ 给核心函数加 60 秒超时
    @timeout(60)  # 60秒 = 1分钟
    def run_dispatch():
        dispatch_from_first_g(doc, msp, color=7)

    # 执行（超时自动抛异常）
    run_dispatch()

    out_dxf.parent.mkdir(parents=True, exist_ok=True)
    dxf_doc.saveas(out_dxf)

    if not out_dxf.exists():
        raise FileNotFoundError(f"DXF 文件未生成: {out_dxf}")


