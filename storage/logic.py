class Storage:
    def __init__(self):
        self._storage = {}

    def create(self, key, value):
        self._storage[key] = value

    def read(self, key):
        return self._storage.get(key)

    def update(self, key, value):
        if key in self._storage:
            self._storage[key] = value
        else:
            raise KeyError(f"Key {key} not found")

    def delete(self, key):
        if key in self._storage:
            self._storage.pop(key)
        else:
            raise KeyError(f"Key {key} not found")
