import abstract_request_strategy
from ..errors import InvalidRequestError

class FlaskRequestStrategy(abstract_request_strategy.AbstractRequestStrategy):
    def __init__(self, request, session):
        try:
            self.request = request
            self.session = session
            self.path = request.path
            self.data = request.data or {}
            self.data.update(request.view_args)
            self.method = request.method
            self.form = request.form or {}
        except:
            raise InvalidRequestError(value="FlaskRequestStrategy cannot properly bind all needed variables for request %s." % request)
