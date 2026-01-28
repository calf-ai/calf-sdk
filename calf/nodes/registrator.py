from abc import ABC, abstractmethod
from typing import Any

from calf.broker.broker import Broker


class Registrator(ABC):
    @abstractmethod
    def register_on(self, broker: Broker, *args: Any, **kwargs: Any):
        """Function to fluently register a node's handlers onto a broker to serve traffic"""
        pass
