# pitivi_mover

This script tries to fix asset paths in Pitivi files after they have been moved.  The provided `xges_path` path with be searched for all files ending with ".xges".  Then the asset paths within each xges file will be updated by changing `old_path` into `new_path`.  A backup copy of the original xges file is created if it does not already exist.  

## Project Status

Works for me.  Your mileage may vary.  Issues and pull requests are welcome.

## Usage

### positional arguments

  **`xges_path`**
  :    A directory path with xges files that need to be updated.
  
  **`old_path`**
  :    The path to the assets previous location.
  
  **`new_path`**
  :    The path to the assets current location.

### options
  -h, --help  show this help message and exit

### Note

Only the portion of the paths that differ needs to be specified.  I.E. in the `old_path` and the `new_path` arguments, prefixes and suffixes in common can be omitted.
