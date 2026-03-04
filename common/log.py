#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志系统配置
基于 loguru 的简化日志系统
"""
import logging
import sys
from pathlib import Path
from loguru import logger
from core.config import settings




class InterceptHandler(logging.Handler):
    """
    自定义的 logging Handler，将标准日志模块的记录重定向到 loguru
    """

    def emit(self, record: logging.LogRecord):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def setup_loggings():
    """
    配置日志系统
    """
    # 去除默认控制台输出
    logger.remove()

    # 定义日志格式
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: ^8}</level> | "
        "process [<cyan>{process}</cyan>]:<cyan>{thread}</cyan> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    )

    # 创建日志目录
    log_dir = Path(settings.LOG_DIR)
    log_dir.mkdir(parents=True, exist_ok=True)

    # 控制台输出
    logger.add(
        sys.stdout,
        format=log_format,
        level=settings.LOG_LEVEL,
        colorize=True,
        # filter=_logger_filter,
    )

    logger.add(
        log_dir / "access.log",
        format=log_format,
        level="DEBUG",
        rotation="200 MB",
        retention="10 days",
        encoding="utf-8",
        enqueue=True,
        # filter=_logger_filter,
    )

    # 错误日志
    logger.add(
        log_dir / "error.log",
        format=log_format,
        level="ERROR",
        rotation="200 MB",
        retention="10 days",
        encoding="utf-8",
        enqueue=True,
        # filter=_logger_filter,
    )

    # 拦截标准 logging 输出
    root_logger = logging.getLogger()
    root_logger.handlers = []
    root_logger.addHandler(InterceptHandler())
    root_logger.setLevel(logging.DEBUG)


# 初始化日志系统
setup_loggings()
log = logger
