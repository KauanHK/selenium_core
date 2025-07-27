from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.types import WaitExcTypes
from typing import Literal


class Wait:

    def __init__(
        self,
        driver: WebDriver,
        default_timeout: float,
        default_poll_frequency: float | None = None,
        default_ignored_exceptions: WaitExcTypes | None = None
    ) -> None: ...

    def presence_of_element_located(
        self,
        locator: tuple[str, str],
        *,
        timeout: float | None = None,
        poll_frequency: float | None = None,
        ignored_exceptions: WaitExcTypes | None = None
    ) -> WebElement: ...

    def presence_of_all_elements_located(
        self,
        locator: tuple[str, str],
        *,
        timeout: float | None = None,
        poll_frequency: float | None = None,
        ignored_exceptions: WaitExcTypes | None = None
    ) -> list[WebElement]: ...

    def visibility_of_element_located(
        self,
        locator: tuple[str, str],
        *,
        timeout: float | None = None,
        poll_frequency: float | None = None,
        ignored_exceptions: WaitExcTypes | None = None
    ) -> WebElement: ...

    def visibility_of(
        self,
        element: WebElement,
        *,
        timeout: float | None = None,
        poll_frequency: float | None = None,
        ignored_exceptions: WaitExcTypes | None = None
    ) -> WebElement: ...

    def visibility_of_any_elements_located(
        self,
        locator: tuple[str, str],
        *,
        timeout: float | None = None,
        poll_frequency: float | None = None,
        ignored_exceptions: WaitExcTypes | None = None
    ) -> list[WebElement]: ...

    def visibility_of_all_elements_located(
        self,
        locator: tuple[str, str],
        *,
        timeout: float | None = None,
        poll_frequency: float | None = None,
        ignored_exceptions: WaitExcTypes | None = None
    ) -> list[WebElement]: ...

    def invisibility_of_element_located(
        self,
        locator: tuple[str, str],
        *,
        timeout: float | None = None,
        poll_frequency: float | None = None,
        ignored_exceptions: WaitExcTypes | None = None
    ) -> bool: ...
        
    def invisibility_of_element(
        self,
        element: WebElement,
        *,
        timeout: float | None = None,
        poll_frequency: float | None = None,
        ignored_exceptions: WaitExcTypes | None = None
    ) -> bool: ...

    def element_to_be_clickable(
        self,
        locator: WebElement | tuple[str, str],
        *,
        timeout: float | None = None,
        poll_frequency: float | None = None,
        ignored_exceptions: WaitExcTypes | None = None
    ) -> WebElement: ...

    def element_to_be_selected(
        self,
        locator: WebElement | tuple[str, str],
        *,
        timeout: float | None = None,
        poll_frequency: float | None = None,
        ignored_exceptions: WaitExcTypes | None = None
    ) -> bool: ...

    def element_located_to_be_selected(
        self,
        locator: tuple[str, str],
        *,
        timeout: float | None = None,
        poll_frequency: float | None = None,
        ignored_exceptions: WaitExcTypes | None = None
    ) -> bool: ...

    def element_selection_state_to_be(
        self,
        locator: WebElement | tuple[str, str],
        is_selected: bool,
        *,
        timeout: float | None = None,
        poll_frequency: float | None = None,
        ignored_exceptions: WaitExcTypes | None = None
    ) -> bool: ...

    def element_located_selection_state_to_be(
        self,
        locator: tuple[str, str],
        is_selected: bool,
        *,
        timeout: float | None = None,
        poll_frequency: float | None = None,
        ignored_exceptions: WaitExcTypes | None = None
    ) -> bool: ...

    def text_to_be_present_in_element(
        self,
        locator: tuple[str, str], text_: str,
        *,
        timeout: float | None = None,
        poll_frequency: float | None = None,
        ignored_exceptions: WaitExcTypes | None = None
    ) -> bool: ...

    def text_to_be_present_in_element_value(
        self,
        locator: tuple[str, str], text_: str,
        *,
        timeout: float | None = None,
        poll_frequency: float | None = None,
        ignored_exceptions: WaitExcTypes | None = None
    ) -> bool: ...
    
    def text_to_be_present_in_element_attribute(
        self,
        locator: tuple[str, str],
        attribute_: str,
        text_: str,
        *,
        timeout: float | None = None,
        poll_frequency: float | None = None,
        ignored_exceptions: WaitExcTypes | None = None
    ) -> bool: ...

    def attribute_to_be(
        self,
        locator: tuple[str, str],
        attribute_: str,
        value_: str,
        *,
        timeout: float | None = None,
        poll_frequency: float | None = None,
        ignored_exceptions: WaitExcTypes | None = None
    ) -> bool: ...

    def attribute_contains(
        self,
        locator: tuple[str, str],
        attribute_: str,
        value_: str,
        *,
        timeout: float | None = None,
        poll_frequency: float | None = None,
        ignored_exceptions: WaitExcTypes | None = None
    ) -> bool: ...

    def title_is(
        self,
        title: str,
        *,
        timeout: float | None = None,
        poll_frequency: float | None = None,
        ignored_exceptions: WaitExcTypes | None = None
    ) -> bool: ...

    def title_contains(
        self,
        title: str,
        *,
        timeout: float | None = None,
        poll_frequency: float | None = None,
        ignored_exceptions: WaitExcTypes | None = None
    ) -> bool: ...

    def url_to_be(
        self,
        url: str,
        *,
        timeout: float | None = None,
        poll_frequency: float | None = None,
        ignored_exceptions: WaitExcTypes | None = None
    ) -> bool: ...

    def url_contains(
        self,
        url: str,
        *,
        timeout: float | None = None,
        poll_frequency: float | None = None,
        ignored_exceptions: WaitExcTypes | None = None
    ) -> bool: ...

    def url_matches(
        self,
        pattern: str,
        *,
        timeout: float | None = None,
        poll_frequency: float | None = None,
        ignored_exceptions: WaitExcTypes | None = None
    ) -> bool: ...

    def url_changes(
        self,
        url: str,
        *,
        timeout: float | None = None,
        poll_frequency: float | None = None,
        ignored_exceptions: WaitExcTypes | None = None
    ) -> bool: ...

    def alert_is_present(
        self,
        *,
        timeout: float | None = None,
        poll_frequency: float | None = None,
        ignored_exceptions: WaitExcTypes | None = None
    ) -> Literal[True]: ...

    def frame_to_be_available_and_switch_to_it(
        self,
        locator: tuple[str, str] | str,
        *,
        timeout: float | None = None,
        poll_frequency: float | None = None,
        ignored_exceptions: WaitExcTypes | None = None
    ) -> bool: ...

    def number_of_windows_to_be(
        self,
        num_windows: int,
        *,
        timeout: float | None = None,
        poll_frequency: float | None = None,
        ignored_exceptions: WaitExcTypes | None = None
    ) -> bool: ...

    def new_window_is_opened(
        self,
        current_handles: list[str],
        *,
        timeout: float | None = None,
        poll_frequency: float | None = None,
        ignored_exceptions: WaitExcTypes | None = None
    ) -> bool: ...

    def staleness_of(
        self,
        element: WebElement,
        *,
        timeout: float | None = None,
        poll_frequency: float | None = None,
        ignored_exceptions: WaitExcTypes | None = None
    ) -> bool: ...
