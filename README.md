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

License
-------

Distributed under the MIT License.
See [LICENSE.txt] for details.

[LICENSE.txt]: LICENSE.txt
