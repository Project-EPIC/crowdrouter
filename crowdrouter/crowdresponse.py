class CrowdResponse:
    _response = None
    _task = None

    def __init__(self, response, task):
        self._response = response
        self._task = task

    def get_response(self):
        return self._response

    def get_task(self):
        return self._task

    def get_status(self):
        return self._response["status"]

    def get_method(self):
        return self._task.get_method()

    def structure_response(self):
        return {
            "status": "OK",
            "method": self._task.get_method(),
            "task": self._task.get_name()
        }

    def __repr__(self):
        return "<CrowdResponse: %s-%s-%s>" % (self.get_task().get_name(), self.get_method(), self.get_status())
