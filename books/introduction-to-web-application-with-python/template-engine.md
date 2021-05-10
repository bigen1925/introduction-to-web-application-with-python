---
title: "テンプレートエンジンを実装する"
---

# テンプレートエンジン？

さて、この章ではいわゆる「テンプレートエンジン」なるものを実装していくのですが、「テンプレートエンジンとはなにか」をくだくだと説明することはしません。

私達は難しい言葉について理解したいのではなく、単に便利に使えるWebアプリケーションを作りたいだけなのです。

ですので、この章でもやることは単純で、ここまで作ってきたWebアプリケーションを見渡してみて「ここ使いにくいな〜」「ここ見にくいな〜」と思うところをただ改善していくだけです。

それが終わって気がついてみれば、結果的に世の中ではテンプレートエンジンと呼ばれているものを作ることになっていた、と、そういう仕立てになっています。

-----

# STEP1: レスポンスのテンプレートをHTMLファイルに切り出す

では、具体的に「ここ使いにくいな〜」ポイントについて見ていきます。

この章で扱うのは **Pythonのソースコード(`views.py`)の中でHTMLを作っている** 部分です。

以下は、現在の`views.py`からの一部抜粋です。

```python
def now(request: HTTPRequest) -> HTTPResponse:
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
    body = textwrap.dedent(html).encode()
    content_type = "text/html; charset=UTF-8"

    return HTTPResponse(body=body, content_type=content_type, status_code=200)
```

レスポンスとして返すHTMLを、pythonのf-string（変数展開のできる文字列）を使って構築しています。

これはこれでお手軽にHTMLを作れて良いのですが、ちょっと大きめのWebページを作ったことのある人はわかると思いますが、普通のWebページはたった1ページのHTMLだけで何百行〜何千行もあるものです。
それをこの`views.py`に全部書いていては見通しは悪くなるのは自明です。

また、htmlを記述している部分はエディタからするとただのpython文字列に見えるでしょうから、エディタの強力なHTML作成補助機能の恩恵を受けづらいという側面もあります。
（シンタックスエラーなどを表示してくれなかったりなど。）

そこで、htmlを構築する部分を外部ファイルに切り出し、これらの問題を解決していきましょう。

まずはこの`now`関数だけ、HTMLを外部に切り出してみたのが以下になります。

## ソースコード


**`study/views.py`**
https://github.com/bigen1925/introduction-to-web-application-with-python/blob/main/codes/chapter19/views.py

**`study/templates/now.html`**
https://github.com/bigen1925/introduction-to-web-application-with-python/blob/main/codes/chapter19/templates/now.html

レスポンスの雛形となるhtmlファイルは、新たに`templates`というディレクトリを作り、そこの中にまとめることにしました。

## 解説
### `study/views.py`
#### 14-16行目
```python
    with open("./template/now.html") as f:
        template = f.read()
        html = template.format(now=datetime.now())
```

やっていることは難しくないでしょう。

pythonの文字列として作っていたHTMLを外部ファイルから読み込むことにして、`.format()`メソッドによって変数の置き換えを行っているだけです。

ここでは、`now`という変数をHTMLファイルの中に記載しておき、それを後から`.format()`によって現在時刻に置き換えています。

### `study/templates/now.html`
```html
<html>
<body>
    <h1>Now: {now}</h1>
</body>
</html>
```

こちらも特に説明はありません。
pythonの文字列として定義していたものを、HTMLファイルに切り出しただけです。

ただし、注目すべき点として、htmlファイルになったことでエディタの支援が受けられるようになっているということです。
恐らく皆さんが使っているようなモダンなエディタであれば、シンタックスハイライト（色付け）がされるようになったでしょうし、恐らくEmmet記法なども使えると思います。

エディタの機能を豊富に使えるかどうかというのは開発速度に大きく影響する部分なので、これだけでもかなりありがたいですね。

::: details コラム: Emmetとは
`Emmet`とは複雑なHTMLを短い記法で表現する記法（あるいはマークアップ言語）のことで、ご存知でない方は、htmlファイルで何もないところに`!`とだけ入力して、`Tab`キーを押してみてください。または、`h1*3`とだけ入力して`Tab`キーを入力してみてください。
`PyCharm`や`Visual Studio Code`、`Sublime Text`などといった最近のエディタであれば、HTMLタグが展開されると思います。

他にも色々な短縮記法が使えるので、是非調べてみてください。
:::

::: message
f-string記法から`.format()`メソッドへ切り替えていくにあたって、f-string記法とは違って文字列の中で関数呼び出しができないことに注意してください。

例えば今回でいうと、
```python
'<h1>Now: {datetime.now()}</h1>'.format(datetime=datetime)
```
のような使い方はできないということです。
（`now()`メソッドの呼び出しができず、エラーになります。）

関数呼び出しを伴う値で変数を置き換えたい場合は、python側で関数呼び出しを行い、その返り値で置き換えるようにしてください。

なぜこのような仕様になっているのか私も調べてみたのですが、理由はよく分かりませんでした。
:::

## 動作確認

まだ改良したいポイントはたくさんありますが、まずはこまめに動作確認をしておきましょう。
サーバーを再起動したらブラウザで `http://localhost:8080/now` へアクセスしてみましょう。

以前までと変わらず、現在時刻が表示されていれば問題ありません。

# STEP2: お決まりの処理をフレームワーク内に隠蔽する
さて、HTMLファイルを切り出せただけでも結構な偉業ですが、view関数の中に

- ファイルを開く (`open()`)
- ファイルを読み込む (`read()`)
- 変数を置き換えるためのメソッドを呼び出す (`format()`)

などの処理が残ってしまっています。

しかも、これらの処理はHTMLを外部から読み込む場合には今後も毎回必ず必要になります。

たった2行ほどのことではありますが、エンジニアは繰り返しを嫌うものですから、これらもフレームワークの中に隠蔽してしまいましょう。

## ソースコード

それがこちらです。

**`study/henango/template/renderer.py`**
https://github.com/bigen1925/introduction-to-web-application-with-python/blob/main/codes/chapter19-2/henango/template/renderer.py

**`study/views.py`**
https://github.com/bigen1925/introduction-to-web-application-with-python/blob/main/codes/chapter19-2/views.py

`henango`の中に`template`というディレクトリを作り、そこにHTMLの構築に関する共通機能をいれることにしました

## 解説
### `study/henango/template/renderer.py`
```python
def render(template_path: str, context: dict):
    with open(template_path) as f:
        template = f.read()

    return template.format(**context)

```

こちらはview関数の中でやっていたことをそのまま持ってきただけなので、とくに解説することもないでしょう。

### `study/views.py`
#### 15-16行目
```python
    context = {"now": datetime.now()}
    html = render("./templates/now.html", context)
```

ファイルがどうとかwithがこうとか、わずらわしいことは全て`render()`関数に隠蔽し、テンプレートファイル名とパラメータを渡すだけでよくなりました。

ちなみに、パラメータはdjangoに倣って辞書で渡すことにしました。

行数でいうとたった1行減っただけですが、私はかなりスッキリしたように感じます。

## 動作確認
しつこいようですが、動作確認はこまめにやりましょう。
サーバーを再起動したらブラウザで `http://localhost:8080/now` へアクセスし、表示を確認しておいてください。

# STEP3: テンプレートファイルの置き場を設定値で変えられるようにする
ところで、雛形となるHTMLファイル（以下、テンプレートファイルと呼びます）の置き場は独断で`study/templates/`の下にまとめておくことにしましたが、この置き場所はプロジェクトによって変更したくなることがあるでしょう。
`static`ディレクトリのときと同様に、`settings`に設定値を切り出すことで、フレームワークに手をいれなくても簡単に変えられるようにしておきましょう。

## ソースコード
それがこちらです。
**`study/henango/template/renderer.py`**
https://github.com/bigen1925/introduction-to-web-application-with-python/blob/main/codes/chapter19-3/henango/template/renderer.py

**`study/settings.py`**
https://github.com/bigen1925/introduction-to-web-application-with-python/blob/main/codes/chapter19-3/settings.py

**`study/views.py`**
https://github.com/bigen1925/introduction-to-web-application-with-python/blob/main/codes/chapter19-3/views.py


## 解説
### `study/henango/template/renderer.py`
#### 6-10行目
```python
def render(template_name: str, context: dict):
    template_path = os.path.join(settings.TEMPLATES_DIR, template_name)

    with open(template_path) as f:
        template = f.read()
```

テンプレートファイルのディレクトリをsettingsに記載した`TEMPLATES_DIR`から取得するように変更しています。


### `study/views.py`
#### 16行目
```python
    html = render("now.html", context)
```

テンプレートディレクトリはsettingsで決めることにしたので、viewsではファイル名だけ指定すればOKということになりました。
これでテンプレートディレクトリを移動させるときも修正が不要で簡便ですね。


### `study/settings.py`
#### 9-10行目
```python
# テンプレートファイルを置くディレクトリ
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
```

settingsでテンプレートファイル置き場を指定するようにしました。
Djangoっぽい！

## 動作確認
動作確認をお忘れずに！


# STEP4: bodyを文字列のまま返せるようにする

さて、ついでなのでHTMLレンダラー以外も少し扱いやすくしておきましょう。

今、htmlを構築したあと、毎回
```python
body = html.encode()
```
などとしてbytes型へ変換しています。

最終的にsocketに渡す値はbytes型でなくてはならないのでどこかで変換してなくてはならないのですが、毎回これを書くのは億劫です。

なので、最終的にHTTPレスポンスを生成する部分に変換処理を寄せることで共通化してしまいましょう。

## ソースコード

**`study/henango/server/worker.py`**
https://github.com/bigen1925/introduction-to-web-application-with-python/blob/main/codes/chapter19-4/henango/server/worker.py

**`study/views.py`**
https://github.com/bigen1925/introduction-to-web-application-with-python/blob/main/codes/chapter19-4/views.py

## 解説
### `study/henango/server/worker.py`
#### 60-62行目
```python
            # レスポンスボディを変換
            if isinstance(response.body, str):
                response.body = response.body.encode()
```

実際のHTTPレスポンスを生成する処理の直前に、`body`が`str`型だったら`bytes`型へ変換する、という処理を追加しました。
これで、view関数側ではbodyは`str`型のまま渡してしまって大丈夫になりました。

### `study/views.py`
#### 17行目
```python
#     body = html.encode()
```
というわけで、encode処理は削除してしまっています。

## 動作確認
お忘れずに！僕は言いましたよ！どこから動かなくなったのかわからなくなりますよ！

# STEP5: ステータスコードとContent-Typeにデフォルト値を設定する
今回は細かくSTEPを切っているので疲れてきたかもしれませんが、これが実質最後です。
このあとは、他のview関数にも適用していくだけになります。

もう一度view関数を見渡してみると、まだ繰り返し同じことを書いている箇所があります。

```python
        content_type = "text/html; charset=UTF-8"
        status_code = 200
```

こういったステータスコードとContent-Typeの部分ですね。

Webサーバーでは大部分のレスポンスがHTMLであり、レスポンスステータスは200です。

これらはデフォルト値になるようにしておいて、HTMLじゃないものを返したり、200じゃないステータスを返したいときだけ設定すればいいようにしておきましょう。

## ソースコード
それがこちらです。

**`study/henango/server/worker.py`**
https://github.com/bigen1925/introduction-to-web-application-with-python/blob/main/codes/chapter19-5/henango/server/worker.py

**`study/henango/http/response.py`**
https://github.com/bigen1925/introduction-to-web-application-with-python/blob/main/codes/chapter19-5/henango/http/response.py

**`study/views.py`**
https://github.com/bigen1925/introduction-to-web-application-with-python/blob/main/codes/chapter19-5/views.py

## 解説
### `study/henango/server/worker.py`
#### 122-132行目
```python
        # Content-Typeが指定されていない場合はpathから特定する
        if response.content_type is None:
            # pathから拡張子を取得
            if "." in request.path:
                ext = request.path.rsplit(".", maxsplit=1)[-1]
                # 拡張子からMIME Typeを取得
                # 知らない対応していない拡張子の場合はoctet-streamとする
                response.content_type = self.MIME_TYPES.get(ext, "application/octet-stream")
            else:
                # pathに拡張子がない場合はhtml扱いとする
                response.content_type = "text/html; charset=UTF-8"
```
HTTPレスポンスのContent-Typeヘッダーを生成している箇所ですが、pathに拡張子がなかった場合はHTML扱いとしました。

本当は下記のようにHTTPResponseオブジェクトのcontent_type属性のデフォルト値として設定したいのですが、本教材では静的ファイル配信の実装方法がちょっと特殊なため、このようにしています。

### `study/henango/http/response.py`
#### 9行目
```python
    def __init__(self, status_code: int = 200, content_type: str = None, body: Union[bytes, str] = b""):
```
ちょっと分かり難いかもしれませんが、status_codeが指定されなかった時のデフォルト値として`200`を設定しました。

### `study/views.py`
#### 15-18行目
```python
    context = {"now": datetime.now()}
    body = render("now.html", context)

    return HTTPResponse(body=body)
```

`status_code`と`content_type`に関する記述がなくなって、すっきりの極みに到達しましたね！

これで繰り返し同じことを記述していた部分がほぼなくなったといえるでしょう！

# STEP6: 他のviewへ適用していく
では最後に、他のviewへも適用していきましょう。


## ソースコード
**`study/views.py`**
https://github.com/bigen1925/introduction-to-web-application-with-python/blob/main/codes/chapter19-6/views.py

**`study/templates/show_request.html`**
https://github.com/bigen1925/introduction-to-web-application-with-python/blob/main/codes/chapter19-6/templates/show_request.html

**`study/views.py/parameters.html`**
https://github.com/bigen1925/introduction-to-web-application-with-python/blob/main/codes/chapter19-6/templates/parameters.html

**`study/views.py/user_profile.html`**
https://github.com/bigen1925/introduction-to-web-application-with-python/blob/main/codes/chapter19-6/templates/user_profile.html

## 解説
### `study/views.py`
#### 21-87行目
```python
def show_request(request: HTTPRequest) -> HTTPResponse:
    """
    HTTPリクエストの内容を表示するHTMLを生成する
    """
    context = {"request": request, "headers": pformat(request.headers), "body": request.body.decode("utf-8", "ignore")}
    body = render("show_request.html", context)

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
        context = {"params": urllib.parse.parse_qs(request.body.decode())}
        body = render("parameters.html", context)

        return HTTPResponse(body=body)


def user_profile(request: HTTPRequest) -> HTTPResponse:
    context = {"user_id": request.params["user_id"]}

    body = render("user_profile.html", context)

    return HTTPResponse(body=body)

```

これまでやってきたことを他のview関数にも適用していっただけなので、特に解説は不要かと思います。


### `study/templates/show_request.html`
### `study/views.py/parameters.html`
### `study/views.py/user_profile.html`

これらも特に解説不要だと思いますので、割愛させてください。

# ところでテンプレートエンジンって？
さて本章はこれで終わりなのですが、今回みなさんに作ってもらった
「雛形のHTMLファイルを取得してきて、そこに変数やらなんやらで切ったり貼ったりして、完成品のHTML文字列を生成する」
という機能を持ったものを、世の中では **テンプレートエンジン** と呼びます。

今回作ったものはそんなテンプレートエンジンの中でも一番簡素なもので、たんに変数の置き換えを行うだけのものでした。
世の中のテンプレートエンジンは、独自の記法でHTMLを部分的に繰り返し生成（for文のようなもの）することができたり、あるテンプレートファイルが他のテンプレートファイルを読み込めたり、他の豊富な機能を備えています。

しかし、やっていることは「雛形となるファイルを読み込み、整形し、最終的に文字列として返す」というところには変わりありません。

そう考えると、難しいものではないと思いますし、皆さんも少し手間をかければ作るのは難しくないのではないでしょうか。
余裕のある方は、是非Djangoのテンプレートエンジンなどを参考にして、同様の機能を一部実装してみてください。

