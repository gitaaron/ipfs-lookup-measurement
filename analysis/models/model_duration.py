class Duration:
    def __init__(self, duration: float):
        self.duration = duration

    def __repr__(self):
        return f"{round(self.duration, 3)} (sec.)"
