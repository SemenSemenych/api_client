import pytest

from storage.logic import Storage

UNEXISTENT_KEY = 999


def test_storage_create():
    storage = Storage()
    key1 = storage.create("value1")
    key2 = storage.create("value2")

    assert key1 == 0
    assert key2 == 1
    assert storage.read(key1) == "value1"
    assert storage.read(key2) == "value2"


def test_storage_read_nonexistent():
    storage = Storage()
    with pytest.raises(KeyError):
        storage.read(UNEXISTENT_KEY)


def test_storage_update():
    storage = Storage()
    key = storage.create("initial")
    storage.update(key, "updated")
    assert storage.read(key) == "updated"


def test_storage_delete():
    storage = Storage()
    key = storage.create("to delete")
    storage.delete(key)
    with pytest.raises(KeyError):
        storage.read(key)


def test_storage_delete_nonexistent():
    storage = Storage()
    with pytest.raises(KeyError) as excinfo:
        storage.delete(UNEXISTENT_KEY)
    assert "Key 999 not found" in str(excinfo.value)


def test_storage_clear():
    storage = Storage()
    storage.create("v1")
    storage.create("v2")
    storage.clear()
    assert len(storage._storage) == 0
    with pytest.raises(KeyError):
        storage.read(0)


def test_storage_all():
    storage = Storage()
    storage.create("value1")
    storage.create("value2")

    all_data = storage.all()
    assert all_data == {0: "value1", 1: "value2"}
    assert len(all_data) == 2
