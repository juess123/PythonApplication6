import subprocess
from pathlib import Path

from common.log import log

ODA_EXE = r"C:\Program Files\ODA\ODAFileConverter 26.12.0\ODAFileConverter.exe"



def dxf_to_dwg(dxf_dir: str, dwg_dir: str) -> tuple[bool, str]:
    """
    将 DXF 文件转换为 DWG 文件（同步版本）

    Args:
        dxf_dir: DXF 文件所在目录
        dwg_dir: DWG 输出目录

    Returns:
        tuple[bool, str]: (是否成功, DWG 文件路径)
    """
    in_dir = Path(dxf_dir).resolve()
    out_dir = Path(dwg_dir).resolve()

    # 找到所有 DXF
    dxf_files = list(in_dir.glob("*.dxf"))
    if not dxf_files:
        log.error("⚠️ output 目录中没有 DXF 文件")
        return False, ""

    log.info(f"📄 发现 {len(dxf_files)} 个 DXF，开始转换…")

    # 实际上每个目录下只有一个 DXF 文件，所以直接转换即可

    # ODA 批量转换（一次）
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

    dxf_file = dxf_files[0]
    dwg_file = out_dir / (dxf_file.stem + ".dwg")
    if dwg_file.exists():
        log.info(f"成功转换 {dwg_file.name}")
        return True, str(dwg_file)
    else:
        log.error(f"{dxf_file.name} 转换失败")
        return False, ""
