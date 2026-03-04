#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
回调通知模块（同步版本）
用于在任务完成后通知 Go 服务
"""

import time
from typing import Optional

import requests

from common.log import log
from mq.models import CallbackPayload


#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
回调通知模块（同步版本）
用于在任务完成后通知 Go 服务
"""

import time
from typing import Optional

import requests

from common.log import log
from mq.models import CallbackPayload


def notify_callback(
    callback_url: str,
    order_id: str,
    success: bool,
    png_key: Optional[str] = None,
    pdf_key: Optional[str] = None,
    error_msg: Optional[str] = None,
    page_id: Optional[str] = None,
    timeout: float = 30.0,
    max_retries: int = 3,
) -> bool:
    """
    发送回调通知到 Go 服务

    Args:
        callback_url: 回调 URL
        order_id: 订单 ID
        success: 处理是否成功
        png_key: 成功时的 PNG COS key
        pdf_key: 成功时的 PDF COS key
        error_msg: 失败时的错误信息
        page_id: 页面 ID（放入请求头 x-page-id）
        timeout: 请求超时时间（秒）
        max_retries: 最大重试次数

    Returns:
        bool: 回调是否成功
    """
    payload = CallbackPayload(
        order_id=order_id,
        success=success,
        png_key=png_key,
        pdf_key=pdf_key,
        error_msg=error_msg,
    )

    # 构建请求头
    headers = {"Content-Type": "application/json"}
    if page_id:
        headers["x-page-id"] = page_id

    log.info(
        f"准备发送回调通知: url={callback_url}, order_id={order_id}, "
        f"success={success}, page_id={page_id}"
    )

    for attempt in range(1, max_retries + 1):
        try:
            response = requests.post(
                callback_url,
                json=payload.model_dump(),
                headers=headers,
                timeout=timeout,
            )

            if response.status_code == 200:
                log.info(
                    f"回调通知成功: order_id={order_id}, "
                    f"status_code={response.status_code}, "
                    f"response={response.text[:200]}"
                )
                return True
            else:
                log.warning(
                    f"回调通知返回非200状态码: order_id={order_id}, "
                    f"status_code={response.status_code}, "
                    f"response={response.text[:200]}, "
                    f"attempt={attempt}/{max_retries}"
                )

        except requests.Timeout as e:
            log.warning(
                f"回调通知超时: order_id={order_id}, "
                f"attempt={attempt}/{max_retries}, error={e}"
            )

        except requests.RequestException as e:
            log.warning(
                f"回调通知请求错误: order_id={order_id}, "
                f"attempt={attempt}/{max_retries}, error={e}"
            )

        except Exception as e:
            log.error(
                f"回调通知发生未知错误: order_id={order_id}, "
                f"attempt={attempt}/{max_retries}, error={e}",
                exc_info=True,
            )

        # 如果不是最后一次重试，等待后重试
        if attempt < max_retries:
            wait_time = 2**attempt  # 指数退避: 2, 4, 8 秒
            log.info(f"等待 {wait_time} 秒后重试回调...")
            time.sleep(wait_time)

    log.error(f"回调通知最终失败: order_id={order_id}, 已重试 {max_retries} 次")
    return False
