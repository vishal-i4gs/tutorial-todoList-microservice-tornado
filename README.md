# Tutorial: Building, testing and profiling efficient micro-services using Tornado

## 0. Get the source code

Get the source code for the tutorial:

``` bash
$ git clone https://github.com/vishal-i4gs/tutorial-todoList-microservice-tornado.git
$ cd tutorial-todoList-microservice-tornado

$ tree .
.
├── LICENSE
├── README.md
├── taskservice
│   ├── __init__.py
│   ├── service.py
│   └── tornado
│       ├── __init__.py
│       ├── app.py
│       └── server.py
├── configs
│   └── todoList-local.yaml
├── data
│   ├── __init__.py
│   └── tasks
│       ├── task1.json
│       └── task2.json
├── requirements.txt
├── run.py
└── tests
    ├── __init__.py
    ├── integration
    │   ├── __init__.py
    │   └── tornado_app_taskservice_handlers_test.py
    └── unit
        ├── __init__.py
        └── tornado_app_handlers_test.py
```

The directory `taskservice` is  for the source code of the service, and the directory `test` is for keeping the tests.

## 1. Project Setup

Setup Virtual Environment:

``` bash
$ python3 -m venv .venv
$ source ./.venv/bin/activate
$ pip install --upgrade pip
$ pip3 install -r ./requirements.txt
```

Let's start from scratch:

``` bash
$ git checkout -b <branch> tag-01-project-setup
```

You can run static type checker, linter, unit tests, and code coverage by either executing the tool directly or through `run.py` script. In each of the following, In each of the following, you can use either of the commands.

Static Type Checker:

``` bash
$ mypy ./taskservice ./tests

$ ./run.py typecheck
```

Linter:

``` bash
$ flake8 ./taskservice ./tests

$ ./run.py lint
```

Unit Tests:

``` bash
$ python -m unittest discover tests -p '*_test.py'

$ ./run.py test
```

Code Coverage:

``` bash
$ coverage run --source=taskservice --branch -m unittest discover tests -p '*_test.py'

$ coverage run --source=taskservice --branch ./run.py test
```

After running tests with code coverage, you can get the report:

``` bash
$ coverage report
Name                      Stmts   Miss Branch BrPart  Cover
-----------------------------------------------------------
taskservice/__init__.py       2      2      0      0     0%
```

You can also generate HTML report:

``` bash
$ coverage html
$ open htmlcov/index.html
```

If you are able to run all these commands, your project setup has no error and you are all set for coding.

---

## 2. Microservice

Checkout the code:

``` bash
$ git checkout -b <branch> tag-02-microservice
```

File `taskservice/service.py` has business logic for CRUD operations for the todoList. This file is indpendent of any web service framework.
It currenly has just stubs with rudimentry implementation keeing tasks in a dictionary. It is sufficint to implement and test the REST service endpoints.

[Tornado](https://www.tornadoweb.org/) is a framework to develop Python web/microservices. It uses async effectively to achieve high number of open connections. In this tutorial, we create a `tornado.web.Application` and add `tornado.web.RequestHandlers` in file `taskservice/tornado/app.py` to serve various API endpoints for this tasks service. Tornado also has a rich framework for testing.

Web services return HTML back. In todoList microservice, API data interface is JSON. We will examine key Tornado APIs of `Application`, `RequestHandler` and `tornado.testing` to develop it.

But first, let's run the server and test it:

``` bash
$ python3 taskservice/tornado/server.py --port 8080 --config ./configs/taskservice-local.yaml --debug

Starting TodoList on port 8080 ...
```

Also run lint, typecheck and test to verify nothing is broken, and also code coverage:

``` bash
$ ./run.py lint
$ ./run.py typecheck
$ ./run.py test -v
$ coverage run --source=taskservice --omit="taskservice/tornado/server.py" --branch ./run.py test
$ coverage report
Name                              Stmts   Miss Branch BrPart  Cover
-------------------------------------------------------------------
taskservice/__init__.py               2      0      0      0   100%
taskservice/service.py               23      1      0      0    96%
taskservice/tornado/__init__.py       0      0      0      0   100%
taskservice/tornado/app.py           83      4      8      3    92%
-------------------------------------------------------------------
TOTAL                               108      5      8      3    93%
```

The `taskservice/tornado/server.py` has been omitted from coverage. This is the file used to start the server. Since Torando test framework has a mechanism to start the server in the same process where tests are running, this file does not get tested by unit and integration tests.

These are the todoList API endpoints, implemented through two Request Handlers:

`TodoListRequestHandler`:

- `GET /tasks`: gets all tasks in the todoList
- `POST /tasks`: create an entry in the todoList

`TodoListEntryRequestHandler`:

- `GET /tasks/{id}`: get the task entry with given id
- `PUT /tasks/{id}`: update the task entry with given id
- `DELETE /tasks/{id}`: delete the task entry with given id

Here is a sample session exercising all endpoints (notice the POST response has Location in the Headers containing the URI/id `66fdbb78e79846849608b2cfe244a858` of the entry that gets created):

``` bash
# Create an task entry

$ curl -i -X POST http://localhost:8080/tasks -d '{"title": "Task1"}'

HTTP/1.1 201 Created
Server: TornadoServer/6.0.3
Content-Type: text/html; charset=UTF-8
Date: Tue, 10 Mar 2020 14:40:01 GMT
Location: /tasks/66fdbb78e79846849608b2cfe244a858
Content-Length: 0
Vary: Accept-Encoding

# Read the task entry

$ curl -i -X GET http://localhost:8080/tasks/66fdbb78e79846849608b2cfe244a858

HTTP/1.1 200 OK
Server: TornadoServer/6.0.3
Content-Type: application/json; charset=UTF-8
Date: Tue, 10 Mar 2020 14:44:26 GMT
Etag: "5496aee01a83cf2386641b2c43540fc5919d621e"
Content-Length: 22
Vary: Accept-Encoding
{"title": "Bill Task1"}

# Update the task entry

$ curl -i -X PUT http://localhost:8080/tasks/66fdbb78e79846849608b2cfe244a858 -d '{"title": "Task2"}'

HTTP/1.1 204 No Content
Server: TornadoServer/6.0.3
Date: Tue, 10 Mar 2020 14:48:04 GMT
Vary: Accept-Encoding

# List all tasks

$ curl -i -X GET http://localhost:8080/tasks

HTTP/1.1 200 OK
Server: TornadoServer/6.0.3
Content-Type: application/json; charset=UTF-8
Date: Tue, 10 Mar 2020 14:49:10 GMT
Etag: "5601e676f3fa4447feaa8d2dd960be163af7570a"
Content-Length: 73
Vary: Accept-Encoding
{"66fdbb78e79846849608b2cfe244a858": {"title": "Task2"}}

# Delete the task

$ curl -i -X DELETE http://localhost:8080/tasks/66fdbb78e79846849608b2cfe244a858

HTTP/1.1 204 No Content
Server: TornadoServer/6.0.3
Date: Tue, 10 Mar 2020 14:50:38 GMT
Vary: Accept-Encoding

# Verify task is deleted

$ curl -i -X GET http://localhost:8080/tasks

HTTP/1.1 200 OK
Server: TornadoServer/6.0.3
Content-Type: application/json; charset=UTF-8
Date: Tue, 10 Mar 2020 14:52:01 GMT
Etag: "bf21a9e8fbc5a3846fb05b4fa0859e0917b2202f"
Content-Length: 2
Vary: Accept-Encoding
{}

$ curl -i -X GET http://localhost:8080/tasks/66fdbb78e79846849608b2cfe244a858 

HTTP/1.1 404 '66fdbb78e79846849608b2cfe244a858'
Server: TornadoServer/6.0.3
Content-Type: application/json; charset=UTF-8
Date: Tue, 10 Mar 2020 14:53:06 GMT
Content-Length: 1071
Vary: Accept-Encoding
{"method": "GET", "uri": "/tasks/66fdbb78e79846849608b2cfe244a858", "code": 404, "message": "'66fdbb78e79846849608b2cfe244a858'", "trace": "Traceback (most recent call last):\n\n  File \"... redacted call stack trace ... taskservice/tornado/app.py\", line 100, in get\n    raise tornado.web.HTTPError(404, reason=str(e))\n\ntornado.web.HTTPError: HTTP 404: '66fdbb78e79846849608b2cfe244a858'\n"}
```

---