# Copyright (c) 2020. All rights reserved.

from typing import Dict

from taskservice.database.todoList_db import (
    AbstractTodoListDB, InMemoryTodoListDB, FilesystemTodoListDB
)


def create_todolist_db(task_db_config: Dict) -> AbstractTodoListDB:
    db_type = list(task_db_config.keys())[0]
    db_config = task_db_config[db_type]

    return {
        'memory': lambda cfg: InMemoryTodoListDB(),
        'fs': lambda cfg: FilesystemTodoListDB(cfg),
    }[db_type](db_config)
