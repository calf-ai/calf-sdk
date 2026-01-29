from abc import ABC, abstractmethod
from typing import Any

from calf.experimental.handler_repo import HandlerRepo


class BaseNode2(ABC):
    def __init__(self, name):
        self.handler_repo = HandlerRepo()
        self.name = name
        self._save_handlers()

    @abstractmethod
    async def handler(self, *args: Any, **kwargs: Any) -> Any:
        pass

    def _save_handlers(self):
        handler = self.handler_repo.on_enter_(f"{self.name}.on_enter")(self.handler)
        self.handler_repo.post_to_(f"{self.name}.post_to")(handler)

    def get_handler_repo(self) -> HandlerRepo:
        return self.handler_repo
