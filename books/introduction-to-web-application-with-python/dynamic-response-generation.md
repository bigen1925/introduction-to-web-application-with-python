---
title: "「動的に生成したHTML」を返せるようになる"
---

# 「静的ファイル配信」と「動的なHTMLの生成」

さて、ここまでで「適切なヘッダーの生成」（`Date`とか、`Content-Type`とか)ができるようになり、「並列処理」もできるようになり、`HTTPのルールに従ってレスポンスを返す基盤`の部分はかなり整ってきました。

これで **「Webサーバー (=HTTPサーバー) として最低限の機能を揃えていく」** というステップは、ほぼ終わりです。

次のステップとして、 **「レスポンスボディとして何を返すか？」** についてもう少し詳しく見ていきましょう。

-------

既に実装済みである「HTMLファイルや画像ファイルの内容をレスポンスボディとしてそのまま返す」という機能は、一般的には **「静的ファイル配信」** と呼びます。

この機能さえあれば、例えば [IETFによるRFCのWebページ](https://tools.ietf.org/html/rfc7230) などは十分に作成可能です。
内容をHTMLファイルに書いて保存しておけば良いだけですから。

しかし、皆さんの見慣れたホームページを作成するにはまだまだ機能不足です。

例えば [前橋先生のホームページ](http://kmaebashi.com/) ^[本書を書くきっかけを与えて頂いた「Webサーバを作りながら学ぶ 基礎からのWebアプリケーション開発入門」の著者です。詳しくは[こちら](https://zenn.dev/bigen1925/books/introduction-to-web-application-with-python/viewer/preface)] のような比較的簡素な^[前橋先生、すいません。]ホームページですら、まだ作れません。

何が作れないかと言うと、下記のようないわゆる「アクセスカウンター」の部分です。

![](https://storage.googleapis.com/zenn-user-upload/kt7f9wc7howek515f8bwzoxz98io)

アクセスカウンターの数字は、ページを読み込むごとに数字が増えていきます。
この機能を、皆さんの今のWebサーバーで実現するにはどうすればいいでしょうか？

アクセスカウンターの数字が変わるということは、レスポンスボディの内容が変わるということです。
現在のWebサーバーから返却されるレスポンスボディはHTMLファイルの内容そのままですので、レスポンスボディの内容を変えようと思うとHTMLファイルを編集する必要があります。

つまり、この機能を提供しようと思うと、HTTPリクエストが来る度に毎回HTMLファイルを自動で（もしくは手動で）編集して保存するような機能が必要になってしまいます。
これは（実現可能ですが）あまりに非効率そうですし、面倒くさそうです。

そうなってくると、
**「レスポンスボディをファイルから取得するのではなく、Pythonの文字列として生成すれば毎回違うレスポンスボディを生成するのは簡単なのでは？」** 
という発想になるのは自然なことでしょう。

これを **「動的なHTMLの生成」 **（あるいは ** 「動的なレスポンスの生成」**）と呼びます。

:::details コラム: 「静的」と「動的」
「静的」という言葉はなかなか厄介です。また、対義語である「動的」という言葉も同様に厄介です。

「静的」とは「変化しないもの」、「動的」は「変化するもの」を意味するわけですが、「 **何に対して何が静的** なのか」「 **何に対して何が動的** なのか」を常に意識する必要があります。

------

例えば「`静的ファイル`配信」は「`変化しないファイル`の配信」を意味しています。
これは、 **何に対して何が** 変化しないファイルなのでしょうか？

HTMLファイルそのものは、常に変化しえます。ファイルをエディタで編集するだけです。
Webサーバーの機能として見た時も、HTMLファイルを編集してしまうとレスポンスボディも変化してしまうでしょう。

「静的ファイル配信」のことを「"いつも"同じレスポンスが返ってくるWebサービス」と表現する方もいらっしゃいますが、このことを考えると正確ではないことが分かります。
HTMLファイルを編集すればレスポンスも変化するのですから。

答えは、「 **リクエストに対して** 内容が変化しないファイルの配信」です。
「リクエストに応じて内容を変化させないファイルの配信」と言ったほうが分かりやすいかもしれません。

ですので、ファイルを編集したときは、内容が変化してもよいのです。

私がジュニアエンジニアだったころは、
「でもHTMLファイルを編集したらレスポンスは変わるんでしょ？いつも同じって嘘じゃない？」
と思って混乱していました。

------

また他にも、Javascriptを説明する際に「Web上で動的なコンテンツを提供するためのプログラミング言語」と説明されることがあります。
この説明における「動的なコンテンツ」というのは、「時間の経過あるいはユーザーの操作に対して、 **配信済みのHTMLが** 変化するコンテンツ」のことです^[正確にはJavascriptが変化させるのはDOMであってHTMLではありませんが、そこはご愛嬌。]。

ブラウザに表示させるHTMLは一度レスポンスとしてブラウザへ送ってしまうと、サーバー側のプログラムから変更させることは基本的にはできません。
CSSなどは確かにコンテンツの表示内容を変化（文字の色を赤くしたり）させますが、配信済みのHTMLの内容を変化させているわけではありません。

ただし、HTMLと一緒にプログラムをブラウザに送りつけておけば、ブラウザがそのプログラムを後から実行することで配信済みのHTMLを変更させることができます。
（ちなみに、このプログラムがJavascriptです。）

単に「動的なコンテンツ」を「Webページを変化させる」とだけ理解してしまうと、
「文字の色を変化させるCSSも動的コンテンツを提供しているのでは？」
「HTMLのformタグもボタンを押すかどうかでページの挙動が変わるわけだから、動的なのでは？」
などと混乱してしまいます。
（私は混乱していました。）

------

このように「静的」「動的」という言葉はよく出てくるわりに理解が難しいので、何に対して何が変化する/しないのか、常に注意しておきましょう。

:::

# 現在時刻を表示するページを作成する
少し回りくどい説明をしてしまいましたが、やりたいことはソースコードを見てもらったほうが早いかもしれません。

実際に「動的なHTMLの生成」を行い、リクエストする度に結果が変わるようなページを作成してみましょう。

アクセスカウンターをいきなり実装するには過去のアクセス数を保存しておくデータベースのようなものが必要になり少し面倒ですので、まずは簡単のため **`/now`というpathにアクセスすると現在時刻を表示する**だけのページを作成してみましょう。

（アクセスカウンターの実装はもう少し後で取り組みます。）

## ソースコード
現在時刻を表示するページを追加するために、`workerthread.py`を変更したソースコードがこちらです。

**`study/workerthread.py`**
https://github.com/bigen1925/introduction-to-web-application-with-python/blob/main/codes/chapter14/workerthread.py

## 解説

### 51-69行目
```python
            response_body: bytes
            content_type: Optional[str]
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

                # Content-Typeを指定
                content_type = "text/html"

                # レスポンスラインを生成
                response_line = "HTTP/1.1 200 OK\r\n"

            # pathがそれ以外のときは、静的ファイルからレスポンスを生成する
            else:
                # ...
```

メインで追加したのはこの部分です。

やっていることは、
**「pathが`/now`だったら、pythonで現在時刻を表示するHTMLを生成し、レスポンスボディとする」**
ということです。



-----

ソースコードについていくつか補足しておきます。

```python
            response_body: bytes
            content_type: Optional[str]
            response_line: str
```
`response_body`や`response_line`を代入する箇所が複数に分かれてしまっていますので、事前に型注釈をしておくことにしました。
`Optional[str]`は、`str型またはNone`を表す型です。
他の言語ではNullable型などと呼ばれたりもします。

変数の型注釈は、エディタ等に「この変数はこの型の値を代入することを想定していますよ」とヒントを伝える意味があります。
このように記載しておくと、間違って「あっちでは`str`を代入、こっちでは`bytes`を代入」などとしてしまった際にエディタが事前に警告してくれるようになります。

```python
                html = f"""\
                    <html>
                    <body>
                        <h1>Now: {datetime.now()}</h1>
                    </body>
                    </html>
                """
                response_body = textwrap.dedent(html).encode()
```
`ヒアドキュメント` + `dedent()`を使っています。
単に普通のhtmlを書きたいだけなのですが、インデントとか改行とかがpythonでは意味を持ってしまいますので、工夫しています。
それほど難しくはないので、「python ヒアドキュメント」「python dedent」などで調べてみてください。

### 76-77, 87, 147-153行目
```python
                    # Content-Typeを指定
                    content_type = None
```
```python
                    content_type = "text/html"
```
```python
    def build_response_header(self, path: str, response_body: bytes, content_type: Optional[str]) -> str:
        """
        レスポンスヘッダーを構築する
        """

        # Content-Typeが指定されていない場合はpathから特定する
        if content_type is None:
            # ...
```
動的コンテンツを利用する場合通常はpathからはレスポンスボディのフォーマットを特定することができないため、Content-Typeを明示的に指定するようにしています。

逆に、pathからContent-Typeを特定したい場合には`None`を指定してあげるような実装にしてみました。

## 動かしてみる

それでは早速動かしてみましょう。

いつもどおりサーバーを起動した後、Chromeで`http://localhost:8080/now`へアクセスしてみてください。

![](https://storage.googleapis.com/zenn-user-upload/v2rturapukcmsdt2py9clrjwrf63)

質素ではありますが、上記のようなページが表示されたでしょうか？

表示されたら、何度かページをリロードしてみてください。
毎回、表示される内容が変わっているでしょうか？

-----

これで動的なHTMLの生成の完了です。
簡単でしたね。

改めて振り返っておくと、今回やったことの大事なポイントは、
**「サーバ起動後、ソースコードもHTMLファイルも全く編集していないのに毎回違う結果がブラウザに表示されている」**
ということです。

単にファイルの内容をそのままレスポンスボディとして出力しているだけでは実現できなかった機能です。


# HTTPリクエストの内容を表示するページを作成する

せっかくなので、もう1つぐらい動的なHTMLのページを作ってみましょう。

次は、送られてきたHTTPリクエストの内容をそのままHTMLで表示する`/show_request`というページを追加してみます。

## ソースコード
`/show_request`を追加したソースコードがこちらです。

**`study/workerthread.py`**
https://github.com/bigen1925/introduction-to-web-application-with-python/blob/main/codes/chapter14-2/workerthread.py

## 解説

### 72-95行目:
```python
            # pathが/show_requestのときは、HTTPリクエストの内容を表示するHTMLを生成する
            elif path == "/show_request":
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
                content_type = "text/html"

                # レスポンスラインを生成
                response_line = "HTTP/1.1 200 OK\r\n"
```
pathが`/show_request`だったときのレスポンスの生成を追加しました。

とくに難しいところはないと思います。

`pprint.pformat()`は、辞書を改行を交えて見やすい文字列に変換してくれます。

`.decode("utf-8","ignore")`は、バイトデータをutf-8でデコードし、デコードできない文字は無視してそのまま表示します。

なお、次の変更によって、`request_header`の型が`bytes` => `dict`に変更になっていることに気をつけてください。

### 135-163行目:
```python
    def parse_http_request(self, request: bytes) -> Tuple[str, str, str, dict, bytes]:
        """
        HTTPリクエストを
        1. method: str
        2. path: str
        3. http_version: str
        4. request_header: dict
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

        # リクエストヘッダーを辞書にパースする
        headers = {}
        for header_row in request_header.decode().split("\r\n"):
            key, value = re.split(r": *", header_row, maxsplit=1)
            headers[key] = value

        return method, path, http_version, headers, request_body
```
HTTPリクエストをパースする処理に少し変更を加えています。

```python
        # リクエストヘッダーを辞書にパースする
        headers = {}
        for header_row in request_header.decode().split("\r\n"):
            key, value = re.split(r": *", header_row, maxsplit=1)
            headers[key] = value
```
今まで`request_header`は`bytes`のまま放置していたのですが、このままでは扱いにくいので **辞書に変換しています** 。
CRLFでsplitすることで1行ずつにバラしたあと、各行に対して`1つの":"と、0個以上の空白`を表す正規表現で分割してkeyとvalueを取得しています。

```python
    def parse_http_request(self, request: bytes) -> Tuple[str, str, str, dict, bytes]:
```
返り値の型が変わったので、型注釈を変更（`Tuple[str, str, str, bytes, bytes]:` => `Tuple[str, str, str, dict, bytes]:`）することも忘れないでください。^[ある程度賢いエディタであれば、型注釈を変更しないままだと「なんか型がおかしくない？」と警告を出してくれると思います。便利ですね。]

## 動かしてみる

では、サーバーを再起動させてからChromeで`http://localhost:8080/show_request` へアクセスしてみましょう。

![](https://storage.googleapis.com/zenn-user-upload/68tc9qofaon30pn9arxsglzgfhst)

いい感じに表示されていますね。

いつも同じ内容が表示されてしまう人は、`cmd` + `shift` + `R`でリロードしてみてください。
「キャッシュを無効にしてリロードする」
というコマンドですが、普通にリロードした場合と比べてヘッダーに変化があるのが分かると思います。

また、別のブラウザ（SafariやFirefoxなど）で同じURLを開いてみると、User-Agentが変わっているのが分かるはずです。

これで「動的にHTMLを生成する」というのがどういうことか（あるいは、動的 **ではない** HTMLの生成とはどういうものか）がかなり分かってきたのではないでしょうか？

-----

ちなみに`Body`のところが表示されていないのは、リクエストボディが空で送られているからです。
パースする際にリクエストヘッダーを辞書に変換したのと同様、リクエストボディも一緒に文字列に変換してしまったほうが扱いやすいのではないかと思う方もいらっしゃると思いますが、`bytes`のままにしているのには事情があります。

ヘッダーはUTF-8でエンコードされた文字列だと決まっているのですが、ボディは画像やPDFなど、文字列ではなくバイナリデータが送られてくる可能性があるため、常に文字列に変換できるとは限らないのです。
なので、ボディは中身が文字列だと分かっている場合しか文字列に変換してはいけないのです。


