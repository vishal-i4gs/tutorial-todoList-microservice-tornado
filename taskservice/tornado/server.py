# Copyright (c) 2020. All rights reserved.

import argparse
import asyncio
from typing import Dict
import yaml
import aiotask_context as context
import logging
import logging.config

import tornado.web

from taskservice import LOGGER_NAME
from taskservice.service import TodoListService
from taskservice.tornado.app import make_taskservice_app

import taskservice.utils.logutils as logutils


def parse_args(args=None):
    parser = argparse.ArgumentParser(
        description='Run TodoList Server'
    )

    parser.add_argument(
        '-p',
        '--port',
        type=int,
        default=8080,
        help='port number for %(prog)s server to listen; '
        'default: %(default)s'
    )

    parser.add_argument(
        '-d',
        '--debug',
        action='store_true',
        help='turn on debug logging'
    )

    parser.add_argument(
        '-c',
        '--config',
        required=True,
        type=argparse.FileType('r'),
        help='config file for %(prog)s'
    )

    args = parser.parse_args(args)
    return args


def run_server(
    app: tornado.web.Application,
    service: TodoListService,
    config: Dict,
    port: int,
    debug: bool,
    logger: logging.Logger
):
    name = config['service']['name']
    loop = asyncio.get_event_loop()
    loop.set_task_factory(context.task_factory)

    # Start TodoList service
    service.start()

    # Bind http server to port
    http_server_args = {
        'decompress_request': True
    }
    http_server = app.listen(port, '', **http_server_args)
    logutils.log(
        logger,
        logging.INFO,
        message='STARTING',
        service_name=name,
        port=port
    )

    try:
        # Start asyncio IO event loop
        loop.run_forever()
    except KeyboardInterrupt:
        # signal.SIGINT
        pass
    finally:
        loop.stop()
        logutils.log(
            logger,
            logging.INFO,
            message='SHUTTING DOWN',
            service_name=name,
            port=port
        )
        http_server.stop()
        # loop.run_until_complete(asyncio.gather(*asyncio.Task.all_tasks()))
        loop.run_until_complete(loop.shutdown_asyncgens())
        service.stop()
        loop.close()
        logutils.log(
            logger,
            logging.INFO,
            message='STOPPED',
            service_name=name,
            port=port
        )


def main(args=parse_args()):
    '''
    Starts the Tornado server serving TodoList on the given port
    '''

    config = yaml.load(args.config.read(), Loader=yaml.SafeLoader)

    logging.config.dictConfig(config['logging'])
    logger = logging.getLogger(LOGGER_NAME)

    task_service, todoList_app = make_taskservice_app(config, args.debug, logger) # noqa

    run_server(
        app=todoList_app,
        service=task_service,
        config=config,
        port=args.port,
        debug=args.debug,
        logger=logger
    )


if __name__ == '__main__':
    main()
