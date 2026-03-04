# run_cad API 文档

## 📋 概述

`run_cad` 端点用于执行 CAD 转换任务。该端点接收 SVG 文件的位置信息和类别标注，进行 CAD 转换处理。

## 🔗 端点信息

| 属性 | 值 |
|------|-----|
| **URL** | `/run_cad` |
| **方法** | `POST` |
| **内容类型** | `application/json` |
| **认证** | 无（暂时） |

## 📥 请求结构

### 请求体 (Request Body)

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| `svg_key` | `string` | 是 | SVG 文件在 COS 中的存储路径（key） |
| `position` | `array` | 是 | 位置对象列表，每个对象包含类别和边界框 |

### PositionItem 对象

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| `class_name` | `string` | 是 | 类别名称（例如：BznBlock-Rect-Bottom） |
| `bbox_mm` | `array[number]` | 是 | 边界框坐标，格式为 `[x_min, y_min, x_max, y_max]` |

### bbox_mm 坐标说明

```
bbox_mm: [x_min, y_min, x_max, y_max]
         └───────┬───────┘
                 ▼
         边界框的四个坐标值（单位：毫米）
         
  y_max ──────────────────────
        │                     │
        │   ┌───────────┐     │
        │   │           │     │
        │   │  BBOX    │     │
        │   │           │     │
        │   └───────────┘     │
  y_min ──────────────────────
        x_min              x_max
```

## 📝 请求示例

### cURL 示例

```bash
curl -X POST "http://localhost:9000/run_cad" \
  -H "Content-Type: application/json" \
  -d '{
    "svg_key": "drawings/test-drawing.svg",
    "position": [
      {
        "class_name": "BznBlock-Rect-Bottom",
        "bbox_mm": [363.1772370802333, 123.51420261754726, 689.5749447013875, 248.6774600096946]
      },
      {
        "class_name": "BznBlock-Rect-Top",
        "bbox_mm": [400.5, 250.0, 750.8, 380.2]
      },
      {
        "class_name": "Circular-Element",
        "bbox_mm": [100.0, 100.0, 200.0, 200.0]
      }
    ]
  }'
```

### Python 示例

```python
import requests

url = "http://localhost:9000/run_cad"

request_data = {
    "svg_key": "drawings/test-drawing.svg",
    "position": [
        {
            "class_name": "BznBlock-Rect-Bottom",
            "bbox_mm": [363.1772370802333, 123.51420261754726, 689.5749447013875, 248.6774600096946]
        },
        {
            "class_name": "BznBlock-Rect-Top",
            "bbox_mm": [400.5, 250.0, 750.8, 380.2]
        }
    ]
}

response = requests.post(url, json=request_data)
result = response.json()
print(result)
```

### JavaScript/TypeScript 示例

```javascript
const url = "http://localhost:9000/run_cad";

const requestData = {
  svg_key: "drawings/test-drawing.svg",
  position: [
    {
      class_name: "BznBlock-Rect-Bottom",
      bbox_mm: [363.1772370802333, 123.51420261754726, 689.5749447013875, 248.6774600096946]
    },
    {
      class_name: "BznBlock-Rect-Top",
      bbox_mm: [400.5, 250.0, 750.8, 380.2]
    }
  ]
};

fetch(url, {
  method: "POST",
  headers: {
    "Content-Type": "application/json"
  },
  body: JSON.stringify(requestData)
})
  .then(response => response.json())
  .then(data => console.log(data))
  .catch(error => console.error("Error:", error));
```

## 📤 响应结构

### 成功响应 (200 OK)

```json
{
  "message": "CAD 转换请求已接收",
  "svg_key": "drawings/test-drawing.svg",
  "position_count": 2,
  "positions": [
    {
      "class_name": "BznBlock-Rect-Bottom",
      "bbox": [363.1772370802333, 123.51420261754726, 689.5749447013875, 248.6774600096946]
    },
    {
      "class_name": "BznBlock-Rect-Top",
      "bbox": [400.5, 250.0, 750.8, 380.2]
    }
  ]
}
```

### 字段说明

| 字段 | 类型 | 描述 |
|------|------|------|
| `message` | `string` | 响应消息 |
| `svg_key` | `string` | SVG 文件的 COS key |
| `position_count` | `number` | 处理的位置项数量 |
| `positions` | `array` | 返回的位置信息列表 |

### 错误响应

#### 400 Bad Request - 缺少必填字段

```json
{
  "detail": [
    {
      "loc": ["body", "svg_key"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

#### 422 Unprocessable Entity - 数据验证失败

```json
{
  "detail": [
    {
      "loc": ["body", "position", 0, "bbox_mm"],
      "msg": "ensure this value has at least 4 items",
      "type": "value_error.list.min_items",
      "ctx": {"limit_value": 4}
    }
  ]
}
```

#### 500 Internal Server Error - 服务器内部错误

```json
{
  "detail": "Internal server error",
  "message": "CAD 转换处理失败"
}
```

## 🧪 测试

### 使用 Swagger UI 测试

1. 访问 API 文档：http://localhost:9000/docs
2. 找到 `POST /run_cad` 端点
3. 点击 "Try it out"
4. 输入请求体数据
5. 点击 "Execute" 执行测试

### 使用测试脚本

运行提供的测试脚本：

```bash
python test_run_cad_api.py
```

## 💡 使用场景

### 场景 1：单对象转换

```json
{
  "svg_key": "single-object.svg",
  "position": [
    {
      "class_name": "BznBlock-Rect-Bottom",
      "bbox_mm": [363.18, 123.51, 689.57, 248.68]
    }
  ]
}
```

### 场景 2：多对象批量转换

```json
{
  "svg_key": "multi-objects.svg",
  "position": [
    {
      "class_name": "BznBlock-Rect-Bottom",
      "bbox_mm": [363.18, 123.51, 689.57, 248.68]
    },
    {
      "class_name": "BznBlock-Rect-Top",
      "bbox_mm": [400.5, 250.0, 750.8, 380.2]
    },
    {
      "class_name": "Circular-Element",
      "bbox_mm": [100.0, 100.0, 200.0, 200.0]
    }
  ]
}
```

### 场景 3：复杂图纸处理

```json
{
  "svg_key": "complex-drawing.svg",
  "position": [
    {
      "class_name": "BznBlock-Rect-Bottom",
      "bbox_mm": [0.0, 0.0, 500.0, 300.0]
    },
    {
      "class_name": "BznBlock-Rect-Top",
      "bbox_mm": [0.0, 300.0, 500.0, 600.0]
    },
    {
      "class_name": "Connector",
      "bbox_mm": [250.0, 300.0, 350.0, 320.0]
    },
    {
      "class_name": "Label-Area",
      "bbox_mm": [10.0, 10.0, 200.0, 50.0]
    }
  ]
}
```

## ⚠️ 注意事项

1. **SVG 文件存在性**：确保 `svg_key` 指向的文件在 COS 中存在
2. **坐标格式**：`bbox_mm` 必须包含 4 个数值，按 `[x_min, y_min, x_max, y_max]` 顺序
3. **数据精度**：坐标值使用毫米（mm）为单位，建议保留 4 位小数以保证精度
4. **文件大小**：SVG 文件大小应合理，避免过大的文件导致处理超时
5. **并发限制**：注意控制请求频率，避免过多并发请求

## 🔄 未来扩展

- [ ] 支持异步处理，返回任务 ID
- [ ] 添加文件上传功能
- [ ] 支持多种格式输出（PNG、JPG、PDF 等）
- [ ] 添加批量处理接口
- [ ] 支持自定义参数（分辨率、颜色等）
- [ ] 添加认证和授权机制

## 📚 相关文档

- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [项目启动指南](./STARTUP.md)
- [API 测试脚本](./test_run_cad_api.py)

---

**最后更新时间**: 2026-01-21  
**API 版本**: 1.0.0  
**维护团队**: PythonApplication3



dll_path=r"C:\Users\Administrator\Desktop\PythonApplication6\DLL\WindowsFormsApp1.dll",