import logging
import sys
from functools import wraps
import time
import inspect

if sys.argv[0].endswith('client.py'):
    logger = logging.getLogger('client')
else:
    logger = logging.getLogger('server')


def log(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        time_1 = time.time()
        result = func(*args, **kwargs)
        time_2 = time.time()
        elapsed_time = round(time_2-time_1, 10)
        logger.debug(f'Function {func.__name__} was executed in {elapsed_time} s.')
        calling_func_name = inspect.stack()[1].function
        logger.debug(f'Function {func.__name__} was invoked from {calling_func_name}')
        return result
    return decorator
