import logging


class Logger:
    def __init__(self, name=None, level=logging.INFO):
        """Initialize the logger with the given name and level."""
        if name is None:
            name = __name__

        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)

        # Create formatter and add it to handlers
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        console_handler.setFormatter(formatter)

        self.logger.addHandler(console_handler)

    def get_logger(self) -> logging.Logger:
        """Return the configured logger."""
        return self.logger
