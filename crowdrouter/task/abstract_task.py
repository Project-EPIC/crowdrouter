from abc import ABCMeta, abstractmethod, abstractproperty
from ..decorators import task
from ..utils import METHOD_GET, METHOD_POST

#The AbstractTask superclass is inheritable for crowdwork implementations.
#Every AbstractTask has a exec_request() and exec_response() method that mirrors the rendering and validating activities
#that are associated with every crowd task, respectively. Subclasses may extend this definition as necessary.
class AbstractTask:
    __metaclass__ = ABCMeta
    crowd_request = None

    @abstractmethod
    def __init__(self, crowd_request):
        self.crowd_request = crowd_request

    def execute(self):
        if self.crowd_request.method == METHOD_GET:
            return self.exec_request()
        elif self.crowd_request.method == METHOD_POST:
            return self.exec_response()
        raise NoTaskFoundError()

    def get_name(self):
        return self.__class__.__name__

    @abstractmethod
    @task
    def exec_request(self):
        raise NotImplementedError

    @abstractmethod
    @task
    def exec_response(self):
        raise NotImplementedError
