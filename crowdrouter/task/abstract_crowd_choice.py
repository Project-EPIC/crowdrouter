from abc import ABCMeta, abstractmethod
from ..decorators import choice

class AbstractCrowdChoice:
    __metaclass__ = ABCMeta
    t1 = None
    t2 = None
    workflow = None

    def __init__(self, workflow):
        self.workflow = workflow

    #Use this implementation to provide branching.
    def execute(self, crowd_request, **kwargs):
        task = self.choice(crowd_request)(self.workflow)
        return task.execute(crowd_request)

    def get_name(self):
        return self.__class__.__name__

    #The Choice method for this class must return either AbstractTask subclass t1 or t2.
    @abstractmethod
    @choice
    def choice(self, crowd_request):
        pass
