# Copyright (c) 2020. All rights reserved.

from abc import ABCMeta, abstractmethod
import aiofiles  # type: ignore
import json
import os
from typing import AsyncIterator, Dict, Mapping, Tuple
import uuid

from taskservice.datamodel import TaskEntry


class AbstractTodoListDB(metaclass=ABCMeta):
    def start(self):
        pass

    def stop(self):
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
    def read_all_tasks(self) -> AsyncIterator[Tuple[str, TaskEntry]]:
        raise NotImplementedError()


class InMemoryTodoListDB(AbstractTodoListDB):
    def __init__(self):
        self.db: Dict[str, TaskEntry] = {}

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
