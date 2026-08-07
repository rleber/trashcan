import log
from pathlib import Path
from relocator import Relocator
import sys


def main(argv):
  if len(argv) != 3:
    print(f"usage: {argv[0]} from to")
    exit(1)
  log.start_logging(app = "amass_files",)
  Relocator.go(argv[1], argv[2])


if __name__ == "__main__":
  main(sys.argv)