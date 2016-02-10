import abstract_request_strategy
from ..errors import InvalidRequestError

class MockRequestStrategy(abstract_request_strategy.AbstractRequestStrategy):
    def __init__(self, request):
        try:
            self.request = request
            self.session = request.session
            self.path = request.path
            self.data = request.data or {}
            self.method = request.method
            self.form = request.form or {}
        except:
            raise InvalidRequestError(value="MockRequestStrategy cannot properly bind all needed variables for request %s." % request)
