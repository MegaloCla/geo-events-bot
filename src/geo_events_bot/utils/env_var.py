import os
import sys

from geo_events_bot.utils.logger import Logger

logger = Logger(__name__).get_logger()


def get_env_variable(name: str) -> str:
    value = os.getenv(name)
    if not value:
        logger.error(f"Error: The environment variable '{name}' is not set or is empty")  # noqa: G004
        sys.exit(1)
    return value
