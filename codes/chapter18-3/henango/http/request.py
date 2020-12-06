class HTTPRequest:
    path: str
    method: str
    http_version: str
    headers: dict
    body: bytes
    params: dict

    def __init__(
        self,
        path: str = "",
        method: str = "",
        http_version: str = "",
        headers: dict = None,
        body: bytes = b"",
        params: dict = None,
    ):
        if headers is None:
            headers = {}
        if params is None:
            params = {}

        self.path = path
        self.method = method
        self.http_version = http_version
        self.headers = headers
        self.body = body
        self.params = params
