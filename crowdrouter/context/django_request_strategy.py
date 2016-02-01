import abstract_request_strategy
from ..errors import InvalidRequestError

class DjangoRequestStrategy(abstract_request_strategy.AbstractRequestStrategy):
    def __init__(self, request):
        try:
            self.request = request
            self.session = request.session
            self.path = request.path
            self.data = request.REQUEST or request.GET or {}
            self.method = request.method
            self.form = request.POST or request.FILES or {}
        except:
            raise InvalidRequestError(value="DjangoRequestStrategy cannot properly bind all needed variables for request %s." % request)