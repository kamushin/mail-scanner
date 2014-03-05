import re
import poplib
import imaplib
testNum = 5  # retry time for fail login
timeout = 10


class emailError(Exception):

    def __init__(self, msg):
        super().__init__()
        self.msg = msg


class emailFormatError(emailError):

    def __init__(self, msg):
        super().__init__(msg)


class emailDomainNotFind(emailError):

    def __init__(self, msg):
        super().__init__(msg)


class EmailLogin(object):

    """domain,host,hostType are lists.
    When init the class, read the conf.txt file to conf domain,host,hostType
    The checkImapMail/checkPopMail
    will find the suitable (domain,host) in these list to verify the password"""

    def __init__(self):
        super().__init__()
        # read conf file
        self.mailDomainList = []
        self.mailHostList = []
        self.mailType = []
        conf = open('conf', 'r')
        while True:
            line = conf.readline()
            if not line:
                conf.close()
                break
            content = line.split(' ')
            if len(content) == 3:
                self.mailType.append(content[0].strip())
                self.mailDomainList.append(content[1].strip())
                self.mailHostList.append(content[2].strip())

    def getMailDomain(self, email):
        emailparts = email.split('@')
        mailDomain = None
        if(len(emailparts) != 2):
            raise emailFormatError("Email format error:%s" % email)

        for i in self.mailDomainList:
            reDomain = re.compile(i)
            if reDomain.match(str(emailparts[1])):
                mailDomain = i
                break

        if mailDomain == None:
            raise emailDomainNotFind("Email Domain can't find:%s" % email)

        return mailDomain

    def checkImapMail(self, email, password, mailDomain):
        retR = re.compile('^\(\'OK')
        ret = None
        mailHost = None
        for i in range(len(self.mailDomainList)):
            # pop3 mail
            if mailDomain == self.mailDomainList[i] and self.mailType[i] == 'imap':
                mailHost = self.mailHostList[i]
                break
        if mailHost == None:
            return False

        for i in range(testNum):
            try:
                M = imaplib.IMAP4_SSL(mailHost)
                ret = M.login(email, password)
            except:
                pass
            if(retR.match(str(ret))):
                return True

        return False

    def checkPopMail(self, email, password, mailDomain):
        retR = re.compile('\(\d*,\s*\d*')
        mailHost = None
        for i in range(len(self.mailDomainList)):
            # pop3 mail
            if mailDomain == self.mailDomainList[i] and self.mailType[i] == 'pop':
                mailHost = self.mailHostList[i]
                break
        if mailHost == None:
            return False
        for i in range(testNum):
            try:
                mail = poplib.POP3(mailHost, timeout=timeout)
                mail.user(email)
                mail.pass_(password)
                ret = mail.stat()
                if(retR.match(str(ret))):
                    return True
            except:
                pass

        return False

    def login(self, email, password):
        domain = self.getMailDomain(email)
        if self.checkPopMail(email, password, domain):
            return True
        elif self.checkImapMail(email, password, domain):
            return True
        else:
            return False
