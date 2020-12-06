import re
from re import Match
from typing import Callable, Optional
from henango.http.request import HTTPRequest
from henango.http.response import HTTPResponse


class URLPattern:
    pattern: str
    view: Callable[[HTTPRequest], HTTPResponse]

    def __init__(self, pattern: str, view: Callable[[HTTPRequest], HTTPResponse]):
        self.pattern = pattern
        self.view = view

    def match(self, path: str) -> Optional[Match]:
        # URLパターンを正規表現パターンへ変換
        # ex) '/user/<user_id>' => '/user/(?P<user_id>[^/]+)'
        pattern = re.sub(r"<(.+?)>", r"(?P<\1>[^/]+)", self.pattern)

        return re.match(pattern, path)
