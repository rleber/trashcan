"""
Trash:
A reversible Trash object

Trash works like the trash can in the operating system: Files moved to Trash
(using Trash#trash()) disappear from the filesystem, but they can be gotten back.

This __does not__ persist after the script ends: any files not restored by
then are permanently deleted. This behavior can be avoided by running 
Trash#restore_trash() before the program ends
"""

from datetime import datetime
from pathlib import Path
import shutil
import tempfile


class Trash:
    def __init__(self):
        """ Initialize a Trash object """
        # Create a secure temporary directory that manages its own cleanup
        self.trash_dir = tempfile.TemporaryDirectory()
        # Track original locations { temporary_path: original_path }
        self.history = {}

    def trash(self, file, verbose=False):
        """Move a file or folder to the trash """
        file_path = Path(file).resolve()
        if not file_path.exists():
            raise FileNotFoundError(f"{file_path} does not exist.")

        # Generate a unique path inside the temporary trash directory
        timestamp = datetime.now().now().strftime("%Y-%m-%d___%H-%M-%S-%f")
        suffixes = file_path.suffixes
        all_suffixes = "".join(suffixes)
        file_stem = file_path.name.removesuffix(all_suffixes)
        trashed_file_name = file_stem + timestamp + all_suffixes
        trashed_file_path = Path(self.trash_dir.name) / trashed_file_name

        # Log the transaction for potential rollback
        self.history[str(file_path)] = trashed_file_path

        # Move the file/directory to the temporary location
        shutil.move(str(file_path), str(trashed_file_path))

        if verbose:
            print(f"Moved to trash: {file_path.name}")

    def restore(self, file, verbose=False):
        """ Restore a file or folder from the trash """
        if temp_path := self.history.get(file):
            original_path = Path(file)
            if temp_path.exists():
                # Ensure the parent directory still exists
                original_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(temp_path), str(original_path))
                del self.history[file]
                if verbose:
                    print(f"Restored: {original_path}")
            else:
                raise FileNotFoundError(
                    f"Trashed file for {file} ({temp_path}) is missing."
                )
        else:
            raise ValueError(f"File {file} was not placed in the trash.")

    def restore_all(self, verbose=False):
        """ Restore all the files in the trash """
        for trashed_file in self.history:
            self.restore(trashed_file, verbose=verbose)

    def permanently_delete(self, file, verbose=False, strict=True):
        """ Permanently delete a file from the trash """
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

    def permanently_delete_all(self, verbose=False, strict=True):
        """ Permanently delete all the files in the trash """
        for trashed_file in self.history:
            self.permanently_delete(trashed_file, verbose=verbose, strict=strict)
        self.purge()
        if verbose:
            print("All trash contents permanently deleted.")

    def purge(self, verbose=False):
        """ 
        Clean out the trash
        Be careful: This results in the permanent deletion of all files in the trash
        """
        self.trash_dir.cleanup()
        self.history.clear()
        if verbose:
            print("Trash purged.")

    # TODO Ask the user for verification?
    def empty_trash(self, verbose=False, strict=True):
        """ Synonym: Empty the trash can """
        self.permanently_delete_all(verbose=False, strict=strict)
        if verbose:
            print("Trash has been emptied.")

    def restore_trash(self, verbose=False):
        self.restore_all(verbose=False)
        self.purge()
        if verbose:
            print("All files in trash restored.")
