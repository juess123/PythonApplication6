
from svg_model.builder import build_svg_document
from kernel.pipeline import dispatch_from_first_g
import subprocess
import ezdxf
from pathlib import Path
import sys
import time

def svgTodxf():
    # 固定路径（调试用）
    svg_file = Path("./temp/svg/source.svg")
    out_dxf = Path("./temp/dxf/source.dxf")

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
ODA_EXE = r"C:\Program Files\ODA\ODAFileConverter 26.10.0\ODAFileConverter.exe"
def dxfTodwg():
    # 1️⃣ 输入 / 输出目录
    in_dir = Path(r".\temp\dxf").resolve()
    out_dir = Path(r".\temp\dwg").resolve()

    if not in_dir.exists():
        raise FileNotFoundError(f"输入目录不存在: {in_dir}")

    out_dir.mkdir(parents=True, exist_ok=True)

    # 2️⃣ 找到所有 DXF
    dxf_files = list(in_dir.glob("*.dxf"))
    if not dxf_files:
        print("⚠️ output 目录中没有 DXF 文件")
        return

    print(f"📄 发现 {len(dxf_files)} 个 DXF，开始转换…")

    # 3️⃣ ODA 批量转换（一次）
    cmd = [
        ODA_EXE,
        str(in_dir),  # 输入目录
        str(out_dir),  # 输出目录
        "ACAD2018",
        "DWG",
        "0",  # 不递归
        "1",  # 覆盖
    ]

    subprocess.run(
        cmd,
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=subprocess.CREATE_NO_WINDOW,
    )

    # 4️⃣ 校验结果
    success = []
    failed = []

    for dxf in dxf_files:
        dwg = out_dir / (dxf.stem + ".dwg")
        if dwg.exists():
            success.append(dwg.name)
        else:
            failed.append(dxf.name)

    # 5️⃣ 结果汇总
    print(f"✅ 成功转换 {len(success)} 个 DWG")
    if failed:
        print("❌ 以下 DXF 转换失败:")
        for name in failed:
            print("   -", name)

from pathlib import Path

def fix_scr_paths(scr_path):

    scr_path = Path(scr_path)

    lines = scr_path.read_text(encoding="utf-8").splitlines()

    new_lines = []

    for line in lines:

        # 1️⃣ 替换 DLL
        if "WindowsFormsApp1.dll" in line:
            line = r"C:\Users\QRT\source\repos\PythonApplication6\DLL\WindowsFormsApp1.dll"

        # 2️⃣ 替换 JSON
        elif line.endswith("json\\source.json"):
            line = r"C:\Users\QRT\source\repos\PythonApplication6\temp\json\source.json"
        # PDF
        elif ".pdf" in line:
            line = r"C:\Users\QRT\source\repos\PythonApplication6\temp\pdf\source.pdf"

        new_lines.append(line)

    scr_path.write_text("\n".join(new_lines), encoding="utf-8")

    print("SCR 路径已修正")            
def dwgTopdf():
    core = Path(r"C:\Program Files\Autodesk\AutoCAD 2022\AcCoreConsole.exe")
    dwg = Path(r".\temp\dwg\source.dwg").resolve()
    scr = Path(r".\temp\src\source.scr").resolve()
    fix_scr_paths(scr)
    for p in (core, dwg, scr):
        if not p.exists():
            raise FileNotFoundError(p)

    cmd = [str(core), "/i", str(dwg), "/s", str(scr)]

    print("Running:", " ".join(cmd))

    subprocess.run(
        cmd, check=True, cwd=str(dwg.parent), stdout=sys.stdout, stderr=sys.stderr
    )
    print("✅ AutoCAD Core Console 执行完成")    
if __name__ == "__main__":
    start = time.perf_counter()
    svgTodxf()
    end = time.perf_counter()
    print(f"svgTodxf() 耗时: {end - start:.6f} 秒")
    dxfTodwg()
    dwgTopdf()
 
