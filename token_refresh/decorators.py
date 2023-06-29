import functools
from typing import Iterable, Callable
from typing import Any, Iterable, Union


def decode_args_to_string(func):
    """Decorator that decodes bytes arguments to strings before calling the decorated function."""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        args = [arg.decode() if isinstance(arg, bytes) else arg for arg in args]
        kwargs = {key: value.decode() if isinstance(value, bytes) else value for key, value in kwargs.items()}
        return await func(*args, **kwargs)
    return wrapper


def decode_output_to_string(func: Callable) -> Callable:
    """Decorator that decodes the output of a function from bytes to string if needed."""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs) -> Union[str, Iterable[str]]:
        result = await func(*args, **kwargs)

        if isinstance(result, bytes):
            return result.decode()
        elif isinstance(result, str):
            return result
        elif isinstance(result, Iterable):
            return [item.decode() if isinstance(item, bytes) else item for item in result]

        return await result

    return wrapper
