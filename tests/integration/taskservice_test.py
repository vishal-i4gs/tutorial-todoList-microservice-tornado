# Copyright (c) 2020. All rights reserved.

import asynctest  # type: ignore
from io import StringIO
import logging
import logging.config
import unittest
import yaml

from taskservice import LOGGER_NAME
from taskservice.datamodel import TaskEntry
from taskservice.service import TodoListService
from data import task_data_suite

IN_MEMORY_CFG_TXT = '''
service:
  name: TodoList Test

task-db:
  memory: null

logging:
  version: 1
  root:
    level: ERROR
'''

with StringIO(IN_MEMORY_CFG_TXT) as f:
    TEST_CONFIG = yaml.load(f.read(), Loader=yaml.SafeLoader)


class TodoListServiceWithInMemoryDBTest(asynctest.TestCase):
    async def setUp(self) -> None:
        logging.config.dictConfig(TEST_CONFIG['logging'])
        logger = logging.getLogger(LOGGER_NAME)

        self.service = TodoListService(
            config=TEST_CONFIG,
            logger=logger
        )
        self.service.start()

        self.tasks_data = task_data_suite()
        for id, val in self.tasks_data.items():
            task = TaskEntry.from_api_dm(val)
            await self.service.task_db.create_task(task, id)

    async def tearDown(self) -> None:
        self.service.stop()

    @asynctest.fail_on(active_handles=True)
    async def test_get_task(self) -> None:
        for id, task in self.tasks_data.items():
            value = await self.service.get_task(id)
            self.assertEqual(task, value)

    @asynctest.fail_on(active_handles=True)
    async def test_get_all_tasks(self) -> None:
        tasks = {}
        async for id, task in self.service.get_all_tasks():
            tasks[id] = task
        self.assertEqual(len(tasks), 2)

    @asynctest.fail_on(active_handles=True)
    async def test_crud_task(self) -> None:
        ids = list(self.tasks_data.keys())
        self.assertGreaterEqual(len(ids), 2)

        task0 = self.tasks_data[ids[0]]
        key = await self.service.create_task(task0)
        val = await self.service.get_task(key)
        self.assertEqual(task0, val)

        task1 = self.tasks_data[ids[1]]
        await self.service.update_task(key, task1)
        val = await self.service.get_task(key)
        self.assertEqual(task1, val)

        await self.service.delete_task(key)

        with self.assertRaises(KeyError):
            await self.service.get_task(key)


if __name__ == '__main__':
    unittest.main()
