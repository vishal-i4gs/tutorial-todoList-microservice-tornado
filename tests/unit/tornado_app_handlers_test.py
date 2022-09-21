# Copyright (c) 2020. All rights reserved.

import atexit
from io import StringIO
import json
import yaml
import aiotask_context as context  # type: ignore

from tornado.ioloop import IOLoop
import tornado.testing
import logging
import logging.config

from taskservice.tornado.app import make_taskservice_app

from taskservice import LOGGER_NAME
from data import task_data_suite


IN_MEMORY_CFG_TXT = '''
service:
  name: TodoList Test

logging:
  version: 1
  root:
    level: ERROR
'''

with StringIO(IN_MEMORY_CFG_TXT) as f:
    TEST_CONFIG = yaml.load(f.read(), Loader=yaml.SafeLoader)


class TaskServiceTornadoAppTestSetup(tornado.testing.AsyncHTTPTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.headers = {'Content-Type': 'application/json; charset=UTF-8'}
        tasks_data = task_data_suite()
        keys = list(tasks_data.keys())
        self.assertGreaterEqual(len(keys), 2)
        self.task0 = tasks_data[keys[0]]
        self.task1 = tasks_data[keys[1]]

    def get_app(self) -> tornado.web.Application:
        logging.config.dictConfig(TEST_CONFIG['logging'])
        logger = logging.getLogger(LOGGER_NAME)

        task_service, app = make_taskservice_app(
            config=TEST_CONFIG,
            debug=True,
            logger=logger
        )

        task_service.start()
        atexit.register(lambda: task_service.stop())

        return app

    def get_new_ioloop(self):
        instance = IOLoop.current()
        instance.asyncio_loop.set_task_factory(context.task_factory)
        return instance


class TaskServiceTornadoAppUnitTests(TaskServiceTornadoAppTestSetup):
    def test_default_handler(self):
        r = self.fetch(
            '/does-not-exist',
            method='GET',
            headers=None,
        )
        info = json.loads(r.body.decode('utf-8'))

        self.assertEqual(r.code, 404, info)
        self.assertEqual(info['code'], 404)
        self.assertEqual(info['message'], 'Unknown Endpoint')


if __name__ == '__main__':
    tornado.testing.main()
