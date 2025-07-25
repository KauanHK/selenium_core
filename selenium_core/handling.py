from .config import Config
from .log import get_logger
from functools import wraps
from typing import Callable, TypeVar, ParamSpec, Self


logger = get_logger()

class _ExecutionContext:

    _is_executing: bool = False

    def __init__(self, driver, func: Callable) -> None:
        self.driver = driver
        self.func = func

    def is_executing(self) -> bool:
        return self.driver.is_executing()

    def __enter__(self) -> Self:
        self.driver.start_execution()
        return self
    
    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.driver.stop_execution()
        if exc_value is None:
            return
        
        if Config.LOG_FILE_PATH is not None and Config.LOG_FILE_PATH is not None:
            logger.error(f"Erro ao executar {self.func.__name__}: {exc_value}")

        if self.driver._save_screenshot_on_error:
            self.driver.save_screenshot(self.func.__name__)


P = ParamSpec('P')
T = TypeVar('T')

def on_error(func: Callable[P, T]) -> Callable[P, T]:

    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:

        driver = args[0]
        if driver.is_executing():
            return func(*args, **kwargs)

        with _ExecutionContext(driver, func):
            return func(*args, **kwargs)
        
    return wrapper
