import textwrap
import urllib.parse
from datetime import datetime
from pprint import pformat
from typing import Tuple


def now(
    method: str,
    path: str,
    http_version: str,
    request_header: dict,
    request_body: bytes,
) -> Tuple[bytes, str]:
    """
    現在時刻を表示するHTMLを生成する
    """
    html = f"""\
        <html>
        <body>
            <h1>Now: {datetime.now()}</h1>
        </body>
        </html>
    """
    response_body = textwrap.dedent(html).encode()

    # レスポンスラインを生成
    response_line = "HTTP/1.1 200 OK\r\n"

    return response_body, response_line


def show_request(
    method: str,
    path: str,
    http_version: str,
    request_header: dict,
    request_body: bytes,
) -> Tuple[bytes, str]:
    """
    HTTPリクエストの内容を表示するHTMLを生成する
    """
    html = f"""\
        <html>
        <body>
            <h1>Request Line:</h1>
            <p>
                {method} {path} {http_version}
            </p>
            <h1>Headers:</h1>
            <pre>{pformat(request_header)}</pre>
            <h1>Body:</h1>
            <pre>{request_body.decode("utf-8", "ignore")}</pre>

        </body>
        </html>
    """
    response_body = textwrap.dedent(html).encode()

    # レスポンスラインを生成
    response_line = "HTTP/1.1 200 OK\r\n"

    return response_body, response_line


def parameters(
    method: str,
    path: str,
    http_version: str,
    request_header: dict,
    request_body: bytes,
) -> Tuple[bytes, str]:
    """
    POSTパラメータを表示するHTMLを表示する
    """

    # GETリクエストの場合は、405を返す
    if method == "GET":
        response_body = b"<html><body><h1>405 Method Not Allowed</h1></body></html>"
        response_line = "HTTP/1.1 405 Method Not Allowed\r\n"

    elif method == "POST":
        post_params = urllib.parse.parse_qs(request_body.decode())
        html = f"""\
            <html>
            <body>
                <h1>Parameters:</h1>
                <pre>{pformat(post_params)}</pre>                        
            </body>
            </html>
        """
        response_body = textwrap.dedent(html).encode()

        # レスポンスラインを生成
        response_line = "HTTP/1.1 200 OK\r\n"

    return response_body, response_line
