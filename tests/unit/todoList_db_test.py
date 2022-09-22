# Copyright (c) 2020. All rights reserved.

from abc import ABCMeta, abstractmethod
import asynctest  # type: ignore
from io import StringIO
import os
import tempfile
from typing import Dict
import unittest
import yaml

from taskservice.database.todoList_db import (
    AbstractTodoListDB, InMemoryTodoListDB, FilesystemTodoListDB
)
from taskservice.database.db_engines import create_todolist_db
from taskservice.datamodel import TaskEntry

from data import task_data_suite


class AbstractTodoListDBTest(unittest.TestCase):
    def read_config(self, txt: str) -> Dict:
        with StringIO(txt) as f:
            cfg = yaml.load(f.read(), Loader=yaml.SafeLoader)
        return cfg

    def test_in_memory_db_config(self):
        cfg = self.read_config('''
task-db:
  memory: null
        ''')

        self.assertIn('memory', cfg['task-db'])
        db = create_todolist_db(cfg['task-db'])
        self.assertEqual(type(db), InMemoryTodoListDB)

    def test_file_system_db_config(self):
        cfg = self.read_config('''
task-db:
  fs: /tmp
        ''')

        self.assertIn('fs', cfg['task-db'])
        db = create_todolist_db(cfg['task-db'])
        self.assertEqual(type(db), FilesystemTodoListDB)
        self.assertEqual(db.store, '/tmp')


class AbstractTodoListDBTestCase(metaclass=ABCMeta):
    def setUp(self) -> None:
        self.task_data = {
            k: TaskEntry.from_api_dm(v)
            for k, v in task_data_suite().items()
        }
        self.task_db = self.make_task_db()

    @abstractmethod
    def make_task_db(self) -> AbstractTodoListDB:
        raise NotImplementedError()

    @abstractmethod
    def task_count(self) -> int:
        raise NotImplementedError()

    @asynctest.fail_on(active_handles=True)
    async def test_crud_lifecycle(self) -> None:
        # Nothing in the database
        for id in self.task_data:
            with self.assertRaises(KeyError):  # type: ignore
                await self.task_db.read_task(id)

        # Create then Read, again Create(fail)
        for id, task in self.task_data.items():
            await self.task_db.create_task(task, id)
            await self.task_db.read_task(id)
            with self.assertRaises(KeyError):  # type: ignore
                await self.task_db.create_task(task, id)

        self.assertEqual(self.task_count(), 2)  # type: ignore

        # First data in test set
        first_id = list(self.task_data.keys())[0]
        first_task = self.task_data[first_id]

        # Update
        await self.task_db.update_task(first_id, first_task)
        with self.assertRaises(KeyError):  # type: ignore
            await self.task_db.update_task('does not exist', first_task)

        # Create without giving id
        new_id = await self.task_db.create_task(task)
        self.assertIsNotNone(new_id)  # type: ignore
        self.assertEqual(self.task_count(), 3)  # type: ignore

        # Get All Tasks
        tasks = {}
        async for id, task in self.task_db.read_all_tasks():
            tasks[id] = task

        self.assertEqual(len(tasks), 3)  # type: ignore

        # Delete then Read, and the again Delete
        for id in self.task_data:
            await self.task_db.delete_task(id)
            with self.assertRaises(KeyError):  # type: ignore
                await self.task_db.read_task(id)
            with self.assertRaises(KeyError):  # type: ignore
                await self.task_db.delete_task(id)

        self.assertEqual(self.task_count(), 1)  # type: ignore

        await self.task_db.delete_task(new_id)
        self.assertEqual(self.task_count(), 0)  # type: ignore


class InMemoryTodoListDBTest(
    AbstractTodoListDBTestCase,
    asynctest.TestCase
):
    def make_task_db(self) -> AbstractTodoListDB:
        self.mem_db = InMemoryTodoListDB()
        return self.mem_db

    def task_count(self) -> int:
        return len(self.mem_db.db)


class FilesystemTodoListDBTest(
    AbstractTodoListDBTestCase,
    asynctest.TestCase
):
    def make_task_db(self) -> AbstractTodoListDB:
        self.tmp_dir = tempfile.TemporaryDirectory(prefix='todoList-fsdb')
        self.store_dir = self.tmp_dir.name
        self.fs_db = FilesystemTodoListDB(self.store_dir)
        return self.fs_db

    def task_count(self) -> int:
        return len([
            name for name in os.listdir(self.store_dir)
            if os.path.isfile(os.path.join(self.store_dir, name))
        ])

    def tearDown(self):
        self.tmp_dir.cleanup()
        super().tearDown()

    async def test_db_creation(self):
        with tempfile.TemporaryDirectory(prefix='todoList-fsdb') as tempdir:
            store_dir = os.path.join(tempdir, 'abc')
            FilesystemTodoListDB(store_dir)
            tmpfilename = os.path.join(tempdir, 'def.txt')
            with open(tmpfilename, 'w') as f:
                f.write('this is a file and not a dir')
            with self.assertRaises(ValueError):
                FilesystemTodoListDB(tmpfilename)


if __name__ == '__main__':
    unittest.main()
