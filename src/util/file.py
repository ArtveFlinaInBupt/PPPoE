# -*- coding: utf-8 -*-

import os


def try_mkdir(path: str):
    """
    Try to make a directory.

    :param path: Path of the directory.
    :return: None
    """
    try:
        os.mkdir(path)
    except FileExistsError:
        pass


def try_rm(path: str):
    """
    Try to remove a file or directory.

    :param path: Path of the file or directory.
    :return: None
    """
    try:
        if os.path.isfile(path):
            os.remove(path)
        elif os.path.isdir(path):
            os.rmdir(path)
    except FileNotFoundError:
        pass
