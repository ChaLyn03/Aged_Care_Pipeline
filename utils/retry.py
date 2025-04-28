# utils/retry.py

import time
import functools

def retry(times: int, delay: float):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            for i in range(times):
                try:
                    return fn(*args, **kwargs)
                except Exception:
                    if i < times - 1:
                        time.sleep(delay)
                    else:
                        raise
        return wrapper
    return decorator
