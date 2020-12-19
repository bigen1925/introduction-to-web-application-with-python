import urllib.parse
from datetime import datetime
from pprint import pformat

from henango.http.request import HTTPRequest
from henango.http.response import HTTPResponse
from henango.templates.renderer import render


def now(request: HTTPRequest) -> HTTPResponse:
    """
    現在時刻を表示するHTMLを生成する
    """
    body = render("now", now=datetime.now())

    return HTTPResponse(body=body)


def show_request(request: HTTPRequest) -> HTTPResponse:
    """
    HTTPリクエストの内容を表示するHTMLを生成する
    """
    body = render(
        "show_request", request=request, headers=pformat(request.headers), body=request.body.decode("utf-8", "ignore")
    )

    return HTTPResponse(body=body)


def parameters(request: HTTPRequest) -> HTTPResponse:
    """
    POSTパラメータを表示するHTMLを表示する
    """

    # GETリクエストの場合は、405を返す
    if request.method == "GET":
        body = b"<html><body><h1>405 Method Not Allowed</h1></body></html>"

        return HTTPResponse(body=body, status_code=405)

    elif request.method == "POST":
        post_params = urllib.parse.parse_qs(request.body.decode())
        body = render("parameters", params=pformat(post_params))

        return HTTPResponse(body=body)


def user_profile(request: HTTPRequest) -> HTTPResponse:
    user_id = request.params["user_id"]

    body = render("user_profile", user_id=user_id)

    return HTTPResponse(body=body)
