# Copyright (c) 2020. All rights reserved.

import jsonschema  # type: ignore
import logging
import asyncio
from typing import AsyncIterator, Mapping, Tuple

from taskservice import TODOLIST_SCHEMA
from taskservice.database.db_engines import create_todolist_db
from taskservice.datamodel import TaskEntry


class TodoListService:
    def __init__(
        self,
        config: Mapping,
        logger: logging.Logger
    ) -> None:
        self.task_db = create_todolist_db(config['task-db'])
        self.logger = logger

    def start(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.task_db.start())

    def stop(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.task_db.stop())

    def validate_task(self, task: Mapping) -> None:
        try:
            jsonschema.validate(task, TODOLIST_SCHEMA)
        except jsonschema.exceptions.ValidationError:
            raise ValueError('JSON Schema validation failed')

    async def create_task(self, value: Mapping) -> str:
        self.validate_task(value)
        task = TaskEntry.from_api_dm(value)
        key = await self.task_db.create_task(task)
        return key

    async def get_task(self, key: str) -> Mapping:
        task = await self.task_db.read_task(key)
        return task.to_api_dm()

    async def update_task(self, key: str, value: Mapping) -> None:
        self.validate_task(value)
        task = TaskEntry.from_api_dm(value)
        await self.task_db.update_task(key, task)

    async def delete_task(self, key: str) -> None:
        await self.task_db.delete_task(key)

    async def get_all_tasks(self) -> AsyncIterator[Tuple[str, Mapping]]:
        async for id, task in self.task_db.read_all_tasks():
            yield id, task.to_api_dm()

    def clear_all_tasks(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.task_db.clear_all_tasks())
