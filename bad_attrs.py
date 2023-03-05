#!/usr/bin/env python3

# Copyright (c) 2023 Egor Tensin <Egor.Tensin@gmail.com>
# This file is part of the "audit-scripts" project.
# For details, see https://github.com/egor-tensin/audit-scripts.
# Distributed under the MIT License.

import argparse
import array
from contextlib import contextmanager
import errno
import fcntl
import logging
import os
import stat
import sys


@contextmanager
def setup_logging():
    logging.basicConfig(
        format='%(asctime)s | %(levelname)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        level=logging.DEBUG)
    try:
        yield
    except Exception as e:
        logging.exception(e)
        raise


def scandir(dir_path):
    try:
        entry_it = os.scandir(dir_path)
    except (PermissionError, FileNotFoundError) as e:
        logging.warning('%s', e)
        return
    with entry_it:
        yield from entry_it


def traverse_tree(root):
    queue = [root]
    while queue:
        for entry in scandir(queue.pop(0)):
            if entry.is_dir(follow_symlinks=False):
                if os.path.ismount(entry.path):
                    continue
                queue.append(entry.path)
            yield entry


def skip_leaf(entry):
    if entry.is_dir(follow_symlinks=False):
        return False
    if entry.is_file(follow_symlinks=False):
        return False
    return True


@contextmanager
def low_level_open(path, flags):
    fd = os.open(path, flags)
    try:
        yield fd
    finally:
        os.close(fd)


FS_IOC_GETFLAGS = 0x80086601

FS_IMMUTABLE_FL = 0x00000010
FS_APPEND_FL    = 0x00000020

BAD_FLAGS = [FS_IMMUTABLE_FL, FS_APPEND_FL]


def flags_contain_bad_flags(flags):
    return any([flags & bad_flag for bad_flag in BAD_FLAGS])


def fd_get_flags(fd):
    a = array.array('L', [0])
    fcntl.ioctl(fd, FS_IOC_GETFLAGS, a, True)
    return a[0]


def path_get_flags(path):
    with low_level_open(path, os.O_RDONLY) as fd:
        return fd_get_flags(fd)


def path_has_bad_flags(path):
    try:
        flags = path_get_flags(path)
    except OSError as e:
        if e.errno == errno.ENOTTY or e.errno == errno.EPERM:
            # Either one of:
            #     Inappropriate ioctl for device
            #     Permission denied
            logging.warning('%s: %s', path, e)
            return False
        raise
    return flags_contain_bad_flags(flags)


def do_dir(root):
    logging.info('Directory: %s', root)
    for entry in traverse_tree(root):
        if skip_leaf(entry):
            continue
        #logging.debug('Path: %s', entry.path)
        if path_has_bad_flags(entry.path):
            logging.warning('Bad flags: %s', entry.path)


def parse_args(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    parser = argparse.ArgumentParser()
    parser.add_argument('dir', metavar='DIR',
                        help='set root directory')
    return parser.parse_args()


def main(argv=None):
    with setup_logging():
        args = parse_args()
        do_dir(args.dir)


if __name__ == '__main__':
    main()
