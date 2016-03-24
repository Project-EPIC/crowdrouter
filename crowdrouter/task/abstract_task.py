from abc import ABCMeta, abstractmethod, abstractproperty
from ..decorators import task
from ..errors import NoTaskFoundError, TaskError
from ..utils import METHOD_GET, METHOD_POST
import ipdb, inspect

#The AbstractTask superclass is inheritable for crowdwork implementations.
#Every AbstractTask has a get() and post() method that mirrors the rendering and validating activities
#that are associated with every crowd task, respectively. Subclasses may extend this definition as necessary.
class AbstractTask:
    __metaclass__ = ABCMeta
    workflow = None #Parent WorkFlow.
    auth_required = False

    def __init__(self, workflow):
        self.workflow = workflow

    def execute(self, crowd_request, **kwargs):
        method = crowd_request.get_method()
        if method == METHOD_GET:
            return self.get(crowd_request, **kwargs)
        elif method == METHOD_POST:
            return self.post(crowd_request, **kwargs)
        raise NoTaskFoundError(value="No/Invalid Method (%s) found in CrowdRequest." % method)

    #This boolean authentication function needs to be implemented if class decorator is declared.
    #Define authentication protocol for Task here.
    def is_authenticated(self):
        raise NotImplementedError

    def get_name(self):
        return self.__class__.__name__

    @abstractmethod
    @task
    def get(self, crowd_request, data, **kwargs):
        raise NotImplementedError

    @abstractmethod
    @task
    def post(self, crowd_request, form, **kwargs):
        raise NotImplementedError

    def __repr__(self):
        return "<Task: %s>" % (self.__class__.__name__)
