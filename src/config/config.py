# -*- coding: utf-8 -*-

"""
Configurations for the project.
"""

from dataclasses import dataclass


@dataclass
class Config:
    INSTANCE_DIR: str = 'instance'
    ASSETS_DIR: str = 'assets'
    DEFAULT_LOG_LEVEL: str = 'INFO'
    DEFAULT_LOG_FILE: str = 'run.log'
    DEFAULT_ADDR: str = '127.0.0.1'
    DEFAULT_PORT: int = 555

    def __getitem__(self, item):
        return getattr(self, item)

    def __setitem__(self, key, value):
        return setattr(self, key, value)

    def __delitem__(self, key):
        return delattr(self, key)


CONFIG = Config()
