# External Legacy Apps

The original private skill archive contained compiled Windows helper apps under these legacy plugin folders. They are intentionally not included in the public GitHub package because binary executables are not auditable, may carry license constraints, and are not portable.

Keep the folder taxonomy and documentation as migration references only. For new public workflows, replace each helper app with one of the following:

- documented PFC 6.0 command templates;
- Python source scripts in `scripts/`;
- CAD/DXF/STL preprocessing steps that can be reproduced from source;
- an external dependency note that tells users where to obtain their own licensed tool.

Do not recommit `.exe` or `.dll` files to this repository.
