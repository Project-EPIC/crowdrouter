from abc import ABCMeta, abstractmethod, abstractproperty
from ..decorators import task
from ..errors import NoTaskFoundError
from ..utils import METHOD_GET, METHOD_POST
import ipdb

#The AbstractTask superclass is inheritable for crowdwork implementations.
#Every AbstractTask has a get() and post() method that mirrors the rendering and validating activities
#that are associated with every crowd task, respectively. Subclasses may extend this definition as necessary.
class AbstractTask:
    __metaclass__ = ABCMeta
    workflow = None #Parent WorkFlow.
    crowd_request = None
    path = None #Task URI
    auth_required = False

    def __init__(self, crowd_request, workflow):
        self.crowd_request = crowd_request
        self.path = crowd_request.get_path()
        self.workflow = workflow

    def execute(self, **kwargs):
        method = self.crowd_request.get_method()
        if method == METHOD_GET:
            return self.get(**kwargs)
        elif method == METHOD_POST:
            return self.post(**kwargs)
        raise NoTaskFoundError(value="No/Invalid Method (%s) found in CrowdRequest." % method)

    #This boolean authentication function needs to be implemented if class decorator is declared.
    #Define authentication protocol for Task here.
    def is_authenticated(self):
        raise NotImplementedError

    def get_name(self):
        return self.__class__.__name__

    @abstractmethod
    @task("/")
    def get(self, **kwargs):
        raise NotImplementedError

    @abstractmethod
    @task("/")
    def post(self, **kwargs):
        raise NotImplementedError
