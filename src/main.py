# -*- coding: utf-8 -*-

from config import Cli, CONFIG
import util

import logging


def init_file():
    """
    Initialize files.

    :return: None
    """
    util.try_mkdir(CONFIG.INSTANCE_DIR)


def preprocess_main():
    logging.info('Preprocessing data...')
    start = util.get_cur_time_ms()

    from data_manip import DataManipulator
    dm = DataManipulator()
    dm.load_raw()
    dm.process()
    dm.save()

    end = util.get_cur_time_ms()
    logging.info(f'Data preprocessed in {(end - start) / 1000} s.')


def require_arg(arg, name, default):
    if arg is None:
        logging.info(f'No `{name}` specified, default to {default}')
        return default
    return arg


def innocent_arg(arg, name):
    if arg is not None:
        logging.warning(f'`{name}` specified but ignored.')


def main():
    arg_parser = Cli()
    args = arg_parser.parse_args()
    init_file()
    util.init_logging(args.log, args.log_file)

    if not any((args.preprocess, args.client, args.server)):
        logging.error('No action (client, server, preprocess) specified.')
        arg_parser.print_help()

    elif args.preprocess:
        innocent_arg(args.addr, 'addr')
        innocent_arg(args.port, 'port')
        preprocess_main()

    elif args.client:
        addr = require_arg(args.addr, 'addr', CONFIG.DEFAULT_ADDR)
        port = require_arg(args.port, 'port', CONFIG.DEFAULT_PORT)

        from client import Client
        client = Client(addr, port)
        client.run()

    elif args.server:
        innocent_arg(args.addr, 'addr')
        port = require_arg(args.port, 'port', CONFIG.DEFAULT_PORT)

        from server import Server
        server = Server(port)
        server.run()


if __name__ == '__main__':
    main()
