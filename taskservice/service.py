# Copyright (c) 2020. All rights reserved.

import logging
from typing import Dict
import uuid


class TodoListService:
    def __init__(
        self,
        config: Dict,
        logger: logging.Logger
    ) -> None:
        # TODO FIXME full class is just dummy stubs
        self.tasks: Dict[str, Dict] = {}
        self.logger = logger

    def start(self):
        # TODO FIXME
        self.tasks = {}

    def stop(self):
        # TODO FIXME
        pass

    async def create_task(self, value: Dict) -> str:
        # TODO FIXME
        key = uuid.uuid4().hex
        self.tasks[key] = value
        return key

    async def get_task(self, key: str) -> Dict:
        # TODO FIXME
        return self.tasks[key]

    async def update_task(self, key: str, value: Dict) -> None:
        # TODO FIXME
        self.tasks[key]  # will cause exception if key doesn't exist
        self.tasks[key] = value

    async def delete_task(self, key: str) -> None:
        self.tasks[key]  # will cause exception if key doesn't exist
        del self.tasks[key]

    async def get_all_tasks(self) -> Dict[str, Dict]:
        # TODO FIXME
        return self.tasks
