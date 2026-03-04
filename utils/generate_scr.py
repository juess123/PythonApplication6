from pathlib import Path
import os


from pathlib import Path
import os


from pathlib import Path
import os


def generate_run_scr(
    output_dir: str,
    dll_path: str,
    material_json_path: str,
    pdf_output_path: str,
    filename: str = "source.scr",
) -> str:
    os.makedirs(output_dir, exist_ok=True)

    scr_path = Path(output_dir) / filename

    # ⭐ 统一转绝对路径
    dll_path_abs = str(Path(dll_path).resolve())
    material_json_path_abs = str(Path(material_json_path).resolve())
    pdf_output_path_abs = str(Path(pdf_output_path).resolve())

    # ⭐ 所有路径必须加引号（防空格、防中文）
    content = f"""FILEDIA
0
CMDDIA
0
NETLOAD
{dll_path_abs}
RunAllTasks
{material_json_path_abs}
{pdf_output_path_abs}
FILEDIA
1
CMDDIA
1
CLOSE
N

"""

    # ⭐ 关键：用 ANSI（GBK）或 UTF-8 无 BOM
    # Windows + AutoCAD 环境下，ANSI 最稳
    scr_path.write_text(content, encoding="gbk")

    return str(scr_path)

