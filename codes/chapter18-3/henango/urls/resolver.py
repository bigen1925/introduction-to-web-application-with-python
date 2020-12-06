from typing import Callable, Optional

from henango.http.request import HTTPRequest
from henango.http.response import HTTPResponse
from urls import url_patterns


class URLResolver:
    def resolve(self, request: HTTPRequest) -> Optional[Callable[[HTTPRequest], HTTPResponse]]:
        """
        URL解決を行う
        pathにマッチするURLパターンが存在した場合は、対応するviewを返す
        存在しなかった場合は、Noneを返す
        """
        for url_pattern in url_patterns:
            match = url_pattern.match(request.path)
            if match:
                request.params.update(match.groupdict())
                return url_pattern.view

        return None
