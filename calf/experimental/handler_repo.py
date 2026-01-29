from collections.abc import Awaitable, Callable


class HandlerRepo:
    """A collection of instance-based decorators
    For example:
        ```
        class BaseAgent:
            def __init__(self, name):
                self.obj = obj()
                self.name = name

            @abstractmethod
            async def handler(self):
                pass

            def _start(self):
                handler = self.obj.on_enter_(f"{self.name}.on_enter")(self.handler)
                self.obj.post_to_(f"{self.name}.post_to")(handler)

            def get_obj(self):
                return self.obj

            def run_app(self):
            # use this method to deploy this agent, as a singly deployable unit
                agent._start()

                runner = NodeRunner(agent.get_obj())

                broker = KafkaBroker()

                runner.register_on(broker)

                await broker.run_app()


        class Agent(BaseAgent):
            async def handler(self):
                pass

        agent = Agent()
        agent.start()

        runner = NodeRunner(agent.get_obj())

        broker = KafkaBroker()

        runner.register_on(broker)

        broker.run_app()




        a = obj()
        @a.decorate
        def handler():
            pass


        registrator = Registrator(a)

        broker = KafkaBroker()
        registrator.register_on(broker)
        ```
    """

    def __init__(
        self,
    ):
        self._on_enter_handler = None
        self._post_to_handler = None
        self._on_enter_topic = None
        self._post_to_topic = None

    def on_enter_(self, topic: str):
        self._on_enter_topic = topic

        def decorator(handler: Callable | Callable[..., Awaitable]):
            self._on_enter_handler = handler
            return handler

        return decorator

    def post_to_(self, topic: str):
        self._post_to_topic = topic

        def decorator(handler: Callable | Callable[..., Awaitable]):
            self._post_to_handler = handler
            return handler

        return decorator

    @property
    def subscribed_to(self):
        return self._on_enter_topic

    @property
    def publishing_to(self):
        return self._post_to_topic


if __name__ == "__main__":
    pass
