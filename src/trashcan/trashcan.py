"""
Trash:
A reversible Trash object

Trash works like the trash can in the operating system: Files moved to Trash
(using Trash#trash()) disappear from the filesystem, but they can be gotten back.

This __does not__ persist after the script ends: any files not restored by
then are permanently deleted. This behavior can be avoided by running
Trash#restore_trash() before the program ends
"""

import shutil
import tempfile
from datetime import UTC, datetime
from pathlib import Path


class Trash:
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

    def trash_path(self, file):
        """
        Generate a unique path inside the temporary trash directory
        """
        file_path = Path(file).resolve()
        timestamp = datetime.now(UTC).strftime("%Y-%m-%d___%H-%M-%S-%f")
        suffixes = file_path.suffixes
        all_suffixes = "".join(suffixes)
        file_stem = file_path.name.removesuffix(all_suffixes)
        trashed_file_name = file_stem + "___trashed_at___" + timestamp + all_suffixes
        return Path(self.trash_dir.name) / trashed_file_name

    def trash(self, file, verbose=None, debug=None):
        """
        Move a file or folder to the trash
        (delete it, but so that it can be restored later)
        """
        if verbose is None:
            verbose = self.verbose
        if debug is None:
            debug = self.debug

        file_path = Path(file).resolve()
        if not file_path.exists():
            raise FileNotFoundError(f"{file_path} does not exist.")
        trashed_file_path = self.trash_path(file_path)
        trashed_file_path_name = str(trashed_file_path)
        file_to_trash_name = str(file_path)

        # Log the transaction for potential rollback
        self._history[file_to_trash_name] = trashed_file_path
        if debug:
            print(f"In trash(). file stored to history. self._history: {self._history}")

        # Move the file/directory to the temporary location
        if debug:
            print(
                f"In trash(). Moving {file_to_trash_name} to {trashed_file_path_name}"
            )
        shutil.move(file_to_trash_name, trashed_file_path_name)

        if verbose:
            print(f"Moved to trash: {file_path.name}")

    def restore(self, file, verbose=None, debug=None):
        """
        Restore a file or folder from the trash
        """
        if verbose is None:
            verbose = self.verbose
        if debug is None:
            debug = self.debug

        file_path = Path(file).resolve()
        file_path_name = str(file_path)
        if debug:
            print(f"In restore().            file_path_name: {file_path_name!r}")
            print(
                f"In restore(). first key in history: {list(self._history.keys())[0]!r}"
            )
            print(f"In restore().  self._history: {self._history}")
            print(
                f"In restore().  self._history.get(file_path): {self._history.get(file_path_name)}"
            )
            print(
                f"In restore(). file path found?: {file_path_name == list(self._history.keys())[0]}"
            )

        if temp_path := self._history.get(file_path_name):
            original_path = file_path
            if temp_path.exists():
                # Ensure the parent directory still exists
                original_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(temp_path), str(original_path))
                del self.history[file_path_name]
                if verbose:
                    print(f"Restored: {original_path}")
            else:
                raise FileNotFoundError(
                    f"Trashed file for {file} ({temp_path}) is missing."
                )
        else:
            raise ValueError(f"File {file} was not placed in the trash.")

    def restore_all(self, verbose=None, debug=None):
        """
        Restore all the files and folders in the trash
        """
        if verbose is None:
            verbose = self.verbose
        if debug is None:
            debug = self.debug

        for trashed_file in self.history:
            self.restore(trashed_file, verbose=verbose)

    def permanently_delete(self, file, verbose=None, debug=None, strict=True):
        """
        Permanently delete a file or folder from the trash
        """
        if verbose is None:
            verbose = self.verbose
        if debug is None:
            debug = self.debug

        if temp_path := self.history.get(file):
            if temp_path.exists():
                temp_path.unlink()
                del self.history[file]
                if verbose:
                    print(f"Permanently deleted: {file}")
            else:
                if strict:
                    raise FileNotFoundError(
                        f"Trashed file for {file} ({temp_path}) is missing."
                    )
                if Path(file).exists():
                    Path(file).unlink()
                    if verbose:
                        print(
                            f"Permanently deleted {file}. It was missing from the trash"
                        )
                else:
                    if verbose:
                        print(
                            f"Did not permanently delete {file}, but it is gone. (It was missing from the trash.)"
                        )
        else:
            if Path(file).exists():
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
            if strict:
                raise ValueError(f"File {file} was not placed in the trash.")
            elif verbose:
                print(
                    f"Did not permanently delete {file}, but it may be gone since it was never put in the trash."
                )

    def permanently_delete_all(self, verbose=None, debug=None, strict=True):
        """
        Permanently delete all the files and folders in the trash
        """
        if verbose is None:
            verbose = self.verbose
        if debug is None:
            debug = self.debug

        for trashed_file in self.history:
            self.permanently_delete(trashed_file, verbose=verbose, strict=strict)
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

    # TODO Ask the user for verification?
    def empty_trash(self, verbose=None, debug=None, strict=True):
        """
        Synonym: Empty the trash can
        """
        if verbose is None:
            verbose = self.verbose
        if debug is None:
            debug = self.debug

        self.permanently_delete_all(verbose=False, strict=strict)
        if verbose:
            print("Trash has been emptied.")

    def restore_trash(self, verbose=None, debug=None):
        """
        Synonym: Restore everything in the trash can
        """
        if verbose is None:
            verbose = self.verbose
        if debug is None:
            debug = self.debug

        self.restore_all(verbose=verbose)
        self.purge()
        if verbose:
            print("All files in trash restored.")
