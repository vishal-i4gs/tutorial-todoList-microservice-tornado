# Copyright (c) 2020. All rights reserved.

import json

import tornado.testing

from taskservice.tornado.app import (
    TODOLIST_ENTRY_URI_FORMAT_STR
)

from tests.unit.tornado_app_handlers_test import (
    TaskServiceTornadoAppTestSetup
)


class TestTodoListServiceApp(TaskServiceTornadoAppTestSetup):
    def test_todoList_endpoints(self):
        # Get all tasks in the todoList, must be ZERO
        r = self.fetch(
            TODOLIST_ENTRY_URI_FORMAT_STR.format(id=''),
            method='GET',
            headers=None,
        )
        all_tasks = json.loads(r.body.decode('utf-8'))
        self.assertEqual(r.code, 200, all_tasks)
        self.assertEqual(len(all_tasks), 0, all_tasks)

        # Add a task
        r = self.fetch(
            TODOLIST_ENTRY_URI_FORMAT_STR.format(id=''),
            method='POST',
            headers=self.headers,
            body=json.dumps(self.task0),
        )
        self.assertEqual(r.code, 201)
        task_uri = r.headers['Location']

        # POST: error cases
        r = self.fetch(
            TODOLIST_ENTRY_URI_FORMAT_STR.format(id=''),
            method='POST',
            headers=self.headers,
            body='it is not json',
        )
        self.assertEqual(r.code, 400)
        self.assertEqual(r.reason, 'Invalid JSON body')

        # Get the added task
        r = self.fetch(
            task_uri,
            method='GET',
            headers=None,
        )
        self.assertEqual(r.code, 200)
        self.assertEqual(self.task0, json.loads(r.body.decode('utf-8')))

        # GET: error cases
        r = self.fetch(
            TODOLIST_ENTRY_URI_FORMAT_STR.format(id='no-such-id'),
            method='GET',
            headers=None,
        )
        self.assertEqual(r.code, 404)

        # Update that task
        r = self.fetch(
            task_uri,
            method='PUT',
            headers=self.headers,
            body=json.dumps(self.task1),
        )
        self.assertEqual(r.code, 204)
        r = self.fetch(
            task_uri,
            method='GET',
            headers=None,
        )
        self.assertEqual(r.code, 200)
        self.assertEqual(self.task1, json.loads(r.body.decode('utf-8')))

        # PUT: error cases
        r = self.fetch(
            task_uri,
            method='PUT',
            headers=self.headers,
            body='it is not json',
        )
        self.assertEqual(r.code, 400)
        self.assertEqual(r.reason, 'Invalid JSON body')
        r = self.fetch(
            TODOLIST_ENTRY_URI_FORMAT_STR.format(id='1234'),
            method='PUT',
            headers=self.headers,
            body=json.dumps(self.task1),
        )
        self.assertEqual(r.code, 404)

        # Delete that task
        r = self.fetch(
            task_uri,
            method='DELETE',
            headers=None,
        )
        self.assertEqual(r.code, 204)
        r = self.fetch(
            task_uri,
            method='GET',
            headers=None,
        )
        self.assertEqual(r.code, 404)

        # DELETE: error cases
        r = self.fetch(
            task_uri,
            method='DELETE',
            headers=None,
        )
        self.assertEqual(r.code, 404)

        # Get all tasks in the todoList, must be ZERO
        r = self.fetch(
            TODOLIST_ENTRY_URI_FORMAT_STR.format(id=''),
            method='GET',
            headers=None,
        )
        all_tasks = json.loads(r.body.decode('utf-8'))
        self.assertEqual(r.code, 200, all_tasks)
        self.assertEqual(len(all_tasks), 0, all_tasks)


if __name__ == '__main__':
    tornado.testing.main()
