#!/usr/bin/env python3

# Copyright (c) 2018 Egor Tensin <Egor.Tensin@gmail.com>
# This file is part of the "writable-dirs" project.
# For details, see https://github.com/egor-tensin/writable-dirs.
# Distributed under the MIT License.

import argparse
import contextlib
import grp
import logging
import logging.config
import logging.handlers
import multiprocessing as mp
import os
import pwd
import sys


def console_log_formatter():
    fmt = '%(asctime)s | %(processName)s | %(levelname)s | %(message)s'
    datefmt = '%Y-%m-%d %H:%M:%S'
    return logging.Formatter(fmt=fmt, datefmt=datefmt)


def console_log_level():
    return logging.DEBUG


def console_log_handler():
    handler = logging.StreamHandler()
    handler.setFormatter(console_log_formatter())
    handler.setLevel(console_log_level())
    return handler


@contextlib.contextmanager
def launch_logging_thread(queue):
    process = mp.current_process()
    process.name = 'scandir'
    listener = logging.handlers.QueueListener(queue, console_log_handler())
    listener.start()
    try:
        yield
    finally:
        listener.stop()


@contextlib.contextmanager
def setup_logging(queue):
    config = {
        'version': 1,
        'handlers': {
            'sink': {
                'class': 'logging.handlers.QueueHandler',
                'queue': queue,
            },
        },
        'root': {
            'handlers': ['sink'],
            'level': 'DEBUG',
        },
    }
    logging.config.dictConfig(config)
    try:
        yield
    except Exception as e:
        logging.exception(e)


def validate_uid(uid):
    try:
        return pwd.getpwuid(uid).pw_uid
    except KeyError:
        return None


def validate_gid(gid):
    try:
        return grp.getgrgid(gid).gr_gid
    except KeyError:
        return None


def map_user_name(user_name):
    try:
        return pwd.getpwnam(user_name).pw_uid
    except KeyError:
        return None


def map_group_name(group_name):
    try:
        return grp.getgrnam(group_name).gr_gid
    except KeyError:
        return None


def parse_user_name(src):
    uid = map_user_name(src)
    if uid is None:
        raise argparse.ArgumentTypeError('unknown user name: {}'.format(src))
    return uid


def parse_group_name(src):
    gid = map_group_name(src)
    if gid is None:
        raise argparse.ArgumentTypeError('unknown group name: {}'.format(src))
    return gid


def parse_uid(src):
    try:
        uid = int(src)
    except ValueError:
        return parse_user_name(src)
    uid = validate_uid(uid)
    if uid is None:
        raise argparse.ArgumentTypeError('unknown UID: {}'.format(src))
    return uid


def parse_gid(src):
    try:
        gid = int(src)
    except ValueError:
        return parse_group_name(src)
    gid = validate_gid(gid)
    if gid is None:
        raise argparse.ArgumentTypeError('unknown GID: {}'.format(src))
    return gid


def get_primary_gid(uid):
    return pwd.getpwuid(uid).pw_gid


def parse_args(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    parser = argparse.ArgumentParser()
    parser.add_argument('root_dir', default='/', nargs='?', metavar='DIR',
                        help='set root directory')
    parser.add_argument('--user', '-u', dest='uid', required=True,
                        metavar='USER', type=parse_uid,
                        help='set new process\' UID')
    parser.add_argument('--group', '-g', dest='gid',
                        metavar='GROUP', type=parse_gid,
                        help='set new process\' GID')
    args = parser.parse_args(argv)
    if args.gid is None:
        args.gid = get_primary_gid(args.uid)
    return args


def dump_process_info():
    ruid, euid, suid = os.getresuid()
    logging.info('User IDs:')
    logging.info('\tReal: %d', ruid)
    logging.info('\tEffective: %d', euid)
    logging.info('\tSaved: %d', suid)
    rgid, egid, sgid = os.getresgid()
    logging.info('Group IDs:')
    logging.info('\tReal: %d', rgid)
    logging.info('\tEffective: %d', egid)
    logging.info('\tSaved: %d', sgid)


def check_root():
    if os.getuid() == 0:
        return True
    logging.error('Must be run as root')
    return False


def scandir(dir_path):
    try:
        entry_it = os.scandir(dir_path)
    except (PermissionError, FileNotFoundError) as e:
        logging.warning('%s', e)
        return
    # On Python 3.6+:
    # with entry_it:
    yield from entry_it


def enum_dirs(dir_path):
    for entry in scandir(dir_path):
        if entry.is_dir(follow_symlinks=False):
            yield entry.path


def is_writable_via_access(dir_path):
    return os.access(dir_path, os.W_OK | os.X_OK)


def is_writable(dir_path):
    return is_writable_via_access(dir_path)


def drop_privileges(uid, gid):
    if not check_root():
        return
    os.setgroups([])
    os.setgid(gid)
    os.setuid(uid)
    os.umask(0o77)


@contextlib.contextmanager
def close_queue(queue):
    try:
        yield
    finally:
        queue.put(None)


def access_loop(access_queue, scandir_queue):
    for dir_list in iter(access_queue.get, None):
        denied_dir_list = []
        for dir_path in dir_list:
            if is_writable(dir_path):
                logging.info('Writable: %s', dir_path)
            else:
                denied_dir_list.append(dir_path)
        if not denied_dir_list:
            break
        scandir_queue.put(denied_dir_list)


def access_main(args, log_queue, access_queue, scandir_queue):
    with close_queue(scandir_queue), setup_logging(log_queue):
        drop_privileges(args.uid, args.gid)
        dump_process_info()
        access_loop(access_queue, scandir_queue)


def scandir_loop(access_queue, scandir_queue):
    for parent_dir_list in iter(scandir_queue.get, None):
        child_dir_list = [child_dir
                          for parent_dir in parent_dir_list
                          for child_dir in enum_dirs(parent_dir)]
        if not child_dir_list:
            break
        access_queue.put(child_dir_list)


def scandir_main(access_queue, scandir_queue):
    with close_queue(access_queue):
        if not check_root():
            return
        dump_process_info()
        scandir_loop(access_queue, scandir_queue)


def main(argv=None):
    log_queue = mp.Queue()
    with launch_logging_thread(log_queue), setup_logging(log_queue):
        prog_args = parse_args(argv)
        access_queue = mp.SimpleQueue()
        scandir_queue = mp.SimpleQueue()
        access_process_args = prog_args, log_queue, access_queue, scandir_queue
        access_process = mp.Process(target=access_main,
                                    args=access_process_args,
                                    name='access')
        access_queue.put([prog_args.root_dir])
        access_process.start()
        scandir_main(access_queue, scandir_queue)
        access_process.join()


if __name__ == '__main__':
    mp.set_start_method('spawn')
    main()
