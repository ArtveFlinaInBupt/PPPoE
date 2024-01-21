# -*- coding: utf-8 -*-

"""
Cli arguments parser for the project.
"""

from .project_meta import *
from .config import CONFIG

from argparse import ArgumentParser


class Cli(ArgumentParser):
    def __init__(self):
        super().__init__(
            description=__description__,
            epilog=f'Author: {__author__}',
        )
        self.add_argument(
            '-v', '--version',
            action='version',
            version=f'{__project__} {__version__}',
        )
        self.add_argument(
            '-c', '--client',
            action='store_true',
            help='Run client',
        )
        self.add_argument(
            '-s', '--server',
            action='store_true',
            help='Run server',
        )
        self.add_argument(
            '-a', '--addr',
            type=str,
            help='Server address',
        )
        self.add_argument(
            '-p', '--port',
            type=int,
            help='Server port',
        )
        self.add_argument(
            '-l', '--log',
            type=str,
            default=CONFIG.DEFAULT_LOG_LEVEL,
            help='Logging level',
        )
        self.add_argument(
            '--log-file',
            type=str,
            default=CONFIG.DEFAULT_LOG_FILE,
        )
        self.add_argument(
            '--preprocess',
            action='store_true',
            help='Preprocess data',
        )

    def parse(self):
        return self.parse_args()
