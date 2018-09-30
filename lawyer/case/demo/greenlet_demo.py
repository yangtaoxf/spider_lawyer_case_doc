import gevent


def func1():
    print("start func1")
    gevent.sleep(1)
    print("end func1")


def func2():
    print("start func2")
    gevent.sleep(1)
    print("end func2")


gevent.joinall([
    gevent.spawn(func1),
    gevent.spawn(func2),
])
