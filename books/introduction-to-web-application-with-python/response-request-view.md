---
title: "Request / Response / View クラスを作って見通しを良くする"
---
# リファクタリングする

動的レスポンスを生成するエンドポイントも3つになってきて、`workerthread.py`も200行近くになってきました。

現時点でも、1ファイルで多種多様なことをやっているため、200行でもかなり見通しが悪くごちゃごちゃしたモジュールになってきてしまいました。

しかも、皆さんがこのWebアプリケーションを進化させていくとエンドポイントはますます増えていきます。
そのたびに`workerthread.py`に追記していたのではメンテナンスできなくなるのは目に見えています。
責務の切り分けとファイル分割を行って`workerthread.py`の見通しを良くしていく必要がでてきたといえるしょう。

つまり、そろそろ**リファクタリングの季節がやってきた**というわけです。

本章では、「エンドポイントごとに動的にレスポンスボディを生成している処理」を外部モジュールへ切り出して行きます。

# STEP1: 単に関数として切り出してみる

まずは、エンドポイントごとのHTML生成処理を、単純にまるっと別のモジュールへ切り出してみましょう。

切り出す先のモジュールの名前は、`views`とします。
コネクションがどうとか、ヘッダーのパースがこうとか、そういったHTTPの事情は関知せず、見た目(view)の部分（= リクエストボディ）を生成することだけを責務として持つモジュールだからです。

## ソースコード

**`study/workerthread.py`**
https://github.com/bigen1925/introduction-to-web-application-with-python/blob/main/codes/chapter16/workerthread.py#L50-L59

**`study/views.py`**
https://github.com/bigen1925/introduction-to-web-application-with-python/blob/main/codes/chapter16/views.py

## 解説
### `study/workerthread.py`
#### 57-66行目

```python
            if path == "/now":
                response_body, content_type, response_line = views.now()

            elif path == "/show_request":
                response_body, content_type, response_line = views.show_request(
                    method, path, http_version, request_header, request_body
                )

            elif path == "/parameters":
                response_body, content_type, response_line = views.parameters(method, request_body)
```

前回まで、HTMLを生成する処理をpathごとにベタベタと書いていたのですが、まずはその部分を`views`モジュールの関数に切り出すことにしました。

これによって、

- `workerthread.py`は、HTTPリクエストを受け取り、解析(パース)して、pathに応じた`views`モジュールの関数からレスポンスの内容を取得し、HTTPレスポンスを構築してクライアントへ返す。
- `views.py`は、pathごとに応じた関数を持ち、リクエストの内容を受け取り動的に生成したレスポンスの内容を返す

という責務分担となり、「パスに応じたレスポンスの内容を動的に生成する」という仕事が`views`に切り出せました。

### `study/views.py`

```python
import textwrap
import urllib.parse
from datetime import datetime
from pprint import pformat
from typing import Tuple, Optional


def now() -> Tuple[bytes, Optional[str], str]:
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

    # Content-Typeを指定
    content_type = "text/html; charset=UTF-8"

    # レスポンスラインを生成
    response_line = "HTTP/1.1 200 OK\r\n"

    return response_body, content_type, response_line


def show_request(
    method: str,
    path: str,
    http_version: str,
    request_header: dict,
    request_body: bytes,
) -> Tuple[bytes, Optional[str], str]:
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

    # Content-Typeを指定
    content_type = "text/html; charset=UTF-8"

    # レスポンスラインを生成
    response_line = "HTTP/1.1 200 OK\r\n"

    return response_body, content_type, response_line


def parameters(
    method: str,
    request_body: bytes,
) -> Tuple[bytes, Optional[str], str]:
    """
    POSTパラメータを表示するHTMLを表示する
    """

    # GETリクエストの場合は、405を返す
    if method == "GET":
        response_body = b"<html><body><h1>405 Method Not Allowed</h1></body></html>"
        content_type = "text/html; charset=UTF-8"
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

        # Content-Typeを指定
        content_type = "text/html; charset=UTF-8"

        # レスポンスラインを生成
        response_line = "HTTP/1.1 200 OK\r\n"

    return response_body, content_type, response_line
```

こちらも難しいことは特にないでしょう。
もともと`workerthread.py`にかかれていたレスポンスの動的生成の処理をそっくりそのまま持ってきただけです。

-------

views関数を切り出したのは良いのですが、今のままでは関数ごとに引数の数が違い、
「このpathを処理する仮数はコレとコレの引数が必要で、こっちのpathを処理する関数はアレとアレとアレの引数が必要で・・・」
といった具合に呼び出す側が、呼び出される側の詳細を知っていなくてはいけなくなっています。

プログラミングの世界では、片方のモジュールが、相手のモジュールの詳細をできるだけ知らなくて良いように作ると、ソースコードはシンプルになることが知られています。

次のSTEPではもう少しリファクタリングを進め、そのことを実感していきましょう。

# STEP2: views関数のインターフェースを統一する

今`WorkerThread`クラスが`views`関数の詳細を知らなくてはいけないのは、関数ごとに引数として何がいくつ必要かわからないと関数が呼び出せないからです。

この状態を解消するのに簡単な方法は、**「各関数がどのパラメータを使うかはしらないけど、とにかく全部渡しちゃう」** というやり方です。

## ソースコード
実際に、ソースコードを見てみましょう。

**`study/workerthread.py`**
https://github.com/bigen1925/introduction-to-web-application-with-python/blob/main/codes/chapter16-2/workerthread.py

**`study/views.py`**
https://github.com/bigen1925/introduction-to-web-application-with-python/blob/main/codes/chapter16-2/views.py

## 解説
### `study/views.py`
まずは`views.py`から見ておきましょう

#### 8-14行目, 66-72行目
```python
def now(
    method: str,
    path: str,
    http_version: str,
    request_header: dict,
    request_body: bytes,
) -> Tuple[bytes, Optional[str], str]:
```
```python
def parameters(
    method: str,
    path: str,
    http_version: str,
    request_header: dict,
    request_body: bytes,
) -> Tuple[bytes, Optional[str], str]:
```

全てのview関数で引数を統一し、全てのリクエスト情報を受取れるようにしました。
関数内ではこれらの引数は使わないのですが、受け取れるようにしておいてあげることで、呼び出す側は「何が必要で何が不要」かは考えなくて済むようになります。

### `study/workerthread.py`
次に、view関数を呼び出す側です。

#### 29-34行目
```python
    # pathとview関数の対応
    URL_VIEW = {
        "/now": views.now,
        "/show_request": views.show_request,
        "/parameters": views.parameters,
    }
```
pathとview関数の対応を定数として定義しました。
pathをキーとして、pathに対応する**view関数を値にもつ**辞書です。

:::details コラム: pythonの関数は第一級オブジェクト
言語によっては、上記のように「"関数"を辞書(or 連想配列)の値としてセット」したり、「"関数"を変数に代入」したりすることに驚く人もいるかもしれません。

しかし、pythonではこれは正当な扱い方です。

変数への代入や、演算や関数への（引数・戻り値として）受け渡しなど、値としての全ての扱いが可能なオブジェクトを**第一級オブジェクト**といいます。
pythonでは**全てのオブジェクトが第一級オブジェクト**であり、関数も例外ではありません。

そのため、変数に関数を代入したり、関数を受け取り関数を返す関数などを作成することも可能です。

後者は「メタプログラミング」として知られており、興味がある方は調べてみると良いでしょう。
:::

#### 64-69行目

```python
            # pathに対応するview関数があれば、関数を取得して呼び出し、レスポンスを生成する
            if path in self.URL_VIEW:
                view = self.URL_VIEW[path]
                response_body, content_type, response_line = view(
                    method, path, http_version, request_header, request_body
                )
```

`path in self.URL_VIEW`では、`self.URL_VIEW`という辞書のキーの中に`path`が含まれているかどうかを調べています。
つまり、pathに対応するview関数が登録されているか確認しています。

登録されていた場合、そのキーに対応する辞書の値を取得し、変数`view`へ代入しています。
つまり、変数`view`には(view関数を呼び出した返り値ではなく)**view関数**が代入されます。

最後の行では`view(~~)`とすることで、変数`view`に代入された関数を呼び出し、返り値を取得しています。

---

注目すべきなのは、**全てのview関数が同じ引数(`method, path, http_version, request_header, request_body`)を受け取るようになったことで、view関数が抽象化されている点です。**

以前までは関数ごとに引数が違ったので、ひとくちに「view関数を呼び出す」と言っても「その関数が具体的になんという関数なのか」が分からないと正しく呼び出せませんでした。
しかし、引数が統一（= インターフェースが統一）されることで、**「具体的に何ていう関数なのかは知らないけど、とにかく呼び出せる」** ようになっているのです。

これにより、`workerthread`内ではpath（または関数）に応じたif分岐が不要になりました。

::: details コラム: 抽象化
このように、「それが具体的なモノの中から、共通な性質の一部だけを抜き出すことで、具体的なモノを扱わなくてすむようにする」ことを**抽象化する**と呼び、プログラミングにおいては非常に重要なテクニックとなります。

今回でいうと、`now()` `show_rewuest()` `parameters`といった具体的な関数から、インターフェースを統一することで
「`method, path, http_version, request_header, request_body`という5つの引数を受け取り、`response_body, response_line`という2つの値を返す」
という性質だけを抜き出す(=抽象化する)ことで、呼び出す側は
「具体的に何関数かしらないけど、5つの引数を与えて呼び出す」
というように扱えるようにしたということです。

あるいは、「抽象化するためにインターフェースを統一した」とも言えるでしょう。
:::

# STEP3: view関数のインターフェースを簡略化する

view関数のインターフェースが共通化され、呼び出す側の見通しがよくなったのは良いことですが、いかんせん引数5つは多いです。

HTTPリクエストがたくさんの情報を持っていること自体は逃げられない事実ではありますが、それがバラバラの変数に分散して格納されているのはどうも扱いにくいです。

なので、HTTPリクエストを表現するクラスを作成し、そちらに情報をまとめることにしましょう。

これにより、view関数のインターフェースも簡略化されます。

## ソースコード
すこし変更量は増えますが、一気にいってしまいましょう。
`study`の下に**`henango`というディレクトリを新規作成**し、**さらにその下に`http`というディレクトリを作成**し、以下の4ファイルを追加します。

**`study/henango/__init__.py`**
https://github.com/bigen1925/introduction-to-web-application-with-python/blob/main/codes/chapter16-3/henango/__init__.py


**`study/henango/http/__init__.py`**
https://github.com/bigen1925/introduction-to-web-application-with-python/blob/main/codes/chapter16-3/henango/http/__init__.py

**`study/henango/http/request.py`**
https://github.com/bigen1925/introduction-to-web-application-with-python/blob/main/codes/chapter16-3/henango/http/request.py

**`study/henango/http/response.py`**
https://github.com/bigen1925/introduction-to-web-application-with-python/blob/main/codes/chapter16-3/henango/http/response.py


----

また、下記2ファイルも更新します。

**`study/views.py`**
https://github.com/bigen1925/introduction-to-web-application-with-python/blob/main/codes/chapter16-3/views.py

**`study/workerthread.py`**
https://github.com/bigen1925/introduction-to-web-application-with-python/blob/main/codes/chapter16-3/workerthread.py

## 解説

今回から、現在作っているWebアプリケーションのうち、Webサービスの内容に依存しない共通機能部分（メディアであろうが、社内ツールであろうが、どんなWebサービスであったとしても使い回せる部分 = **一般にWebフレームワークと呼ばれる部分**）をひとまとめのモジュールとし、**`henango`**と名付けました。
由来は、もちろん *「へなちょこDjango」* です。

今回新しく作るHTTPリクエスト/レスポンスを表すクラスを始め、今後追加していく共通機能はこのモジュール内に作っていきます。

なお、`webserver.py`や`woerkerthread.py`もこの`henango`モジュールに入っているべきなのですが、そちらのリファクタリングはまた後ほど取り扱います。

### `study/henango/__init__.py`
### `study/henango/http/__init__.py`

```python

```

これらは、空のファイルです。
`henango`と`http`というディレクトリが、pythonのパッケージであることを示すために必要なファイルです。

このファイルがあることで、外部のモジュールから
```python
from henango.http.requset import HTTPRequest
```

といったドットを使った表記でインポートすることが可能になります。

モジュールやインポートについては詳細は込み入ってしまうので、おまじないだと思って作っていただくか、[公式リファレンス](https://docs.python.org/ja/3/tutorial/modules.html) を参照してください。


### `study/henango/http/request.py`
```python
class HTTPRequest:
    path: str
    method: str
    http_version: str
    headers: dict
    body: bytes

    def __init__(
        self, path: str = "", method: str = "", http_version: str = "", headers: dict = None, body: bytes = b""
    ):
        if headers is None:
            headers = {}

        self.path = path
        self.method = method
        self.http_version = http_version
        self.headers = headers
        self.body = body

```
HTTPリクエストに関するデータを格納するクラスです。
これまで5つのデータ（`method`, `path`, `http_version`, `request_header`, `request_body`）はバラバラの変数として扱っていましたが、このクラスを用意することで`request.method`,`request.path`などと扱えるようになり見通しがよくなります。

辞書型であるはずの`headers`のデフォルト値に`None`を使っているのはpythonの仕様上のテクニックで、詳しくは[公式のチュートリアル](https://docs.python.org/ja/3/tutorial/controlflow.html#tut-defining) を参照してください。

このクラスは、例えば次のように使います。

使用例）
```python
request = HTTPRequest(
    method="POST",
    path="/index.html",
    http_version="HTTP/1.1",
    headers={
        "HOST": "localhost:8080",
    },
    body=b"foo=bar&foo2=bar2"
)
print(request.method)  # "POST"
print(request.path)  # "/index.html" 
```

このクラスを利用することで、今までview関数が5つのパラメータを受け取っていたところが1つのパラメータでまとめて受け取れるようになります。

### `study/henango/http/response.py`

```python
from typing import Optional


class HTTPResponse:
    status_code: int
    content_type: Optional[str]
    body: bytes

    def __init__(self, status_code: int = 200, content_type: str = None, body: bytes = b""):
        self.status_code = status_code
        self.content_type = content_type
        self.body = body

```

次にレスポンスクラスですが、こちらも同様にのHTTPレスポンスの情報を格納するクラスです。

もう詳しい説明は不要でしょう。

リクエストと同じく、view関数から値を返す際に使われます。

### `study/henango/http/views.py`

#### 9-75行目
```python
def now(request: HTTPRequest) -> HTTPResponse:
    #...

    return HTTPResponse(body=body, content_type=content_type, status_code=200)


def show_request(request: HTTPRequest) -> HTTPResponse:
    #...

    return HTTPResponse(body=body, content_type=content_type, status_code=200)


def parameters(request: HTTPRequest) -> HTTPResponse:
    # ...

    return HTTPResponse(body=body, content_type=content_type, status_code=status_code)

```
view関数の引数と返り値の型を変更しています。

これまで、引数は`method, path, http_version, request_header, request_body`の5つの値を受け取っていましたが、`HTTPRequest`型の`request`というパラメータを1つだけ受け取るようにしました。

また、返り値は`response_body, content_type, response_line`という3つの値を返していましたが、`HTTPRequest`型の値を1つだけ返すようにしました。
ここで注意してほしいのは、これまでresponse_lineという形で`status_code`以外にも`reason phrase`や`http_version`の情報も返していましたが、今回から`status_code`のみを返すようにResponseクラスを作っています。

これは、viewクラスはあくまで「動的なレスポンスの内容を生成する」ことだけに専念させ、HTTPのルールや慣習は極力扱わせないようにするためです。
（責務をできるだけ小さく保とうとしている）

なお上記では省略していますが、引数が変わったことにより関数内でのパラメータの参照の仕方も`path` => `request.path`などのように変更しています。

### `study/henango/http/workerthread.py`
こちらのファイルも色々な箇所が変わりました。
重要な場所から見ていきます。

#### 62-72行目, 112-133行目
```python
            # クライアントから送られてきたデータを取得する
            request_bytes = self.client_socket.recv(4096)
    
            # ...

            # HTTPリクエストをパースする
            request = self.parse_http_request(request_bytes)

            # pathに対応するview関数があれば、関数を取得して呼び出し、レスポンスを生成する
            if request.path in self.URL_VIEW:
                view = self.URL_VIEW[request.path]
                response = view(request)
```

```python
    def parse_http_request(self, request: bytes) -> HTTPRequest:
        # ...

        return HTTPRequest(method=method, path=path, http_version=http_version, headers=headers, body=request_body)
```

これまでHTTPリクエストをパースした後は5つの変数にバラバラに代入していましたが、パースした時点でHTTPRequestクラスとしてまとめて値を使うようにしています。

また、生のHTTPリクエストのバイト列と、パース後のHTTPRequestインスタンスを区別するために、生のHTTPリクエストのほうは`request_bytes`とrenameしています。
混同しないように気をつけてください。


### 38-43行目, 89-90行目, 148-153行目
```python
    # ステータスコードとステータスラインの対応
    STATUS_LINES = {
        200: "200 OK",
        404: "404 Not Found",
        405: "405 Method Not Allowed",
    }
```

```python
            # レスポンスラインを生成
            response_line = self.build_response_line(response)
```

```python
    def build_response_line(self, response: HTTPResponse) -> str:
        """
        レスポンスラインを構築する
        """
        status_line = self.STATUS_LINES[response.status_code]
        return f"HTTP/1.1 {status_line}"
```

これまでレスポンスラインの生成はviewが扱っていましたが、これを期にworkerthread側に寄せることにしました。
view関数では`status_code`だけを指定し、`response_line`の構築はここでやっています。


#### 92-94行目, 155-178行目
```python
            # レスポンスヘッダーを生成
            response_header = self.build_response_header(response, request)
```

```python
    def build_response_header(self, response: HTTPResponse, request: HTTPRequest) -> str:
        # ...

        return response_header
```

ヘッダーの生成処理も、HTTPResponseクラスとHTTPRequestクラスを使って引数を受け取るように変更しています。


# STEP4: URL_VIEWを外部モジュールへ切り出す
ところで、もともとの目的であった
「エンドポイントをどんどん増やしていくことを念頭においた時、拡張性やメンテナンス性があるようにする」
というのは果たされたでしょうか？
少なくとも、動的にレスポンスを生成する部分は`views`モジュールに集約したため、「エンドポイントに関わらず共通の処理」と「エンドポイントに特有の処理」は切り離せたため、メンテナンス性はかなり良くなったでしょう。

しかし、URLとview関数のマッピングを管理する`URL_VIEW`がまだ`workerthread`モジュール内にあるため、**エンドポイントを追加するたびに`workerthread`を変更しなければならない**ということには変わりません。
「拡張性が高い」と言うにはあと一工夫が必要そうです。

エンドポイントの拡張と共通機能部分を完全に切り離されている、つまり
**「エンドポイントを増やす時に共通機能部分を一切変更しなくてよいし、意識すらしなくてよい」**
という状態になっているとかなり拡張性が高い（安全かつ簡単に拡張できる）と言えるでしょう。

## ソースコード
そのように変更したのが下記です。

変更といっても実に簡単で、辞書`URL_VIEW`を外部モジュール`urls.py`へ切り出しただけです。

**`study/workerthread.py`**
https://github.com/bigen1925/introduction-to-web-application-with-python/blob/main/codes/chapter16-4/workerthread.py

**`study/urls.py`**
https://github.com/bigen1925/introduction-to-web-application-with-python/blob/main/codes/chapter16-4/urls.py

## 解説
### `study/workerthread.py`
#### 31行目付近
クラス変数としてURL_VIEWを定義していましたが、削除して`urls.py`内で定義するようにしました。

#### 62-65行目
```python
            # pathに対応するview関数があれば、関数を取得して呼び出し、レスポンスを生成する
            if request.path in URL_VIEW:
                view = URL_VIEW[request.path]
                response = view(request)
```
URL_VIEWを`urls.py`へ移動したため、参照方法が`self.URL_VIEW`から`URL_VIEW`へ変更になっています。

### `study/urls.py`
```python
import views

# pathとview関数の対応
URL_VIEW = {
    "/now": views.now,
    "/show_request": views.show_request,
    "/parameters": views.parameters,
}

```
`WorkerThread`クラスから移動してきました。


## 動かしてみる
この辺りでひとまず動作確認はしておきましょう。
今回はリファクタリングを行っただけですので、表面的な機能に変更はありません。

逆に、既存の機能が正常に動いているかどうかを確認しておいてください。
特に、`/index.html`で画像やCSSが適用されていることや、`/parameters`にGETリクエストしたときの`405 Method Not Allowed`などの確認を忘れないようにしてください。


# ここまでの振り返り
さて、ここまでかなりソースコードをいじくってきましたが、全体としてかなり見通しはよくなってきたのではないでしょうか！

また、エンドポイントを追加したい時には

1. `urls.py`にパスとview関数の対応を追加する
1. `views.py`にview関数を追加する

とするだけでよくなったので、とても簡単になりましたし共通部分機能について一切意識する必要がなくなりました。

保守性も拡張性も高くなり、有意義なリファクタリングとなりました。


