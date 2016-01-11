from crowdresponse import CrowdResponse
from crowdrequest import CrowdRequest
from utils import print_msg
import ipdb

def task(run_func):
    def _wrapper(self, *args, **kwargs):
        print_msg("@task called for %s." % self)
        response = run_func(self, args, kwargs)
        return CrowdResponse(response, self)
    return _wrapper

def workflow(run_func):
    def _wrapper(self, crowd_request, *args, **kwargs):
        print_msg("@workflow called.")
        return run_func(self, crowd_request, args, kwargs)
    return _wrapper

def crowdrouter(run_func):
    def _wrapper(self, task, request, *args, **kwargs):
        print_msg("@crowdrouter called.")
        crowd_request = CrowdRequest(task, request)
        response = run_func(self, crowd_request, args, kwargs)
        if not isinstance(response, CrowdResponse):
            raise TypeError("CrowdRouter must return a CrowdResponse instance.")
        return response
    return _wrapper
