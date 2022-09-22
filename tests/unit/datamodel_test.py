# Copyright (c) 2020. All rights reserved.

import unittest

from taskservice.datamodel import (
    TaskPriority, TaskEntry
)


class DataModelTest(unittest.TestCase):
    def test_data_model(self) -> None:
        task_entry = TaskEntry(
            priority=TaskPriority.urgent,
            title='Data Model',
            description='Data Model Description',
            due_date=1,
            completed=False
        )
        self.assertEqual(task_entry.priority, TaskPriority.urgent)
        self.assertEqual(task_entry.title, 'Data Model')
        self.assertEqual(task_entry.description, 'Data Model Description')
        self.assertEqual(task_entry.due_date, 1)
        self.assertEqual(task_entry.completed, False)

        task_dict_1 = task_entry.to_api_dm()
        task_dict_2 = TaskEntry.from_api_dm(task_dict_1).to_api_dm()
        self.assertEqual(task_dict_1, task_dict_2)

        # Setters
        task_entry.title = 'New Title'
        task_entry.priority = TaskPriority.low
        task_entry.description = ''
        task_entry.due_date = 2
        task_entry.completed = True

        # Exceptions
        with self.assertRaises(ValueError):
            TaskEntry(title=None)  # type: ignore

        a = TaskEntry(title='title')

        with self.assertRaises(ValueError):
            a.title = None  # type: ignore

        with self.assertRaises(ValueError):
            a.priority = None  # type: ignore


if __name__ == '__main__':
    unittest.main()
