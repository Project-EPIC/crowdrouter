from errors import ImproperResponseError
import ipdb

class CrowdResponse:
    crowd_request = None
    status = None
    task = None
    response = None

    def __init__(self, response, task):
        try:
            self.task = task
            self.crowd_request = task.crowd_request
            self.response = response
            self.status = response["status"]
        except:
            raise ImproperResponseError

    def __repr__(self):
        return "<CrowdResponse: %s-%s-%s>" % (self.task.name, self.crowd_request.method, self.status)
