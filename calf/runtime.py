from abc import ABC
from collections.abc import Iterable

from boltons.typeutils import classproperty
from faststream import FastStream

from calf.broker.broker import Broker


class CalfRuntime(ABC):
    _calf: Broker | None = None
    _initialized = False

    @classmethod
    def initialize(cls, bootstrap_servers: str | Iterable[str] | None = None, **broker_kwargs):
        if cls._initialized:
            raise RuntimeError("Calf runtime already initialized")
        cls._calf = Broker(bootstrap_servers, **broker_kwargs)
        cls._initialized = True

    @classproperty
    def initialized(cls):  # noqa: N805
        return cls._initialized

    @classproperty
    def calf(cls) -> Broker:  # noqa: N805
        if not cls._calf:
            raise RuntimeError("Calf runtime not initialized. Run `initialize()`")
        return cls._calf

    @classproperty
    def runnable(cls):  # noqa: N805
        return FastStream(CalfRuntime.calf)

    @classproperty
    def start(cls):  # noqa: N805
        return cls.runnable.run()
