# CAD 转换接口快速使用指南

## 🚀 快速开始

### 1. 环境准备

#### 必需软件
确保以下工具已安装并可访问：

```bash
# Poppler (PDF 转 PNG)
C:\Tools\poppler\Library\bin\pdftoppm.exe

# AutoCAD Core Console (DWG 转 PDF)
C:\Program Files\Autodesk\AutoCAD 2022\AcCoreConsole.exe

# ODA File Converter (DXF 转 DWG)
C:\Program Files\ODA\ODAFileConverter 26.10.0\ODAFileConverter.exe
```

#### Python 依赖
```bash
pip install fastapi pydantic qcloud-cos pillow numpy ezdxf
```

### 2. 配置文件

#### `core/config.py`
```python
class Settings:
    # COS 配置
    COS_REGION = "ap-guangzhou"
    COS_SECRET_ID = "your-secret-id"
    COS_SECRET_KEY = "your-secret-key"
    COS_BUCKET = "your-bucket"
    COS_SCHEME = "https"
    
    # 临时文件目录
    TEMP_DIR = "E:\\temp\\cad"
    
    # 可选：调试模式保留临时文件
    KEEP_TEMP_FILES = False  # 生产环境设为 False
```

### 3. API 调用示例

#### 请求
```bash
POST http://your-domain/run_cad
Content-Type: application/json

{
  "svg_key": "input/20240101/design.svg",
  "position": [
    {
      "class_name": "part1",
      "bbox": [0, 0, 100, 100]
    }
  ],
  "material_data": [
    {
      "yolo_detail_id": 1,
      "category_uuid": "cat-001",
      "category_name": "金属",
      "category_name_en": "Metal",
      "material_uuid": "mat-001",
      "material_name": "不锈钢",
      "material_name_en": "Stainless Steel",
      "material_process": "CNC加工",
      "bbox": [0, 0, 50, 50],
      "preset_id": 1
    }
  ],
  "order_id": "ORD-2024-001"
}
```

#### 成功响应
```json
{
  "code": 200,
  "msg": "CAD 转换成功",
  "data": {
    "png_key": "output/20240101/ORD-2024-001/design.png",
    "png_url": "https://bucket.cos.ap-guangzhou.myqcloud.com/output/20240101/ORD-2024-001/design.png",
    "order_id": "ORD-2024-001",
    "filename": "design.png"
  }
}
```

#### 错误响应
```json
{
  "code": 400,
  "msg": "SVG 文件下载失败: 文件不存在",
  "data": null
}
```

---

## 📝 转换流程

```
┌─────────┐
│ SVG 文件 │ (COS 云端)
└────┬────┘
     │ 步骤 1-3: 下载
     ▼
┌─────────┐
│ SVG     │ (本地)
└────┬────┘
     │ 步骤 4: svg_to_dxf
     ▼
┌─────────┐
│ DXF     │
└────┬────┘
     │ 步骤 5: dxf_to_dwg
     ▼
┌─────────┐
│ DWG     │
└────┬────┘
     │ 步骤 6: dwg_to_pdf
     ▼
┌─────────┐
│ PDF     │
└────┬────┘
     │ 步骤 7: pdf_to_png
     ▼
┌─────────┐
│ PNG     │
└────┬────┘
     │ 步骤 8: 上传
     ▼
┌─────────┐
│ PNG 文件 │ (COS 云端)
└─────────┘
```

---

## 🛠️ 常见问题

### 1. 转换失败：工具未找到
**错误**: `pdftoppm 工具不存在`

**解决**: 
```bash
# 检查工具路径
dir "C:\Tools\poppler\Library\bin\pdftoppm.exe"

# 如果不存在，下载 Poppler for Windows
# https://github.com/oschwartz10612/poppler-windows/releases
```

### 2. COS 上传失败
**错误**: `COS客户端错误`

**解决**:
```python
# 检查配置
1. 验证 SECRET_ID 和 SECRET_KEY
2. 确认 Bucket 名称正确
3. 检查网络连接
4. 验证 IAM 权限
```

### 3. 临时文件堆积
**问题**: 磁盘空间不足

**解决**:
```python
# 方案 1: 确保自动清理开启
KEEP_TEMP_FILES = False

# 方案 2: 手动清理
import shutil
shutil.rmtree("E:\\temp\\cad", ignore_errors=True)
```

### 4. 转换速度慢
**优化建议**:
- 使用 SSD 存储临时文件
- 提高服务器配置
- 考虑添加任务队列
- 实现缓存机制

---

## 📊 性能指标

### 典型转换时间 (A4 尺寸图纸)

| 步骤 | 预计时间 |
|------|---------|
| COS 下载 | 1-2 秒 |
| SVG → DXF | 2-3 秒 |
| DXF → DWG | 3-5 秒 |
| DWG → PDF | 5-10 秒 |
| PDF → PNG | 3-5 秒 |
| COS 上传 | 1-2 秒 |
| **总计** | **15-27 秒** |

### 文件大小参考

| 格式 | 典型大小 |
|------|---------|
| SVG | 50-500 KB |
| DXF | 100-1 MB |
| DWG | 200-2 MB |
| PDF | 500 KB - 5 MB |
| PNG | 1-10 MB (取决于 DPI) |

---

## 🔍 调试技巧

### 1. 查看详细日志
```python
# 在 main.py 中设置日志级别
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 2. 保留临时文件检查
```python
# settings.py
KEEP_TEMP_FILES = True  # 开启后不会删除临时文件
```

### 3. 查看中间文件
```bash
# 临时文件位置
E:\temp\cad\20240101\ORD-2024-001\
├── design.svg       # 原始 SVG
├── dxf\design.dxf   # DXF 中间文件
├── dwg\design.dwg   # DWG 中间文件
├── pdf\design.pdf   # PDF 中间文件
└── png\design.png   # 最终 PNG
```

### 4. 测试单个转换步骤
```python
# 测试 PDF → PNG
from converters.PdfToPng import pdf_to_png

result = await pdf_to_png(
    pdf_path="test.pdf",
    output_png_path="output.png",
    dpi=600,
    trim_border=True
)
print(result)
```

---

## 📦 Python 客户端示例

```python
import requests
import json

class CADConverter:
    def __init__(self, base_url):
        self.base_url = base_url
    
    def convert(self, svg_key, order_id, position=None, material_data=None):
        """
        执行 CAD 转换
        
        Args:
            svg_key: SVG 文件的 COS key
            order_id: 订单ID
            position: 位置数据列表
            material_data: 材料数据列表
        
        Returns:
            dict: 转换结果
        """
        url = f"{self.base_url}/run_cad"
        
        payload = {
            "svg_key": svg_key,
            "order_id": order_id,
            "position": position or [],
            "material_data": material_data or []
        }
        
        response = requests.post(url, json=payload)
        return response.json()

# 使用示例
converter = CADConverter("http://localhost:8000")

result = converter.convert(
    svg_key="input/20240101/design.svg",
    order_id="ORD-2024-001",
    position=[
        {
            "class_name": "part1",
            "bbox": [0, 0, 100, 100]
        }
    ],
    material_data=[
        {
            "yolo_detail_id": 1,
            "category_uuid": "cat-001",
            "category_name": "金属",
            "category_name_en": "Metal",
            "material_uuid": "mat-001",
            "material_name": "不锈钢",
            "material_name_en": "Stainless Steel",
            "material_process": "CNC加工",
            "bbox": [0, 0, 50, 50],
            "preset_id": 1
        }
    ]
)

if result["code"] == 200:
    print(f"✅ 转换成功!")
    print(f"PNG Key: {result['data']['png_key']}")
    print(f"PNG URL: {result['data']['png_url']}")
else:
    print(f"❌ 转换失败: {result['msg']}")
```

---

## 🔐 安全建议

1. **敏感信息保护**
   - 不要在代码中硬编码密钥
   - 使用环境变量或配置文件
   - 定期轮换 COS 密钥

2. **访问控制**
   - 实现 API 认证
   - 限制请求频率
   - 验证文件大小和类型

3. **数据清理**
   - 确保临时文件自动清理
   - 定期清理失败任务的残留文件
   - 监控磁盘使用情况

---

## 📚 相关文档

- [完整优化说明](OPTIMIZATION_SUMMARY.md)
- [优化前后对比](BEFORE_AFTER_COMPARISON.md)
- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [腾讯云 COS 文档](https://cloud.tencent.com/document/product/436)

---

## 🆘 获取帮助

如果遇到问题：

1. 查看日志文件获取详细错误信息
2. 检查工具路径是否正确
3. 验证 COS 配置和权限
4. 确保临时目录有写入权限
5. 查看相关文档寻找解决方案

---

**祝使用愉快！** 🎉