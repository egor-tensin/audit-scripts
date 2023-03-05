audit-scripts
=============

Scripts to run quick audits.

bad_attrs.py
------------

Find files with the immutable (`+i`) or append-only (`+a`) flag set.

    ./bad_attrs.py /

writable_dirs.py
----------------

Which directories are writable by a user?

    ./writable_dirs.py -u USERNAME /

License
-------

Distributed under the MIT License.
See [LICENSE.txt] for details.

[LICENSE.txt]: LICENSE.txt
