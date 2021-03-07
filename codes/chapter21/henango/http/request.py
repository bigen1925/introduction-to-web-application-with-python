class HTTPRequest:
    path: str
    method: str
    http_version: str
    headers: dict
    cookies: dict
    body: bytes
    params: dict

    def __init__(
        self,
        path: str = "",
        method: str = "",
        http_version: str = "",
        headers: dict = None,
        cookies: dict = None,
        body: bytes = b"",
        params: dict = None,
    ):
        if headers is None:
            headers = {}
        if cookies is None:
            cookies = {}
        if params is None:
            params = {}

        self.path = path
        self.method = method
        self.http_version = http_version
        self.headers = headers
        self.cookies = cookies
        self.body = body
        self.params = params
