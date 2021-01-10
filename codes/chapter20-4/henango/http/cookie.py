from datetime import datetime
from typing import Optional


class Cookie:
    name: str
    value: str
    expires: Optional[datetime]
    max_age: Optional[int]
    domain: str
    path: str
    secure: bool
    http_only: bool

    def __init__(
        self,
        name: str,
        value: str,
        expires: datetime = None,
        max_age: int = None,
        domain: str = "",
        path: str = "",
        secure: bool = False,
        http_only: bool = False,
    ):
        self.name = name
        self.value = value
        self.expires = expires
        self.max_age = max_age
        self.domain = domain
        self.path = path
        self.secure = secure
        self.http_only = http_only
