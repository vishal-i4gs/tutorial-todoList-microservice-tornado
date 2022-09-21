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
│   ├── tornado
│   │   ├── __init__.py
│   │   ├── app.py
│   │   └── server.py
│   └── utils
│       ├── __init__.py
│       ├── app.py
│       └── server.py
│       └── logutils.py
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

## 3. Logging

Checkout the code:

``` bash
$ git checkout -b <branch> tag-03-logging
```

Effective logs can cut down diagnosis time and facilitate monitoring and altering.

### Log Format

[Logfmt](https://pypi.org/project/logfmt/) log format consists of *key-value* pairs.
It offers good balance between processing using standard tools and human readibility.

### Canonical Logs

Emiting one canonical log line](https://brandur.org/canonical-log-lines) for each request makes manual inspection easier.
Assigning and logging a *request id* to each request, and passing that id to all called service helps correlate logs across services.
The *key-value* pairs for the log are stored in a [task context](https://github.com/Skyscanner/aiotask-context), which is maintained across asyncio task interleaving.

### Log Configuration

Logging are useful in diagnosing services, more so when async is involved. Python has a standard [logging](https://docs.python.org/3/library/logging.html) package, and its documentation includes an excellent [HOWTO](https://docs.python.org/3/howto/logging.html) guide and [Cookbook](https://docs.python.org/3/howto/logging-cookbook.html). These are rich source of information, and leave nothoing much to add. Following are some of the best practices in my opinion:

- Do NOT use ROOT logger directly throgh `logging.debug()`, `logging.error()` methods directly because it is easy to overlook their default behavior.
- Do NOT use module level loggers of variety `logging.getLogger(__name__)` because any complex project will require controlling logging through configuration (see next point). These may cause surprise if you forget to set `disable_existing_loggers` to false or overlook how modules are loaded and initialized. If use at all, call `logging.getLogger(__name__)` inside function, rather than outside at the beginning of a module.
- `dictConfig` (in `yaml`) offers right balance of versatility and flexibility compared to `ini` based `fileConfig`or doing it in code. Specifying logger in config files allows you to use different logging levels and infra in prod deployment, stage deployments, and local debugging (with increasingly more logs).

Sending logs to multiple data stores and tools for processing can be controled by a [log configuration](https://docs.python.org/3/library/logging.config.html). Each logger has a format and multiple handlers can be associated with a logger. Here is a part of `configs/todoList-local.yaml`:

``` yaml
logging:
  version: 1
  formatters:
    brief:
      format: '%(asctime)s %(name)s %(levelname)s : %(message)s'
    detailed:
      format: 'time="%(asctime)s" logger="%(name)s" level="%(levelname)s" file="%(filename)s" lineno=%(lineno)d function="%(funcName)s" %(message)s'
  handlers:
    console:
      class: logging.StreamHandler
      level: INFO
      formatter: brief
      stream: ext://sys.stdout
    file:
      class : logging.handlers.RotatingFileHandler
      level: DEBUG
      formatter: detailed
      filename: /tmp/taskservice-app.log
      backupCount: 3
  loggers:
    taskservice:
      level: DEBUG
      handlers:
        - console
        - file
      propagate: no
    tornado.access:
      level: DEBUG
      handlers:
        - file
    tornado.application:
      level: DEBUG
      handlers:
        - file
    tornado.general:
      level: DEBUG
      handlers:
        - file
  root:
    level: WARNING
    handlers:
      - console
```

Notice that this configuration not just defines a logger `taskservice` for this service, but also modifies behavior of Tornado's general logger. There are several pre-defined [handlers](https://docs.python.org/3/library/logging.handlers.html). Here the SteamHandler and RotatingFileHandler are being used to write to console and log files respectively.

### Tornado

Tornado has several hooks to control when and how logging is done:

- [`log_function`](https://www.tornadoweb.org/en/stable/web.html#tornado.web.Application.settings): function Tornado calls at the end of every request to log the result.
- [`write_error`](https://www.tornadoweb.org/en/stable/web.html#tornado.web.RequestHandler.write_error): to customize the error response. Information about the error is added to the log context.
- [`log_exception`](): to log uncaught exceptions. It can be overwritten to log in logfmt format.

### Log Inspection

**Start the server:**

It will show the console log:

``` bash
$ python3 taskservice/tornado/server.py --port 8080 --config ./configs/todoList-local.yaml --debug

2022-09-21 15:29:02,243 taskservice INFO : message="STARTING" service_name="TodoList" port=8080
```

**Watch the logs:**

``` bash
$ tail -f /tmp/taskservice-app.log

time="2022-09-21 15:29:52,088" logger="taskservice" level="DEBUG" file="logutils.py" lineno=56 function="log" req_id="c297ded2a4454d7cbf3cb21aec114b24" method="GET" uri="/tasks" ip="127.0.0.1" message="REQUEST"
```

**Send a request:**

```bash
$ curl -i -X POST http://localhost:8080/tasks -d '{"title": "Task1"}'

HTTP/1.1 201 Created
Server: TornadoServer/6.0.3
Content-Type: text/html; charset=UTF-8
Date: Tue, 17 Mar 2020 07:26:32 GMT
Location: /tasks/7feec2df29fd4b039028ad351bafe422
Content-Length: 0
Vary: Accept-Encoding
```

The console log will show brief log entries:

``` log
2020-03-17 12:56:32,784 taskservice INFO : req_id="e6cd3072530f46b9932946fd65a13779" method="POST" uri="/tasks" ip="::1" message="RESPONSE" status=201 time_ms=1.2888908386230469
```

The log file will show logfmt-style one-line detailed canonical log entries:

``` log
time="2022-09-21 15:56:05,291" logger="taskservice" level="DEBUG" file="logutils.py" lineno=56 function="log" req_id="f9845edaab90435abcc0312eca43336e" method="GET" uri="/tasks" ip="127.0.0.1" message="REQUEST" service_name="TodoList"
```

### Unit and Integration Tests

Tests are quiet by default:

``` bash
$ ./run.py lint
$ ./run.py typecheck

$ ./run.py test -v

test_todoList_endpoints (integration.tornado_app_taskservice_handlers_test.TestTodoListServiceApp) ... ok
test_default_handler (unit.tornado_app_handlers_test.TaskServiceTornadoAppUnitTests) ... ok

----------------------------------------------------------------------
Ran 2 tests in 0.049s

OK

$ coverage run --source=taskservice --omit="taskservice/tornado/server.py" --branch ./run.py test

..
----------------------------------------------------------------------
Ran 2 tests in 0.062s
OK

$ coverage report

Name                              Stmts   Miss Branch BrPart  Cover
-------------------------------------------------------------------
taskservice/__init__.py               3      0      0      0   100%
taskservice/service.py               25      1      0      0    96%
taskservice/tornado/__init__.py       0      0      0      0   100%
taskservice/tornado/app.py          105      6     18      6    90%
taskservice/utils/__init__.py         0      0      0      0   100%
taskservice/utils/logutils.py        28      0      6      0   100%
-------------------------------------------------------------------
TOTAL                               161      7     24      6    93%
```

If you want to change the log message during tests, change log level from ERROR to INFO:

``` python
# tests/unit/tornado_app_handlers_test.py

IN_MEMORY_CFG_TXT = '''
service:
  name: Todo List Test
logging:
  version: 1
  root:
    level: INFO
'''
```

With that change, if you run the tests, you can examine the logs:

``` log
$ ./run.py test

INFO:taskservice:req_id="fa90c2cecffe42059ee456e9b0eda30e" method="GET" uri="/tasks/" ip="127.0.0.1" message="RESPONSE" status=200 time_ms=0.8268356323242188
INFO:taskservice:req_id="8d31f561267f4f1b9c33fb0430841e35" method="POST" uri="/tasks/" ip="127.0.0.1" message="RESPONSE" status=201 time_ms=0.3809928894042969
WARNING:taskservice:req_id="181fd03c2da34a359183674a82f388b6" method="POST" uri="/tasks/" ip="127.0.0.1" reason="Invalid JSON body" message="RESPONSE" status=400 time_ms=1.6570091247558594 trace=Traceback.....
```