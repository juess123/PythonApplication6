import subprocess
import sys
import os
from pathlib import Path

from common.log import log


def dwgTopdf():
    core = Path(r"C:\Program Files\Autodesk\AutoCAD 2022\AcCoreConsole.exe")

    dwg = Path(r".\dwg\test.dwg").resolve()
    scr = Path(r".\run.scr").resolve()

    for p in (core, dwg, scr):
        if not p.exists():
            raise FileNotFoundError(p)

    cmd = [str(core), "/i", str(dwg), "/s", str(scr)]

    print("Running:", " ".join(cmd))

    subprocess.run(
        cmd, check=True, cwd=str(dwg.parent), stdout=sys.stdout, stderr=sys.stderr
    )
    print("✅ AutoCAD Core Console 执行完成")


def dwg_to_pdf(dwg_path: str, pdf_output_path: str, scr_path: str) -> str:
    """
    将 DWG 文件转换为指定的 PDF 路径（同步版本）

    Args:
        dwg_path: DWG 文件路径
        pdf_output_path: PDF 输出路径
        scr_path: SCR 脚本路径

    Returns:
        str: PDF 文件路径
    """
    try:
        core = Path(r"C:\Program Files\Autodesk\AutoCAD 2022\AcCoreConsole.exe")
        dwg_file = Path(dwg_path).resolve()
        pdf_file = Path(pdf_output_path).resolve()
        scr_file = Path(scr_path).resolve()

        # ================= 基础校验 =================
        if not core.exists():
            raise FileNotFoundError(f"AutoCAD Core Console 未找到: {core}")

        if not dwg_file.exists():
            raise FileNotFoundError(f"DWG 文件未找到: {dwg_file}")

        if not scr_file.exists():
            raise FileNotFoundError(f"脚本文件未找到: {scr_file}")

        # 确保输出目录存在
        pdf_file.parent.mkdir(parents=True, exist_ok=True)

        log.info(f"开始 DWG → PDF: {dwg_file}")

        cmd = [
            str(core),
            "/i",
            str(dwg_file),
            "/s",
            str(scr_file),
        ]

        # ================= 调用 AutoCAD Core Console =================
        with open(os.devnull, "w") as devnull:
            subprocess.run(
                cmd,
                cwd=str(dwg_file.parent),
                stdin=devnull,
                stdout=devnull,
                stderr=devnull,
                creationflags=subprocess.CREATE_NO_WINDOW,
                check=True,
            )

        # ================= 成功判据 =================
        if not pdf_file.exists():
            raise FileNotFoundError(f"PDF 未生成: {pdf_file}")

        file_size = pdf_file.stat().st_size
        log.info(f"DWG 转 PDF 成功: {pdf_file} ({file_size} bytes)")

        return str(pdf_file)

    except subprocess.CalledProcessError as e:
        log.error("AutoCAD Core Console 执行失败", exc_info=True)
        raise

    except Exception as e:
        log.error(f"DWG 转 PDF 发生错误: {e}", exc_info=True)
        raise
