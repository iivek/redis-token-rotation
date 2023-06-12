from functools import wraps


def handle_exception(error):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                raise error from e

        return wrapper

    return decorator