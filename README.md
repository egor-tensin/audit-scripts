audit-scripts
=============

Scripts to run quick audits.

bad-attrs
---------

Find files with the immutable (`+i`) or append-only (`+a`) flag set.

    ./src/bad-attrs /

writable-dirs
-------------

Which directories are writable by a user?

    ./src/writable-dirs -u USERNAME /

Ubuntu
------

Ubuntu-specific (or Debian-specific) scripts.

### check-integrity.sh

Use `debsums` to verify file integrity against the package database.

    ./src/ubuntu/check-integrity.sh

### unmanaged.sh

Use `cruft` to view a list of unmanaged files and directories.
Some common directories are excluded automatically.

    ./src/ubuntu/unmanaged.sh

License
-------

Distributed under the MIT License.
See [LICENSE.txt] for details.

[LICENSE.txt]: LICENSE.txt
