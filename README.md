<!-- TODO: Complete information -->

# trashcan

Implement a trash can object like macOS Trash

## Description

trashcan implements a Trash class which proivdes functionality like
macOS (or Linus or Windows) Trash:
i.e, files can be moved to trash, then "undeleted"
later.

## Getting Started

### Dependencies

See requirements.txt

### Installing
```
pip install trashcan
```
### Executing program

trashcan has no executables

### Using trashcan

```
from pathlib import Path
import trashcan

# Create trashcan
trash = trashcan.Trash()

# Create a file
with open("foo.txt", "w") as file:
    file.write("bar\n")
print(Path("foo.txt").exists) # => True

# Temporarily delete the file
trash.trash("foo.txt") # Delete a file
print(Path("foo.txt").exists) # => False

# Restore the deleted file
trash.restore("foo.txt")
print(Path("foo.txt").exists) # => True

# Read it back to ensure it's intact
with open("foo.txt", "r") as file:
    lines = file.readlines()
print lines # => ["bar"]
```

## Author

Richard LeBer  
richard.leber@gmail.com

## Version History

* 0.0.1
    * Initial Release

## License

This project is licensed under the MIT License - see the LICENSE.md file for details

For options, see [license.md](https://license.md/licenses/)

