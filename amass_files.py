import log
import logging
from pathlib import Path
import shutil
import sys

def main(argv):
  if len(argv) != 3:
    print(f"usage: {argv[0]} from to")
    exit(1)
  log.start_logging(app = "amass_files",)
  relocate(argv[1], argv[2])

def relocate(from_path: str | Path, to_path: str| Path, force=True) -> None:
  from_path = Path(from_path).resolve()
  to_path = Path(to_path).resolve()

  if not from_path.exists():
    raise FileNotFoundError(f"File {from_path} does not exist")
  
  if to_path.exists():
    if not force:
      raise FileExistsError(f"File {to_path} already exists")
    to_path.unlink()

  to_dir = to_path.parent

  # TODO logging
  # TODO what if only part of this works? We should back out if we can
  to_dir.mkdir(parents=True, exist_ok=True)
  shutil.move(from_path, to_path)
  from_path.symlink_to(to_path)
  logging.info({"action": "relocate", "from": str(from_path), "to": str(to_path)})


if __name__ == "__main__":
  main(sys.argv)