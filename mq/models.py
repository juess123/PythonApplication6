#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RabbitMQ 消息模型定义
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class PositionItem(BaseModel):
    """位置项模型"""

    class_name: str = Field(..., description="类别名称")
    bbox: List[float] = Field(
        ..., description="边界框坐标 [x_min, y_min, x_max, y_max]"
    )


class MaterialItem(BaseModel):
    """材料项模型"""

    yolo_detail_id: int = Field(description="YOLO检测详情ID（关联 YoloDetails）")
    category_uuid: str = Field(..., description="分类UUID")
    category_name: str = Field(..., description="分类名称")
    category_name_en: str = Field(..., description="分类名称英文")
    material_uuid: str = Field(..., description="材料UUID")
    material_name: str = Field(..., description="材料名称")
    material_name_en: str = Field(..., description="材料名称英文")
    material_process: str = Field("", description="材料工艺处理")
    bbox: List[float] = Field(..., description="yolo检测区域")
    preset_id: int = Field(..., description="预设ID")
    com_sets: List[str] = Field(description="组件ID")
    category_alias: str = Field(..., description="组件分类")


class CadTaskPayload(BaseModel):
    """CAD 任务 payload（嵌套在 Task.payload 中）"""

    svg_key: str = Field(..., description="SVG cos key")
    position: List[PositionItem] = Field(
        default_factory=list, description="位置列表，包含类别名称和边界框坐标"
    )
    material_data: List[MaterialItem] = Field(
        default_factory=list, description="材料数据列表"
    )
    order_id: str = Field(..., description="订单ID")
    thickness_data: dict
    page_id: str = Field(..., description="页面ID")
    cad_call_back_url: str = Field(..., description="回调通知URL")


class RabbitMQTask(BaseModel):
    """
    RabbitMQ 任务消息（外层包装）

    消息格式示例:
    {
        "id": "20260126185141681100",
        "type": "cad_task",
        "payload": { ... },
        "created_at": "2026-01-26T18:51:47.4893126+08:00",
        "delay": 0
    }
    """

    id: str = Field(..., description="任务ID")
    type: str = Field(..., description="任务类型")
    payload: Dict[str, Any] = Field(..., description="任务载荷（原始字典）")
    created_at: datetime = Field(..., description="创建时间")
    delay: int = Field(default=0, description="延迟时间")

    def get_cad_payload(self) -> CadTaskPayload:
        """解析并返回 CAD 任务 payload"""
        return CadTaskPayload.model_validate(self.payload)


class CallbackPayload(BaseModel):
    """回调通知载荷"""

    order_id: str = Field(..., description="订单ID")
    success: bool = Field(..., description="处理是否成功")
    png_key: Optional[str] = Field(
        None, description="成功时的 PNG COS key"
    )
    pdf_key: Optional[str] = Field(
        None, description="成功时的 PDF COS key"
    )
    error_msg: Optional[str] = Field(
        None, description="失败时的错误信息"
    )

