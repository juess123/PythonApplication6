#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RabbitMQ 消息队列模块

包含:
- consumer: 消费者逻辑
- callback: 回调通知
- models: 消息模型
"""

from mq.callback import notify_callback
from mq.consumer import CadTaskConsumer, run_consumer
from mq.models import (
    CadTaskPayload,
    CallbackPayload,
    MaterialItem,
    PositionItem,
    RabbitMQTask,
)

__all__ = [
    "CadTaskConsumer",
    "run_consumer",
    "notify_callback",
    "RabbitMQTask",
    "CadTaskPayload",
    "CallbackPayload",
    "PositionItem",
    "MaterialItem",
]
