# Copyright (c) 2020. All rights reserved.

import atexit
from io import StringIO
import json
import yaml

from tornado.ioloop import IOLoop
import tornado.testing

from taskservice.tornado.app import make_taskservice_app

from data import task_data_suite


IN_MEMORY_CFG_TXT = '''
service:
  name: TodoList Test
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
        addr_service, app = make_taskservice_app(
            config=TEST_CONFIG,
            debug=True
        )

        addr_service.start()
        atexit.register(lambda: addr_service.stop())

        return app

    def get_new_ioloop(self):
        return IOLoop.current()


class AddressServiceTornadoAppUnitTests(TaskServiceTornadoAppTestSetup):
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
