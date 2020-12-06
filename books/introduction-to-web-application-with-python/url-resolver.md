---
title: "[執筆中] URLパラメータを受け取れるようにする"
---

# 中〜大規模なWebサービスで必要となる機能
もうかなりフレームワークっぽくなってきて、現在ある機能だけでもそれなりのWebサービスが構築できると思います。
もうWebアプリケーションの基本的な仕組みが理解できて、満足してきた人もいるでしょう。

しかし、サービスが少し大きくなってくると共通して欲しくなる機能がまだ不足しています。
これ以降の章はそういった
*「小さなサービスでは今すぐに必要ではないが、世間ではよく使われる機能」*
について扱っていくことになります。

具体的な例として、

- URLパラメータ
- テンプレートエンジン
- Cookie
- Session
- Middleware
- Database連携

などがあります。

手始めに、本章では**URLパラメータ**を扱えるようにしていきます。

# URLパラメータを扱う
「URLパラメータを扱う」とは、URLの中に現れる文字列（= URLパラメータ）を変数としてアプリケーション内で扱うことを意味します。

言葉で説明すると難しいですが、よくある例として、
`/user/132/profile`
のようなpathにアクセスすると、IDが132のユーザーの詳細情報が表示される、などのWebページを見たことはないでしょうか。

私達の今のアプリケーションでは上記の`123`のような文字列を変数としては扱えないため、
```python
URL_VIEW = {
    '/user/1/profile': views.user1,
    '/user/2/profile': views.user2,
    '/user/3/profile': views.user3,
    # ...
}
```
などと1つずつpathを追加していくしかありません。
しかも、ユーザーの数が増えたり減ったりした状況には対応できません。

コレに対しては、例えば
```python
URL_VIEW = {
    '/user/<user_id>/profile': views.user
}
```
などと設定しておけば`/user/(数字)/profile`のpathが全てviews.userに紐付いて、view関数の中から`(数字)`の値にアクセスできるようになっていると便利です。

このような機能は、一般的なWebフレームワークであれば必ず備えている機能ですので、私達も実装してみましょう。

-----

URLパターンの扱い方は、

- URLパラメータのパターン指定の方法
→　`/user/<user_id>/profile`と書くのか、`/user/:user_id/profile`と書くのか
- パラメータへのアクセスの仕方
→　`request.params["user_id]`でアクセスできるのか、view関数の第2引数として渡されてくる(`def user(request, user_id):`となる)のか

などの観点でフレームワークごとに特色があります。

私たちのフレームワークでは、比較的簡単な下記の仕様で実装していこうと思います。

- **ルーティング設定には`/user/<user_id>/profile`のように、`<変数名>`の形式で指定する**
- **パラメータは、リクエストオブジェクトのparams属性(`request.params`)に`dict型`で格納/アクセスする**

## ソースコード
では、まずは上記の機能を実装したソースコードを見てみましょう

**`study/urls.py`**
https://github.com/bigen1925/introduction-to-web-application-with-python/blob/main/codes/chapter18/urls.py

**`study/views.py`**
https://github.com/bigen1925/introduction-to-web-application-with-python/blob/main/codes/chapter18/views.py

**`study/henango/http/request.py`**
https://github.com/bigen1925/introduction-to-web-application-with-python/blob/main/codes/chapter18/henango/http/request.py

**`study/henango/server/worker.py`**
https://github.com/bigen1925/introduction-to-web-application-with-python/blob/main/codes/chapter18/henango/server/worker.py

## 解説

### `study/urls.py`
#### 8行目
```python
URL_VIEW = {
    # ...
    "/user/<user_id>/profile": views.user_profile,
}
```
動作確認用のサンプルとして、URLパラメータを含むのパスを追加しました

### `study/views.py`
#### 80-94行目
```python
def user_profile(request: HTTPRequest) -> HTTPResponse:
    user_id = request.params["user_id"]
    html = f"""\
        <html>
        <body>
            <h1>プロフィール</h1>
            <p>ID: {user_id}
        </body>
        </html>
    """
    body = textwrap.dedent(html).encode()
    content_type = "text/html; charset=UTF-8"
    status_code = 200

    return HTTPResponse(body=body, content_type=content_type, status_code=status_code)
```
URLパラメータを扱うviewを追加しました。
```python
user_id = request.params["user_id"]
```
この部分で、`HTTPRequest`オブジェクトからURLパラメータを取得しているところが注目ポイントです。

画面としては、シンプルにユーザーIDのみが表示されるのみです。

### `study/henango/http/request.py`
```python
class HTTPRequest:
    # ...
    params: dict

    def __init__(
        # ...
        params: dict = None,
    ):
        # ...
        if params is None:
            params = {}

        # ...
        self.params = params

```
クエリパラメータをセットするため、`HTTPRequest`クラスに`params`属性を追加しました。

### `study/henango/server/worker.py`
#### 58-67行目

```python
            # pathにマッチするurl_patternを探し、見つかればviewからレスポンスを生成する
            for url_pattern, view in URL_VIEW.items():
                match = self.url_match(url_pattern, request.path)
                if match:
                    request.params.update(match.groupdict())
                    response = view(request)
                    break

            # pathにマッチするurl_patternが見つからなければ、静的ファイルからレスポンスを生成する
            else:
                # ...
```

今までは単純に`URL_VIEW`辞書のキーとpathが文字列として一致するかどうかでviewを検索していましたが、今回からは判定ロジックが複雑になるため`self.url_match()`というメソッドを新しく作成してその中で判定するようにしました。

`url_match()`の詳細は次に説明しますが、この関数はurl_patternがpathにマッチした場合は正規表現でお馴染みの`re`モジュールの`Match`オブジェクトを返します。
URLパラメータが含まれている場合は`.groupdict()`メソッドを実行することでパラメータが辞書で取得できます。

マッチしなかった場合は`None`を返すので、if文は実行されません。


また、`python`以外が母国語の方は馴染みがないかもしれませんが、ここでは`for-else`文を使っています。
`for`句が最後まで実行された（＝途中でbreakが呼ばれなかった）場合のみ、`else`句が実行されます。

### 174-178行目
```python
    def url_match(self, url_pattern: str, path: str) -> Optional[Match]:
        # URLパターンを正規表現パターンに変換する
        # ex) '/user/<user_id>/profile' => '/user/(?P<user_id>[^/]+)/profile'
        re_pattern = re.sub(r"<(.+?)>", r"(?P<\1>[^/]+)", url_pattern)
        return re.match(re_pattern, path)
```

ここでは、`/user/<user_id>/profile`のような私達独自のURL表現のことを、本プログラムでは`URLパターン`と呼ぶことにしています。
URLパターンは私達独自の記法ですので、そのままではpythonはpathとマッチするかどうかを判定できません。

ですので、まずはURLパターンを正規表現パターンに変換してpythonで扱えるようにしてから、マッチング判定をしています。
`(?P<name>pattern)`は名前付きグループといって、マッチしたグループを後から`.groupdict()`などを使って名前で取り出すことができます。

参考）https://docs.python.org/ja/3/howto/regex.html#non-capturing-and-named-groups

## 動作確認
では、まずは動作確認してみましょう。

サーバーを再起動したら、Chromeで`http://localhost:8080/user/123/profile`へアクセスしてみましょう。

次のような画面が表示されれば成功です。

![](https://storage.googleapis.com/zenn-user-upload/povdssdupnaeue6duipr7ka98ddh)

うまく表示された人は、`123`の部分を変えてみて、URLに合わせて画面表示が変わることも確認しておきましょう。

# リファクタリング STEP1 URLマッチング判定
最近リファクタリングしたばっかりですが、`worker.py`の責務がまた増えて複雑になってしまったので、またリファクタリングしておきましょう。
これぐらいの規模になると、機能追加とリファクタリングはセットになってきますね。

pathから目当てのviewを取得する処理（＝**URL解決**）だけでかなりのボリュームをしめているので、これを外部モジュールに切り出してスリムにしていきましょう。

まずは、pathとURLパターンのマッチング判定を外部へ切り出します。
色々なやり方がありますが、本書ではpathとviewの組み合わせの情報をオブジェクト化し、そのオブジェクト内にマッチング判定機能も持たせてしまうことにします。

## ソースコード
`henango`モジュールの下に、URL処理に関する機能をまとめた`urls`モジュールを作成しています。
`urls.py`というプロジェクト直下のファイルと同じ名前のモジュールでややこしいのですが、`Django`ではこのような名前になっていますので、リスペクトを込めてあえて同じにしています。

**`study/henango/urls/pattern.py`**
https://github.com/bigen1925/introduction-to-web-application-with-python/blob/main/codes/chapter18-2/henango/urls/pattern.py

**`study/urls.py`**
https://github.com/bigen1925/introduction-to-web-application-with-python/blob/main/codes/chapter18-2/urls.py

**`study/henango/server/worker.py`**
https://github.com/bigen1925/introduction-to-web-application-with-python/blob/main/codes/chapter18-2/henango/server/worker.py

## 解説
### `study/henango/urls/pattern.py`
```python
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
        """
        pathがURLパターンにマッチするか判定する
        マッチした場合はMatchオブジェクトを返し、マッチしなかった場合はNoneを返す
        """
        # URLパターンを正規表現パターンに変換する
        # ex) '/user/<user_id>/profile' => '/user/(?P<user_id>[^/]+)/profile'
        pattern = re.sub(r"<(.+?)>", r"(?P<\1>[^/]+)", self.pattern)
        return re.match(pattern, path)


```
attributeとしてURLパターンとview関数を持ち、`.match(path)`メソッドでpathとのマッチング判定ができるクラスです。

内容自体は単純だと思いますが、型注釈について補足しておきます。

`Callable[[HTTPRequest], HTTPResponse]`は関数を表す型注釈で、この場合は`HTTPRequest`インスタンスを受け取り、`HTTPResponse`を返す関数を意味します。

また、`Optional[Match]`は、「`Match`インスタンス、または`None`」を表す型です。

:::details コラム：pythonのCallable
便宜上`Callable`のことを「関数」と説明しましたが、厳密には「呼び出し可能オブジェクト」を意味します。
単純なスクリプトでは違いを覚える必要はありませんが、pythonistaを目指す方はきちんと理解しておく必要があるでしょう。

「呼び出し可能オブジェクト」は、オブジェクトの後ろに`()`を付けて特定の処理を呼び出せるオブジェクト全般のことで、関数は呼び出し可能オブジェクトの一種です。

このように言うということは、関数以外にも「呼び出し可能オブジェクト」はあるということです。

関数以外のCallableの代表例としては、「クラス」があります。
「クラス」の後ろに`()`をつけて「呼び出す」ことでインスタンス生成を行うことができます。

クラスは分かりやすい例ですが、他にも`__call__`メソッドが実装されたクラスのインスタンスがあります。
`__call__`を使うと、「関数として定義したわけではないが、まるで関数のように振る舞うオブジェクト」を作ることができます。

知らなかった方は、是非調べてみると良いでしょう。
:::

### `study/urls.py`

```python
import views
from henango.urls.pattern import URLPattern

# pathとview関数の対応
url_patterns = [
    URLPattern("/now", views.now),
    URLPattern("/show_request", views.show_request),
    URLPattern("/parameters", views.parameters),
    URLPattern("/user/<user_id>/profile", views.user_profile),
]

```
これまで`URL_VIEW`という「辞書」でルーティングを管理していましたが、要素のひとつひとつが`URLPattern`インスタンスとなり、キーも不要になったため「リスト」に変更しました。
また、要素のクラス名にあわせて、変数名を`url_patterns`に変更しています。

（ますますDjangoっぽくなってきましたね）

### `study/henango/server/worker.py`

#### 56-63行目
```python
            # pathにマッチするurl_patternを探し、見つかればviewからレスポンスを生成する
            for url_pattern in url_patterns:
                match = url_pattern.match(request.path)
                if match:
                    request.params.update(match.groupdict())
                    view = url_pattern.view
                    response = view(request)
                    break
```
これまで`URL_VIEW`だったところが`url_patterns`に変更になっています。

また、url_patternとpathのマッチング判定を`Worker`内のメソッドでやっていたところを、url_patternオブジェクト自身にやらせるようにしました。

これで、WorkerはURLのマッチング方法について何も知らなくてよくなり、責務が軽くなりました。

## 動作確認
リファクタリングですので機能に変更はありませんが、こまめに動作確認はしておきましょう。
`http://localhost:8080/user/123/profile` にアクセスしてエラーがないか確認しておいてください。

# リファクタリング STEP2 URL解決
マッチング判定を外部モジュールに切り出せたのはいいですが、URL解決処理はまだまだworkerに残っています。

残っているURL解決の部分も頑張って外部モジュールへ移していきましょう。

## ソースコード
URL解決部分を切り出したのがこちらです。

**`study/henango/urls/resolver.py`**
https://github.com/bigen1925/introduction-to-web-application-with-python/blob/main/codes/chapter18-3/henango/urls/resolver.py

**`study/henango/server/worker.py`**
https://github.com/bigen1925/introduction-to-web-application-with-python/blob/main/codes/chapter18-3/henango/server/worker.py

## 解説
### `study/henango/urls/resolver.py`
```python
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

```
以前まで`Worker`でやっていたURL解決の処理だけ切り出したクラスとなります。

処理の内容は変わっていないので、難しいところはないかと思います。

### `study/henango/server/worker.py`
### 57-64行目
```python
            # URL解決を試みる
            view = URLResolver().resolve(request)

            if view:
                # URL解決できた場合は、viewからレスポンスを取得する
                response = view(request)
            else:
                # URL解決できなかった場合は、静的ファイルからレスポンスを取得する
```

URL解決のための処理が外部に切り出せたおかげで、`Worker`クラスはURL解決の方法について何も知らなくて良くなり、また一つ責務が減りました。

かなり見通しが良くなって来たのではないでしょうか？

## 動作確認をする
本設も同じくリファクタリングなので機能変更はありませんが、またサーバーを再起動して `http://localhost:8080/user/123/profile` にアクセスして動作確認をしておいてください。


# リファクタリング STEP3 静的ファイルの処理をview化する
URL解決に関する処理はかなり切り出せたのですが、まだ静的ファイルに関する処理だけが残ってしまっています。
うまく切り出せなかったのは、静的ファイルのレスポンス生成と、他のURLのレスポンス生成ではインターフェースが違う（requestを渡したらresponseが返ってくる、と単純化されてない）ため、うまく共通化できなかったからです。

というわけで、静的レスポンス生成処理もview化することで、共通化してURL解決を外部モジュールへ追いやってしまいましょう。

## ソースコード
