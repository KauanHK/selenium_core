import logging
import os
from datetime import datetime
import time
from .config import Config
from typing import Callable, Self


class LogConfig:

    def __init__(
        self,
        logger: logging.Logger | None = None,
        log_level: int = logging.INFO,
        file_path: str | None = ...,
        stream_handler: logging.StreamHandler | None = ...,
        file_handler: logging.FileHandler | None = ...,
        formatter: logging.Formatter | None = ...,
        indent: int = 2,
    ) -> None:
        
        self.logger = logger
        self.file_path = file_path
        self.log_level = log_level
        self.stream_handler = stream_handler
        self.file_handler = file_handler
        self.formatter = formatter
        self.indent = indent


class LogManager:

    def __init__(
        self,
        logger: logging.Logger | None = None,
        log_level: int = logging.INFO,
        file_path: str | None = ...,
        stream_handler: logging.StreamHandler | None = ...,
        file_handler: logging.FileHandler | None = ...,
        formatter: logging.Formatter | None = ...,
        indent: int = 2,
    ) -> None:

        self._logger = logger if logger is not None else self._create_logger(log_level, file_path, stream_handler, file_handler, formatter)
        self._current_indent_level = 0
        self._indent = indent
        self._is_active = True
    
    @classmethod
    def from_config(cls, log_config: LogConfig | None = ...) -> Self:
        config = log_config if log_config is not None else LogConfig()
        log_manager = cls(
            logger = config.logger,
            log_level = config.log_level,
            file_path = config.file_path,
            stream_handler = config.stream_handler,
            file_handler = config.file_handler,
            formatter = config.formatter,
            indent = config.indent
        )
        if log_config is None:
            log_manager.deactivate()
        return log_manager
    
    def is_active(self) -> bool:
        return self._is_active
    
    def activate(self) -> None:
        self._is_active = True

    def deactivate(self) -> None:
        self._is_active = False

    def debug(self, message: str) -> None:
        self._log(logging.DEBUG, message)
    
    def info(self, message: str) -> None:
        self._log(logging.INFO, message)
        
    def warning(self, message: str) -> None:
        self._log(logging.WARNING, message)
    
    def error(self, message: str) -> None:
        self._log(logging.ERROR, message)
    
    def critical(self, message: str) -> None:
        self._log(logging.CRITICAL, message)

    def step(self, description: str, level: int = logging.INFO) -> Callable:
        
        def decorator(func: Callable) -> Callable:

            def wrapper(*args, **kwargs):

                self._log(level, f">> {description}")
                self._current_indent_level += 1
                start_time = time.perf_counter()
                try:
                    result = func(*args, **kwargs)
                except Exception as e:
                    self._current_indent_level -= 1
                    self._log(logging.ERROR, f"<< {description} falhou: {e}")
                    raise
                
                self._current_indent_level -= 1

                duration = time.perf_counter() - start_time
                self._log(level, f"<< {description} finalizado com sucesso em {duration:.3f} segundos")
                return result
            
            return wrapper
        
        return decorator

    def _log(self, level: int, message: str, indent: int | None = None) -> None:
        """Método interno que adiciona indentação antes de logar."""
        if not self.is_active():
            return
        indent = indent if indent is not None else self._indent
        indent = " " * self._current_indent_level * indent
        self._logger.log(level, f"{indent}{message}")

    def _create_logger(
        self,
        log_level: int | None = ...,
        file_path: str | None = None,
        stream_handler: logging.StreamHandler | None = ...,
        file_handler: logging.FileHandler | None = ...,
        formatter: logging.Formatter | None = ...
    ) -> logging.Logger:
        
        # Criação do logger
        log_level = log_level if log_level is not None else Config.LOG_LEVEL
        logger = logging.getLogger(__name__)
        logger.setLevel(log_level)

        if formatter is ...:
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        if file_handler is ...:
            file_path = file_path if file_path is not None else os.path.join(Config.LOG_DIR, f'{datetime.now().strftime("%d-%m-%Y_%H-%M")}.log')
            dirname = os.path.dirname(file_path)
            if dirname:
                os.makedirs(dirname, exist_ok=True)

            file_handler = logging.FileHandler(file_path, mode='w', encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)

        if stream_handler is ...:
            stream_handler = logging.StreamHandler()
            stream_handler.setLevel(log_level)
            stream_handler.setFormatter(formatter)

        # Adicionando os handlers ao logger
        if file_handler:
            logger.addHandler(file_handler)
        if stream_handler:
            logger.addHandler(stream_handler)

        return logger
