from contextlib import contextmanager
from typing import Callable, TypeVar, ParamSpec, Hashable, Generator, TYPE_CHECKING


if TYPE_CHECKING:
    from .driver import Driver

_execution_controller: dict[Hashable, bool] = {}

P = ParamSpec('P')
T = TypeVar('T')

class _ControllerWrapper:

    def __init__(
        self,
        controller: 'Controller',
        func: Callable[P, T]
    ) -> None:
        
        self._func = func
        self._instance = None
        self._controller = controller
    
    def handle_error(self, exception: Exception) -> None:

        self._controller.exception_handler(self._instance, exception)

        handler = self._controller.exceptions_handler.get(type(exception))
        if handler is not None:
            handler(exception)
        else:
            raise exception

    @contextmanager
    def _execution_context(self, instance) -> Generator[None, None, None]:
        _execution_controller[instance] = True
        try:
            yield
        except Exception as e:
            self.handle_error(e)
            raise
        finally:
            _execution_controller[instance] = False

    def __get__(self, instance: Hashable, owner: type) -> Callable:
        self._instance = instance
        return self

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> T:

        if _execution_controller.get(self._instance, False):
            return self._func(self._instance, *args, **kwargs)

        with self._execution_context(self._instance):
            self._func(self._instance, *args, **kwargs)


class Controller:

    def __init__(
        self,
        save_screenshot_on_error: bool = True,
        exceptions_handler: dict[type[Exception], Callable] | None = None,
        exception_handler: Callable[[object, Exception], None] | None = None
    ) -> None:
        
        self.save_screenshot_on_error = save_screenshot_on_error
        self.exceptions_handler = exceptions_handler if exceptions_handler is not None else {}
        self.exception_handler = exception_handler

    def on_error(self, func: Callable[P, T]) -> Callable[P, T]:
        return _ControllerWrapper(self, func)
