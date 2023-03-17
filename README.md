audit-scripts
=============

Scripts to run quick audits.

bad-attrs
---------

Find files with the immutable (`+i`) or append-only (`+a`) flag set.

    ./src/bad-attrs /

open-ports.sh
-------------

List open ports for a host.

    ./src/open-ports.sh HOST               # Scan all ports
    ./src/open-ports.sh -6 HOST            # Resolve domains to IPv6 addresses
    ./src/open-ports.sh -t 1000 HOST       # Scan the top 1000 most popular ports
    ./src/open-ports.sh -p 8080-8100 HOST  # Specify port ranges in the nmap format

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
