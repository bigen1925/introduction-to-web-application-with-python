---
title: "「伸び悩んでいる3年目Webエンジニアのための、Python Webアプリケーション自作入門」を更新しました"
emoji: "🚶"
type: "tech"
topics: [python, web, http]
published: true
---

# 本を更新しました

[チャプター「Request / Response / View クラスを作って見通しを良くする」](https://zenn.dev/bigen1925/books/introduction-to-web-application-with-python/viewer/response-request-view) を更新しました。

続きを読みたい方は、ぜひBookの「いいね」か「筆者フォロー」をお願いします ;-)

:::message alert
既存の記事/ソースコードについて、Chapter13以降で間違いがありました。

具体的には、処理の並列化を行ったあたりからContent-Typeを取り扱う処理が抜け落ちてしまっていたため、Chapter13-15に渡って修正を行いました。
すでにChapter13-15を実装済みの方は、再度記事とソースコードを見返してみてください。
:::

----

以下、書籍の内容の抜粋です。

------
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

------

# 続きはBookで！

[チャプター「Request / Response / View クラスを作って見通しを良くする」](https://zenn.dev/bigen1925/books/introduction-to-web-application-with-python/viewer/response-request-view) 
