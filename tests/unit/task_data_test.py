# Copyright (c) 2020. All rights reserved.

import jsonschema  # type: ignore
import unittest

from taskservice import TODOLIST_SCHEMA
from data import task_data_suite
import taskservice.datamodel as datamodel


class TaskDataTest(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.task_data = task_data_suite()

    def test_json_schema(self) -> None:
        # Validate TodoList Schema
        jsonschema.Draft7Validator.check_schema(TODOLIST_SCHEMA)

    def test_task_data_json(self) -> None:
        # Validate Task Test Data
        for id, task in self.task_data.items():
            # validate using application subschema
            jsonschema.validate(task, TODOLIST_SCHEMA)

            # Roundrtrip Test
            task_obj = datamodel.TaskEntry.from_api_dm(task)
            task_dict = task_obj.to_api_dm()
            self.assertEqual(task, task_dict)


if __name__ == '__main__':
    unittest.main()
