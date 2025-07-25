from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver import Chrome
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import logging
from datetime import datetime
import os
from typing import Callable, Self, Any
from .handling import on_error
from .config import Config
from .log import get_logger
from .utils import get_predicate, get_locator, is_web_element
from .types import ExpectedConditionPredicate, T_EC


class Driver:

    def __init__(
        self,
        options: Options | None = None,
        service: Service | None = None,
        keep_alive: bool = True,
        driver_cls: type[WebDriver] = Chrome,
        save_screenshot_on_error: bool = True,
        default_timeout: float = 30,
        logger: logging.Logger | None = None
    ) -> None:
        """
        Gerenciador de driver do Selenium.

        Args:
            options: Opções do Driver.
        """
        
        self._driver_cls = driver_cls
        self.options = options
        self.service = service
        self.keep_alive = keep_alive
        self.default_timeout = default_timeout
        self.logger = logger if logger is not None else get_logger()

        self._save_screenshot_on_error = save_screenshot_on_error

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
        self.logger.info("Iniciando driver")
        self.quit()
        self._driver = self._start_driver()
    
    def quit(self) -> None:
        
        if self._driver is None:
            return
        
        self.logger.info("Fechando driver")
        self._driver.quit()
        self._driver = None

    @on_error
    def get(self, url: str) -> None:
        self.logger.info(f"Acessando URL: {url}")
        self.driver.get(url)

    @on_error
    def wait(
        self,
        locator: tuple[str, str] | Callable[..., T_EC],
        timeout: float | None = None
    ) -> T_EC:

        timeout = timeout if timeout is not None else self.default_timeout
        ec_predicate = get_predicate(locator)
        self.logger.debug(f"Aguardando a condição {ec_predicate} por {timeout} segundos")
        return WebDriverWait(self.driver, timeout).until(ec_predicate)
    
    @on_error
    def wait_not(self,
        locator: tuple[str, str] | Callable[..., T_EC],
        timeout: float | None = None
    ) -> T_EC:

        timeout = timeout if timeout is not None else self.default_timeout
        ec_predicate = get_predicate(locator)
        self.logger.debug(f"Aguardando a não condição {ec_predicate} por {timeout} segundos")
        return WebDriverWait(self.driver, timeout).until_not(ec_predicate)
    
    @on_error
    def find_element(
        self,
        by: str,
        value: str,
        timeout: float | None = None
    ) -> WebElement:
        """ Encontra um único elemento na página.
        
        Args:
            by: O método de localização (ex: 'id', 'xpath', etc).
            value: O valor do seletor.
        """
        timeout = timeout if timeout is not None else self.default_timeout
        ec_predicate = get_predicate((by, value), EC.presence_of_element_located)
        self.logger.debug(f"Procurando elemento por {by}='{value}'")
        return self.wait(ec_predicate, timeout)

    @on_error
    def find_elements(
        self,
        by: str,
        value: str,
        timeout: float | None = None
    ) -> list[WebElement]:
        """
        Encontra múltiplos elementos na página.
        
        Args:
            by: O método de localização (ex: 'id', 'xpath', etc).
            value: O valor do seletor.
            expected_condition: Uma função que retorna uma condição esperada.
            timeout: Tempo máximo para aguardar os elementos.
        
        Returns:
            Uma lista de WebElements encontrados.
        """
        timeout = timeout if timeout is not None else self.default_timeout
        ec_predicate = get_predicate((by, value), EC.presence_of_all_elements_located)
        self.logger.debug(f"Procurando elementos por {by}='{value}'")
        return self.wait(ec_predicate, timeout)
    
    @on_error
    def click(
        self,
        locator: WebElement | tuple[str, str] | ExpectedConditionPredicate,
        timeout: float | None = None
    ) -> None:
        timeout = timeout if timeout is not None else self.default_timeout
        locator = get_locator(locator, EC.element_to_be_clickable)
        element = self.wait(locator, timeout)
        self.logger.debug('Clicando no elemento')
        element.click()

    @on_error
    def hover(
        self,
        locator: WebElement | tuple[str, str] | ExpectedConditionPredicate,
        timeout: float | None = None
    ) -> None:
        """Move o mouse para cima do elemento especificado."""

        timeout = timeout if timeout is not None else self.default_timeout
        locator = get_locator(locator, EC.element_to_be_clickable)
        element = self.wait(locator, timeout)

        self.logger.debug(f"Movendo o mouse para o elemento: {element}")
        actions = ActionChains(self.driver)
        actions.move_to_element(element)
        actions.perform()
    
    @on_error
    def send_keys(
        self,
        locator: WebElement | tuple[str, str] | ExpectedConditionPredicate,
        keys: str,
        timeout: float | None = None,
        clear: bool = True
    ) -> None:
        
        timeout = timeout if timeout is not None else self.default_timeout
        locator = get_locator(locator, EC.element_to_be_clickable)
        element = self.wait(locator, timeout)

        if clear:
            self.logger.debug(f"Limpando o campo: {locator}")
            element.clear()

        self.logger.debug(f"Enviando texto {keys} para o elemento: {locator}")
        element.send_keys(keys)

    @on_error
    def execute_script(self, script: str, *args) -> Any:
        """Executa um script JavaScript e retorna o resultado."""
        self.logger.debug(f"Executando script: {script} com argumentos: {args}")
        return self.driver.execute_script(script, *args)

    @on_error
    def switch_to_window(self, window_index: int = -1) -> None:
        """Muda o foco para uma janela/aba diferente."""
        all_windows = self.driver.window_handles
        try:
            self.driver.switch_to.window(all_windows[window_index])
        except IndexError:
            self.logger.error(f"Índice da janela {window_index} fora do intervalo. Total de janelas: {len(all_windows)}")
            raise
    
    @on_error
    def get_text(self, locator: WebElement | tuple[str, str]) -> str:
        """Retorna o texto de um elemento."""
        element = self._get_element(locator)
        self.logger.debug(f"Obtendo texto do elemento: {locator}")
        return element.text
    
    def is_visible(self, locator: tuple[str, str], timeout: float | None = None) -> bool:
        """Verifica se um elemento está visível na página."""
        
        timeout = timeout if timeout is not None else self.default_timeout
        try:
            self.wait(EC.visibility_of_element_located(locator), timeout)
            return True
        except TimeoutException:
            return False

    def is_enabled(self, locator: WebElement | tuple[str, str]) -> bool:
        """Verifica se um elemento está habilitado."""
        element = self._get_element(locator)
        self.logger.debug(f"Verificando se o elemento está habilitado: {locator}")
        return element.is_enabled()
    
    def get_title(self) -> str:
        """Retorna o título da página atual."""
        self.logger.debug("Obtendo título da página atual")
        return self.driver.title

    def get_current_url(self) -> str:
        """Retorna a URL da página atual."""
        self.logger.debug("Obtendo URL da página atual")
        return self.driver.current_url
    
    @on_error
    def scroll_to_element(self, locator: WebElement | tuple[str, str]) -> None:
        """Rola a página até que o elemento esteja visível."""
        element = self._get_element(locator)
        self.logger.debug(f"Scrollando a página até o elemento: {locator}")
        self.execute_script("arguments[0].scrollIntoView(true);", element)

    @on_error
    def scroll_to_bottom(self) -> None:
        """Rola a página até o final."""
        self.logger.debug("Scrollando a página até o final")
        self.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    @on_error
    def scroll_to_top(self) -> None:
        """Rola a página até o topo."""
        self.logger.debug("Scrollando a página até o topo")
        self.execute_script("window.scrollTo(0, 0);")
    
    @on_error
    def select_by_value(self, locator: tuple[str, str], value: str) -> None:
        """Seleciona uma opção em um dropdown pelo seu atributo 'value'."""
        element = self.find_element(*locator)
        self.logger.debug(f"Selecionando opção com value '{value}' no dropdown: {locator}")
        select = Select(element)
        select.select_by_value(value)

    @on_error
    def select_by_visible_text(self, locator: tuple[str, str], text: str) -> None:
        """Seleciona uma opção em um dropdown pelo texto visível."""
        element = self.find_element(*locator)
        self.logger.debug(f"Selecionando opção com texto visível '{text}' no dropdown: {locator}")
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
            self.logger.info(f"Screenshot salvo em: {file_path}")
        except Exception as e:
            self.logger.error(f"Falha ao salvar screenshot. Erro:\n{e}")

    def _get_element(self, locator: WebElement | tuple[str, str]) -> WebElement:
        """Retorna um elemento localizado pelo seletor especificado."""
        if is_web_element(locator):
            return locator
        return self.find_element(*locator)

    def _start_driver(self) -> WebDriver:
        return self._driver_cls(self.options, self.service, self.keep_alive)
    
    def start_execution(self) -> None:
        self._is_executing = True
    
    def stop_execution(self) -> None:
        self._is_executing = False
    
    def is_executing(self) -> bool:
        return self._is_executing

    def __enter__(self) -> Self:
        self.init()
        return self
    
    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.quit()
