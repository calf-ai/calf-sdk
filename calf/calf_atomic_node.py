from abc import ABC
import itertools
from typing import Callable, Optional

from faststream import FastStream
from typing import Self
from calf.runtime import CalfRuntime

class CalfAtomicNode(ABC):
    
    _counter = itertools.count()
                
    def __init__(
        self,
        name: Optional[str] = None,
    ):   
        if not CalfRuntime.initialized:
            raise RuntimeError("Calf runtime not initialized. Run `initialize()`")
             
        if name:
            self.name = name
        else:
            self.name = "calf-node-" + str(next(self._counter))
        
        self.runtime = CalfRuntime
    
    async def run_node(self):
        await self.runnable.run()
        
    @property
    def runnable(self) -> FastStream:
        return self.runtime.runnable
    
    @property
    def calf(self):
        return self.runtime.calf
        

def on(*topics: str, pattern: Optional[str] = None, **subscriber_kwargs) -> Callable:
    """Thin decorator wrapper over FastStream subscription registration.
    
    Args:
        topics: Topics to subscribe to.
        **subscriber_kwargs: Passed directly to `KafkaBroker.subscriber()`.
            See FastStream docs for available options.
    """
    subscriber_kwargs = subscriber_kwargs.copy()
    if pattern:
        subscriber_kwargs['pattern'] = pattern
    
    return CalfRuntime.calf.subscriber(*topics, pattern=pattern, **subscriber_kwargs)

def post_to(topic: str, **publisher_kwargs):
        """Thin decorator wrapper over FastStream publisher registration.
        
        Args:
            topic: Topic to publish to.
            **publisher_kwargs: Passed directly to `KafkaBroker.publisher()`.
                See FastStream docs for available options.
        """
        return CalfRuntime.calf.publisher(topic, **publisher_kwargs)