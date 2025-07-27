from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.types import WaitExcTypes
from typing import Callable


class Wait:

    def __init__(
        self,
        driver: WebDriver,
        default_timeout: float,
        default_poll_frequency: float | None = None,
        default_ignored_exceptions: WaitExcTypes | None = None
    ) -> None:
        
        self._driver = driver
        self._default_timeout = default_timeout
        self._default_poll_frequency = default_poll_frequency
        self._default_ignored_exceptions = default_ignored_exceptions

    def __getattr__(self, name: str) -> Callable:
        
        condition = getattr(EC, name, None)
        if condition is None:
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

        def wait_wrapper(*args, **kwargs) -> any:

            timeout = kwargs.pop('timeout', self._default_timeout)
            poll_frequency = kwargs.pop('poll_frequency', self._default_poll_frequency)
            ignored_exceptions = kwargs.pop('ignored_exceptions', self._default_ignored_exceptions)

            ec_predicate = condition(*args, **kwargs)
            return WebDriverWait(self._driver, timeout, poll_frequency, ignored_exceptions).until(ec_predicate)

        return wait_wrapper
