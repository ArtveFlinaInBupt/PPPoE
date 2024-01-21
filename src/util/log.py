# -*- coding: utf-8 -*-

from config import CONFIG

import logging
import colorlog
import os

from typing import Optional


def init_logging(level: str, log_file: str):
    """
    Initialize logging system.

    :param level: Logging level.
    :param log_file: Logging file.
    :return: None
    """
    log_file = os.path.join(CONFIG.INSTANCE_DIR, log_file)
    numeric_level: Optional[int] = getattr(logging, level.upper(), None)

    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {numeric_level}')

    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s %(levelname)s %(message)s',
        datefmt='%H:%M:%S',
        handlers=[
            logging.FileHandler(log_file),
            # logging.StreamHandler()
        ]
    )

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(colorlog.ColoredFormatter(
        '%(log_color)s%(asctime)s %(levelname)s %(message)s',
        datefmt='%H:%M:%S',
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'purple',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    ))
    logging.getLogger().addHandler(stream_handler)

    logging.info('Logging service initialised.')
