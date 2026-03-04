#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CAD 处理服务模块

包含:
- cad_service: CAD 转换核心处理逻辑
"""

from service.cad_service import CadTaskResult, process_cad_task

__all__ = [
    "CadTaskResult",
    "process_cad_task",
]
