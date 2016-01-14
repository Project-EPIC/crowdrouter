from decorators import task
from abc import ABCMeta, abstractmethod, abstractproperty
from utils import METHOD_GET, METHOD_POST

#The AbstractTask superclass is inheritable for crowdwork implementations.
#Every AbstractTask has a exec_request() and exec_response() method that mirrors the rendering and validating activities
#that are associated with every crowd task, respectively. Subclasses may extend this definition as necessary.
class AbstractTask:
    __metaclass__ = ABCMeta
    _crowd_request = None

    @abstractmethod
    def __init__(self, crowd_request):
        self._crowd_request = crowd_request

    def execute(self, *args, **kwargs):
        if self.get_method() == METHOD_GET:
            return self.exec_request()
        elif self.get_method() == METHOD_POST:
            return self.exec_response()
        raise NoTaskFoundError()

    @abstractmethod
    @task
    def exec_request(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    @task
    def exec_response(self, *args, **kwargs):
        raise NotImplementedError

    def get_crowd_request(self):
        return self._crowd_request

    def get_name(self):
        return self._crowd_request.get_task_name()

    def get_method(self):
        return self._crowd_request.get_request().get("method")
