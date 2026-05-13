from abc import ABC, abstractmethod
from typing import Generic, TypeVar

CommonStorageType = TypeVar("CommonStorageType")


class StorageInterface(ABC, Generic[CommonStorageType]):
    @abstractmethod
    def create(self, new_value: CommonStorageType) -> int:
        """Create a new entry in the storage and return the key."""

    @abstractmethod
    def read(self, key: int) -> CommonStorageType:
        """Read the value associated with the given key."""

    @abstractmethod
    def update(self, key: int, new_value: CommonStorageType):
        """Update the value associated with the given key."""

    @abstractmethod
    def delete(self, key: int):
        """Delete the entry associated with the given key."""

    @abstractmethod
    def clear(self):
        """Clear all entries in the storage."""

    @abstractmethod
    def all(self) -> dict[int, CommonStorageType]:
        """Return all entries in the storage."""


class Storage(StorageInterface, Generic[CommonStorageType]):
    def __init__(self):
        self._storage = {}
        self._last_index = -1

    def create(self, new_value: CommonStorageType):
        self._last_index += 1
        self._storage[self._last_index] = new_value
        return self._last_index

    def read(self, key: int) -> CommonStorageType:
        return self._storage[key]

    def update(self, key: int, new_value: CommonStorageType):
        self._storage[key] = new_value

    def delete(self, key: int):
        if key in self._storage:
            self._storage.pop(key)
        else:
            raise KeyError(f"Key {key} not found")

    def clear(self):
        self._storage = {}

    def all(self) -> dict[int, CommonStorageType]:
        return self._storage
