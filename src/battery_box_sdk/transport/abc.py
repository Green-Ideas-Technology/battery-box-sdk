"""Abstract transport interface."""

from abc import ABC, abstractmethod


class Transport(ABC):
    @abstractmethod
    def exchange(self, command: int, data: bytes, expected_response: int) -> bytes:
        """Send a command packet, await the response, and return the response payload.

        Raises BatteryBoxError (or a subclass) on any communication failure.
        """
        ...

    @abstractmethod
    def close(self) -> None: ...

    def __enter__(self) -> "Transport":
        return self

    def __exit__(self, *args: object) -> None:
        self.close()
