"""ZAI Endpoint 自动检测"""
import asyncio
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass

import httpx

logger = logging.getLogger(__name__)

# Endpoint 配置
ZAI_ENDPOINTS_CONFIG = {
    "coding-global": {
        "base_url": "https://api.z.ai/api/paas/v4",
        "test_endpoint": "/chat/completions",
        "default_model": "glm-5",
        "description": "GLM Coding Plan (Global)",
    },
    "coding-cn": {
        "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "test_endpoint": "/chat/completions",
        "default_model": "glm-5",
        "description": "GLM Coding Plan (China)",
    },
    "global": {
        "base_url": "https://api.z.ai/api/paas/v4",
        "test_endpoint": "/chat/completions",
        "default_model": "glm-5",
        "description": "Z.AI Global API",
    },
    "cn": {
        "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "test_endpoint": "/chat/completions",
        "default_model": "glm-5",
        "description": "Z.AI China API",
    },
}

# 检测超时
DETECT_TIMEOUT = 10.0


@dataclass
class DetectResult:
    """检测结果"""
    endpoint: str
    base_url: str
    default_model: str
    description: str
    success: bool
    error: Optional[str] = None


async def _test_endpoint(
    api_key: str,
    endpoint_name: str,
    config: Dict[str, Any],
) -> DetectResult:
    """
    测试单个 endpoint

    Args:
        api_key: API Key
        endpoint_name: endpoint 名称
        config: endpoint 配置

    Returns:
        检测结果
    """
    base_url = config["base_url"]
    url = f"{base_url}{config['test_endpoint']}"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    # 发送最小化测试请求
    payload = {
        "model": config["default_model"],
        "messages": [{"role": "user", "content": "hi"}],
        "max_tokens": 1,
    }

    try:
        async with httpx.AsyncClient(timeout=DETECT_TIMEOUT) as client:
            response = await client.post(url, json=payload, headers=headers)

            # 检查响应
            if response.status_code == 200:
                return DetectResult(
                    endpoint=endpoint_name,
                    base_url=base_url,
                    default_model=config["default_model"],
                    description=config["description"],
                    success=True,
                )

            # 认证错误 - API Key 无效或 endpoint 不匹配
            if response.status_code in (401, 403):
                return DetectResult(
                    endpoint=endpoint_name,
                    base_url=base_url,
                    default_model=config["default_model"],
                    description=config["description"],
                    success=False,
                    error=f"Auth failed: {response.status_code}",
                )

            # 其他错误
            return DetectResult(
                endpoint=endpoint_name,
                base_url=base_url,
                default_model=config["default_model"],
                description=config["description"],
                success=False,
                error=f"HTTP {response.status_code}",
            )

    except httpx.TimeoutException:
        return DetectResult(
            endpoint=endpoint_name,
            base_url=base_url,
            default_model=config["default_model"],
            description=config["description"],
            success=False,
            error="Timeout",
        )
    except Exception as e:
        return DetectResult(
            endpoint=endpoint_name,
            base_url=base_url,
            default_model=config["default_model"],
            description=config["description"],
            success=False,
            error=str(e),
        )


async def detect_zai_endpoint_async(api_key: str) -> Dict[str, Any]:
    """
    异步检测最佳 ZAI endpoint

    Args:
        api_key: ZAI API Key

    Returns:
        检测结果字典
    """
    if not api_key:
        return {
            "endpoint": "coding-global",
            "base_url": ZAI_ENDPOINTS_CONFIG["coding-global"]["base_url"],
            "default_model": ZAI_ENDPOINTS_CONFIG["coding-global"]["default_model"],
            "success": False,
            "error": "No API key provided",
        }

    # 按优先级测试 endpoint
    # Coding Plan 用户优先
    priority_order = ["coding-global", "coding-cn", "global", "cn"]

    for endpoint_name in priority_order:
        config = ZAI_ENDPOINTS_CONFIG[endpoint_name]
        result = await _test_endpoint(api_key, endpoint_name, config)

        if result.success:
            logger.info(f"ZAI endpoint detected: {endpoint_name}")
            return {
                "endpoint": result.endpoint,
                "base_url": result.base_url,
                "default_model": result.default_model,
                "description": result.description,
                "success": True,
            }

    # 所有 endpoint 都失败，返回默认值
    logger.warning("ZAI endpoint detection failed, using default")
    return {
        "endpoint": "coding-global",
        "base_url": ZAI_ENDPOINTS_CONFIG["coding-global"]["base_url"],
        "default_model": ZAI_ENDPOINTS_CONFIG["coding-global"]["default_model"],
        "success": False,
        "error": "All endpoints failed",
    }


def detect_zai_endpoint(api_key: str) -> Dict[str, Any]:
    """
    同步检测最佳 ZAI endpoint

    Args:
        api_key: ZAI API Key

    Returns:
        检测结果字典
    """
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # 如果已经在异步上下文中，创建新线程
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(
                    asyncio.run,
                    detect_zai_endpoint_async(api_key)
                )
                return future.result()
        else:
            return loop.run_until_complete(detect_zai_endpoint_async(api_key))
    except RuntimeError:
        # 没有事件循环
        return asyncio.run(detect_zai_endpoint_async(api_key))


def get_endpoint_info(endpoint: str) -> Optional[Dict[str, Any]]:
    """
    获取 endpoint 信息

    Args:
        endpoint: endpoint 名称

    Returns:
        endpoint 配置或 None
    """
    return ZAI_ENDPOINTS_CONFIG.get(endpoint)


def list_available_endpoints() -> list[Dict[str, str]]:
    """
    列出所有可用的 endpoint

    Returns:
        endpoint 列表
    """
    return [
        {
            "name": name,
            "base_url": config["base_url"],
            "default_model": config["default_model"],
            "description": config["description"],
        }
        for name, config in ZAI_ENDPOINTS_CONFIG.items()
    ]
