from abc import ABC, abstractmethod


class Observer(ABC):
    @abstractmethod
    def send_message(self, message: str):
        pass
