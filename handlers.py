from selenium.webdriver.chrome.webdriver import WebDriver
from exceptions import StopErrorHandling
from functools import wraps
import logging
import time
from typing import Callable, Literal, Any, Self


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def error_handling(
    func: Callable | None = None,
    on_error: str | Literal['raise', 'ignore'] = 'raise',
    screenshot: bool = True,
    log_level: int | None = logging.INFO,
    max_attempts: int = 1,
    retry_delay: float = 1.0
) -> Callable:
    """
    Decorador configurável para manipulação de erros em métodos do Driver.

    Args:
        on_error (str): Ação a tomar em caso de erro.
            'raise': Relança a exceção (padrão).
            'ignore': Suprime a exceção e retorna 'default_return'.
            'retry': Tenta executar o método novamente.
        screenshot (bool): Se True, salva um screenshot em caso de erro.
        log_level (int): Nível do logging (ex: logging.INFO, logging.WARNING, logging.ERROR).
        retries (int): Número de tentativas extras após a primeira falha.
        retry_delay (float): Tempo em segundos para esperar entre as tentativas.
        default_return (Any): Valor a ser retornado se on_error='ignore'.
    """
    def decorator(func: Callable) -> Callable:

        @wraps(func)
        def wrapper(driver, *args, **kwargs) -> Any:

            for _ in range(max_attempts):
                try:
                    return func(driver, *args, **kwargs)
                except Exception as e:

                    error_context = driver.error_context(
                        func=func,
                        on_error = on_error,
                        screenshot = screenshot,
                        log_level = log_level,
                        max_attempts = max_attempts,
                        retry_delay = retry_delay
                    )
                    with error_context as error_handler:
                        error_handler.handle_error(e)
                    error_handler.execution_number += 1
            
            driver.raise_last_exception()
            
        return wrapper
    
    if func is None:
        return decorator
    return decorator(func)


class ErrorHandling:

    def __init__(
        self,
        driver,
        func: Callable,
        on_error: str | Literal['raise', 'ignore'] = 'raise',
        screenshot: bool = True,
        log_level: int | None = logging.INFO,
        max_attempts: int = 1,
        retry_delay: float = 1.0
    ) -> None:
        
        self.driver = driver
        self.func = func
        self.on_error = on_error
        self.screenshot = screenshot
        self.log_level = log_level
        self.max_attempts = max_attempts
        self.retry_delay = retry_delay

        self.exceptions: list[Exception] = []
        self.execution_number = 1
    
    def handle_error(self, exception: Exception) -> None:
        
        self.exceptions.append(exception)

        if self.log_level:
            logging.log(self.log_level, f"Tentativa {self.execution_number}/{self.max_attempts} falhou")

        if self.screenshot:
            self.driver.save_screenshot()
        
        if self.execution_number >= self.max_attempts:
            if self.on_error == 'ignore':
                logging.warning(f"Erro ignorado após {self.max_attempts+1} tentativas")
                raise StopErrorHandling
            raise exception
        
        time.sleep(self.retry_delay)
    
    def raise_last_exception(self) -> None:
        if not self.exceptions:
            raise RuntimeError("Nenhum erro registrado para relançar")
        raise self.exceptions[-1]


class ErrorsHandling:

    def __init__(self) -> None:
        self._stack: list[ErrorHandling] = []
    
    def is_in_error_handling(self) -> bool:
        return len(self._stack) > 0
    
    def error_handling(
        self,
        func: Callable | None = None,
        on_error: str | Literal['raise', 'ignore'] = 'raise',
        screenshot: bool = True,
        log_level: int | None = logging.INFO,
        retries: int = 0,
        retry_delay: float = 1.0
    ) -> Callable:
        
        return error_handling(
            func=func,
            on_error=on_error,
            screenshot=screenshot,
            log_level=log_level,
            max_attempts=retries,
            retry_delay=retry_delay
        )
    
    def raise_last_exception(self) -> None:
        if not self._stack:
            raise RuntimeError("Nenhum erro para lançar exceção")
        self._stack[-1].raise_last_exception()
    
    def context(
        self,
        driver,
        on_error: str,
        screenshot: bool,
        log_level: int | None,
        max_attempts: int,
        retry_delay: float,
        func: Callable
    ) -> Self:
        
        if not self._stack or self._stack[-1].func != func:
            self._stack.append(
                ErrorHandling(
                    driver=driver,
                    func=func,
                    on_error=on_error,
                    screenshot=screenshot,
                    log_level=log_level,
                    max_attempts=max_attempts,
                    retry_delay=retry_delay
                )
            )
        return self
        
    def __enter__(self) -> ErrorHandling:
        if not self._stack:
            raise RuntimeError("Nenhum erro para tratar")
        return self._stack[-1]
    
    def __exit__(self, exc_type, exc_value, traceback) -> None:

        if isinstance(exc_value, StopErrorHandling):
            return
        
        if exc_value is not None:
            self._stack.pop()
            raise exc_value
        