# Copyright (c) 2020. All rights reserved.

from abc import ABCMeta, abstractmethod
import aiofiles  # type: ignore
import json
import os
from typing import AsyncIterator, Dict, Mapping, Tuple
import uuid
import sqlite3
import aiosqlite

from taskservice.datamodel import TaskEntry, TaskPriority


class AbstractTodoListDB(metaclass=ABCMeta):
    @abstractmethod
    async def start(self):
        pass

    @abstractmethod
    async def stop(self):
        pass

    # CRUD

    @abstractmethod
    async def create_task(
        self,
        task: TaskEntry,
        id: str = None
    ) -> str:
        raise NotImplementedError()

    @abstractmethod
    async def read_task(self, id: str) -> TaskEntry:
        raise NotImplementedError()

    @abstractmethod
    async def update_task(self, id: str, task: TaskEntry) -> None:
        raise NotImplementedError()

    @abstractmethod
    async def delete_task(self, id: str) -> None:
        raise NotImplementedError()

    @abstractmethod
    async def read_all_tasks(self) -> AsyncIterator[Tuple[str, TaskEntry]]:
        raise NotImplementedError()

    @abstractmethod
    async def clear_all_tasks(self) -> None:
        raise NotImplementedError()


class InMemoryTodoListDB(AbstractTodoListDB):
    def __init__(self):
        self.db: Dict[str, TaskEntry] = {}

    async def start(self):
        await super().start()

    async def stop(self):
        await super().stop()

    async def create_task(
        self,
        task: TaskEntry,
        id: str = None
    ) -> str:
        if id is None:
            id = uuid.uuid4().hex

        if id in self.db:
            raise KeyError('{} already exists'.format(id))

        self.db[id] = task
        return id

    async def read_task(self, id: str) -> TaskEntry:
        return self.db[id]

    async def update_task(self, id: str, task: TaskEntry) -> None:
        if id is None or id not in self.db:
            raise KeyError('{} does not exist'.format(id))

        self.db[id] = task

    async def delete_task(self, id: str) -> None:
        if id is None or id not in self.db:
            raise KeyError('{} does not exist'.format(id))

        del self.db[id]

    async def read_all_tasks(
        self
    ) -> AsyncIterator[Tuple[str, TaskEntry]]:
        for id, task in self.db.items():
            yield id, task

    async def clear_all_tasks(self) -> None:
        self.db: Dict[str, TaskEntry] = {}


class FilesystemTodoListDB(AbstractTodoListDB):
    def __init__(self, store_dir_path: str):
        store_dir = os.path.abspath(store_dir_path)
        if not os.path.exists(store_dir):
            os.makedirs(store_dir)
        if not (os.path.isdir(store_dir) and os.access(store_dir, os.W_OK)):
            raise ValueError(
                'String store "{}" is not a writable directory'.format(
                    store_dir
                )
            )
        self._store = store_dir

    async def start(self):
        await super().start()

    async def stop(self):
        await super().stop()

    @property
    def store(self) -> str:
        return self._store

    def _file_name(self, id: str) -> str:
        return os.path.join(
            self.store,
            id + '.json'
        )

    def _file_exists(self, id: str) -> bool:
        return os.path.exists(self._file_name(id))

    async def _file_read(self, id: str) -> Dict:
        try:
            async with aiofiles.open(
                self._file_name(id),
                encoding='utf-8',
                mode='r'
            ) as f:
                contents = await f.read()
                return json.loads(contents)
        except FileNotFoundError:
            raise KeyError(id)

    async def _file_write(self, id: str, addr: Mapping) -> None:
        async with aiofiles.open(
            self._file_name(id),
            mode='w',
            encoding='utf-8'
        ) as f:
            await f.write(json.dumps(addr))

    async def _file_delete(self, id: str) -> None:
        os.remove(self._file_name(id))

    async def _file_read_all(self) -> AsyncIterator[Tuple[str, Dict]]:
        all_files = os.listdir(self.store)
        extn_end = '.json'
        extn_len = len(extn_end)
        for f in all_files:
            if f.endswith(extn_end):
                id = f[:-extn_len]
                task = await self._file_read(id)
                yield id, task

    async def create_task(
        self,
        task: TaskEntry,
        id: str = None
    ) -> str:
        if id is None:
            id = uuid.uuid4().hex

        if self._file_exists(id):
            raise KeyError('{} already exists'.format(id))

        await self._file_write(id, task.to_api_dm())
        return id

    async def read_task(self, id: str) -> TaskEntry:
        task = await self._file_read(id)
        return TaskEntry.from_api_dm(task)

    async def update_task(self, id: str, task: TaskEntry) -> None:
        if self._file_exists(id):
            await self._file_write(id, task.to_api_dm())
        else:
            raise KeyError(id)

    async def delete_task(self, id: str) -> None:
        if self._file_exists(id):
            await self._file_delete(id)
        else:
            raise KeyError(id)

    async def read_all_tasks(
        self
    ) -> AsyncIterator[Tuple[str, TaskEntry]]:
        async for id, task in self._file_read_all():
            yield id, TaskEntry.from_api_dm(task)

    async def clear_all_tasks(self) -> None:
        all_files = os.listdir(self.store)
        extn_end = '.json'
        extn_len = len(extn_end)
        for f in all_files:
            if f.endswith(extn_end):
                id = f[:-extn_len]
                os.remove(self._file_name(id))


class SQLTodoListDB(AbstractTodoListDB):
    def __init__(self, sql_db_path: str) -> None:
        self.sql_db_path = sql_db_path

    async def start(self):
        self.conn = await aiosqlite.connect(self.sql_db_path)
        task_entry_table = await self.conn.execute(
            """
                SELECT name FROM sqlite_master
                WHERE type=\'table\' AND name=(?);
            """, ("task_entries",))

        if await task_entry_table.fetchall() == []:
            await self.conn.execute(
                """
                    CREATE TABLE task_entries(
                        id VARCHAR(255),
                        title VARCHAR(255),
                        description VARCHAR(255),
                        priority VARCHAR(10),
                        dueDate INTEGER,
                        completed BOOLEAN
                    );
                """
            )
            await self.conn.commit()

    async def stop(self):
        await self.conn.close()

    async def _row_exists(self, key: str) -> bool:
        rows = await self.conn.execute(
            """
                SELECT * FROM task_entries WHERE id = (?)
            """, (key,)
        )

        if await rows.fetchall() == []:
            return False
        else:
            return True

    async def create_task(self, task: TaskEntry, id: str = None) -> str:
        if id is None:
            id = uuid.uuid4().hex

        if await self._row_exists(id):
            raise KeyError('{} already exists'.format(id))

        await self.conn.execute(
            """
                INSERT INTO task_entries (
                    id,
                    title,
                    description,
                    priority,
                    dueDate,
                    completed
                )
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                id,
                task.title,
                task.description,
                task.priority.name,
                task.due_date,
                task.completed
            )
        )
        await self.conn.commit()
        return id

    async def delete_task(self, id: str) -> None:
        if await self._row_exists(id):
            await self.conn.execute(
                """
                    DELETE FROM task_entries WHERE id = (?)
                """, (id, )
            )
            await self.conn.commit()
        else:
            raise KeyError(id)

    async def update_task(self, id: str, task: TaskEntry) -> None:
        if await self._row_exists(id):
            await self.conn.execute(
                """
                    UPDATE task_entries SET
                        title=(?),
                        description=(?),
                        priority=(?),
                        dueDate=(?),
                        completed=(?)
                    WHERE
                        id=(?)
                """, (
                    task.title,
                    task.description,
                    task.priority.name,
                    task.due_date,
                    task.completed,
                    id
                )
            )
            await self.conn.commit()
        else:
            raise KeyError(id)

    async def read_task(self, id: str) -> TaskEntry:
        if await self._row_exists(id):
            async with aiosqlite.connect(self.sql_db_path) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute("SELECT * FROM task_entries WHERE id=(?)", (id, )) as cursor: # noqa
                    async for row in cursor:
                        return TaskEntry(
                            title=row['title'],
                            description=row['description'],
                            priority=TaskPriority[row['priority']],
                            due_date=row['dueDate'],
                            completed=row['completed']
                        )
        else:
            raise KeyError(id)

    async def read_all_tasks(self) -> AsyncIterator[Tuple[str, Dict]]:
        async with aiosqlite.connect(self.sql_db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM task_entries") as cursor:
                async for row in cursor:
                    yield row['id'], TaskEntry(
                        title=row['title'],
                        description=row['description'],
                        priority=TaskPriority[row['priority']],
                        due_date=row['dueDate'],
                        completed=row['completed']
                    )

    async def clear_all_tasks(self) -> None:
        await self.conn.execute(
                """
                DELETE FROM task_entries
                """
        )
        await self.conn.commit()
