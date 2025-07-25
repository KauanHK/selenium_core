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

    @classmethod
    def is_executing(cls) -> bool:
        return cls._is_executing

    @classmethod
    def start_execution(cls) -> None:
        cls._is_executing = True

    @classmethod
    def stop_execution(cls) -> None:
        cls._is_executing = False

    def __enter__(self) -> Self:
        self.start_execution()
        return self
    
    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.stop_execution()
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
        if _ExecutionContext.is_executing():
            return func(*args, **kwargs)

        with _ExecutionContext(driver, func):
            return func(*args, **kwargs)
        
    return wrapper
