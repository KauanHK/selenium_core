import pytest
import os
from driver import Driver
from config import Config


@pytest.fixture(scope="session")
def driver():
    """
    Fixture que cria uma instância do Driver para cada função de teste.
    O 'yield' entrega o driver para o teste e o código após ele
    (o bloco 'with' cuida disso) é executado na finalização.
    """
    
    with Driver(Config.OPTIONS, Config.SERVICE) as d:
        yield d


@pytest.fixture
def local_page_url():
    """Retorna a URL do arquivo HTML de teste local."""
    return "file://" + os.path.abspath("tests/test_page.html")
