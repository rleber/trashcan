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


def makefile(file_path: str | Path, contents: list[str]) -> None:
    file_path = Path(file_path)
    with open(file_path, "w") as file:
        file.write("\n".join(contents))


def ensurefile(file_path: str | Path, contents: list[str]) -> None:
    file_path = Path(file_path)
    makefile(file_path, contents)
    assert file_path.exists()
    assert readfile(file_path) == contents


def readfile(path: str | Path) -> list[str]:
    with open(path, "r") as file:
        lines = file.read().splitlines()
    return lines


def dir_contents(dir: str | Path) -> list[Path]:
    directory_path = Path(dir)
    return sorted([file for file in directory_path.iterdir()])


def verify_dir_contents(
    dir: str | Path, files: list[str | Path], contents: list[list[str]]
) -> None:
    dir_path = Path(dir)
    if len(files) != len(contents):
        raise ValueError("There should be one list of contents for each file")
    dir_path = Path(dir)
    assert dir_path.exists()
    assert dir_contents(dir_path) == sorted(files)
    for file, content in zip(files, contents):
        assert file.exists()
        assert readfile(file) == content


def test_trash_and_restore_file():
    # Create trashcan
    can = Trash(verbose=True, debug=True)
    assert can.contents() == []

    # Create a file
    test_data_file = "tests/data/foo.txt"
    test_data_file_contents = ["bar"]
    ensurefile(test_data_file, test_data_file_contents)

    # Temporarily delete the file
    can.trash(test_data_file)  # Delete a file
    assert not Path(test_data_file).exists()
    assert can.contents() == [test_data_file]

    # Restore the deleted file
    can.restore(test_data_file)
    assert Path(test_data_file).exists()

    # Read it back to ensure it's intact
    assert readfile(test_data_file) == test_data_file_contents

    assert can.contents() == []


def test_trash_and_restore_path():
    # Create trashcan
    can = Trash(verbose=True, debug=True)
    assert can.contents() == []

    # Create a file
    test_data_file = "tests/data/foo.txt"
    test_data_path = Path(test_data_file)
    test_data_file_contents = ["bar"]
    ensurefile(test_data_file, test_data_file_contents)

    # Temporarily delete the file
    can.trash(test_data_path)  # Delete a file
    assert not test_data_path.exists()

    # Restore the deleted file
    can.restore(test_data_path)
    assert test_data_path.exists()

    # Read it back to ensure it's intact
    assert readfile(test_data_path) == test_data_file_contents

    assert can.contents() == []


def test_trash_and_restore_empty_folder():
    # Create trashcan
    can = Trash(verbose=True, debug=True)

    # Create a folder
    test_dir = Path("tests/data/dir_bar")
    test_dir.mkdir(parents=True)
    verify_dir_contents(test_dir, [], [])

    # Temporarily delete the folder
    can.trash(test_dir)  # Delete the folder
    assert not test_dir.exists()

    # Restore the deleted folder
    can.restore(test_dir)
    verify_dir_contents(test_dir, [], [])


def test_trash_and_restore_nonempty_folder():
    # Create trashcan
    can = Trash(verbose=True, debug=True)

    # Create a folder
    test_dir = Path("tests/data/dir_bar")
    test_dir.mkdir(parents=True)

    # Create files in the folder
    test_data_file1 = test_dir / "foo.xls"
    test_data_file1_contents = ["baz", "bat"]
    makefile(test_data_file1, test_data_file1_contents)

    test_data_file2 = test_dir / "bar.pdf"
    test_data_file2_contents = ["frodo", "sam", "elmo"]
    makefile(test_data_file2, test_data_file2_contents)

    verify_dir_contents(
        test_dir,
        [test_data_file1, test_data_file2],
        [test_data_file1_contents, test_data_file2_contents],
    )

    # Temporarily delete the folder
    can.trash(test_dir)  # Delete the folder
    assert not test_dir.exists()
    assert not test_data_file1.exists()
    assert not test_data_file2.exists()

    # Restore the deleted folder
    can.restore(test_dir)
    verify_dir_contents(
        test_dir,
        [test_data_file1, test_data_file2],
        [test_data_file1_contents, test_data_file2_contents],
    )


def test_trash_and_restore_file_in_subfolder():
    # Create trashcan
    can = Trash(verbose=True, debug=True)

    # Create a folder
    test_dir = Path("tests/data/dir_bar")
    test_dir.mkdir(parents=True)

    # Create files in the folder
    test_data_file1 = test_dir / "foo.xls"
    test_data_file1_contents = ["baz", "bat"]
    makefile(test_data_file1, test_data_file1_contents)

    test_data_file2 = test_dir / "bar.pdf"
    test_data_file2_contents = ["frodo", "sam", "elmo"]
    makefile(test_data_file2, test_data_file2_contents)

    verify_dir_contents(
        test_dir,
        [test_data_file1, test_data_file2],
        [test_data_file1_contents, test_data_file2_contents],
    )

    # Temporarily delete one of the files
    can.trash(test_data_file2)  # Delete the file
    verify_dir_contents(
        test_dir,
        [test_data_file1],
        [test_data_file1_contents],
    )

    assert test_dir.exists()
    assert test_data_file1.exists()
    assert readfile(test_data_file1) == test_data_file1_contents
    assert not test_data_file2.exists()
    assert dir_contents(test_dir) == [test_data_file1]

    # Restore the deleted file
    can.restore(test_data_file2)
    verify_dir_contents(
        test_dir,
        [test_data_file1, test_data_file2],
        [test_data_file1_contents, test_data_file2_contents],
    )


def test_restore_all():
    # Create trashcan
    can = Trash(verbose=True, debug=True)

    # Create a folder
    test_dir = Path("tests/data/dir_bar")
    test_dir.mkdir(parents=True)

    # Create files in the folder
    test_data_file1 = test_dir / "foo.xls"
    test_data_file1_contents = ["baz", "bat"]
    makefile(test_data_file1, test_data_file1_contents)

    test_data_file2 = test_dir / "bar.pdf"
    test_data_file2_contents = ["frodo", "sam", "elmo"]
    makefile(test_data_file2, test_data_file2_contents)

    test_data_file3 = test_dir / "oopsie.yaml"
    test_data_file3_contents = []
    makefile(test_data_file3, test_data_file3_contents)

    verify_dir_contents(
        test_dir,
        [test_data_file1, test_data_file2, test_data_file3],
        [test_data_file1_contents, test_data_file2_contents, test_data_file3_contents],
    )

    # Temporarily delete two of the files in the folder
    can.trash(test_data_file1)  # Delete a file
    can.trash(test_data_file3)  # Delete another file
    verify_dir_contents(
        test_dir,
        [test_data_file2],
        [test_data_file2_contents],
    )

    # Restore the deleted files
    can.restore_all()
    verify_dir_contents(
        test_dir,
        [test_data_file1, test_data_file2, test_data_file3],
        [test_data_file1_contents, test_data_file2_contents, test_data_file3_contents],
    )


def test_permanently_delete():
    # Create trashcan
    can = Trash(verbose=True, debug=True)
    assert can.contents() == []

    # Create a folder
    test_dir = Path("tests/data/dir_bar")
    test_dir.mkdir(parents=True)

    # Create files in the folder
    test_data_file1 = test_dir / "foo.xls"
    test_data_file1_contents = ["baz", "bat"]
    makefile(test_data_file1, test_data_file1_contents)

    test_data_file2 = test_dir / "bar.pdf"
    test_data_file2_contents = ["frodo", "sam", "elmo"]
    makefile(test_data_file2, test_data_file2_contents)

    test_data_file3 = test_dir / "oopsie.yaml"
    test_data_file3_contents = []
    makefile(test_data_file3, test_data_file3_contents)

    verify_dir_contents(
        test_dir,
        [test_data_file1, test_data_file2, test_data_file3],
        [test_data_file1_contents, test_data_file2_contents, test_data_file3_contents],
    )

    # Temporarily delete two of the files in the folder
    can.trash(test_data_file1)  # Delete a file
    can.trash(test_data_file3)  # Delete another file
    verify_dir_contents(
        test_dir,
        [test_data_file2],
        [test_data_file2_contents],
    )
    assert sorted(can.contents()) == sorted(
        [str(test_data_file1), str(test_data_file3)]
    )

    # Now permanently delete one of them
    can.permanently_delete(test_data_file1)  # Delete the file
    verify_dir_contents(
        test_dir,
        [test_data_file2],
        [test_data_file2_contents],
    )
    assert can.contents() == [str(test_data_file3)]

    # Attempt to restore the deleted files
    with pytest.raises(FileNotFoundError):
        can.restore(test_data_file1)

    # Restore the remaining file
    can.restore_all()
    verify_dir_contents(
        test_dir,
        [test_data_file2, test_data_file3],
        [test_data_file2_contents, test_data_file3_contents],
    )


def test_permanently_delete_all():
    # Create trashcan
    can = Trash(verbose=True, debug=True)
    assert can.contents() == []

    # Create a folder
    test_dir = Path("tests/data/dir_bar")
    test_dir.mkdir(parents=True)

    # Create files in the folder
    test_data_file1 = test_dir / "foo.xls"
    test_data_file1_contents = ["baz", "bat"]
    makefile(test_data_file1, test_data_file1_contents)

    test_data_file2 = test_dir / "bar.pdf"
    test_data_file2_contents = ["frodo", "sam", "elmo"]
    makefile(test_data_file2, test_data_file2_contents)

    test_data_file3 = test_dir / "oopsie.yaml"
    test_data_file3_contents = []
    makefile(test_data_file3, test_data_file3_contents)

    verify_dir_contents(
        test_dir,
        [test_data_file1, test_data_file2, test_data_file3],
        [test_data_file1_contents, test_data_file2_contents, test_data_file3_contents],
    )

    # Temporarily delete two of the files in the folder
    can.trash(test_data_file1)  # Delete a file
    can.trash(test_data_file3)  # Delete another file
    verify_dir_contents(
        test_dir,
        [test_data_file2],
        [test_data_file2_contents],
    )
    assert sorted(can.contents()) == sorted(
        [str(test_data_file1), str(test_data_file3)]
    )

    # Now permanently all of the files in the trash
    can.permanently_delete_all()
    verify_dir_contents(
        test_dir,
        [test_data_file2],
        [test_data_file2_contents],
    )
    assert can.contents() == []

    # Attempt to restore the deleted files
    with pytest.raises(FileNotFoundError):
        can.restore(test_data_file1)
    with pytest.raises(FileNotFoundError):
        can.restore(test_data_file3)

    # Restore any remaining files
    can.restore_all()
    verify_dir_contents(
        test_dir,
        [test_data_file2],
        [test_data_file2_contents],
    )


def test_purge():
    # Create trashcan
    can = Trash(verbose=True, debug=True)
    assert can.contents() == []

    # Create a folder
    test_dir = Path("tests/data/dir_bar")
    test_dir.mkdir(parents=True)

    # Create files in the folder
    test_data_file1 = test_dir / "foo.xls"
    test_data_file1_contents = ["baz", "bat"]
    makefile(test_data_file1, test_data_file1_contents)

    test_data_file2 = test_dir / "bar.pdf"
    test_data_file2_contents = ["frodo", "sam", "elmo"]
    makefile(test_data_file2, test_data_file2_contents)

    test_data_file3 = test_dir / "oopsie.yaml"
    test_data_file3_contents = []
    makefile(test_data_file3, test_data_file3_contents)

    verify_dir_contents(
        test_dir,
        [test_data_file1, test_data_file2, test_data_file3],
        [test_data_file1_contents, test_data_file2_contents, test_data_file3_contents],
    )

    # Temporarily delete two of the files in the folder
    can.trash(test_data_file1)  # Delete a file
    can.trash(test_data_file3)  # Delete another file
    verify_dir_contents(
        test_dir,
        [test_data_file2],
        [test_data_file2_contents],
    )
    assert sorted(can.contents()) == sorted(
        [str(test_data_file1), str(test_data_file3)]
    )

    # Now permanently all of the files in the trash
    can.purge()
    verify_dir_contents(
        test_dir,
        [test_data_file2],
        [test_data_file2_contents],
    )
    assert can.contents() == []

    # Attempt to restore the deleted files
    with pytest.raises(FileNotFoundError):
        can.restore(test_data_file1)
    with pytest.raises(FileNotFoundError):
        can.restore(test_data_file3)

    # Restore any remaining files
    can.restore_all()
    verify_dir_contents(
        test_dir,
        [test_data_file2],
        [test_data_file2_contents],
    )


# TODO def test_deletions_are_permanent_after_program_exits():

# TODO def test_restored_files_remain_after_program_exits():

# TODO def test_error_missing_file():

# TODO def test_error_restore_file_not_trashed():

# TODO def test_error_restore_file_trashcan_missing():

# TODO def test_error_restore_collision():

# TODO def test_error_trash_collision():
