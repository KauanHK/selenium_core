from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.types import WaitExcTypes
from typing import Callable, TypeVar, Self


T = TypeVar('T')

class Wait:

    def __init__(
        self,
        driver: WebDriver,
        default_timeout: float = 30,
        default_poll_frequency: float = 0.5,
        default_ignored_exceptions: WaitExcTypes | None = None
    ) -> None:
        
        self._driver = driver
        self._default_timeout = default_timeout
        self._default_poll_frequency = default_poll_frequency
        self._default_ignored_exceptions = default_ignored_exceptions
        self._negated = False
    
    @property
    def Not(self) -> Self:
        self._negated = True
        return self
    
    def until(
        self,
        condition: Callable[..., T],
        timeout: float | None = None,
        poll_frequency: float | None = None,
        ignored_exceptions: WaitExcTypes | None = None
    ) -> T:
        """Aguarda até que a condição especificada seja atendida."""
        
        timeout, poll_frequency, ignored_exceptions = self._get_wait_params(
            timeout, poll_frequency, ignored_exceptions
        )
        
        wait = WebDriverWait(self._driver, timeout, poll_frequency, ignored_exceptions)
        if self._negated:
            self._negated = False
            return wait.until_not(condition)
        return wait.until(condition)

    def _get_timeout(self, timeout: float | None) -> float:
        """Retorna o tempo limite padrão se nenhum for especificado."""
        return timeout if timeout is not None else self._default_timeout
    
    def _get_poll_frequency(self, poll_frequency: float | None) -> float | None:
        """Retorna a frequência de verificação padrão se nenhuma for especificada."""
        return poll_frequency if poll_frequency is not None else self._default_poll_frequency
    
    def _get_ignored_exceptions(self, ignored_exceptions: WaitExcTypes | None) -> WaitExcTypes | None:
        """Retorna as exceções ignoradas padrão se nenhuma for especificada."""
        return ignored_exceptions if ignored_exceptions is not None else self._default_ignored_exceptions

    def _get_wait_params(
        self,
        timeout: float | None,
        poll_frequency: float | None,
        ignored_exceptions: WaitExcTypes | None
    ) -> tuple[float, float | None, WaitExcTypes | None]:
        """Obtém os parâmetros de espera com valores padrão se não forem especificados."""
        
        timeout = self._get_timeout(timeout)
        poll_frequency = self._get_poll_frequency(poll_frequency)
        ignored_exceptions = self._get_ignored_exceptions(ignored_exceptions)
        return timeout, poll_frequency, ignored_exceptions

    def __getattr__(self, name: str) -> Callable:
        
        condition = getattr(EC, name, None)
        if condition is None:
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

        def wait_wrapper(*args, **kwargs) -> any:
            
            # O nome do primeiro parâmetro varia de acordo com a condição ('locator', 'mark', 'element')
            # Por isso, passamos como primeiro argumento
            if 'locator' in kwargs:
                locator = kwargs.pop('locator')
            else:
                locator, *args = args[:]
            
            timeout = kwargs.pop('timeout', None)
            poll_frequency = kwargs.pop('poll_frequency', None)
            ignored_exceptions = kwargs.pop('ignored_exceptions', None)

            predicate = condition(locator, *args, **kwargs)
            return self.until(predicate, timeout, poll_frequency, ignored_exceptions)

        return wait_wrapper
