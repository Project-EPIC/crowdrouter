class InvalidRequestError(Exception):
    def __init__(self, value=None):
        if value:
            self.value = value
        else:
            self.value = "This request object cannot be used because it is not recognized by the CrowdRouter."

class InvalidSessionError(Exception):
    def __init__(self, value=None):
        if value:
            self.value = value
        else:
            self.value = "This session class cannot be used because it is not recognized by the CrowdRouter. Please use a dictionary-like interface."

class ImproperResponseError(Exception):
    def __init__(self, value=None):
        if value:
            self.value = value
        else:
            self.value = "Improper Response. Please make sure response is formatted as dict and contains required fields."

class NoRequestFoundError(Exception):
    def __init__(self, value=None):
        if value:
            self.value = value
        else:
            self.value = "No Request was found. CrowdRouter must have a request+session object in order to function properly."

class NoSessionFoundError(Exception):
    def __init__(self, value=None):
        if value:
            self.value = value
        else:
            self.value = "No Session was found. CrowdRouter must have a request+session object in order to function properly."

class NoTaskFoundError(Exception):
    def __init__(self, value=None):
        if value:
            self.value = value
        else:
            self.value = "No Task was found with that name."

class NoWorkFlowFoundError(Exception):
    def __init__(self, value=None):
        if value:
            self.value = value
        else:
            self.value = "No WorkFlow was found with that name."

class TaskError(Exception):
    ERROR_CODE_STATUS_MISSING = 0
    def __init__(self, value=None):
        if value:
            self.value = value
        else:
            self.value = "Something went wrong with the Task. Please check stack trace."
