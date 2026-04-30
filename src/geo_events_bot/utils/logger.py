import logging


class Logger:
    def __init__(self, name=None, level=logging.INFO):
        if name is None:
            name = __name__

        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        if not self.logger.handlers:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(level)

            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            console_handler.setFormatter(formatter)

            self.logger.addHandler(console_handler)

    def get_logger(self) -> logging.Logger:
        return self.logger
