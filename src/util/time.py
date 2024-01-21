# -*- coding: utf-8 -*-

import time


def get_cur_time_ms():
    """
    Get current time in milliseconds.

    :return: Current time in milliseconds.
    """
    return int(round(time.time() * 1000))
