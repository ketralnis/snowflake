from threading import RLock


class LockBox(object):
    "Simple abstraction for mutable value locked by a recursive Lock"

    def __init__(self, value):
        self.lock = RLock()
        self.box = value

    def set(self, value):
        """
        Safely set the box to a new value.

        Useful for immutable value types
        """
        # we're recursive so this should work if we already hold it
        with self as old_value:
            self.box = value
            return old_value

    def get(self):
        """
        Safely get the current value

        This is only useful for immutable value types
        """
        with self as value:
            return value

    def cas(self, before, after, compare=lambda x, y: x is y):
        with self as current:
            if compare(before, current):
                self.box = after
                return True
            return False

    def __enter__(self):
        self.lock.__enter__()
        return self.box

    def __exit__(self, *a):
        self.lock.__exit__(*a)