from pathlib import Path
import ezdxf
from svg_model.builder import build_svg_document
from kernel.pipeline import dispatch_from_first_g

def svgTodxf():
    # 固定路径（调试用）
    svg_file = Path("./input/source.svg")
    out_dxf = Path("./output/source.dxf")

    # 1️⃣ 构建 SVG 文档
    doc = build_svg_document(svg_file)
    #dump_svg_document(doc);
    # 2️⃣ 创建 DXF 文档
    dxf_doc = ezdxf.new("R2018")
    msp = dxf_doc.modelspace()

    # 3️⃣ 调度（把控制权交出去）
   
    dispatch_from_first_g(doc, msp, color=7)
  
    
    # 4️⃣ 保存 DXF
    
    out_dxf.parent.mkdir(parents=True, exist_ok=True)
    dxf_doc.saveas(out_dxf)
   
 
    #生成dwg文件
def svg_to_dxf(svg_path: str, dxf_path: str):
    """
    将 SVG 文件转换为 DXF 文件（同步版本）

    Args:
        svg_path (str): SVG 文件路径
        dxf_path (str): 输出 DXF 文件路径
    """
    # 转换为 Path 对象
    out_dxf = Path(dxf_path)

    # 1️⃣ 构建 SVG 文档
    doc = build_svg_document(svg_path)

    # 2️⃣ 创建 DXF 文档
    dxf_doc = ezdxf.new("R2018")
    msp = dxf_doc.modelspace()

    # 3️⃣ 调度（把控制权交出去）

    dispatch_from_first_g(doc, msp, color=7)
    out_dxf.parent.mkdir(parents=True, exist_ok=True)
    dxf_doc.saveas(out_dxf)
    # 判断文件是否生成
    if not out_dxf.exists():
        raise FileNotFoundError(f"DXF 文件未生成: {out_dxf}")


if __name__ == "__main__":
    svgTodxf()
