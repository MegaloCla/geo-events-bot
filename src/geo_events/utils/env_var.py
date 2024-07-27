import os
import sys

from geo_events.utils.logger import Logger

logger = Logger(__name__).get_logger()


def get_env_variable(name: str) -> str:
    value = os.getenv(name)
    if (
        not value
    ):  # Questo controllerà sia se il valore è None che se è una stringa vuota
        logger.error(f"Error: The environment variable '{name}' is not set or is empty")  # noqa: G004
        sys.exit(
            1
        )  # Termina il programma con un codice di uscita 1 per indicare un errore
    return value
