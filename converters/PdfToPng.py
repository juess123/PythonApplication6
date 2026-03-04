import asyncio
import subprocess
from pathlib import Path
from typing import Optional

import numpy as np
from PIL import Image

from common.log import log


def trim_white_border(png_path, out_path, threshold=245, margin=10):
    """
    去除 PNG 白边（适用于打印 PDF / 扫描 PDF）

    threshold: 判定为"白色"的像素阈值（0~255）
    margin: 裁剪后保留的安全边距（像素）
    """
    img = Image.open(png_path).convert("RGB")
    arr = np.array(img)

    # 非白色像素 mask
    mask = np.any(arr < threshold, axis=2)
    coords = np.argwhere(mask)

    if coords.size == 0:
        raise RuntimeError("图片中未检测到有效内容")

    y0, x0 = coords.min(axis=0)
    y1, x1 = coords.max(axis=0)

    # 加安全边距
    h, w = arr.shape[:2]
    x0 = max(0, x0 - margin)
    y0 = max(0, y0 - margin)
    x1 = min(w, x1 + margin)
    y1 = min(h, y1 + margin)

    cropped = img.crop((x0, y0, x1 + 1, y1 + 1))
    cropped.save(out_path)


def pdfTopng():
    """
    ./dwg/test.pdf  ->  ./dwg/test.png
    Poppler 转 PNG + 图像级裁白（最终版）
    """

    base_dir = Path("./dwg").resolve()
    pdf_path = base_dir / "test.pdf"
    tmp_png = base_dir / "test-raw.png"
    out_png = base_dir / "test.png"

    if not pdf_path.exists():
        raise FileNotFoundError(pdf_path)

    pdftoppm = r"C:\Tools\poppler\Library\bin\pdftoppm.exe"

    # 1️⃣ PDF → PNG（不裁，完整转）
    subprocess.run(
        [
            pdftoppm,
            "-png",
            "-r",
            "600",
            "-singlefile",
            str(pdf_path),
            str(base_dir / "test-raw"),
        ],
        check=True,
    )

    if not tmp_png.exists():
        raise RuntimeError("PNG not generated")

    # 2️⃣ 图像级裁白
    trim_white_border(tmp_png, out_png)

    # 可选：删除中间文件
    tmp_png.unlink(missing_ok=True)

    return out_png


async def pdf_to_png(pdf_path: str,output_png_path: str,dpi: int = 150,trim_border: bool = True,) -> Optional[str]:
    """
    异步将 PDF 转换为 PNG（支持就地裁剪白边）
    流程：
        PDF -> pdftoppm -> out_png
        如果 trim_border=True:
            out_png -> 裁剪 -> 覆盖 out_png

    Args:
        pdf_path: 输入 PDF 文件路径
        output_png_path: 输出 PNG 文件路径
        dpi: 分辨率，默认 600
        trim_border: 是否裁剪白边

    Returns:
        成功返回 PNG 路径字符串，失败返回 None
    """
    try:
        pdf_file = Path(pdf_path).resolve()
        out_png = Path(output_png_path).resolve()

        # 1️⃣ 校验输入 PDF
        if not pdf_file.exists():
            log.error(f"PDF 文件不存在: {pdf_file}")
            return None

        # 2️⃣ 确保输出目录存在
        await asyncio.to_thread(out_png.parent.mkdir, parents=True, exist_ok=True)

        # 3️⃣ 检查 pdftoppm
        pdftoppm = Path(r"C:\Tools\poppler\Library\bin\pdftoppm.exe")
        if not pdftoppm.exists():
            log.error(f"pdftoppm 工具不存在: {pdftoppm}")
            return None

        log.info(f"开始转换 PDF → PNG: {pdf_file} -> {out_png}")

        # 4️⃣ PDF → PNG（始终生成 out_png）
        out_base = out_png.parent / out_png.stem

        cmd = [
            str(pdftoppm),
            "-png",
            "-r", str(dpi),
            "-singlefile",
            str(pdf_file),
            str(out_base),
        ]

        await asyncio.to_thread(
            subprocess.run,
            cmd,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )

        if not out_png.exists():
            log.error(f"PNG 文件未生成: {out_png}")
            return None

        # 5️⃣ 就地裁剪白边（可选）
        if trim_border:
            log.info("开始裁剪白边...")
            await asyncio.to_thread(trim_white_border, out_png, out_png)

        # 6️⃣ 最终校验
        file_stat = await asyncio.to_thread(out_png.stat)
        log.info(
            f"✅ PNG 转换成功: {out_png}, 大小: {file_stat.st_size} bytes"
        )

        return str(out_png)

    except subprocess.CalledProcessError as e:
        stderr = e.stderr.decode(errors="ignore") if e.stderr else str(e)
        log.error(f"PDF 转 PNG 执行失败:\n{stderr}")
        return None

    except Exception as e:
        log.error("PDF 转 PNG 发生未知错误", exc_info=True)
        return None
def trim_png_white_border(
    png_path: str,
    white_threshold: int = 250,
):
    """
    就地裁剪 PNG 白边（覆盖原文件）

    Args:
        png_path: PNG 文件路径
        white_threshold: 灰度阈值，>= 该值视为白
    """
    from PIL import Image
    import numpy as np

    img = Image.open(png_path).convert("L")  # 转灰度
    arr = np.array(img)

    # 找到非白像素
    ys, xs = np.where(arr < white_threshold)

    # 全白保护
    if len(xs) == 0 or len(ys) == 0:
        # 全白图，不裁
        return

    left   = xs.min()
    right  = xs.max()
    top    = ys.min()
    bottom = ys.max()

    # Pillow crop: (left, upper, right, lower)
    cropped = img.crop((left, top, right + 1, bottom + 1))

    # 覆盖原文件（保持 PNG）
    cropped.save(png_path)