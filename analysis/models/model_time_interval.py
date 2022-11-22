from datetime import timedelta

class TimeInterval:
    def __init__(self, start: timedelta, end: timedelta):
        if end < start:
            raise Exception('start interval must be less than end')

        self.start = start
        self.end = end

    def __str__(self):
        return f"{self.start} to {self.end}"
