"""工具参数验证装饰器

提供参数验证装饰器，用于工具方法：
- @validate_params 参数验证装饰器
- @sanitize_input 输入清理装饰器
"""

from functools import wraps
from typing import Any, Callable, Dict, List, Optional, TypeVar, ParamSpec

from anyclaw.security.validators import ValidationError
from anyclaw.security.sanitizers import ContentSanitizer

P = ParamSpec('P')
T = TypeVar('T')


def validate_params(**validators: Callable[[Any], Any]) -> Callable:
    """
    参数验证装饰器

    在工具执行前验证参数，如果验证失败则返回错误消息。

    Usage:
        @validate_params(
            path=lambda x: PathValidator.validate_path(x),
            timeout=lambda x: Validator.in_range(x, 1, 300)
        )
        async def execute(self, path, timeout, **kwargs):
            ...

    Args:
        **validators: 参数名到验证函数的映射

    Returns:
        装饰器函数
    """
    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @wraps(func)
        async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            # 验证每个参数
            for param_name, validator in validators.items():
                if param_name in kwargs:
                    value = kwargs[param_name]
                    # 跳过 None 值（可选参数）
                    if value is None:
                        continue
                    try:
                        kwargs[param_name] = validator(value)
                    except ValidationError as e:
                        return f"Error: {e.message}"  # type: ignore
            return await func(*args, **kwargs)  # type: ignore

        @wraps(func)
        def sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            # 验证每个参数
            for param_name, validator in validators.items():
                if param_name in kwargs:
                    value = kwargs[param_name]
                    if value is None:
                        continue
                    try:
                        kwargs[param_name] = validator(value)
                    except ValidationError as e:
                        return f"Error: {e.message}"  # type: ignore
            return func(*args, **kwargs)  # type: ignore

        # 根据函数类型返回对应的 wrapper
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper  # type: ignore
        return sync_wrapper  # type: ignore

    return decorator


def sanitize_input(
    *param_names: str,
    max_length: Optional[int] = None,
    truncate: bool = True
) -> Callable:
    """
    输入清理装饰器

    对指定参数进行内容清理。

    Usage:
        @sanitize_input("content", "prompt")
        async def execute(self, content, prompt, **kwargs):
            ...

    Args:
        *param_names: 要清理的参数名
        max_length: 最大长度
        truncate: 是否截断超长内容

    Returns:
        装饰器函数
    """
    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @wraps(func)
        async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            for param_name in param_names:
                if param_name in kwargs:
                    value = kwargs[param_name]
                    if isinstance(value, str):
                        try:
                            kwargs[param_name] = ContentSanitizer.sanitize_message(
                                value,
                                max_length=max_length,
                                truncate=truncate
                            )
                        except ValueError as e:
                            return f"Error: {e}"  # type: ignore
            return await func(*args, **kwargs)  # type: ignore

        @wraps(func)
        def sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            for param_name in param_names:
                if param_name in kwargs:
                    value = kwargs[param_name]
                    if isinstance(value, str):
                        try:
                            kwargs[param_name] = ContentSanitizer.sanitize_message(
                                value,
                                max_length=max_length,
                                truncate=truncate
                            )
                        except ValueError as e:
                            return f"Error: {e}"  # type: ignore
            return func(*args, **kwargs)  # type: ignore

        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper  # type: ignore
        return sync_wrapper  # type: ignore

    return decorator


def require_params(*required_params: str) -> Callable:
    """
    必需参数检查装饰器

    检查必需参数是否存在且非空。

    Usage:
        @require_params("path", "content")
        async def execute(self, path, content, **kwargs):
            ...

    Args:
        *required_params: 必需的参数名

    Returns:
        装饰器函数
    """
    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @wraps(func)
        async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            missing: List[str] = []
            for param_name in required_params:
                if param_name not in kwargs or kwargs[param_name] is None:
                    missing.append(param_name)
                elif isinstance(kwargs[param_name], str) and not kwargs[param_name].strip():
                    missing.append(param_name)

            if missing:
                return f"Error: Missing required parameters: {', '.join(missing)}"  # type: ignore

            return await func(*args, **kwargs)  # type: ignore

        @wraps(func)
        def sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            missing: List[str] = []
            for param_name in required_params:
                if param_name not in kwargs or kwargs[param_name] is None:
                    missing.append(param_name)
                elif isinstance(kwargs[param_name], str) and not kwargs[param_name].strip():
                    missing.append(param_name)

            if missing:
                return f"Error: Missing required parameters: {', '.join(missing)}"  # type: ignore

            return func(*args, **kwargs)  # type: ignore

        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper  # type: ignore
        return sync_wrapper  # type: ignore

    return decorator


def validate_and_sanitize(
    validators: Optional[Dict[str, Callable[[Any], Any]]] = None,
    sanitize_params: Optional[List[str]] = None,
    required_params: Optional[List[str]] = None,
    max_length: Optional[int] = None
) -> Callable:
    """
    组合验证和清理装饰器

    提供一站式参数验证和清理。

    Usage:
        @validate_and_sanitize(
            validators={
                "timeout": lambda x: Validator.in_range(x, 1, 300)
            },
            sanitize_params=["content"],
            required_params=["path"]
        )
        async def execute(self, path, content, timeout, **kwargs):
            ...

    Args:
        validators: 参数验证器字典
        sanitize_params: 要清理的参数列表
        required_params: 必需参数列表
        max_length: 清理时的最大长度

    Returns:
        装饰器函数
    """
    validators = validators or {}
    sanitize_params = sanitize_params or []
    required_params = required_params or []

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @wraps(func)
        async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            # 1. 检查必需参数
            missing: List[str] = []
            for param_name in required_params:
                if param_name not in kwargs or kwargs[param_name] is None:
                    missing.append(param_name)
                elif isinstance(kwargs[param_name], str) and not kwargs[param_name].strip():
                    missing.append(param_name)

            if missing:
                return f"Error: Missing required parameters: {', '.join(missing)}"  # type: ignore

            # 2. 验证参数
            for param_name, validator in validators.items():
                if param_name in kwargs and kwargs[param_name] is not None:
                    try:
                        kwargs[param_name] = validator(kwargs[param_name])
                    except ValidationError as e:
                        return f"Error: {e.message}"  # type: ignore

            # 3. 清理参数
            for param_name in sanitize_params:
                if param_name in kwargs and isinstance(kwargs[param_name], str):
                    try:
                        kwargs[param_name] = ContentSanitizer.sanitize_message(
                            kwargs[param_name],
                            max_length=max_length,
                            truncate=True
                        )
                    except ValueError as e:
                        return f"Error: {e}"  # type: ignore

            return await func(*args, **kwargs)  # type: ignore

        @wraps(func)
        def sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            # 1. 检查必需参数
            missing: List[str] = []
            for param_name in required_params:
                if param_name not in kwargs or kwargs[param_name] is None:
                    missing.append(param_name)
                elif isinstance(kwargs[param_name], str) and not kwargs[param_name].strip():
                    missing.append(param_name)

            if missing:
                return f"Error: Missing required parameters: {', '.join(missing)}"  # type: ignore

            # 2. 验证参数
            for param_name, validator in validators.items():
                if param_name in kwargs and kwargs[param_name] is not None:
                    try:
                        kwargs[param_name] = validator(kwargs[param_name])
                    except ValidationError as e:
                        return f"Error: {e.message}"  # type: ignore

            # 3. 清理参数
            for param_name in sanitize_params:
                if param_name in kwargs and isinstance(kwargs[param_name], str):
                    try:
                        kwargs[param_name] = ContentSanitizer.sanitize_message(
                            kwargs[param_name],
                            max_length=max_length,
                            truncate=True
                        )
                    except ValueError as e:
                        return f"Error: {e}"  # type: ignore

            return func(*args, **kwargs)  # type: ignore

        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper  # type: ignore
        return sync_wrapper  # type: ignore

    return decorator
