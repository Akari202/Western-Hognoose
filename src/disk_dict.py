import atexit
import json
import logging
import os
from logging import debug, error, info, warning


class DiskDict(dict):
    def __init__(self, filename: str = "cache.json"):
        self.filename = filename
        self._dirty = False
        self._ensure_directory_exists()
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r") as f:
                    super().__init__(json.load(f))
                    debug(f"Using cached dict {filename}")
            except (json.JSONDecodeError, IOError):
                warning(f"Unable to decode {filename}, defauting to empty")
                super().__init__()
        else:
            super().__init__()

        atexit.register(self.save)

    def _ensure_directory_exists(self) -> None:
        dirname = os.path.dirname(self.filename)
        if dirname:
            os.makedirs(dirname, exist_ok=True)

    def save(self):
        def log_or_print(level: int, msg: str):
            logger = logging.getLogger()
            if logger.handlers:
                logger.log(level, msg)
            else:
                level_name = logging.getLevelName(level)
                print(f"{level_name}: {msg}")

        if not self._dirty:
            log_or_print(
                logging.INFO, f"Skipping write, no changes detected for {self.filename}"
            )
            return

        try:
            self._ensure_directory_exists()
            with open(self.filename, "w") as file:
                json.dump(self, file, indent=4)
            self._dirty = False
            log_or_print(logging.INFO, f"Successfully written {self.filename}")
        except IOError as e:
            log_or_print(logging.ERROR, f"Failed to write {self.filename}: {e}")

    def __setitem__(self, key, value):
        if key not in self or super().__getitem__(key) != value:
            super().__setitem__(key, value)
            self._dirty = True

    def __delitem__(self, key):
        super().__delitem__(key)
        self._dirty = True

    def update(self, *args, **kwargs):
        temp = dict(*args, **kwargs)
        for k, v in temp.items():
            self[k] = v

    def pop(self, key, default=None):
        if key in self:
            self._dirty = True
        return super().pop(key, default)

    def popitem(self):
        if self:
            self._dirty = True
        return super().popitem()

    def clear(self):
        if self:
            super().clear()
            self._dirty = True
