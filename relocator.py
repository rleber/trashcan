import logging
from pathlib import Path
import shutil
from trash import Trash

class Relocator:
    def __init__(self, from_path: str | Path, to_path: str | Path):
        self._from_path = Path(from_path)
        self._to_path = Path(to_path)
        self._actions = []
        self._trash = Trash()

    @property
    def from_path(self):
        return self._from_path

    @property
    def to_path(self):
        return self._to_path

    @property
    def actions(self):
        return self._actions

    @property
    def trash(self):
        return self._trash

    def relocate(self, from_path: str | Path, to_path: str| Path, force=True) -> bool:
        from_path = Path(from_path).resolve()
        to_path = Path(to_path).resolve()
        trashed = False

        if not from_path.exists():
            raise FileNotFoundError(f"File {from_path} does not exist")
        
        if to_path.exists():
            if not force:
                raise FileExistsError(f"File {to_path} already exists")
            self.trash.trash(to_path, verbose=True) # Reverse by restoring file
            trashed = True

        to_dir = to_path.parent

        # TODO logging
        # TODO what if only part of this works? We should back out if we can
        to_dir.mkdir(parents=True, exist_ok=True) # Reverse by removing the 
        shutil.move(from_path, to_path) # Reverse by moving it back again
        from_path.symlink_to(to_path) # Reverse by deleting the symlink
        # Undo the initial move (created by --force), if any
        if trashed:
            self.trash.permanently_delete(to_path)
        logging.info({"action": "relocate", "from": str(from_path), "to": str(to_path)})
        return True

    def undo(self) -> bool:
        return False

    @classmethod
    def go(cls, from_path: str | Path, to_path: str | Path) -> bool:
        engine = cls(from_path, to_path)
        return engine.relocate(from_path, to_path)
  
