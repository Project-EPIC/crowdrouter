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
