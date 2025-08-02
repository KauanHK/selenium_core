from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver import Chrome
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.types import WaitExcTypes
import logging
from typing import Callable, Self, Any
from .wait import Wait
from .log import LogManager
from .types import P, T


class Driver:

    def __init__(
        self,
        options: Options | None = None,
        service: Service | None = None,
        keep_alive: bool = True,
        driver_cls: type[WebDriver] = Chrome,
        save_screenshot_on_error: bool = True,
        default_timeout: float = 30,
        default_poll_frequency: float = 0.5,
        default_ignored_exceptions: WaitExcTypes | None = None,
        logger: logging.Logger | None = None,
        log_level: int | None = None,
        log_file_path: str | None = None,
        log_indent: int | None = None
    ) -> None: ...

    @property
    def driver(self) -> WebDriver: ...

    @property
    def wait(self) -> Wait: ...

    def is_initialized(self) -> bool: ...

    def init(self) -> None: ...

    def quit(self) -> None: ...

    def get(self, url: str) -> None: ...

    def find_element(
        self,
        by: str,
        value: str,
        timeout: float | None = None,
        poll_frequency: float | None = None,
        ignored_exceptions: WaitExcTypes | None = None
    ) -> WebElement: ...

    def find_elements(
        self,
        by: str,
        value: str,
        timeout: float | None = None,
        poll_frequency: float | None = None,
        ignored_exceptions: WaitExcTypes | None = None
    ) -> list[WebElement]: ...

    def click(
        self,
        locator: WebElement | tuple[str, str],
        timeout: float | None = None,
        poll_frequency: float | None = None,
        ignored_exceptions: WaitExcTypes | None = None
    ) -> None: ...

    def hover(
        self,
        locator: WebElement | tuple[str, str],
        timeout: float | None = None,
        poll_frequency: float | None = None,
        ignored_exceptions: WaitExcTypes | None = None
    ) -> None: ...

    def send_keys(
        self,
        locator: WebElement | tuple[str, str],
        keys: str,
        clear: bool = True,
        timeout: float | None = None,
        poll_frequency: float | None = None,
        ignored_exceptions: WaitExcTypes | None = None
    ) -> None: ...

    def execute_script(self, script: str, *args) -> Any: ...

    def switch_to_window(self, window_index: int = -1) -> None: ...

    def get_text(
        self,
        locator: WebElement | tuple[str, str],
        timeout: float | None = None,
        poll_frequency: float | None = None,
        ignored_exceptions: WaitExcTypes | None = None
    ) -> str: ...

    def is_displayed(
        self,
        locator: WebElement | tuple[str, str],
        timeout: float | None = None,
        poll_frequency: float | None = None,
        ignored_exceptions: WaitExcTypes | None = None
    ) -> bool: ...

    def is_enabled(
        self,
        locator: WebElement | tuple[str, str],
        timeout: float | None = None,
        poll_frequency: float | None = None,
        ignored_exceptions: WaitExcTypes | None = None
    ) -> bool: ...

    def get_title(self) -> str: ...

    def get_current_url(self) -> str: ...

    def scroll_to_element(
        self,
        locator: WebElement | tuple[str, str],
        timeout: float | None = None,
        poll_frequency: float | None = None,
        ignored_exceptions: WaitExcTypes | None = None
    ) -> None: ...

    def scroll_to_bottom(self) -> None: ...

    def scroll_to_top(self) -> None: ...

    def select_by_value(
        self,
        locator: WebElement | tuple[str, str],
        value: str,
        timeout: float | None = None,
        poll_frequency: float | None = None,
        ignored_exceptions: WaitExcTypes | None = None
    ) -> None: ...

    def select_by_visible_text(
        self,
        locator: WebElement | tuple[str, str],
        text: str,
        timeout: float | None = None,
        poll_frequency: float | None = None,
        ignored_exceptions: WaitExcTypes | None = None
    ) -> None: ...

    def get_attribute(
        self,
        locator: WebElement | tuple[str, str],
        attribute: str,
        timeout: float | None = None,
        poll_frequency: float | None = None,
        ignored_exceptions: WaitExcTypes | None = None
    ) -> str | None: ...

    def wait_for_element_visible(
        self,
        locator: tuple[str, str],
        timeout: float | None = None,
        poll_frequency: float | None = None,
        ignored_exceptions: WaitExcTypes | None = None
    ) -> WebElement: ...

    def wait_for_element_invisible(
        self,
        locator: tuple[str, str],
        timeout: float | None = None,
        poll_frequency: float | None = None,
        ignored_exceptions: WaitExcTypes | None = None
    ) -> bool: ...

    def double_click(
        self,
        locator: WebElement | tuple[str, str],
        timeout: float | None = None,
        poll_frequency: float | None = None,
        ignored_exceptions: WaitExcTypes | None = None
    ) -> None: ...

    def right_click(
        self,
        locator: WebElement | tuple[str, str],
        timeout: float | None = None,
        poll_frequency: float | None = None,
        ignored_exceptions: WaitExcTypes | None = None
    ) -> None: ...

    def refresh(self) -> None: ...

    def back(self) -> None: ...

    def forward(self) -> None: ...

    def save_screenshot(self, exception: Exception | None = None) -> None: ...

    def step(
        self,
        description: str,
        log_level: int = logging.INFO,
        exception_handler: Callable | None = None,
        retries: int = 0,
        retry_delay: float = 0.0
    ) -> Callable[[Callable[P, T]], Callable[P, T]]: ...

    def __enter__(self) -> Self: ...

    def __exit__(self, exc_type, exc_value, traceback) -> None: ...
