import logging

import hydra
from omegaconf import DictConfig

from .errors import IncorrectLoggingLevelError


def get_logger() -> logging.Logger:
    format = "%(levelname).8s %(name).12s %(asctime)s %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"
    logging.basicConfig(level=set_level(), format=format, datefmt=datefmt)

    logger = logging.getLogger(__name__)
    return logger


@hydra.main(config_path="../conf", config_name="config", version_base=None)
def set_level(config: DictConfig):
    match config.log_level.lower():
        case "notset":
            return logging.NOTSET
        case "debug":
            return logging.DEBUG
        case "info":
            return logging.INFO
        case "warning":
            return logging.WARNING
        case "error":
            return logging.ERROR
        case "critical":
            return logging.CRITICAL
        case _:
            raise IncorrectLoggingLevelError("Logging level incorrect or not set")
