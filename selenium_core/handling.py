from functools import wraps
from typing import Callable, TypeVar, ParamSpec, Self, TYPE_CHECKING

if TYPE_CHECKING:
    from .driver import Driver


class _ExecutionContext:

    def __init__(self, driver: 'Driver', func: Callable) -> None:
        self.driver = driver
        self.func = func

    def __enter__(self) -> Self:
        self.driver.start_execution()
        return self
    
    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.driver.stop_execution()
        if exc_value is None:
            return
        
        self.driver.logger.error(f"Erro ao executar {self.func.__name__}: {exc_value}")

        if self.driver._save_screenshot_on_error:
            self.driver.save_screenshot(self.func.__name__)


P = ParamSpec('P')
T = TypeVar('T')

def on_error(func: Callable[..., T]) -> Callable[..., T]:

    @wraps(func)
    def wrapper(driver: 'Driver', *args: P.args, **kwargs: P.kwargs) -> T:

        if driver.is_executing():
            return func(driver, *args, **kwargs)

        with _ExecutionContext(driver, func):
            return func(driver, *args, **kwargs)

    return wrapper
