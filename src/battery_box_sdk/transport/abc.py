"""Abstract transport interface."""

from abc import ABC, abstractmethod


class Transport(ABC):
    @abstractmethod
    def send_command(self, command: bytes) -> bytes:
        """Send a command packet and return the response payload bytes."""
        ...

    @abstractmethod
    def close(self) -> None:
        ...

    def __enter__(self) -> "Transport":
        return self

    def __exit__(self, *args: object) -> None:
        self.close()
