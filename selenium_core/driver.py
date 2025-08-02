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
from .controller import Controller
from .config import Config
from .log import LogManager
from .utils import is_web_element, describe_element


controller = Controller()

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
    ) -> None:
        """
        Gerenciador de driver do Selenium.

        Args:
            options: Opções Selenium do Driver.
            service: Serviço Selenium do Driver.
            keep_alive: Se deve manter o driver ativo.
            driver_cls: Classe do driver a ser usada.
            save_screenshot_on_error: Se deve salvar screenshot em caso de erro.
            default_timeout: Tempo padrão de espera para condições.
            default_poll_frequency: Frequência padrão de polling para condições.
            default_ignored_exceptions: Exceções a serem ignoradas durante as esperas.
            logger: Logger para registrar eventos. Se não for passado um, criará um logger padrão.
        """
        
        self._options = options
        self._service = service
        self._keep_alive = keep_alive
        self._driver_cls = driver_cls
        self._default_timeout = default_timeout
        self._default_poll_frequency = default_poll_frequency
        self._default_ignored_exceptions = default_ignored_exceptions
        self.log = LogManager(
            logger=logger,
            log_level=log_level,
            file_path=log_file_path,
            indent=log_indent
        )

        self._driver = None
        self._wait = None

        if save_screenshot_on_error:
            controller.exception_handler = self.save_screenshot
    
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
        """Inicializa o driver. Caso já esteja inicializado, reinicia."""
        self.log.info("Iniciando driver")
        self.quit()
        self._driver = self._start_driver()
    
    def quit(self) -> None:
        """Fecha o driver e libera os recursos. Caso não esteja inicializado, não faz nada."""
        
        if self._driver is None:
            return
        
        self.log.info("Fechando driver")
        self._driver.quit()
        self._driver = None

    @controller.on_error
    def get(self, url: str) -> None:
        """Navega para a URL especificada."""
        self.log.info(f"Acessando URL: {url}")
        self.driver.get(url)

    @controller.on_error
    def find_element(
        self,
        by: str,
        value: str,
        timeout: float | None = None,
        poll_frequency: float | None = None,
        ignored_exceptions: WaitExcTypes | None = None
    ) -> WebElement:
        """
        Encontra um único elemento na página.
        
        Args:
            by: O método de localização.
            value: O valor do seletor.
            timeout: Tempo máximo para aguardar o elemento.
            poll_frequency: Frequência de polling para verificar a presença do elemento.
            ignored_exceptions: Exceções a serem ignoradas durante a espera.
        """
        self.log.info(f'Procurando elemento ({by}="{value}")')
        return self.wait.presence_of_element_located(
            locator=(by, value),
            timeout=timeout,
            poll_frequency=poll_frequency,
            ignored_exceptions=ignored_exceptions
        )

    @controller.on_error
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
            by: O método de localização.
            value: O valor do seletor.
            timeout: Tempo máximo para aguardar os elementos.
            poll_frequency: Frequência de polling para verificar a presença dos elementos.
            ignored_exceptions: Exceções a serem ignoradas durante a espera.
        """
        self.log.info(f"Procurando elementos por {by}='{value}'")
        return self.wait.presence_of_all_elements_located(
            locator=(by, value),
            timeout=timeout,
            poll_frequency=poll_frequency,
            ignored_exceptions=ignored_exceptions
        )

    @controller.on_error
    def click(
        self,
        locator: WebElement | tuple[str, str],
        timeout: float | None = None,
        poll_frequency: float | None = None,
        ignored_exceptions: WaitExcTypes | None = None
    ) -> None:
        """
        Clica no elemento especificado.

        Args:
            locator: O WebElement ou tupla (by, value) do seletor.
            timeout: Tempo máximo para aguardar o elemento ser clicável.
            poll_frequency: Frequência de polling para verificar se o elemento está clicável.
            ignored_exceptions: Exceções a serem ignoradas durante a espera.
        """
        
        self.log.info(f"Aguardando o elemento ser clicável: {describe_element(locator)}")
        element = self.wait.element_to_be_clickable(
            locator=locator,
            timeout=timeout,
            poll_frequency=poll_frequency,
            ignored_exceptions=ignored_exceptions
        )

        self.log.info(f'Clicando no elemento {describe_element(element)}')
        element.click()

    @controller.on_error
    def hover(
        self,
        locator: WebElement | tuple[str, str],
        timeout: float | None = None,
        poll_frequency: float | None = None,
        ignored_exceptions: WaitExcTypes | None = None
    ) -> None:
        """
        Move o mouse para cima do elemento especificado.
        
        Args:
            locator: O WebElement ou tupla (by, value) do seletor.
            timeout: Tempo máximo para aguardar o elemento ser clicável.
            poll_frequency: Frequência de polling para verificar se o elemento está clicável.
            ignored_exceptions: Exceções a serem ignoradas durante a espera.
        """

        self.log.info(f"Aguardando o elemento ser clicável para hover: {describe_element(locator)}")
        element = self.wait.element_to_be_clickable(
            locator=locator,
            timeout=timeout,
            poll_frequency=poll_frequency,
            ignored_exceptions=ignored_exceptions
        )

        self.log.info(f"Movendo o mouse para o elemento: {describe_element(element)}")
        actions = ActionChains(self.driver)
        actions.move_to_element(element)
        actions.perform()
    
    @controller.on_error
    def send_keys(
        self,
        locator: WebElement | tuple[str, str],
        keys: str,
        clear: bool = True,
        timeout: float | None = None,
        poll_frequency: float | None = None,
        ignored_exceptions: WaitExcTypes | None = None
    ) -> None:
        """
        Envia teclas para o elemento especificado.

        Args:
            locator: O WebElement ou tupla (by, value) do seletor.
            keys: As teclas a serem enviadas.
            clear: Se deve limpar o campo antes de enviar as teclas.
            timeout: Tempo máximo para aguardar o elemento ser clicável.
            poll_frequency: Frequência de polling para verificar se o elemento está clicável.
            ignored_exceptions: Exceções a serem ignoradas durante a espera.
        """

        element = self.wait.element_to_be_clickable(
            locator=locator,
            timeout=timeout,
            poll_frequency=poll_frequency,
            ignored_exceptions=ignored_exceptions
        )

        if clear:
            self.log.info(f"Limpando o campo: {describe_element(element)}")
            element.clear()

        self.log.info(f"Enviando texto {keys} para o elemento: {describe_element(element)}")
        element.send_keys(keys)

    @controller.on_error
    def execute_script(self, script: str, *args) -> Any:
        """
        Executa um script JavaScript e retorna o resultado.
        
        Args:
            script: O código JavaScript a ser executado.
            *args: Argumentos adicionais a serem passados para o script.
        """
        self.log.info(f"Executando script: {script} com argumentos: {args}")
        return self.driver.execute_script(script, *args)

    @controller.on_error
    def switch_to_window(self, window_index: int = -1) -> None:
        """Muda o foco para uma janela/aba diferente."""
        all_windows = self.driver.window_handles
        self.log.info(f"Alterando para a janela/aba de índice {window_index}. Total de janelas: {len(all_windows)}")
        try:
            self.driver.switch_to.window(all_windows[window_index])
        except IndexError:
            self.log.error(f"Índice da janela {window_index} fora do intervalo. Total de janelas: {len(all_windows)}")
            raise
    
    @controller.on_error
    def get_text(
        self,
        locator: WebElement | tuple[str, str],
        timeout: float | None = None,
        poll_frequency: float | None = None,
        ignored_exceptions: WaitExcTypes | None = None
    ) -> str:
        """
        Retorna o texto de um elemento.
        
        Args:
            locator: O WebElement ou tupla (by, value) do seletor.
            timeout: Tempo máximo para aguardar o elemento estar presente.
            poll_frequency: Frequência de polling para verificar a presença do elemento.
            ignored_exceptions: Exceções a serem ignoradas durante a espera.
        """
        
        element = self._get_element(
            locator=locator,
            timeout=timeout,
            poll_frequency=poll_frequency,
            ignored_exceptions=ignored_exceptions
        )
        self.log.info(f"Obtendo texto do elemento: {describe_element(element)}")
        return element.text
    
    def is_displayed(
        self,
        locator: WebElement | tuple[str, str],
        timeout: float | None = None,
        poll_frequency: float | None = None,
        ignored_exceptions: WaitExcTypes | None = None
    ) -> bool:
        """
        Verifica se um elemento está visível na página.
        
        Args:
            locator: O WebElement ou tupla (by, value) do seletor.
            timeout: Tempo máximo para aguardar o elemento estar presente.
            poll_frequency: Frequência de polling para verificar a presença do elemento.
            ignored_exceptions: Exceções a serem ignoradas durante a espera.
        """

        element = self._get_element(
            locator=locator,
            timeout=timeout,
            poll_frequency=poll_frequency,
            ignored_exceptions=ignored_exceptions
        )
        
        self.log.info(f"Verificando visibilidade do elemento: {locator}")
        return element.is_displayed()

    def is_enabled(
        self,
        locator: WebElement | tuple[str,str],
        timeout: float | None = None,
        poll_frequency: float | None = None,
        ignored_exceptions: WaitExcTypes | None = None
    ) -> bool:
        """
        Verifica se um elemento está habilitado.

        Args:
            locator: O WebElement ou tupla (by, value) do seletor.
            timeout: Tempo máximo para aguardar o elemento estar presente.
            poll_frequency: Frequência de polling para verificar a presença do elemento.
            ignored_exceptions: Exceções a serem ignoradas durante a espera.
        """
    
        element = self._get_element(
            locator=locator,
            timeout=timeout,
            poll_frequency=poll_frequency,
            ignored_exceptions=ignored_exceptions
        )

        self.log.info(f"Verificando se o elemento está habilitado: {describe_element(element)}")
        return element.is_enabled()

    def get_title(self) -> str:
        """Retorna o título da página atual."""
        self.log.info("Obtendo título da página atual")
        return self.driver.title

    def get_current_url(self) -> str:
        """Retorna a URL da página atual."""
        self.log.info("Obtendo URL da página atual")
        return self.driver.current_url
    
    @controller.on_error
    def scroll_to_element(
        self,
        locator: WebElement | tuple[str, str],
        timeout: float | None = None,
        poll_frequency: float | None = None,
        ignored_exceptions: WaitExcTypes | None = None
    ) -> None:
        """
        Rola a página até que o elemento esteja visível.
        
        Args:
            locator: O WebElement ou tupla (by, value) do seletor.
            timeout: Tempo máximo para aguardar o elemento estar presente.
            poll_frequency: Frequência de polling para verificar a presença do elemento.
            ignored_exceptions: Exceções a serem ignoradas durante a espera.
        """

        element = self._get_element(
            locator=locator,
            timeout=timeout,
            poll_frequency=poll_frequency,
            ignored_exceptions=ignored_exceptions
        )

        self.log.info(f"Scrollando a página até o elemento: {describe_element(element)}")
        self.execute_script("arguments[0].scrollIntoView(true);", element)

    @controller.on_error
    def scroll_to_bottom(self) -> None:
        """Rola a página até o final."""
        self.log.info("Scrollando a página até o final")
        self.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    @controller.on_error
    def scroll_to_top(self) -> None:
        """Rola a página até o topo."""
        self.log.info("Scrollando a página até o topo")
        self.execute_script("window.scrollTo(0, 0);")
    
    @controller.on_error
    def select_by_value(
        self,
        locator: WebElement | tuple[str, str],
        value: str,
        timeout: float | None = None,
        poll_frequency: float | None = None,
        ignored_exceptions: WaitExcTypes | None = None
    ) -> None:
        """
        Seleciona uma opção em um dropdown pelo seu atributo 'value'.

        Args:
            locator: O WebElement ou tupla (by, value) do seletor.
            value: O valor da opção a ser selecionada.
            timeout: Tempo máximo para aguardar o elemento estar presente.
            poll_frequency: Frequência de polling para verificar a presença do elemento.
            ignored_exceptions: Exceções a serem ignoradas durante a espera.
        """

        element = self._get_element(
            locator=locator,
            timeout=timeout,
            poll_frequency=poll_frequency,
            ignored_exceptions=ignored_exceptions
        )

        self.log.info(f"Selecionando opção com value '{value}' no dropdown: {describe_element(element)}")
        select = Select(element)
        select.select_by_value(value)

    @controller.on_error
    def select_by_visible_text(
        self,
        locator: tuple[str, str],
        text: str,
        timeout: float | None = None,
        poll_frequency: float | None = None,
        ignored_exceptions: WaitExcTypes | None = None
    ) -> None:
        """
        Seleciona uma opção em um dropdown pelo texto visível.

        Args:
            locator: O WebElement ou tupla (by, value) do seletor.
            text: O texto visível da opção a ser selecionada.
            timeout: Tempo máximo para aguardar o elemento estar presente.
            poll_frequency: Frequência de polling para verificar a presença do elemento.
            ignored_exceptions: Exceções a serem ignoradas durante a espera.
        """

        element = self._get_element(
            locator=locator,
            timeout=timeout,
            poll_frequency=poll_frequency,
            ignored_exceptions=ignored_exceptions
        )

        self.log.info(f"Selecionando opção com texto visível '{text}' no dropdown: {describe_element(element)}")
        select = Select(element)
        select.select_by_visible_text(text)
    
    def save_screenshot(self: 'Driver', exception: Exception | None = None) -> None:
        """
        Salva um screenshot do driver com um nome de arquivo dinâmico e informativo.
        
        Args:
            exception: A exceção que ocorreu, se houver. Usado para nomear o arquivo.
        """
        
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        if exception is None:
            file_name = f"{timestamp}.png"
        else:
            file_name = f"{timestamp}_{exception.__class__.__name__}.png"

        file_path = os.path.join(Config.SCREENSHOT_DIR, file_name)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        self.driver.save_screenshot(file_path)

    def _get_element(
        self,
        locator: WebElement | tuple[str, str],
        timeout: float | None = None,
        poll_frequency: float | None = None,
        ignored_exceptions: WaitExcTypes | None = None
    ) -> WebElement:
        """
        Retorna o WebElement desejado. Caso 'locator' seja um WebElement, retorna ele diretamente.
        Se for uma tupla, procura o elemento na página.
        
        Args:
            locator: O WebElement ou tupla (by, value).
            timeout: Tempo máximo para aguardar o elemento estar presente.
            poll_frequency: Frequência de polling para verificar a presença do elemento.
            ignored_exceptions: Exceções a serem ignoradas durante a espera.
        """

        if is_web_element(locator):
            return locator

        return self.find_element(
            *locator,
            timeout=timeout,
            poll_frequency=poll_frequency,
            ignored_exceptions=ignored_exceptions
        )

    def _start_driver(self) -> WebDriver:
        """Inicia o driver Selenium com as configurações fornecidas."""
        return self._driver_cls(self._options, self._service, self._keep_alive)
    
    def __enter__(self) -> Self:
        self.init()
        return self
    
    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.quit()
