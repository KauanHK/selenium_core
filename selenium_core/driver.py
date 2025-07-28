from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver import Chrome
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
from selenium.types import WaitExcTypes
import logging
from datetime import datetime
import os
from typing import Self, Any
from .wait import Wait
from .handling import on_error
from .config import Config
from .log import get_logger
from .utils import is_web_element, describe_element


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
        logger: logging.Logger | None = None
    ) -> None:
        """
        Gerenciador de driver do Selenium.

        Args:
            options: Opções do Driver.
        """
        
        self._options = options
        self._service = service
        self._keep_alive = keep_alive
        self._driver_cls = driver_cls
        self._save_screenshot_on_error = save_screenshot_on_error
        self._default_timeout = default_timeout
        self._default_poll_frequency = default_poll_frequency
        self._default_ignored_exceptions = default_ignored_exceptions
        self._logger = logger if logger is not None else get_logger()

        self._driver = None
        self._wait = None
        self._is_executing = False
    
    @property
    def driver(self) -> WebDriver:
        if self._driver is None:
            self._driver = self._start_driver()
        return self._driver
    
    @property
    def wait(self) -> Wait:
        if self._wait is None:
            self._wait = Wait(
                driver=self.driver,
                default_timeout=self._default_timeout,
                default_poll_frequency=self._default_poll_frequency,
                default_ignored_exceptions=self._default_ignored_exceptions
            )
        return self._wait
    
    def is_initialized(self) -> bool:
        """Verifica se o driver foi inicializado."""
        return self._driver is not None
    
    def init(self) -> None:
        self._logger.info("Iniciando driver")
        self.quit()
        self._driver = self._start_driver()
    
    def quit(self) -> None:
        
        if self._driver is None:
            return
        
        self._logger.info("Fechando driver")
        self._driver.quit()
        self._driver = None

    @on_error
    def get(self, url: str) -> None:
        self._logger.info(f"Acessando URL: {url}")
        self.driver.get(url)

    @on_error
    def find_element(
        self,
        by: str,
        value: str,
        timeout: float | None = None,
        poll_frequency: float | None = None,
        ignored_exceptions: WaitExcTypes | None = None
    ) -> WebElement:
        """ Encontra um único elemento na página.
        
        Args:
            by: O método de localização (ex: 'id', 'xpath', etc).
            value: O valor do seletor.
        """
        self._logger.info(f'Procurando elemento ({by}="{value}")')
        return self.wait.presence_of_element_located(
            locator=(by, value),
            timeout=timeout,
            poll_frequency=poll_frequency,
            ignored_exceptions=ignored_exceptions
        )

    @on_error
    def find_elements(
        self,
        by: str,
        value: str,
        timeout: float | None = None,
        poll_frequency: float | None = None,
        ignored_exceptions: WaitExcTypes | None = None
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
        self._logger.info(f"Procurando elementos por {by}='{value}'")
        return self.wait.presence_of_all_elements_located(
            locator=(by, value),
            timeout=timeout,
            poll_frequency=poll_frequency,
            ignored_exceptions=ignored_exceptions
        )

    @on_error
    def click(
        self,
        locator: WebElement | tuple[str, str],
        timeout: float | None = None,
        poll_frequency: float | None = None,
        ignored_exceptions: WaitExcTypes | None = None
    ) -> None:
        
        self._logger.info(f"Aguardando o elemento ser clicável: {describe_element(locator)}")
        element = self.wait.element_to_be_clickable(
            locator=locator,
            timeout=timeout,
            poll_frequency=poll_frequency,
            ignored_exceptions=ignored_exceptions
        )

        self._logger.info(f'Clicando no elemento {describe_element(element)}')
        element.click()

    @on_error
    def hover(
        self,
        locator: WebElement | tuple[str, str],
        timeout: float | None = None,
        poll_frequency: float | None = None,
        ignored_exceptions: WaitExcTypes | None = None
    ) -> None:
        """Move o mouse para cima do elemento especificado."""

        self._logger.info(f"Aguardando o elemento ser clicável para hover: {describe_element(locator)}")
        element = self.wait.element_to_be_clickable(
            locator=locator,
            timeout=timeout,
            poll_frequency=poll_frequency,
            ignored_exceptions=ignored_exceptions
        )

        self._logger.info(f"Movendo o mouse para o elemento: {describe_element(element)}")
        actions = ActionChains(self.driver)
        actions.move_to_element(element)
        actions.perform()
    
    @on_error
    def send_keys(
        self,
        locator: WebElement | tuple[str, str],
        keys: str,
        clear: bool = True,
        timeout: float | None = None,
        poll_frequency: float | None = None,
        ignored_exceptions: WaitExcTypes | None = None
    ) -> None:

        element = self.wait.element_to_be_clickable(
            locator=locator,
            timeout=timeout,
            poll_frequency=poll_frequency,
            ignored_exceptions=ignored_exceptions
        )

        if clear:
            self._logger.info(f"Limpando o campo: {describe_element(element)}")
            element.clear()

        self._logger.info(f"Enviando texto {keys} para o elemento: {describe_element(element)}")
        element.send_keys(keys)

    @on_error
    def execute_script(self, script: str, *args) -> Any:
        """Executa um script JavaScript e retorna o resultado."""
        self._logger.info(f"Executando script: {script} com argumentos: {args}")
        return self.driver.execute_script(script, *args)

    @on_error
    def switch_to_window(self, window_index: int = -1) -> None:
        """Muda o foco para uma janela/aba diferente."""
        all_windows = self.driver.window_handles
        self._logger.info(f"Alterando para a janela/aba de índice {window_index}. Total de janelas: {len(all_windows)}")
        try:
            self.driver.switch_to.window(all_windows[window_index])
        except IndexError:
            self._logger.error(f"Índice da janela {window_index} fora do intervalo. Total de janelas: {len(all_windows)}")
            raise
    
    @on_error
    def get_text(
        self,
        locator: WebElement | tuple[str, str],
        timeout: float | None = None,
        poll_frequency: float | None = None,
        ignored_exceptions: WaitExcTypes | None = None
    ) -> str:
        """Retorna o texto de um elemento."""
        
        element = self._get_element(
            locator=locator,
            timeout=timeout,
            poll_frequency=poll_frequency,
            ignored_exceptions=ignored_exceptions
        )
        self._logger.info(f"Obtendo texto do elemento: {describe_element(element)}")
        return element.text
    
    def is_displayed(
        self,
        locator: WebElement | tuple[str, str],
        timeout: float | None = None,
        poll_frequency: float | None = None,
        ignored_exceptions: WaitExcTypes | None = None
    ) -> bool:
        """Verifica se um elemento está visível na página."""
        
        element =  self._get_element(
            locator=locator,
            timeout=timeout,
            poll_frequency=poll_frequency,
            ignored_exceptions=ignored_exceptions
        )
        
        self._logger.info(f"Verificando visibilidade do elemento: {locator}")
        return element.is_displayed()

    def is_enabled(
        self,
        locator: WebElement | tuple[str,str],
        timeout: float | None = None,
        poll_frequency: float | None = None,
        ignored_exceptions: WaitExcTypes | None = None
    ) -> bool:
        """Verifica se um elemento está habilitado."""
    
        element = self._get_element(
            locator=locator,
            timeout=timeout,
            poll_frequency=poll_frequency,
            ignored_exceptions=ignored_exceptions
        )

        self._logger.info(f"Verificando se o elemento está habilitado: {describe_element(element)}")
        return element.is_enabled()

    def get_title(self) -> str:
        """Retorna o título da página atual."""
        self._logger.info("Obtendo título da página atual")
        return self.driver.title

    def get_current_url(self) -> str:
        """Retorna a URL da página atual."""
        self._logger.info("Obtendo URL da página atual")
        return self.driver.current_url
    
    @on_error
    def scroll_to_element(
        self,
        locator: WebElement | tuple[str, str],
        timeout: float | None = None,
        poll_frequency: float | None = None,
        ignored_exceptions: WaitExcTypes | None = None
    ) -> None:
        """Rola a página até que o elemento esteja visível."""

        element = self._get_element(
            locator=locator,
            timeout=timeout,
            poll_frequency=poll_frequency,
            ignored_exceptions=ignored_exceptions
        )

        self._logger.info(f"Scrollando a página até o elemento: {describe_element(element)}")
        self.execute_script("arguments[0].scrollIntoView(true);", element)

    @on_error
    def scroll_to_bottom(self) -> None:
        """Rola a página até o final."""
        self._logger.info("Scrollando a página até o final")
        self.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    @on_error
    def scroll_to_top(self) -> None:
        """Rola a página até o topo."""
        self._logger.info("Scrollando a página até o topo")
        self.execute_script("window.scrollTo(0, 0);")
    
    @on_error
    def select_by_value(
        self,
        locator: WebElement | tuple[str, str],
        value: str,
        timeout: float | None = None,
        poll_frequency: float | None = None,
        ignored_exceptions: WaitExcTypes | None = None
    ) -> None:
        """Seleciona uma opção em um dropdown pelo seu atributo 'value'."""
        
        element = self._get_element(
            locator=locator,
            timeout=timeout,
            poll_frequency=poll_frequency,
            ignored_exceptions=ignored_exceptions
        )

        self._logger.info(f"Selecionando opção com value '{value}' no dropdown: {describe_element(element)}")
        select = Select(element)
        select.select_by_value(value)

    @on_error
    def select_by_visible_text(
        self,
        locator: tuple[str, str],
        text: str,
        timeout: float | None = None,
        poll_frequency: float | None = None,
        ignored_exceptions: WaitExcTypes | None = None
    ) -> None:
        """Seleciona uma opção em um dropdown pelo texto visível."""

        element = self._get_element(
            locator=locator,
            timeout=timeout,
            poll_frequency=poll_frequency,
            ignored_exceptions=ignored_exceptions
        )

        self._logger.info(f"Selecionando opção com texto visível '{text}' no dropdown: {describe_element(element)}")
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

    def start_execution(self) -> None:
        self._is_executing = True
    
    def stop_execution(self) -> None:
        self._is_executing = False
    
    def is_executing(self) -> bool:
        return self._is_executing

    def _get_element(
        self,
        locator: WebElement | tuple[str, str],
        timeout: float | None = None,
        poll_frequency: float | None = None,
        ignored_exceptions: WaitExcTypes | None = None
    ) -> WebElement:
        """Retorna um elemento localizado pelo seletor especificado."""

        if is_web_element(locator):
            return locator

        return self.find_element(
            *locator,
            timeout=timeout,
            poll_frequency=poll_frequency,
            ignored_exceptions=ignored_exceptions
        )

    def _start_driver(self) -> WebDriver:
        return self._driver_cls(self._options, self._service, self._keep_alive)
    
    def __enter__(self) -> Self:
        self.init()
        return self
    
    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.quit()
