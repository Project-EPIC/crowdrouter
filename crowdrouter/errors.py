class CrowdRouterError(Exception):
    def __init__(self, value=None):
        if value:
            self.value = value
        else:
            self.value = "Something went wrong in the CrowdRouter."

class AuthenticationError(CrowdRouterError):
    def __init__(self, value=None):
        if value:
            self.value = value
        else:
            self.value = "Authentication failed for this request."

class PipelineError(CrowdRouterError):
    def __init__(self, value=None):
        if value:
            self.value = value
        else:
            self.value = "Something went wrong with the Pipeline. Please try again."

class CrowdChoiceError(CrowdRouterError):
    def __init__(self, value=None):
        if value:
            self.value = value
        else:
            self.value = "Something went wrong with the CrowdChoice. Please try again."

class InvalidRequestStrategyError(CrowdRouterError):
    def __init__(self, value=None):
        if value:
            self.value = value
        else:
            self.value = "Invalid RequestStrategy instance used."

class InvalidRequestError(CrowdRouterError):
    def __init__(self, value=None):
        if value:
            self.value = value
        else:
            self.value = "This request object cannot be used because it is not recognized by the CrowdRouter."

class InvalidSessionError(CrowdRouterError):
    def __init__(self, value=None):
        if value:
            self.value = value
        else:
            self.value = "This session class cannot be used because it is not recognized by the CrowdRouter. Please use a dictionary-like interface."

class ImproperResponseError(CrowdRouterError):
    def __init__(self, value=None):
        if value:
            self.value = value
        else:
            self.value = "Improper Response. Please make sure response is formatted as dict and contains required fields."

class NoRequestFoundError(CrowdRouterError):
    def __init__(self, value=None):
        if value:
            self.value = value
        else:
            self.value = "No Request was found. CrowdRouter must have a request+session object in order to function properly."

class NoSessionFoundError(CrowdRouterError):
    def __init__(self, value=None):
        if value:
            self.value = value
        else:
            self.value = "No Session was found. CrowdRouter must have a request+session object in order to function properly."

class NoTaskFoundError(CrowdRouterError):
    def __init__(self, value=None):
        if value:
            self.value = value
        else:
            self.value = "No Task was found with that name."

class NoWorkFlowFoundError(CrowdRouterError):
    def __init__(self, value=None):
        if value:
            self.value = value
        else:
            self.value = "No WorkFlow was found with that name."

class TaskError(CrowdRouterError):
    ERROR_CODE_STATUS_MISSING = 0
    def __init__(self, value=None):
        if value:
            self.value = value
        else:
            self.value = "Something went wrong with the Task. Please check stack trace."
