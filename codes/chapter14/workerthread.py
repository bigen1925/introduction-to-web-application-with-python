import os
import textwrap
import traceback
from datetime import datetime
from socket import socket
from threading import Thread
from typing import Tuple


class WorkerThread(Thread):
    # 実行ファイルのあるディレクトリ
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    # 静的配信するファイルを置くディレクトリ
    STATIC_ROOT = os.path.join(BASE_DIR, "static")
    # 静的ファイルを配信するパスのprefix
    STATIC_URL = "/static/"

    def __init__(self, client_socket: socket, address: Tuple[str, int]):
        super().__init__()

        self.client_socket = client_socket
        self.client_address = address

    def run(self) -> None:
        """
        クライアントと接続済みのsocketを引数として受け取り、
        リクエストを処理してレスポンスを送信する
        """

        try:

            # クライアントから送られてきたデータを取得する
            request = self.client_socket.recv(4096)

            # クライアントから送られてきたデータをファイルに書き出す
            with open("server_recv.txt", "wb") as f:
                f.write(request)

            # HTTPリクエストをパースする
            method, path, http_version, request_header, request_body = self.parse_http_request(request)

            response_body: bytes
            response_line: str
            # pathが/nowのときは、現在時刻を表示するHTMLを生成する
            if path == "/now":
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

            # pathがそれ以外のときは、静的ファイルからレスポンスを生成する
            else:
                try:
                    response_body = self.get_static_file_content(path)

                    # レスポンスラインを生成
                    response_line = "HTTP/1.1 200 OK\r\n"
                except OSError:
                    # レスポンスを取得できなかった場合は、ログを出力して404を返す
                    traceback.print_exc()

                    response_body = b"<html><body><h1>404 Not Found</h1></body></html>"
                    response_line = "HTTP/1.1 404 Not Found\r\n"

            # レスポンスヘッダーを生成
            response_header = self.build_response_header(response_body)

            # レスポンス全体を生成する
            response = (response_line + response_header + "\r\n").encode() + response_body

            # クライアントへレスポンスを送信する
            self.client_socket.send(response)

        except Exception:
            # リクエストの処理中に例外が発生した場合はコンソールにエラーログを出力し、
            # 処理を続行する
            print("=== Worker: リクエストの処理中にエラーが発生しました ===")
            traceback.print_exc()

        finally:
            # 例外が発生した場合も、発生しなかった場合も、TCP通信のcloseは行う
            print(f"=== Worker: クライアントとの通信を終了します remote_address: {self.client_address} ===")
            self.client_socket.close()

    def parse_http_request(self, request: bytes) -> Tuple[str, str, str, bytes, bytes]:
        """
        HTTPリクエストを
        1. method: str
        2. path: str
        3. http_version: str
        4. request_header: bytes
        5. request_body: bytes
        に分割/変換する
        """

        # リクエスト全体を
        # - リクエストライン(1行目)
        # - リクエストヘッダー(2行目〜空行)
        # - リクエストボディ(空行〜)
        # にパースする
        request_line, remain = request.split(b"\r\n", maxsplit=1)
        request_header, request_body = remain.split(b"\r\n\r\n", maxsplit=1)

        # リクエストラインを文字列に変換してパースする
        method, path, http_version = request_line.decode().split(" ")

        return method, path, http_version, request_header, request_body

    def get_static_file_content(self, path: str) -> bytes:
        """
        リクエストpathから、staticファイルの内容を取得する
        """

        # pathの先頭の/を削除し、相対パスにしておく
        relative_path = path.lstrip("/")
        # ファイルのpathを取得
        static_file_path = os.path.join(self.STATIC_ROOT, relative_path)

        with open(static_file_path, "rb") as f:
            return f.read()

    def build_response_header(self, response_body: bytes) -> str:
        """
        レスポンスヘッダーを構築する
        """

        response_header = ""
        response_header += f"Date: {datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')}\r\n"
        response_header += "Host: HenaServer/0.1\r\n"
        response_header += f"Content-Length: {len(response_body)}\r\n"
        response_header += "Connection: Close\r\n"
        response_header += "Content-Type: text/html\r\n"

        return response_header
