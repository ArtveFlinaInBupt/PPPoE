# -*- coding: utf-8 -*-

from config import CONFIG

import logging
import numpy as np
import os


class DataManipulator:
    DATASET = 'gpw-v4-population-count-rev11_2020_30_sec_asc'
    FOLDER = os.path.join(CONFIG.ASSETS_DIR, DATASET)
    FILE_PREFIX = 'gpw_v4_population_count_rev11_2020_30_sec_'

    def __init__(self):
        self._data_raw = []
        self._data_processed = None

    def load_raw(self):
        for i in range(8):
            file_name = f'{self.FILE_PREFIX}{i + 1}.asc'
            logging.info(f'Loading file {file_name}...')
            file = os.path.join(self.FOLDER, file_name)
            data = np.loadtxt(file, skiprows=6, dtype=np.float32)
            self._data_raw.append(data)
            logging.info(f'File {file_name} loaded.')

    def process(self):
        layout = (
            (0, 0), (0, 1), (0, 2), (0, 3),
            (1, 0), (1, 1), (1, 2), (1, 3),
        )
        logging.info('Concatenating data...')
        self._data_processed = np.zeros((21600, 43200), dtype=np.float32)
        for i, data in enumerate(self._data_raw):
            x, y = layout[i]
            x *= 10800
            y *= 10800
            self._data_processed[x:x + 10800, y:y + 10800] = data

        del self._data_raw
        import gc
        gc.collect()

        logging.info('Data concatenated.')

        logging.info('Transforming data...')
        self._data_processed = np.where(
            self._data_processed == -9999, 0, self._data_processed
        )
        self._data_processed = np.cumsum(self._data_processed, axis=1)

        s = 0
        for i in range(21600):
            s += self._data_processed[i, -1]
        logging.info(f'Sum: {s}')

    def save(self):
        logging.info('Saving preprocessed data...')
        file = os.path.join(CONFIG.INSTANCE_DIR, 'data.npz')
        np.savez_compressed(file, data=self._data_processed)
        logging.info('Data saved.')

    def load(self):
        logging.info('Loading preprocessed data...')
        file = os.path.join(CONFIG.INSTANCE_DIR, 'data.npz')
        self._data_processed = np.load(file)['data']
