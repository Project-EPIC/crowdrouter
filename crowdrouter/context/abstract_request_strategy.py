from abc import ABCMeta, abstractmethod, abstractproperty
from ..errors import NoRequestFoundError, NoSessionFoundError, InvalidRequestError
import ipdb

#The AbstractRequestStrategy class encapsulates differences in the request objects passed to the
#CrowdRouter via varying frameworks such as Django, Flask, Tornado, etc.
class AbstractRequestStrategy:
    __metaclass__ = ABCMeta
    request = None
    session = None
    path = None
    method = None
    form = None
    data = None
    auth = None

    @abstractmethod
    def __init__(self):
        pass

    @staticmethod
    def factory(request, session=None):
        from flask_request_strategy import FlaskRequestStrategy
        from django_request_strategy import DjangoRequestStrategy
        from mock_request_strategy import MockRequestStrategy
        clazz = request.__class__.__name__

        #Request MUST exist.
        if request == None:
            raise NoRequestFoundError
        #Sessions MUST be turned ON.
        if session == None:
            if not hasattr(request, "session") or request.session == None:
                raise NoSessionFoundError
        #These are required Request paramters.
        if not request.method:
            raise InvalidRequestError(value="Request parameter 'method' is required.")
        if not request.path:
            raise InvalidRequestError(value="Request parameter 'path' is required.")

        if clazz == "LocalProxy":
            return FlaskRequestStrategy(request, session)
        elif clazz == "WSGIRequest":
            return DjangoRequestStrategy(request)
        elif clazz == "MockRequest":
            return MockRequestStrategy(request)
        else:
            raise NoRequestFoundError(value="Request Class %s not found. Cannot continue." % clazz)


    def __repr__(self):
        return "<%s>" % self.__class__.__name__