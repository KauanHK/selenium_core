from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from typing import Any, TypeIs, Callable
from .types import T_EC


def is_web_element(element: Any) -> TypeIs[WebElement]:
    return isinstance(element, WebElement)


def is_by_tuple(element: Any) -> TypeIs[tuple[str, str]]:
    return isinstance(element, tuple) and len(element) == 2 and isinstance(element[0], str) and isinstance(element[1], str)


def check_locator(locator: WebElement | tuple[str, str]) -> bool:

    if is_web_element(locator):
        return True

    if is_by_tuple(locator):
        return True
    
    raise TypeError(f"O parâmetro 'locator' deve ser do tipo 'WebElement' ou 'tuple', não {type(locator).__name__}")


def get_predicate(
    locator: tuple[str, str] | Callable[..., T_EC],
    expected_condition: Callable[..., Callable[..., T_EC]] = EC.presence_of_element_located
) -> Callable[..., T_EC]:
    """
    Obtém a função de condição esperada a partir do localizador.
    
    Args:
        locator: Um tupla contendo o método de localização e o valor, ou uma função de condição esperada.
    
    Returns:
        Uma função de condição esperada.
    """
    
    if callable(locator):
        return locator
    if is_by_tuple(locator):
        return expected_condition(locator)

    raise TypeError(f"O parâmetro 'locator' deve ser do tipo 'tuple' ou 'Callable', não {type(locator).__name__}")


def get_locator(
    locator: WebElement | tuple[str, str] | Callable[..., T_EC],
    expected_condition: Callable[..., Callable[..., T_EC]]
) -> Callable[..., T_EC]:

    if not callable(locator):
        return expected_condition(locator)
    return locator
