class NoTaskFoundError(Exception):
    def __init__(self):
        self.value = "No Task was found with that name."
