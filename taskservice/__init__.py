# Copyright (c) 2020. All rights reserved.

import json
import os

TASK_SERVICE_ROOT_DIR = os.path.abspath(os.path.dirname(__file__))

TODOLIST_SCHEMA_FILE = os.path.abspath(os.path.join(
    TASK_SERVICE_ROOT_DIR,
    '../schema/todoList-v1.0.json'
))

with open(TODOLIST_SCHEMA_FILE, mode='r', encoding='utf-8') as f:
    TODOLIST_SCHEMA = json.load(f)

LOGGER_NAME = 'taskservice'
