import json
import os
from typing import List
import os
import json
from typing import List, Dict, Any

def export_material_json(
    thickness_data: Dict[str, int | float],  # 键是addidxxx，值是数字
    material_data: List[Any],
    svg_width: float,
    svg_height: float,
    output_dir: str,
    filename: str = "source.json"
) -> str:
    """
    导出材料数据为JSON文件，将item.com_sets中的键替换为thickness_data对应的值
    
    Args:
        thickness_data: 键为addidxxx，值为对应数字的字典
        material_data: 材料数据列表，每个item需包含material_name、bbox、com_sets等属性
        svg_width: SVG宽度
        svg_height: SVG高度
        output_dir: 输出目录
        filename: 输出文件名
    
    Returns:
        生成的JSON文件路径
    """
    # ===== 1. 基础参数校验（错误处理）=====
    if not isinstance(thickness_data, dict):
        raise TypeError(f"thickness_data必须是字典类型，当前类型：{type(thickness_data)}")
    if not isinstance(material_data, list):
        raise TypeError(f"material_data必须是列表类型，当前类型：{type(material_data)}")
    if svg_width <= 0 or svg_height <= 0:
        raise ValueError(f"SVG宽高必须大于0，当前宽：{svg_width}，高：{svg_height}")
    if not output_dir:
        raise ValueError("输出目录output_dir不能为空")

    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    payload = {
        "svg": {
            "width": svg_width,
            "height": svg_height,
        },
        "materials": [],
    }

   

    # ===== 2. 核心逻辑：提取com_sets对应的数值 =====
    for item in material_data:
        # 跳过无效的材料项（基础过滤）
        if not getattr(item, "material_name", None) or not getattr(item, "bbox", None):
            print(f"跳过无效材料项：material_name/bbox为空 - {item}")
            continue

        # 获取item中的com_sets键列表（比如["addid0258", "addid0257"]）
        item_com_sets = getattr(item, "com_sets", [])
        if not isinstance(item_com_sets, list):
            print(f"警告：item.com_sets不是列表类型，已重置为空列表 - {item_com_sets}")
            item_com_sets = []

        # 从thickness_data中提取对应的值，处理键不存在的情况
        com_sets_values = []
        for key in item_com_sets:
            if key in thickness_data:
                com_sets_values.append(thickness_data[key])
            else:
                # 键不存在时的容错处理（可选：抛异常/填默认值/跳过）
                print(f"警告：thickness_data中未找到键 {key}，已跳过该键")
                # 如果你想填默认值，取消下面注释：
                # com_sets_values.append(0)

        # 将处理后的值列表加入payload
        payload["materials"].append({
            "material_name": item.material_name,
            "category_name_en": getattr(item, "category_name_en", ""),  # 容错：属性不存在时填空字符串
            "category_alias": item.category_alias,
            "com_sets": com_sets_values,  # 核心：替换为数值列表
            
            "bbox": item.bbox
        })
        

    # ===== 3. 写入JSON文件（含异常处理）=====
    json_path = os.path.join(output_dir, filename)
    try:
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        print(f"JSON文件已成功生成：{json_path}")
    except Exception as e:
        raise IOError(f"写入JSON文件失败：{str(e)}") from e

    return json_path