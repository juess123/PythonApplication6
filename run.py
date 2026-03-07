#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RabbitMQ 消费者启动脚本（同步版本）

监听 cad_task 队列，处理 CAD 转换任务
"""

import sys
from pathlib import Path
import logging
# 将项目根目录添加到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from common.log import log, setup_loggings
from core.cos_client import get_cos_client
from mq.consumer import run_consumer


def main():
    """主函数"""
    # 初始化日志
    setup_loggings()
    logging.getLogger("ezdxf").setLevel(logging.WARNING)
    logging.getLogger("pika").setLevel(logging.WARNING)   # 👈 加这一行
    log.info("=" * 60)
    log.info("CAD 任务消费者服务启动中...")
    log.info("=" * 60)

    # 预初始化 COS 客户端（验证配置）
    try:
        log.info("正在初始化 COS 客户端...")
        cos_client = get_cos_client()
        log.info(
            f"COS 客户端初始化成功: bucket={cos_client.bucket}, region={cos_client.region}"
        )
    except Exception as e:
        log.error(f"COS 客户端初始化失败: {e}", exc_info=True)
        log.error("请检查 .env 配置文件中的 COS 配置")
        sys.exit(1)

    # 启动消费者
    try:
        run_consumer()
    except KeyboardInterrupt:
        log.info("收到键盘中断信号，正在退出...")
    except Exception as e:
        log.error(f"消费者运行异常: {e}", exc_info=True)
        sys.exit(1)

    log.info("=" * 60)
    log.info("CAD 任务消费者服务已停止")
    log.info("=" * 60)


if __name__ == "__main__":
    main()
