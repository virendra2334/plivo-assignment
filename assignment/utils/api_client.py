import requests


class RequestType(object):
    """More request types can be added here as and when we have more."""

    GET = 'GET'
    POST = 'POST'
    PUT = 'PUT'
    DELETE = 'DELETE'

class APIClient(object):
    """Generic class based implementation to inherited by 
    clients of all apis."""


    __rmethod_method_map = {
        RequestType.GET: requests.get,
        RequestType.POST: requests.post,
        RequestType.PUT: requests.put,
        RequestType.DELETE: requests.delete,
    }

    def _send_request(self, url, request_type, auth=None, data=None):
        
        method = self.__rmethod_method_map[request_type]
        kwargs = {}
        if auth:
            kwargs['auth'] = auth
        if data:
            kwargs['data'] = data

        return method(url, **kwargs)
