import pytest
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from unittest.mock import MagicMock
from driver import Driver

driver_instance = Driver()


def test_is_web_element():
    """Testa a verificação de tipo para WebElement."""

    mock_element = MagicMock(spec=WebElement)

    assert driver_instance._is_web_element(mock_element) == True
    assert driver_instance._is_web_element((By.ID, "teste")) == False
    assert driver_instance._is_web_element("uma string") == False
    assert driver_instance._is_web_element(None) == False


def test_is_by_tuple():
    """Testa a verificação de tipo para tuplas de localizador."""
    
    assert driver_instance._is_by_tuple(("id", "meu-id")) == True
    assert driver_instance._is_by_tuple(("css selector", ".classe")) == True
    assert driver_instance._is_by_tuple(("id",)) == False # Tupla com 1 elemento
    assert driver_instance._is_by_tuple((123, "valor")) == False # Primeiro item não é string


def test_check_locator_com_tipos_invalidos():
    """Verifica se _check_locator levanta TypeError para tipos inválidos."""
    
    with pytest.raises(TypeError, match="deve ser do tipo 'WebElement' ou 'tuple'"):
        driver_instance._check_locator("locator_invalido")
        
    with pytest.raises(TypeError):
        driver_instance._check_locator(12345)
