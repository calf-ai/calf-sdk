from abc import ABC, abstractmethod
from functools import cached_property
from typing import Callable


def subscribe_to(topic_name):
    def decorator(fn):
        fn._subscribe_to_topic_name = topic_name
        return fn

    return decorator


def publish_to(topic_name):
    def decorator(fn):
        fn._publish_to_topic_name = topic_name
        return fn

    return decorator


class BaseNode(ABC):
    _handler_registry: dict[Callable, dict[str, str]] = {}

    def __init__(self, *args, **kwargs):
        self.bound_registry = {
            fn.__get__(self): topics_dict for fn, topics_dict in self._handler_registry.items()
        }

    def __init_subclass__(cls):
        super().__init_subclass__()

        cls._handler_registry = {}

        for attr in cls.__dict__.values():
            publish_to_topic_name = getattr(attr, "_publish_to_topic_name", None)
            subscribe_to_topic_name = getattr(attr, "_subscribe_to_topic_name", None)
            if publish_to_topic_name:
                cls._handler_registry[attr] = {"publish_topic": publish_to_topic_name}
            if subscribe_to_topic_name:
                cls._handler_registry[attr] = cls._handler_registry.get(attr, {}) | {
                    "subscribe_topic": subscribe_to_topic_name
                }

    @cached_property
    def subscribed_topic(self) -> str | None:
        for topics_dict in self._handler_registry.values():
            if "subscribe_topic" in topics_dict:
                return topics_dict["subscribe_topic"]
        return None

    @cached_property
    def publish_to_topic(self) -> str | None:
        for topics_dict in self._handler_registry.values():
            if "publish_topic" in topics_dict:
                return topics_dict["publish_topic"]
        return None
