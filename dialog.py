import datetime


class Dialog:
    def __init__(self, ask, response, file):
        self.ask = ask
        self.response = response
        self.file = file
        self.time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
