# Copyright (c) 2020. All rights reserved.

from enum import Enum, unique
from typing import (
    Any,
    Mapping,
    Optional,
)


VALUE_ERR_MSG = '{} has invalid value {}'


@unique
class TaskPriority(Enum):
    urgent = 0,
    high = 1,
    normal = 2,
    low = 3,
    none = 4


class TaskEntry:
    def __init__(
        self,
        title: str,
        priority: TaskPriority = TaskPriority.none,
        description: str = None,
        completed: bool = False,
        due_date: int = None,
    ):
        if title is None:
            raise ValueError(VALUE_ERR_MSG.format('title', title))

        self._title = title
        self._priority = priority
        self._description = description
        self._completed = completed
        self._due_date = due_date

    @classmethod
    def from_api_dm(cls, vars: Mapping[str, Any]) -> 'TaskEntry':
        return TaskEntry(
            priority=TaskPriority[vars['priority']],
            title=vars['title'],
            description=vars['description'],
            completed=vars['completed'],
            due_date=vars.get('due_date'),
        )

    @property
    def priority(self) -> TaskPriority:
        return self._priority

    @priority.setter
    def priority(self, value: TaskPriority) -> None:
        if value is None:
            raise ValueError(VALUE_ERR_MSG.format('value', value))

        self._priority = value

    @property
    def description(self) -> Optional[str]:
        return self._description

    @description.setter
    def description(self, value: str) -> None:
        self._description = value

    @property
    def due_date(self) -> Optional[int]:
        return self._due_date

    @due_date.setter
    def due_date(self, value: int) -> None:
        self._due_date = value

    @property
    def title(self) -> str:
        return self._title

    @title.setter
    def title(self, value: str) -> None:
        if not value:
            raise ValueError(VALUE_ERR_MSG.format('value', value))

        self._title = value

    @property
    def completed(self) -> bool:
        return self._completed

    @completed.setter
    def completed(self, value: bool) -> None:
        self._completed = value

    def to_api_dm(self) -> Mapping[str, Any]:
        d = {
            'priority': self.priority.name,
            'title': self.title,
            'description': self.description,
            'completed': self.completed,
            'due_date': self.due_date
        }

        return {k: v for k, v in d.items() if v is not None}
