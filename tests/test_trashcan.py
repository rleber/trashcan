import shutil
import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parent.parent / "src" / "trashcan"))


from trashcan import Trash


@pytest.fixture(autouse=True)
def set_up_and_tear_down_data_directory():
    parent_dir = Path(__file__).parent
    # Create the tests/data directory
    data_path = parent_dir / "data"
    data_path.mkdir(parents=True)
    yield
    # Delete the tests/data directory
    shutil.rmtree(data_path)


def readfile(path: str) -> list[str]:
    with open(path, "r") as file:
        lines = file.read().splitlines()
    return lines


def test_trash_and_restore_file():
    # Create trashcan
    can = Trash(verbose=True, debug=True)

    test_data_file = "tests/data/foo.txt"

    # Create a file
    with open(test_data_file, "w") as file:
        file.write("bar\n")
    assert Path(test_data_file).exists()
    assert readfile(test_data_file) == ["bar"]

    # Temporarily delete the file
    can.trash(test_data_file)  # Delete a file
    assert not Path(test_data_file).exists()

    # Restore the deleted file
    can.restore(test_data_file)
    assert Path(test_data_file).exists()

    # Read it back to ensure it's intact
    assert readfile(test_data_file) == ["bar"]


# def test_trash_and_restore_folder():

# def test_trash_and_restore_file_in_subfolder():

# def test_restore_all():

# def test_permanently_delete():

# def test_permanently_delete_all():

# def test_purge():

# def test_empty_trash():

# def test_restore_trash():

# def test_deletions_are_permanent_after_program_exits():

# def test_restored_files_remain_after_program_exits():

# def test_error_missing_file():

# def test_error_restore_file_not_trashed():

# def test_error_restore_file_trashcan_missing():

# def test_error_restore_collision():

# def test_errors_trash_collision():
