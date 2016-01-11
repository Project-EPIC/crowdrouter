class CrowdRequest:
    _task_name = None
    _request = None

    def __init__(self, task_name, request):
        self._task_name = task_name
        self._request = request

    def get_task_name(self):
        return self._task_name

    def get_request(self):
        return self._request
