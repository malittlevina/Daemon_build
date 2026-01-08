from abc import ABC, abstractmethod

class Module(ABC):
    def __init__(self, kernel):
        self.kernel = kernel

    @abstractmethod
    def initialize(self):
        """Called during kernel initialization."""
        pass

    @abstractmethod
    def start(self):
        """Called when kernel starts services."""
        pass

    @abstractmethod
    def stop(self):
        """Called when kernel shuts down."""
        pass

    def on_event(self, event_type, data):
        """Optional event handler."""
        pass
