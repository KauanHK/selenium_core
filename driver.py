from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from datetime import datetime
from typing import Callable, Self, Literal, Any, TypeIs


class Driver:

    def __init__(
        self,
        options: Options | None = None,
        service: Service | None = None,
        keep_alive: bool = True
    ) -> None:
        
        self.options = options
        self.service = service
        self.keep_alive = keep_alive

        self._driver = None
    
    @property
    def driver(self) -> WebDriver:
        if self._driver is None:
            self._driver = self._start_driver()
        return self._driver
    
    def init(self) -> None:

        if self._driver is not None:
            self._driver.close()
        self._driver = self._start_driver()
    
    def close(self) -> None:
        if self._driver is not None:
            self._driver.close()
    
    def get(self, url: str) -> None:
        self.driver.get(url)

    def wait(
        self,
        locator: WebElement | tuple[str, str],
        expected_condition: Callable = EC.presence_of_element_located,
        timeout: float = 10,
        timeout_handler: Callable | None = None
    ) -> WebElement:
        
        self._check_locator(locator)
        if expected_condition is not None and not callable(expected_condition):
            raise TypeError(f"O parâmetro 'expected_condition' deve ser do tipo 'Callable', não {type(expected_condition).__name__}")

        try:
            return WebDriverWait(self.driver, timeout).until(expected_condition(locator))
        except TimeoutException:
            if timeout_handler is not None:
                return timeout_handler()
            raise
    
    def wait_not(self,
        locator: WebElement | tuple[str, str],
        expected_condition: Callable = EC.presence_of_element_located,
        timeout: float = 10,
        timeout_handler: Callable | None = None
    ) -> WebElement | Literal[True]:
    
        if expected_condition is not None and not callable(expected_condition):
            raise TypeError(f"O parâmetro 'expected_condition' deve ser do tipo 'Callable', não {type(expected_condition).__name__}")
        
        try:
            return WebDriverWait(self.driver, timeout).until_not(expected_condition(locator))
        except TimeoutException:
            if timeout_handler is not None:
                return timeout_handler()
            raise
    
    def find_element(
        self,
        by: str,
        value: str,
        expected_condition: Callable | None = EC.presence_of_element_located,
        timeout: float = 10,
        exceptions_handlers: dict[type[Exception], Callable] | None = None
    ) -> WebElement:
        
        if exceptions_handlers is not None and not isinstance(exceptions_handlers, dict):
            raise TypeError(f"O parâmetro 'exceptions_handlers' deve ser do tipo 'dict', não {type(exceptions_handlers).__name__}")
        
        try:
            if expected_condition is not None:
                return self.wait((by, value), expected_condition, timeout)
            return self.driver.find_element(by, value)
        except Exception as e:
            if exceptions_handlers is None or type(e) not in exceptions_handlers:
                raise
            handler = exceptions_handlers[type(e)]
            return handler(e)
    
    def find_elements(
        self,
        by: str,
        value: str,
        expected_condition: Callable | None = EC.presence_of_all_elements_located,
        timeout: float = 10,
        exceptions_handlers: dict[type[Exception], Callable] | None = None
    ) -> list[WebElement]:
        
        if exceptions_handlers is not None and not isinstance(exceptions_handlers, dict):
            raise TypeError(f"O parâmetro 'exceptions_handlers' deve ser do tipo 'dict', não {type(exceptions_handlers).__name__}")
        
        try:
            if expected_condition is not None:
                self.wait((by, value), expected_condition, timeout)
            return self.driver.find_elements(by, value)
        except Exception as e:
            if exceptions_handlers is None or type(e) not in exceptions_handlers:
                raise
            handler = exceptions_handlers[type(e)]
            return handler(e)
    
    def click(
        self,
        locator: WebElement | tuple[str, str],
        exceptions_handlers: dict[type[Exception], Callable] | None = None
    ) -> None:

        self._check_locator(locator)
        try:
            self.wait(locator, EC.element_to_be_clickable).click()
        except Exception as e:
            if exceptions_handlers is not None and type(e) in exceptions_handlers:
                handler = exceptions_handlers[type(e)]
                return handler(e)
            raise
    
    def hover(self, locator: WebElement | tuple[str, str]) -> None:
        """Move o mouse para cima do elemento especificado."""
        self._check_locator(locator)
        if isinstance(locator, tuple):
            element = self.find_element(*locator)
        else:
            element = locator
        
        actions = ActionChains(self.driver)
        actions.move_to_element(element)
        actions.perform()
    
    def send_keys(
        self,
        locator: WebElement | tuple[str, str],
        keys: str,
        clear: bool = True
    ) -> None:
        
        self._check_locator(locator)
        if self._is_web_element(locator):
            element = locator
        else:
            element = self.find_element(*locator)
        
        if clear:
            element.clear()
        element.send_keys(keys)

    def execute_script(self, script: str, *args) -> Any:
        """Executa um script JavaScript e retorna o resultado."""
        return self.driver.execute_script(script, *args)
    
    def switch_to_window(self, window_index: int = -1) -> None:
        """Muda o foco para uma janela/aba diferente."""
        all_windows = self.driver.window_handles
        if len(all_windows) > abs(window_index):
            self.driver.switch_to.window(all_windows[window_index])
    
    def get_text(self, locator: WebElement | tuple[str, str]) -> str:
        """Retorna o texto de um elemento."""
        if self._is_web_element(locator):
            element = locator
        else:
            element = self.find_element(*locator)
        return element.text
    
    def is_visible(self, locator: tuple[str, str], timeout: float = 5) -> bool:
        """Verifica se um elemento está visível na página."""
        try:
            self.wait(locator, EC.visibility_of_element_located, timeout)
            return True
        except TimeoutException:
            return False

    def is_enabled(self, locator: WebElement | tuple[str, str]) -> bool:
        """Verifica se um elemento está habilitado."""
        if self._is_web_element(locator):
            element = locator
        else:
            element = self.find_element(*locator)
        return element.is_enabled()
    
    def get_title(self) -> str:
        """Retorna o título da página atual."""
        return self.driver.title

    def get_current_url(self) -> str:
        """Retorna a URL da página atual."""
        return self.driver.current_url
    
    def scroll_to_element(self, locator: WebElement | tuple[str, str]) -> None:
        """Rola a página até que o elemento esteja visível."""
        if self._is_web_element(locator):
            element = locator
        else:
            element = self.find_element(*locator)
        self.execute_script("arguments[0].scrollIntoView(true);", element)

    def scroll_to_bottom(self) -> None:
        """Rola a página até o final."""
        self.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    def scroll_to_top(self) -> None:
        """Rola a página até o topo."""
        self.execute_script("window.scrollTo(0, 0);")
    
    def select_by_value(self, locator: tuple[str, str], value: str) -> None:
        """Seleciona uma opção em um dropdown pelo seu atributo 'value'."""
        element = self.find_element(*locator)
        select = Select(element)
        select.select_by_value(value)

    def select_by_visible_text(self, locator: tuple[str, str], text: str) -> None:
        """Seleciona uma opção em um dropdown pelo texto visível."""
        element = self.find_element(*locator)
        select = Select(element)
        select.select_by_visible_text(text)
    
    def _start_driver(self) -> WebDriver:
        return WebDriver(self.options, self.service, self.keep_alive)
    
    def _check_locator(self, locator: WebElement | tuple[str, str]) -> bool:

        if self._is_web_element(locator):
            return True
        
        if self._is_by_tuple(locator):
            return True
        
        raise TypeError(f"O parâmetro 'locator' deve ser do tipo 'WebElement' ou 'tuple', não {type(locator).__name__}")
    
    def _is_web_element(self, element: Any) -> TypeIs[WebElement]:
        return isinstance(element, WebElement)
    
    def _is_by_tuple(self, element: Any) -> TypeIs[tuple[str, str]]:
        return isinstance(element, tuple) and len(element) == 2 and isinstance(element[0], str) and isinstance(element[1], str)
    
    def __enter__(self) -> Self:
        self.init()
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):

        if exc_type is not None:
            screenshot_path = f"error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            print(f"Ocorreu um erro. Salvando screenshot em: {screenshot_path}")
            self.driver.save_screenshot(screenshot_path)
        
        self.close()
