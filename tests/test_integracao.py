import pytest
from selenium.common.exceptions import TimeoutException


def test_get_page(driver, local_page_url):
    """Testa se o driver consegue carregar uma página local."""
    driver.get(local_page_url)
    # O método get_title seria útil aqui!
    assert "Página de Teste" in driver.driver.title


def test_find_element(driver, local_page_url):
    """Testa a busca de um elemento pelo ID."""
    driver.get(local_page_url)
    titulo = driver.find_element("id", "titulo")
    assert titulo is not None
    assert titulo.text == "Bem-vindo à Página de Teste"


def test_click_element(driver, local_page_url):
    """Testa a funcionalidade de clique."""
    driver.get(local_page_url)

    titulo_antes = driver.find_element("id", "titulo")
    assert titulo_antes.text == "Bem-vindo à Página de Teste"

    # Clica no botão
    driver.click(("id", "botao_clicavel"))

    # Verifica se o texto do título mudou após o clique
    titulo_depois = driver.find_element("id", "titulo")
    assert titulo_depois.text == "Botão Clicado!"


def test_send_keys(driver, local_page_url):
    """Testa o envio de texto para um campo de input."""
    driver.get(local_page_url)
    campo = ("id", "campo_nome")

    # Envia novo texto, limpando o campo antes (comportamento padrão)
    driver.send_keys(campo, "Novo Texto")

    elemento_campo = driver.find_element(*campo)
    # get_attribute seria útil aqui!
    assert elemento_campo.get_attribute("value") == "Novo Texto"


def test_screenshot_on_error(driver, local_page_url):
    """Testa se um screenshot é salvo quando ocorre um erro dentro do 'with'."""
    import os

    screenshot_file = None
    try:
        # Forçamos um erro dentro do 'with'
        with pytest.raises(TimeoutException):
            driver.save_screenshot_on_error = True
            driver.get(local_page_url)
            driver.find_element("id", "id_inexistente", timeout=1)
    finally:
        # Verificamos se o screenshot foi criado
        # (Este é um jeito simplificado, o ideal seria ter um nome de arquivo previsível)
        files = [f for f in os.listdir(os.path.join(os.getcwd(), 'screenshots')) if f.endswith('.png')]
        assert len(files) > 0, "O screenshot de erro não foi salvo."
        # Limpa o arquivo criado
        for f in files:
            os.remove(os.path.join(os.getcwd(), 'screenshots', f))
