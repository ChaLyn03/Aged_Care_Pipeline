# interfaces/base_scheduler.py

from abc import ABC, abstractmethod

class BaseScheduler(ABC):
    @abstractmethod
    def start(self) -> None:
        """Boot the scheduler and begin firing jobs."""
        ...
