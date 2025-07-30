import logging
import os
from datetime import datetime
import time
from typing import Callable
from .config import Config


class LogManager:

    def __init__(
        self,
        logger: logging.Logger | None = None,
        log_level: int | None = None,
        file_path: str | None = None,
        indent: int | None = None
    ) -> None:

        self._logger = logger if logger is not None else self._create_logger(log_level, file_path)
        self._current_indent_level = 0
        self._indent = indent if indent is not None else 3
    
    def info(self, message: str) -> None:
        self._log(logging.INFO, message)

    def debug(self, message: str) -> None:
        self._log(logging.DEBUG, message)
        
    def error(self, message: str) -> None:
        self._log(logging.ERROR, message)

    def step(self, description: str, level: int = logging.INFO) -> Callable:
        
        def decorator(func: Callable) -> Callable:

            def wrapper(*args, **kwargs):

                self._log(level, f">> {description}")
                self._current_indent_level += 1
                start_time = time.perf_counter()
                try:
                    result = func(*args, **kwargs)
                except Exception as e:
                    self._log(logging.ERROR, f"<<{description} falhou: {e}")
                    raise
                finally:
                    self._current_indent_level -= 1

                duration = time.perf_counter() - start_time
                self._log(level, f"<< {description} finalizado com sucesso em {duration:.3f} segundos")
                return result
            
            return wrapper
        
        return decorator

    def _log(self, level: int, message: str, indent: int | None = None) -> None:
        """Método interno que adiciona indentação antes de logar."""
        indent = indent if indent is not None else self._indent
        indent = " " * self._current_indent_level * indent
        self._logger.log(level, f"{indent}{message}")

    def _create_logger(self, log_level: int | None = None, file_path: str | None = None) -> logging.Logger:
        
        # Criação do logger
        log_level = log_level if log_level is not None else Config.LOG_LEVEL
        logger = logging.getLogger(__name__)
        logger.setLevel(log_level)

        # Formatação padrão
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        # Handler para arquivo
        if file_path is None:
            file_path = os.path.join(Config.LOG_DIR, f'{datetime.now().strftime("%d-%m-%Y_%H-%M")}.log')

        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        file_handler = logging.FileHandler(file_path, mode='w', encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)

        # Handler para console (terminal)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)

        # Adicionando os handlers ao logger
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        return logger
