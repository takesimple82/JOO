from abc import ABC, abstractmethod

from ExecutionEngine.models import ExecutionLog


class ExecutionLogger(ABC):
    @abstractmethod
    def record(self, entry: ExecutionLog) -> None:
        raise NotImplementedError


class MemoryExecutionLogger(ExecutionLogger):
    def __init__(self) -> None:
        self._entries: list[ExecutionLog] = []

    def record(self, entry: ExecutionLog) -> None:
        if not isinstance(entry, ExecutionLog):
            raise TypeError("entry must be ExecutionLog")
        self._entries.append(entry)

    def entries(self) -> tuple[ExecutionLog, ...]:
        return tuple(self._entries)
