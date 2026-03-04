# SVG2CAD - RabbitMQ 消费者服务

一个基于几何优先的 SVG 到 CAD (DXF/DWG) 转换服务，通过 RabbitMQ 消息队列接收任务。

## 架构

```
Go 服务 → RabbitMQ (cad_task 队列) → Python 消费者 → CAD 转换 → 回调通知 Go 服务
```

### 转换流程

```
SVG (从 COS 下载)
 → Python (SVG 解析 & 语义推理)
 → Geometry Model (几何模型)
 → DXF (ezdxf 生成)
 → DWG (ODA File Converter)
 → PDF (AutoCAD Core Console)
 → PNG (裁剪白边)
 → COS (上传)
 → 回调通知
```

## 目录结构

```
PythonApplication4/
├── mq/                    # RabbitMQ 消息队列模块
│   ├── consumer.py        # 消费者逻辑
│   ├── callback.py        # 回调通知
│   └── models.py          # 消息模型定义
│
├── service/               # 业务服务层
│   └── cad_service.py     # CAD 转换核心逻辑
│
├── svg/                   # SVG 解析和语义分析
│   ├── builder.py         # SVG 文档构建
│   ├── model.py           # SVG 数据模型
│   ├── clip_geoms.py      # 裁剪几何
│   └── viewport.py        # 视口和坐标变换
│
├── geometry/              # 纯几何数据结构
│   ├── types.py           # 点、几何节点等类型
│   ├── bezier.py          # 贝塞尔曲线
│   ├── polygon.py         # 多边形处理
│   └── clip.py            # 几何裁剪
│
├── kernel/                # 处理管线
│   ├── pipeline.py        # 主调度管线
│   ├── node.py            # 节点处理
│   └── writer.py          # DXF 写入
│
├── converters/            # 格式转换器
│   ├── SvgToDxf.py        # SVG → DXF
│   ├── DxfToDwg.py        # DXF → DWG (ODA)
│   ├── DwgToPdf.py        # DWG → PDF (AutoCAD)
│   └── PdfToPng.py        # PDF → PNG
│
├── core/                  # 核心配置
│   ├── config.py          # 配置管理
│   └── cos_client.py      # COS 客户端
│
├── common/                # 公共模块
│   ├── log.py             # 日志
│   └── response.py        # 响应模型
│
├── utils/                 # 工具
│   ├── generate_scr.py    # SCR 脚本生成
│   └── material_export.py # 材料导出
│
├── run.py                 # 启动入口
└── requirements.txt       # Python 依赖
```

## 环境要求

- Python 3.10+
- RabbitMQ Server
- ODA File Converter 26.10.0
- AutoCAD 2022 (AcCoreConsole)

## 安装

```bash
# 安装 Python 依赖
pip install -r requirements.txt
```

## 配置

在项目根目录创建 `.env` 文件：

```env
# ========== 腾讯云 COS 配置 ==========
COS_SECRET_ID=your_secret_id
COS_SECRET_KEY=your_secret_key
COS_REGION=ap-shanghai
COS_BUCKET=your_bucket_name
COS_SCHEME=https
COS_CDN_DOMAIN=
COS_BASE_PATH=cad

# ========== 日志配置 ==========
LOG_DIR=./logs
LOG_LEVEL=INFO

# ========== 临时目录配置 ==========
TEMP_DIR=./temp
KEEP_TEMP_FILES=false

# ========== RabbitMQ 配置 ==========
RABBITMQ_HOST=127.0.0.1
RABBITMQ_PORT=5672
RABBITMQ_USERNAME=guest
RABBITMQ_PASSWORD=guest
RABBITMQ_VHOST=/
RABBITMQ_QUEUE_NAME=cad_task

# ========== 回调配置 ==========
CALLBACK_TIMEOUT=30.0
CALLBACK_MAX_RETRIES=3
```

## 启动

```bash
python run.py
```

## 消息格式

### 任务消息 (Go → Python)

Go 服务投递到 `cad_task` 队列的消息格式（外层 Task 包装 + 内层 payload）：

```json
{
    "id": "20260126185141681100",
    "type": "cad_task",
    "payload": {
        "svg_key": "svg-local/278/2026-01-26/test.svg",
        "order_id": "20260126185141681100",
        "page_id": "b9fee592-179f-480a-830d-13bab370808c",
        "cad_call_back_url": "http://your-go-service/api/cad/callback",
        "position": [
            {
                "class_name": "OTitle-N-N-H",
                "bbox": [0.161184, 0.376135, 0.077235, 0.036116]
            }
        ],
        "material_data": [
            {
                "yolo_detail_id": 4113,
                "category_uuid": "b95b5dce-e87d-4fbd-aea3-c2f0bce10280",
                "category_name": "横状文字",
                "category_name_en": "OTitle-N-N-H",
                "material_uuid": "a0f8a351-9530-4a57-a4fb-ec7a67f3e1c8",
                "material_name": "3mm亚克力",
                "material_name_en": "acrylic-mirror",
                "material_process": "",
                "bbox": [0.161184, 0.376135, 0.077235, 0.036116],
                "preset_id": 134
            }
        ]
    },
    "created_at": "2026-01-26T18:51:47.4893126+08:00",
    "delay": 0
}
```

**外层 Task 字段说明：**
| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | string | 任务ID（通常与 order_id 相同） |
| `type` | string | 任务类型，固定为 `cad_task` |
| `payload` | object | 实际的任务数据 |
| `created_at` | datetime | 任务创建时间 |
| `delay` | int | 延迟时间（秒） |

### 回调通知 (Python → Go)

任务完成后，Python 服务会向 `cad_call_back_url` 发送 POST 请求。

**请求头：**
```
Content-Type: application/json
x-page-id: b9fee592-179f-480a-830d-13bab370808c    # 来自 payload 中的 page_id
```

**成功响应体：**
```json
{
    "order_id": "20260126185141681100",
    "success": true,
    "png_key": "cad/20260126/20260126185141681100/source.png",
    "error_msg": null
}
```

**失败响应体：**
```json
{
    "order_id": "20260126185141681100",
    "success": false,
    "png_key": null,
    "error_msg": "SVG 文件下载失败: ..."
}
```

## 特性

- **单任务串行处理**：通过 `prefetch_count=1` 确保每次只处理一个任务
- **CAD 锁机制**：保证 AutoCAD Core Console 的串行调用
- **自动重连**：使用 `aio_pika.connect_robust` 实现 RabbitMQ 连接自动恢复
- **回调重试**：支持指数退避的回调重试机制
- **消息确认**：处理完成后才确认消息，避免任务丢失

## 外部工具路径

代码中硬编码的外部工具路径（根据实际情况修改）：

- ODA File Converter: `C:\Program Files\ODA\ODAFileConverter 26.10.0\ODAFileConverter.exe`
- AutoCAD Core Console: `C:\Program Files\Autodesk\AutoCAD 2022\AcCoreConsole.exe`
- DLL 路径: `C:\Users\QRT\source\repos\PythonApplication4\DLL\WindowsFormsApp1.dll`
