"""Client for reporting completed CAD tasks to the billing service."""

import time
from typing import Any, Optional
from urllib.parse import quote

import requests

from common.log import log
from core.config import settings


def _request_with_retries(
    method: str,
    url: str,
    *,
    params: Optional[dict[str, Any]] = None,
    json_body: Optional[dict[str, Any]] = None,
) -> Optional[requests.Response]:
    """Retry only transient transport/service failures; report business errors once."""
    headers = {"Authorization": f"Bearer {settings.BILLING_SERVICE_TOKEN}"}

    for attempt in range(1, settings.BILLING_CALLBACK_MAX_RETRIES + 1):
        try:
            response = requests.request(
                method,
                url,
                params=params,
                json=json_body,
                headers=headers,
                timeout=settings.BILLING_CALLBACK_TIMEOUT,
            )
        except requests.RequestException as exc:
            if attempt < settings.BILLING_CALLBACK_MAX_RETRIES:
                delay = 2 ** (attempt - 1)
                log.warning(
                    "计费服务请求异常，将重试: method={}, attempt={}/{}, delay={}s, error={}",
                    method,
                    attempt,
                    settings.BILLING_CALLBACK_MAX_RETRIES,
                    delay,
                    exc,
                )
                time.sleep(delay)
                continue
            log.error("计费服务请求失败: method={}, url={}, error={}", method, url, exc)
            return None

        if response.status_code in (429, 503):
            if attempt < settings.BILLING_CALLBACK_MAX_RETRIES:
                retry_after = response.headers.get("Retry-After")
                try:
                    delay = (
                        max(1, int(retry_after))
                        if retry_after
                        else 2 ** (attempt - 1)
                    )
                except ValueError:
                    delay = 2 ** (attempt - 1)
                log.warning(
                    "计费服务暂时不可用，将重试: method={}, attempt={}/{}, delay={}s, status={}",
                    method,
                    attempt,
                    settings.BILLING_CALLBACK_MAX_RETRIES,
                    delay,
                    response.status_code,
                )
                time.sleep(delay)
                continue

        if not response.ok:
            try:
                error = response.json()
            except ValueError:
                error = {"body": response.text[:2000]}
            if not isinstance(error, dict):
                error = {"body": str(error)[:2000]}
            log.error(
                "计费服务返回错误: method={}, status={}, code={}, message={}, "
                "missing_call_ids={}, unready_call_ids={}, unexpected_call_ids={}",
                method,
                response.status_code,
                error.get("code"),
                error.get("message"),
                error.get("missing_call_ids"),
                error.get("unready_call_ids"),
                error.get("unexpected_call_ids"),
            )
            return None

        return response

    return None


def _get_billing_call_ids(billing_order_id: str, order_url: str) -> Optional[list[str]]:
    """Read the order's complete call manifest for complete's call_ids form."""
    call_ids: list[str] = []
    cursor: Optional[str] = None

    while True:
        params: dict[str, Any] = {"limit": 100}
        if cursor:
            params["cursor"] = cursor
        response = _request_with_retries("GET", f"{order_url}/calls", params=params)
        if response is None:
            log.error("读取计费调用清单失败: billing_order_id={}", billing_order_id)
            return None

        try:
            page = response.json().get("data", {})
            items = page.get("items", [])
            call_ids.extend(item["call_id"] for item in items)
            cursor = page.get("next_cursor")
        except (ValueError, AttributeError, KeyError, TypeError) as exc:
            log.error(
                "计费调用清单响应格式异常: billing_order_id={}, error={}",
                billing_order_id,
                exc,
            )
            return None

        if not cursor:
            break
        if len(call_ids) > 1000:
            log.error(
                "计费调用数量超过 complete 接口上限: billing_order_id={}, count={}",
                billing_order_id,
                len(call_ids),
            )
            return None

    if len(call_ids) > 1000:
        log.error(
            "计费调用数量超过 complete 接口上限: billing_order_id={}, count={}",
            billing_order_id,
            len(call_ids),
        )
        return None

    # Preserve order while protecting against duplicate records across pages.
    return list(dict.fromkeys(call_ids))


def complete_billing_order(billing_order_id: str, *, success: bool) -> bool:
    """Submit the final outcome with the complete billing order call manifest."""
    token = settings.BILLING_SERVICE_TOKEN
    if not token:
        log.error(
            "计费完成通知未发送：未配置 BILLING_SERVICE_TOKEN，billing_order_id={}",
            billing_order_id,
        )
        return False

    base_url = settings.BILLING_BASE_URL.rstrip("/")
    if not base_url.endswith("/v1"):
        base_url = f"{base_url}/v1"
    order_url = f"{base_url}/billing-orders/{quote(billing_order_id, safe='')}"
    call_ids = _get_billing_call_ids(billing_order_id, order_url)
    if call_ids is None:
        return False

    payload = {
        "outcome": "SUCCEEDED" if success else "FAILED",
        "call_ids": call_ids,
    }
    response = _request_with_retries(
        "POST", f"{order_url}/complete", json_body=payload
    )
    if response is None:
        return False

    try:
        response_body = response.json()
        settlement = response_body.get("data", {}) if isinstance(response_body, dict) else {}
    except ValueError as exc:
        log.error(
            "计费完成响应不是有效 JSON: billing_order_id={}, error={}",
            billing_order_id,
            exc,
        )
        return False

    if settlement.get("state") != "SETTLED":
        log.error(
            "计费完成接口未返回 SETTLED: billing_order_id={}, data={}",
            billing_order_id,
            settlement,
        )
        return False

    log.info(
        "计费订单完成并结算: billing_order_id={}, settlement_id={}",
        billing_order_id,
        settlement.get("settlement_id"),
    )
    return True
