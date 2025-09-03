from contextlib import contextmanager
from time import sleep
from typing import Callable, Hashable, Generator
from .types import P, T


_execution_controller: dict[Hashable, bool] = {}

class _ControllerWrapper:

    def __init__(
        self,
        controller: 'Controller',
        func: Callable[P, T],
        exception_handler: Callable[[object, Exception], None] | None = None,
        retries: int | None = None,
        retry_delay: float = None,
    ) -> None:
        
        self._controller = controller
        self._func = func
        self._retries = retries
        self._retry_delay = retry_delay
        self._instance = None
        self._exception_handler = exception_handler if exception_handler is not None else controller.exception_handler
    
    def handle_error(self, exception: Exception) -> None:

        if not self._exception_handler:
            raise exception
        
        args = (self._instance, exception) if self._instance is not None else (exception,)
        self._exception_handler(*args)
        raise exception
        

    @contextmanager
    def _execution_context(self, instance) -> Generator[None, None, None]:

        _execution_controller[instance] = True
        try:
            yield
        except Exception as e:
            return self.handle_error(e)
        finally:
            _execution_controller[instance] = False
            self._instance = None
    
    def _execute(self, *args: P.args, **kwargs: P.kwargs) -> T:

        retries = self._retries if self._retries is not None else self._controller.retries
        retry_delay = self._retry_delay if self._retry_delay is not None else self._controller.retry_delay
        
        for i in range(retries+1):
            try:
                return self._func(*args, **kwargs)
            except Exception as e:
                if i >= retries:
                    raise e
                sleep(retry_delay)

    def __get__(self, instance: Hashable, owner: type) -> Callable:
        self._instance = instance
        return self

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> T:

        if self._instance is not None:
            args = (self._instance, *args)
            if _execution_controller.get(self._instance, False):
                return self._func(*args, **kwargs)

        with self._execution_context(self._instance):
            return self._execute(*args, **kwargs)


class Controller:

    def __init__(
        self,
        exception_handler: Callable[[object, Exception], None] | None = None,
        retries: int = 0,
        retry_delay: float = 0.0,
    ) -> None:
        
        self.exception_handler = exception_handler
        self.retries = retries
        self.retry_delay = retry_delay

    def on_error(
        self,
        func: Callable[P, T] | None = None,
        exception_handler: Callable[[object, Exception], None] | None = None,
        retries: int | None = None,
        retry_delay: float | None = None
    ) -> Callable[P, T]:

        def decorator(func: Callable[P, T]):
            return _ControllerWrapper(
                controller=self,
                func=func,
                exception_handler=exception_handler,
                retries=retries,
                retry_delay=retry_delay
            )

        if func is None:
            return decorator
        return decorator(func)
