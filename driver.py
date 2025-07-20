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
import logging
import os
from functools import wraps
from typing import Callable, Self, Literal, Any, TypeIs, TypeVar, overload, ParamSpec


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

P = ParamSpec('P')
T = TypeVar('T')

@overload
def error_handling(
    *,
    on_error: dict[type[Exception], Callable] | None = None,
    screenshot: bool = True,
    log_level: int | None = logging.INFO
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    ...


@overload
def error_handling(func: Callable[P, T]) -> Callable[P, T]:
    ...


def error_handling(
    func: Callable[P, T] | None = None,
    *,
    on_error: dict[type[Exception], Callable] | None = None,
    screenshot: bool = True,
    log_level: int | None = logging.INFO
) -> Callable[[Callable[P, T]], Callable[P, T]] | Callable[P, T]:
    
    def decorator(f: Callable[P, T]) -> Callable[P, T]:

        @wraps(f)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:

            driver = args[0] if args else None
            if driver is None or not isinstance(driver, Driver):
                raise TypeError("O primeiro argumento deve ser uma instância de 'Driver'.")

            if driver.is_executing():
                return f(*args, **kwargs)

            with driver.execution_context(
                func = f,
                on_error = on_error,
                screenshot = screenshot,
                log_level = log_level
            ):
                return f(*args, **kwargs)
            
        return wrapper
    
    if func is None:
        return decorator
    return decorator(func)


class ExecutionContext:

    def __init__(
        self,
        driver: 'Driver',
        func: Callable,
        on_error: dict[type[Exception], Callable] | None = None,
        screenshot: bool = True,
        log_level: int | None = logging.INFO
    ) -> None:
        
        self.driver = driver
        self.func = func
        self.on_error = on_error
        self.screenshot = screenshot
        self.log_level = log_level
    
    def __enter__(self) -> Self:
        self.driver.start_execution()
        return self
    
    def __exit__(self, exc_type, exc_value, traceback) -> bool:

        self.driver.stop_execution()

        if exc_value is None:
            return True
        
        if self.on_error is None:
            if self.screenshot:
                self.driver.save_screenshot()
            return False

        error_handler = self.on_error.get(exc_type)
        if error_handler is not None:
            with self.driver.execution_context(
                func = error_handler,
                on_error = None,
                screenshot = self.screenshot,
                log_level = self.log_level
            ):
                error_handler(self.driver, exc_value)
                return True
        
        return False


T_EC = TypeVar('T_EC')


class Driver:

    def __init__(
        self,
        options: Options | None = None,
        service: Service | None = None,
        keep_alive: bool = True,
        save_screenshot_on_error: bool = True
    ) -> None:
        
        self.options = options
        self.service = service
        self.keep_alive = keep_alive
        self.save_screenshot_on_error = save_screenshot_on_error

        self._driver = None
        self._is_executing = False
    
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
    
    @error_handling(screenshot=False)
    def get(self, url: str) -> None:
        self.driver.get(url)

    @error_handling
    def wait(
        self,
        locator: WebElement | tuple[str, str],
        expected_condition: Callable[..., Callable[..., T_EC]] = EC.presence_of_element_located,
        timeout: float = 10
    ) -> T_EC:
        
        self._check_locator(locator)
        if expected_condition is not None and not callable(expected_condition):
            raise TypeError(f"O parâmetro 'expected_condition' deve ser do tipo 'Callable', não {type(expected_condition).__name__}")

        return WebDriverWait(self.driver, timeout).until(expected_condition(locator))
    
    @error_handling
    def wait_not(self,
        locator: WebElement | tuple[str, str],
        expected_condition: Callable[..., Callable[..., T_EC]] = EC.presence_of_element_located,
        timeout: float = 10
    ) -> T_EC | Literal[True]:
    
        if expected_condition is not None and not callable(expected_condition):
            raise TypeError(f"O parâmetro 'expected_condition' deve ser do tipo 'Callable', não {type(expected_condition).__name__}")
        
        return WebDriverWait(self.driver, timeout).until_not(expected_condition(locator))
    
    @error_handling
    def find_element(
        self,
        by: str,
        value: str,
        expected_condition: Callable | None = EC.presence_of_element_located,
        timeout: float = 1
    ) -> WebElement:
        
        if expected_condition is not None:
            return self.wait((by, value), expected_condition, timeout)
        return self.driver.find_element(by, value)
    
    @error_handling
    def find_elements(
        self,
        by: str,
        value: str,
        expected_condition: Callable | None = EC.presence_of_all_elements_located,
        timeout: float = 10
    ) -> list[WebElement]:
        
        if expected_condition is not None:
            return self.wait((by, value), expected_condition, timeout)
        return self.driver.find_elements(by, value)
    
    @error_handling
    def click(
        self,
        locator: WebElement | tuple[str, str]
    ) -> None:

        self._check_locator(locator)
        self.wait(locator, EC.element_to_be_clickable).click()
    
    @error_handling
    def hover(self, locator: WebElement | tuple[str, str]) -> None:
        """Move o mouse para cima do elemento especificado."""
        self._check_locator(locator)
        element = self._get_element(locator)
        
        actions = ActionChains(self.driver)
        actions.move_to_element(element)
        actions.perform()
    
    @error_handling
    def send_keys(
        self,
        locator: WebElement | tuple[str, str],
        keys: str,
        clear: bool = True
    ) -> None:
        
        self._check_locator(locator)
        element = self._get_element(locator)
        
        if clear:
            element.clear()
        element.send_keys(keys)

    @error_handling
    def execute_script(self, script: str, *args) -> Any:
        """Executa um script JavaScript e retorna o resultado."""
        return self.driver.execute_script(script, *args)
    
    @error_handling(screenshot=False)
    def switch_to_window(self, window_index: int = -1) -> None:
        """Muda o foco para uma janela/aba diferente."""
        all_windows = self.driver.window_handles
        if len(all_windows) > abs(window_index):
            self.driver.switch_to.window(all_windows[window_index])
    
    @error_handling
    def get_text(self, locator: WebElement | tuple[str, str]) -> str:
        """Retorna o texto de um elemento."""
        if self._is_web_element(locator):
            element = locator
        else:
            element = self.find_element(*locator)
        return element.text
    
    @error_handling(screenshot=False)
    def is_visible(self, locator: tuple[str, str], timeout: float = 5) -> bool:
        """Verifica se um elemento está visível na página."""
        try:
            self.wait(locator, EC.visibility_of_element_located, timeout)
            return True
        except TimeoutException:
            return False

    @error_handling(screenshot=False)
    def is_enabled(self, locator: WebElement | tuple[str, str]) -> bool:
        """Verifica se um elemento está habilitado."""
        if self._is_web_element(locator):
            element = locator
        else:
            element = self.find_element(*locator)
        return element.is_enabled()
    
    @error_handling(screenshot=False)
    def get_title(self) -> str:
        """Retorna o título da página atual."""
        return self.driver.title

    @error_handling(screenshot=False)
    def get_current_url(self) -> str:
        """Retorna a URL da página atual."""
        return self.driver.current_url
    
    @error_handling
    def scroll_to_element(self, locator: WebElement | tuple[str, str]) -> None:
        """Rola a página até que o elemento esteja visível."""
        if self._is_web_element(locator):
            element = locator
        else:
            element = self.find_element(*locator)
        self.execute_script("arguments[0].scrollIntoView(true);", element)

    @error_handling
    def scroll_to_bottom(self) -> None:
        """Rola a página até o final."""
        self.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    @error_handling
    def scroll_to_top(self) -> None:
        """Rola a página até o topo."""
        self.execute_script("window.scrollTo(0, 0);")
    
    @error_handling
    def select_by_value(self, locator: tuple[str, str], value: str) -> None:
        """Seleciona uma opção em um dropdown pelo seu atributo 'value'."""
        element = self.find_element(*locator)
        select = Select(element)
        select.select_by_value(value)

    @error_handling
    def select_by_visible_text(self, locator: tuple[str, str], text: str) -> None:
        """Seleciona uma opção em um dropdown pelo texto visível."""
        element = self.find_element(*locator)
        select = Select(element)
        select.select_by_visible_text(text)
    
    def save_screenshot(self, path: str | None = None) -> None:
        """Salva um screenshot do driver."""

        if path is None:
            path = os.path.join(os.getcwd(), 'screenshots', f'{datetime.now().strftime('%Y%m%d_%H%M%S')}.png')
        
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        try:
            self.driver.save_screenshot(path)
            logging.info(f"Screenshot salvo em: {path}")
        except Exception as e:
            logging.error(f"Falha ao salvar screenshot. Erro:\n{e}")
    
    def execution_context(
        self,
        func: Callable,
        on_error: dict[type[Exception], Callable] | None = None,
        screenshot: bool = True,
        log_level: int | None = logging.INFO
    ) -> ExecutionContext:
        
        return ExecutionContext(
            driver=self,
            func=func,
            on_error=on_error,
            screenshot=screenshot,
            log_level=log_level
        )
    
    def start_execution(self) -> None:
        """Inicia o contexto de execução do driver."""
        self._is_executing = True
    
    def stop_execution(self) -> None:
        """Encerra o contexto de execução do driver."""
        self._is_executing = False

    def is_executing(self) -> bool:
        """Verifica se o driver está atualmente executando um comando."""
        return self._is_executing
    
    def _get_element(self, locator: WebElement | tuple[str, str]) -> WebElement:
        """Retorna um elemento localizado pelo seletor especificado."""
        if self._is_web_element(locator):
            return locator
        return self.find_element(*locator)
    
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
        self.close()
