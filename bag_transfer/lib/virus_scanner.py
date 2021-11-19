import pyclamd


class VirusScan:
    RESULT_CONNERR = 0

    def __init__(self):
        self.clamObj = {}
        self.scan_result = None

    def is_ready(self):
        return self.conn()

    def conn(self):
        connected = False
        try:
            self.clamObj = pyclamd.ClamdUnixSocket()
            self.clamObj.ping()
            connected = True

        except pyclamd.ConnectionError as e:
            print(e)
            print("trying ClamdNetworkSocket")

            try:
                self.clamObj = pyclamd.ClamdNetworkSocket()
                self.clamObj.ping()
                connected = True
            except pyclamd.ConnectionError as e:
                # todo: can chain an email here
                print(e)
                print(
                    "could not connect to clamd server either by unix or network socket"
                )
        return connected

    def scan(self, file_or_dir):
        self.scan_result = self.clamObj.scan_file(file_or_dir)
