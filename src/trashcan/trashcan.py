#!/usr/bin/env python3
"""
Trash:
A reversible Trash object

Trash works like the trash can in the operating system: Files moved to Trash
(using Trash#trash()) disappear from the filesystem, but they can be gotten back.

This __does not__ persist after the script ends: any files not restored by
then are permanently deleted. This behavior can be avoided by running
Trash#restore_trash() before the program ends
"""

# TODO remove debugging code
# TODO remove verbose mode
# TODO remove non-strict mode

import shutil
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import NamedTuple


class Trash:
    class TrashElement(NamedTuple):
        key: str
        file: Path
        absolute_file: Path
        time: datetime
        cache: Path

    def __init__(self, verbose=False, debug=False):
        """Initialize a Trash object"""
        # Create a secure temporary directory that manages its own cleanup
        self.trash_dir = tempfile.TemporaryDirectory()
        # Track original locations { temporary_path: original_path }
        self._verbose = verbose
        self._debug = debug
        self._history = {}

    @property
    def verbose(self):
        return self._verbose

    @property
    def debug(self):
        return self._debug

    @property
    def history(self):
        return self._history

    def contents(self, absolute=False):
        content_list = []
        for element in self._history.values():
            if absolute:
                path = element.absolute_file
            else:
                path = element.file
            content_list.append(str(path))
        return content_list

    @staticmethod
    def absolute_path_for(file):
        return Path(file).expanduser().resolve()

    @staticmethod
    def trash_key_for(file):
        return str(Trash.absolute_path_for(file))

    def trash_element_for(self, file: str | Path):
        """
        Generate a unique TrashElement for a file
        """
        file_path = Path(file)
        time = datetime.now(UTC)

        suffixes = file_path.suffixes
        all_suffixes = "".join(suffixes)
        file_stem = file_path.name.removesuffix(all_suffixes)
        timestamp = time.strftime("%Y-%m-%d___%H-%M-%S-%f")
        cache_file_name = file_stem + "___trashed_at___" + timestamp + all_suffixes
        cache = Path(self.trash_dir.name) / cache_file_name
        trash_key = self.trash_key_for(file)
        trash_element = self.TrashElement(
            key=trash_key,
            file=str(file_path),
            absolute_file=self.absolute_path_for(file),
            time=time,
            cache=cache,
        )
        return trash_element

    def trash(self, file, verbose=None, debug=None):
        """
        Move a file or folder to the trash
        (delete it, but so that it can be restored later)
        """
        if verbose is None:
            verbose = self.verbose
        if debug is None:
            debug = self.debug

        trash_element = self.trash_element_for(file)
        if not trash_element.absolute_file.exists():
            raise FileNotFoundError(
                f"Cannot trash {trash_element.absolute_file}. It does not exist."
            )

        if self._history.get(trash_element.key):
            # A file with this path has already been sent to the trash
            raise FileExistsError(
                f"Cannot trash {trash_element.absolute_file}. There is a file with the same path in the Trashcan already."
            )

        # Log the transaction for potential rollback
        self._history[trash_element.key] = trash_element
        if debug:
            print(f"In trash(). file stored to history. self._history: {self._history}")

        # Move the file/directory to the temporary location
        if debug:
            print(f"In trash(). Moving {trash_element.key} to {trash_element.cache}")
        shutil.move(trash_element.key, trash_element.cache)

        if verbose:
            print(f"Moved to trash: {trash_element.absolute_file}")

    def restore(self, file, verbose=None, debug=None):
        """
        Restore a file or folder from the trash
        """
        if verbose is None:
            verbose = self.verbose
        if debug is None:
            debug = self.debug

        file_path = self.absolute_path_for(file)
        file_path_name = str(file_path)
        if debug:
            print(f"In restore().       file_path_name: {file_path_name!r}")
            if len(self._history) > 0:
                print(
                    f"In restore(). first key in history: {next(iter(self._history.keys()))!r}"
                )
                print(f"In restore().  self._history: {self._history}")
                print(
                    f"In restore().  self._history.get(file_path): {self._history.get(file_path_name)}"
                )
                print(
                    f"In restore(). file path found?: {file_path_name == next(iter(self._history.keys()))}"
                )
            else:
                print("In restore(). history is empty")

        if element := self._history.get(file_path_name):
            if element.cache.exists():
                # Check to ensure that restoring the file isn't going to clobber another one
                if element.absolute_file.exists():
                    raise FileExistsError(
                        f"Can't restore {element.absolute_file}. That file already exists."
                    )
                # Ensure the parent directory still exists
                element.absolute_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(element.cache, element.absolute_file)
                del self.history[element.key]
                if verbose:
                    print(f"Restored: {element.absolute_file}")
            else:
                raise RuntimeError(  # This should not happen
                    f"Trashed file for {file} ({element.cache}) is missing."
                )
        else:
            raise FileNotFoundError(f"File {file} is not in the trash.")

    def restore_all(self, verbose=None, debug=None):
        """
        Restore all the files and folders in the trash
        """
        if verbose is None:
            verbose = self.verbose
        if debug is None:
            debug = self.debug

        for trashed_file in list(self.history.keys()).copy():
            self.restore(trashed_file, verbose=verbose)

    def permanently_delete(self, file, verbose=None, debug=None, strict=True):
        """
        Permanently delete a file or folder from the trash
        """
        if verbose is None:
            verbose = self.verbose
        if debug is None:
            debug = self.debug

        key = self.trash_key_for(file)
        if element := self.history.get(key):
            if element.cache.exists():
                element.cache.unlink()
                del self.history[key]
                if verbose:
                    print(f"Permanently deleted: {file}")
            else:
                if strict:
                    raise RuntimeError(  # This should not happen
                        f"Trashed file for {file} ({element.cache}) is missing."
                    )
                if Path(file).exists():
                    Path(file).unlink()
                    if verbose:
                        print(f"Permanently deleted {file}. It was not in the trash")
                else:
                    if verbose:
                        print(
                            f"Did not permanently delete {file}, but it is gone. (It was not in the trash.)"
                        )
        else:
            if strict:
                raise FileNotFoundError(f"File {file} was never placed in the trash.")
            elif Path(file).exists():
                Path(file).unlink()
                if verbose:
                    print(
                        f"Permanently deleted {file}, which was never sent to the trash"
                    )
            else:
                if verbose:
                    print(
                        f"Did not permanently delete {file}, but it is gone. (It was never sent to the trash.)"
                    )

    def permanently_delete_all(self, verbose=None, debug=None, strict=True):
        """
        Permanently delete all the files and folders in the trash
        """
        if verbose is None:
            verbose = self.verbose
        if debug is None:
            debug = self.debug

        for element in self.history.copy().values():
            self.permanently_delete(element.file, verbose=verbose, strict=strict)
        self.purge()
        if verbose:
            print("All trash contents permanently deleted.")

    def purge(self, verbose=None, debug=None):
        """
        Clean out the trash
        Be careful: This results in the permanent deletion of all files
        and folders in the trash
        """
        if verbose is None:
            verbose = self.verbose
        if debug is None:
            debug = self.debug

        self.trash_dir.cleanup()
        self.history.clear()
        if verbose:
            print("Trash purged.")
