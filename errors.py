class NoTaskFoundError(Exception):
    def __init__(self, value=None):
        if value:
            self.value = value
        else:
            self.value = "No Task was found with that name."

class NoWorkFlowFoundError(Exception):
    def __init__(self, value):
        if value:
            self.value = value
        else:
            self.value = "No WorkFlow was found with that name."

class TaskError(Exception):
    ERROR_CODE_STATUS_MISSING = 0
    def __init__(self, code):
        if code == ERROR_CODE_STATUS_MISSING:
            self.value = "The Task Response was not formatted properly. Please include a 'status' key to determine whether the task failed or succeeded."
        else:
            self.value = "Something went wrong with the Task. Please check stack trace."
