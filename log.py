import logging
import os
from config import Config


class _Logger:
    _instance = None

    @classmethod
    def get_logger(cls, log_level: int | None = None, file_path: str | None = None) -> logging.Logger:
        if cls._instance is not None:
            return cls._instance

        # Criação do logger
        log_level = log_level if log_level is not None else Config.LOG_LEVEL
        cls._instance = logging.getLogger(__name__)
        cls._instance.setLevel(log_level)

        # Formatação padrão
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        # Handler para arquivo
        file_path = file_path if file_path is not None else Config.LOG_FILE_PATH

        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        file_handler = logging.FileHandler(file_path, mode='w', encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)

        # Handler para console (terminal)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)

        # Adicionando os handlers ao logger
        cls._instance.addHandler(file_handler)
        cls._instance.addHandler(console_handler)

        return cls._instance



def get_logger(log_level: int = logging.INFO, file_path: str | None = None) -> logging.Logger:
    return _Logger.get_logger(log_level, file_path)
