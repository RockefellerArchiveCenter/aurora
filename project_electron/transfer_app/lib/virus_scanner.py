import pyclamd

class VirusScan:
    RESULT_CONNERR = 0

    def __init__(self):
        self.clamObj = {}
        self.conn()
        self.current = None

    def conn(self):
        try:
            self.clamObj = pyclamd.ClamdUnixSocket()
            self.clamObj.ping()

        except pyclamd.ConnectionError:
            self.clamObj = pyclamd.ClamdNetworkSocket()
            try:
                self.clamObj.ping()
            except pyclamd.ConnectionError:
                raise ValueError('could not connect to clamd server either by unix or network socket')

    def scan(self, file_or_dir):

        return self.clamObj.scan_file(file_or_dir)



