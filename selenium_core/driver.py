from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from .handling import on_error
from .config import Config
from .log import get_logger
from datetime import datetime
import os
from typing import Callable, Self, Literal, Any, TypeIs, TypeVar


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
        self._save_screenshot_on_error = save_screenshot_on_error

        self._logger = get_logger()
        self._driver = None
        self._is_executing = False
    
    @property
    def driver(self) -> WebDriver:
        if self._driver is None:
            self._driver = self._start_driver()
        return self._driver
    
    def is_initialized(self) -> bool:
        """Verifica se o driver foi inicializado."""
        return self._driver is not None
    
    def init(self) -> None:
        self._logger.info("Iniciando driver")

        self.quit()
        self._driver = self._start_driver()
    
    def quit(self) -> None:
        if self._driver is not None:
            self._logger.info("Fechando driver")
            self._driver.quit()
            self._driver = None

    @on_error
    def get(self, url: str) -> None:
        self._logger.info(f"Acessando URL: {url}")
        self.driver.get(url)

    @on_error
    def wait(
        self,
        locator: WebElement | tuple[str, str],
        expected_condition: Callable[..., Callable[..., T_EC]] = EC.presence_of_element_located,
        timeout: float = 30
    ) -> T_EC:
        
        self._check_locator(locator)
        if expected_condition is not None and not callable(expected_condition):
            raise TypeError(f"O parâmetro 'expected_condition' deve ser do tipo 'Callable', não {type(expected_condition).__name__}")

        self._logger.debug(f"Aguardando elemento: {locator} com condição: {expected_condition.__name__} por {timeout} segundos")
        return WebDriverWait(self.driver, timeout).until(expected_condition(locator))
    
    @on_error
    def wait_not(self,
        locator: WebElement | tuple[str, str],
        expected_condition: Callable[..., Callable[..., T_EC]] = EC.presence_of_element_located,
        timeout: float = 30
    ) -> T_EC | Literal[True]:
    
        if expected_condition is not None and not callable(expected_condition):
            raise TypeError(f"Aguardando elemento: {locator} com condição: {expected_condition.__name__} por {timeout} segundos")

        self._logger.debug(f"Aguardando elemento: {locator} com condição: not {expected_condition.__name__} por {timeout} segundos")
        return WebDriverWait(self.driver, timeout).until_not(expected_condition(locator))
    
    @on_error
    def find_element(
        self,
        by: str,
        value: str,
        expected_condition: Callable | None = EC.presence_of_element_located,
        timeout: float = 30
    ) -> WebElement:
        
        if expected_condition is not None:
            return self.wait((by, value), expected_condition, timeout)
        return self.driver.find_element(by, value)
    
    @on_error
    def find_elements(
        self,
        by: str,
        value: str,
        expected_condition: Callable | None = EC.presence_of_all_elements_located,
        timeout: float = 30
    ) -> list[WebElement]:
        
        if expected_condition is not None:
            return self.wait((by, value), expected_condition, timeout)
        return self.driver.find_elements(by, value)
    
    @on_error
    def click(
        self,
        locator: WebElement | tuple[str, str]
    ) -> None:

        self._check_locator(locator)
        element = self.wait(locator, EC.element_to_be_clickable)

        self._logger.debug(f"Clicando no elemento: {locator}")
        element.click()

    @on_error
    def hover(self, locator: WebElement | tuple[str, str]) -> None:
        """Move o mouse para cima do elemento especificado."""
        self._check_locator(locator)
        element = self._get_element(locator)

        self._logger.debug(f"Movendo o mouse para o elemento: {locator}")
        actions = ActionChains(self.driver)
        actions.move_to_element(element)
        actions.perform()
    
    @on_error
    def send_keys(
        self,
        locator: WebElement | tuple[str, str],
        keys: str,
        clear: bool = True
    ) -> None:
        
        self._check_locator(locator)
        element = self._get_element(locator)
        
        if clear:
            self._logger.debug(f"Limpando o campo: {locator}")
            element.clear()

        self._logger.debug(f"Enviando texto {keys} para o elemento: {locator}")
        element.send_keys(keys)

    @on_error
    def execute_script(self, script: str, *args) -> Any:
        """Executa um script JavaScript e retorna o resultado."""
        self._logger.debug(f"Executando script: {script} com argumentos: {args}")
        return self.driver.execute_script(script, *args)
    
    def switch_to_window(self, window_index: int = -1) -> None:
        """Muda o foco para uma janela/aba diferente."""
        all_windows = self.driver.window_handles
        if len(all_windows) > abs(window_index):
            self.driver.switch_to.window(all_windows[window_index])
    
    @on_error
    def get_text(self, locator: WebElement | tuple[str, str]) -> str:
        """Retorna o texto de um elemento."""
        element = self._get_element(locator)
        self._logger.debug(f"Obtendo texto do elemento: {locator}")
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
        element = self._get_element(locator)
        self._logger.debug(f"Verificando se o elemento está habilitado: {locator}")
        return element.is_enabled()
    
    def get_title(self) -> str:
        """Retorna o título da página atual."""
        self._logger.debug("Obtendo título da página atual")
        return self.driver.title

    def get_current_url(self) -> str:
        """Retorna a URL da página atual."""
        self._logger.debug("Obtendo URL da página atual")
        return self.driver.current_url
    
    @on_error
    def scroll_to_element(self, locator: WebElement | tuple[str, str]) -> None:
        """Rola a página até que o elemento esteja visível."""
        element = self._get_element(locator)
        self._logger.debug(f"Scrollando a página até o elemento: {locator}")
        self.execute_script("arguments[0].scrollIntoView(true);", element)

    @on_error
    def scroll_to_bottom(self) -> None:
        """Rola a página até o final."""
        self._logger.debug("Scrollando a página até o final")
        self.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    @on_error
    def scroll_to_top(self) -> None:
        """Rola a página até o topo."""
        self._logger.debug("Scrollando a página até o topo")
        self.execute_script("window.scrollTo(0, 0);")
    
    @on_error
    def select_by_value(self, locator: tuple[str, str], value: str) -> None:
        """Seleciona uma opção em um dropdown pelo seu atributo 'value'."""
        element = self.find_element(*locator)
        self._logger.debug(f"Selecionando opção com value '{value}' no dropdown: {locator}")
        select = Select(element)
        select.select_by_value(value)

    @on_error
    def select_by_visible_text(self, locator: tuple[str, str], text: str) -> None:
        """Seleciona uma opção em um dropdown pelo texto visível."""
        element = self.find_element(*locator)
        self._logger.debug(f"Selecionando opção com texto visível '{text}' no dropdown: {locator}")
        select = Select(element)
        select.select_by_visible_text(text)
    
    def save_screenshot(self, context_name: str | None = None) -> None:
        """
        Salva um screenshot do driver com um nome de arquivo dinâmico e informativo.
        
        Args:
            context_name: Um nome para o contexto (ex: o nome da função que falhou).
        """
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        if context_name is not None:
            file_name = f"{timestamp}_{context_name}.png"
        else:
            file_name = f"{timestamp}.png"
        
        file_path = os.path.join(Config.SCREENSHOT_DIR, file_name)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        try:
            self.driver.save_screenshot(file_path)
            self._logger.info(f"Screenshot salvo em: {file_path}")
        except Exception as e:
            self._logger.error(f"Falha ao salvar screenshot. Erro:\n{e}")

    def _get_element(self, locator: WebElement | tuple[str, str]) -> WebElement:
        """Retorna um elemento localizado pelo seletor especificado."""
        if self._is_web_element(locator):
            return locator
        return self.find_element(*locator, expected_condition=None)

    def _start_driver(self) -> WebDriver:
        return WebDriver(self.options, self.service, self.keep_alive)
    
    def _check_locator(self, locator: WebElement | tuple[str, str]) -> bool:

        if self._is_web_element(locator):
            return True
        
        if self._is_by_tuple(locator):
            return True
        
        self._logger.error(f"O parâmetro 'locator' deve ser do tipo 'WebElement' ou 'tuple', não {type(locator).__name__}")
        raise TypeError(f"O parâmetro 'locator' deve ser do tipo 'WebElement' ou 'tuple', não {type(locator).__name__}")
    
    def _is_web_element(self, element: Any) -> TypeIs[WebElement]:
        return isinstance(element, WebElement)
    
    def _is_by_tuple(self, element: Any) -> TypeIs[tuple[str, str]]:
        return isinstance(element, tuple) and len(element) == 2 and isinstance(element[0], str) and isinstance(element[1], str)
    
    def __enter__(self) -> Self:
        self.init()
        return self
    
    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.quit()
