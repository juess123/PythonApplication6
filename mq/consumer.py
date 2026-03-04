#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RabbitMQ 消费者模块（同步版本）
监听 cad_task 队列，处理 CAD 转换任务
"""

import json
import signal
import threading
import time
from typing import Optional

import pika
from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import Basic, BasicProperties

from common.log import log
from core.config import settings
from mq.callback import notify_callback
from mq.models import RabbitMQTask
from service.cad_service import process_cad_task


class CadTaskConsumer:
    """CAD 任务消费者（同步版本）"""

    def __init__(self):
        self._queue_name = settings.RABBITMQ_QUEUE_NAME
        self._connection: Optional[pika.BlockingConnection] = None
        self._channel: Optional[BlockingChannel] = None
        self._running = False
        self._should_stop = threading.Event()

    def connect(self) -> bool:
        """
        连接到 RabbitMQ

        Returns:
            bool: 连接是否成功
        """
        try:
            log.info(
                f"正在连接 RabbitMQ: {settings.RABBITMQ_HOST}:{settings.RABBITMQ_PORT}"
            )

            # 创建连接参数
            credentials = pika.PlainCredentials(
                settings.RABBITMQ_USERNAME,
                settings.RABBITMQ_PASSWORD,
            )
            parameters = pika.ConnectionParameters(
                host=settings.RABBITMQ_HOST,
                port=settings.RABBITMQ_PORT,
                virtual_host=settings.RABBITMQ_VHOST,
                credentials=credentials,
                heartbeat=600,
                blocked_connection_timeout=300,
            )

            # 创建连接
            self._connection = pika.BlockingConnection(parameters)
            self._channel = self._connection.channel()

            # 设置 prefetch，每次只取一个任务
            self._channel.basic_qos(prefetch_count=1)

            # 声明队列（确保队列存在）
            self._channel.queue_declare(queue=self._queue_name, durable=True)

            # ⭐⭐⭐ 启动时清空历史任务 ⭐⭐⭐
            log.warning(f"启动消费者，清空队列中的历史任务: {self._queue_name}")
            self._channel.queue_purge(queue=self._queue_name)

            log.info(f"RabbitMQ 连接成功，监听队列: {self._queue_name}")
            return True

        except Exception as e:
            log.error(f"RabbitMQ 连接失败: {e}", exc_info=True)
            return False

    def disconnect(self):
        """断开 RabbitMQ 连接"""
        try:
            if self._channel and self._channel.is_open:
                self._channel.close()
            if self._connection and self._connection.is_open:
                self._connection.close()
            log.info("RabbitMQ 连接已关闭")
        except Exception as e:
            log.warning(f"关闭 RabbitMQ 连接时出错: {e}")

    def process_message(
        self,
        channel: BlockingChannel,
        method: Basic.Deliver,
        properties: BasicProperties,
        body: bytes,
    ):
        """
        处理单条消息

        Args:
            channel: RabbitMQ channel
            method: 消息投递信息
            properties: 消息属性
            body: 消息体
        """
        order_id = "unknown"
        callback_url = None
        page_id = None

        try:
            # 解析消息体
            body_str = body.decode("utf-8")
            

            # 解析 JSON
            data = json.loads(body_str)
            

            # 验证并解析为 Pydantic 模型（外层 Task 包装）
            task = RabbitMQTask.model_validate(data)

            # 检查任务类型
            if task.type != "cad_task":
                log.warning(f"未知任务类型: {task.type}, 跳过处理")
                channel.basic_ack(delivery_tag=method.delivery_tag)
                return

            # 解析内层 payload
            payload = task.get_cad_payload()
            order_id = payload.order_id
            callback_url = payload.cad_call_back_url
            page_id = payload.page_id
            thickness_data = payload.thickness_data

            log.info(
                f"开始处理任务: task_id={task.id}, order_id={order_id}, "
                f"svg_key={payload.svg_key}, "
                f"page_id={page_id}, "
                f"callback_url={callback_url}"
            )

            # 调用 CAD 处理服务
            start = time.perf_counter()
            result = process_cad_task(
                svg_key=payload.svg_key,
                position=payload.position,
                material_data=payload.material_data,
                order_id=payload.order_id,
                thickness_data=thickness_data
            )
            end = time.perf_counter() - start;
            # 发送回调通知
            if callback_url:
                notify_callback(
                    callback_url=callback_url,
                    order_id=order_id,
                    success=result.success,
                    png_key=result.png_key,
                    pdf_key=result.pdf_key,
                    error_msg=result.error_msg,
                    page_id=page_id,
                    timeout=settings.CALLBACK_TIMEOUT,
                    max_retries=settings.CALLBACK_MAX_RETRIES,
                )

            if result.success:
                log.info(f"任务处理成功: order_id={order_id}, png_key={result.png_key}")
            else:
                log.error(
                    f"任务处理失败: order_id={order_id}, error={result.error_msg}"
                )

            # 确认消息（无论成功失败都确认，避免无限重试）
            channel.basic_ack(delivery_tag=method.delivery_tag)
            log.info(f"消息已确认: order_id={order_id}")
            log.info(f"✅整个svg到dwg的总时长={end}")

        except json.JSONDecodeError as e:
            log.error(f"消息 JSON 解析失败: {e}, body={body[:200]}")
            # JSON 格式错误，无法处理，直接丢弃
            channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

        except Exception as e:
            log.error(
                f"处理消息时发生错误: order_id={order_id}, error={e}", exc_info=True
            )

            # 尝试发送失败回调
            if callback_url:
                try:
                    notify_callback(
                        callback_url=callback_url,
                        order_id=order_id,
                        success=False,
                        error_msg=f"消息处理异常: {str(e)}",
                        page_id=page_id,
                        timeout=settings.CALLBACK_TIMEOUT,
                        max_retries=settings.CALLBACK_MAX_RETRIES,
                    )
                except Exception as cb_err:
                    log.error(f"发送失败回调时出错: {cb_err}")

            # 不重新入队，避免无限循环
            channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    def start_consuming(self):
        """开始消费消息"""
        if not self._channel:
            raise RuntimeError("未连接到 RabbitMQ，请先调用 connect()")

        self._running = True
        log.info("=" * 60)
        log.info("CAD 任务消费者已启动，等待消息...")
        log.info("=" * 60)

        try:
            # 设置消费者
            self._channel.basic_consume(
                queue=self._queue_name,
                on_message_callback=self.process_message,
                auto_ack=False,
            )

            # 开始消费循环
            while self._running and not self._should_stop.is_set():
                # 使用 process_data_events 而非 start_consuming
                # 这样可以定期检查停止标志
                self._connection.process_data_events(time_limit=1)

        except Exception as e:
            if not self._should_stop.is_set():
                log.error(f"消费过程中发生错误: {e}", exc_info=True)
        finally:
            self._running = False

    def stop(self):
        """停止消费者"""
        log.info("正在停止消费者...")
        self._running = False
        self._should_stop.set()

        # 尝试取消消费
        try:
            if self._channel and self._channel.is_open:
                self._channel.stop_consuming()
        except Exception as e:
            log.warning(f"停止消费时出错: {e}")

        self.disconnect()
        log.info("消费者已停止")

    def run(self):
        """运行消费者（主入口）"""
        # 连接并开始消费
        try:
            while not self._should_stop.is_set():
                try:
                    if self.connect():
                        self.start_consuming()
                        # 正常退出消费循环，检查是否需要停止
                        if self._should_stop.is_set():
                            break
                    else:
                        if self._should_stop.is_set():
                            break
                        log.warning("连接失败，5秒后重试...")
                        # 使用可中断的等待
                        self._should_stop.wait(timeout=5)
                except Exception as e:
                    if self._should_stop.is_set():
                        break
                    log.error(f"消费者运行异常: {e}", exc_info=True)
                    log.info("5秒后尝试重新连接...")
                    self._should_stop.wait(timeout=5)
        finally:
            self.disconnect()


def run_consumer():
    """启动消费者的便捷函数"""
    consumer = CadTaskConsumer()

    # 设置信号处理
    def signal_handler(signum, frame):
        log.info(f"收到信号 {signum}，正在停止...")
        consumer.stop()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    consumer.run()
