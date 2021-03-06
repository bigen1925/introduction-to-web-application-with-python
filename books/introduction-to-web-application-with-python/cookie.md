---
title: "Cookieを扱う"
---

# Cookieとは

本章では、現代のWeb技術では理解が欠かせない`Cookie`について取り扱っていきます。
本章のボリュームはかなり多くなっていますが、重要な機能ですのでぜひ最後まで読んでマスターしておいてください。 
 
  
Cookieとは、主にサーバーからブラウザに対して送信され^[Javascriptを使うことでブラウザサイドでCookieを生成することも可能ですが、簡単のために本書ではサーバーサイドから送信される場合のみを扱います]、ブラウザ内で保存される小さな文字列データのことです。

一度サーバーからブラウザに対して送信されブラウザ内に保存されたCookieは、ブラウザが次回以降同じサーバーにリクエストを送る際にHTTPヘッダーにそのまま付与して送信されます。

言葉で説明してもわかりにくいと思いますが、図にすると以下のような感じです。

------

**PHASE 1: ブラウザからサーバーへHTTPリクエストが送られる** 
![](https://storage.googleapis.com/zenn-user-upload/6v2620i1qs512yoqdzjv92z8si6e)

**PHASE 2: サーバーからHTTPレスポンスが返却される。このとき、保存すべきCookieの値を指示する**
![](https://storage.googleapis.com/zenn-user-upload/bw2kffivomt9bevnavt1tsw8jodn)

**PHASE 3: ブラウザは内部でCookieの値を保持しておき、次回同じサーバーへリクエストを送信する際、HTTPリクエストにCookieを付与して送信する**
![](https://storage.googleapis.com/zenn-user-upload/lwplkcag20m7ydpk2c02jrt3blwk)

------

図の中でも表現されているように、Cookieの値はサーバーからの送信もブラウザからの送信もHTTPヘッダーを通じて行われます。

このCookieの仕組みを使うことで、Webサーバーはクライアントが以前にどのような行動をしていたのかをある程度トラッキングすることができます。


ただし、**ブラウザはCookieを常に送り返してくれると限らない**ということに注意してください。
これらの条件や仕様については後ほど詳細に説明します。

------

## 概観

実際のソースコードに移る前に、Cookieの仕様についてもう少し詳しくみておきましょう。

例によって、RFCを参照します。
Cookieに関しては親切にもRFC内に「概観(overview)」という項目があり、全体感を理解するのにはちょうどよい平易さで書かれています。

RFC6252 - 概観: https://triple-underscore.github.io/http-cookie-ja.html#overview

[3.1 例）](https://triple-underscore.github.io/http-cookie-ja.html#rfc.section.3.1) を読んでいただければわかると思いますが、簡単にまとめると

- サーバーは *Set-Cookie* というヘッダーを使ってCookieを送りなさい
- *Set-Cookie*ヘッダーは複数あって構わないが、1つのヘッダーで1つのCookieのみおくるべきである
- サーバーは、Cookieの利用に制限を加えたい場合は、`Path`, `Domain`, `Secure`, `HttpOnly`, `Expire`などの属性を付与してもよい
- UA (= User Agent = ブラウザ)は、`Cookie` というヘッダーを使って送り返しなさい
- `Cookie`ヘッダーは1つしか送ってはならず、複数の値を送る場合は`;`で区切る

などということが書かれています。

Webサービスを運用したことがある方であればCookieに関連するトラブルは一度は経験したことがあると思いますし、トラブル時には何が起きているのかを理解するのが難しい領域ではありますが、基本的なしくみ自体は何も難しいことはないことがわかると思います。

以下では、中級者を卒業するならば知っておいたほうがよい内容のみピックアップしてもう少し詳細に見ていきます。

## サーバー要件

以下は、サーバーサイド側の仕様です。

https://triple-underscore.github.io/http-cookie-ja.html#sane-profile

### Expires属性
RFC: https://triple-underscore.github.io/http-cookie-ja.html#sane-expires

サーバーはCookieに有効期限を指定したい場合はこの属性で日時を指定します。
日時のフォーマットは*Date*ヘッダーと同じです。

ブラウザはこの有効期限を過ぎたCookieは削除し、サーバー側へ送り返されることはなくなります。
```http request
Set-Cookie: foo=bar; Expires=Thu, 12 Jul 2012 07:12:20 GMT
```

### Max-Age属性
RFC: https://triple-underscore.github.io/http-cookie-ja.html#sane-max-age

概観では出てきていませんでしたが、この属性も有効期限を指定できます。
*Max-Age*は日時ではなく、秒数を指定します。

*Max-Age*と*Expires*の両方が指定された場合は、*Max-Age*が優先されます。
両方とも指定がない場合は、ブラウザごとに独自に定める「セッション」なる期間が終了するまで保持されるということになっており、これは最近のブラウザであればだいたい「ブラウザを終了するまで」となっています。

```http request
Set-Cookie: foo=bar; Max-Age=3600
```

### Domain属性
RFC: https://triple-underscore.github.io/http-cookie-ja.html#sane-domain

サーバーは、Cookieを送り返すドメインを制限したい場合にこの属性を指定します。

> 例えば， Domain 属性の値が "example.com" ならば、 UA は，［ example.com ／ www.example.com ／ www.corp.example.com ］へ向けて HTTP 要請を送信する際にそのクッキーを Cookie ヘッダに内包することになる。

という解説がそのままわかりやすいですね。

Domain属性を省略した場合は、

> サーバが Domain 属性を省略した場合、 UA は，生成元サーバに限りクッキーを返すことになる。

と書かれており、`example.com`で付与されたCookieは `www.example.com` には送信してはいけない、と定められています。
ただし、一部のブラウザはこのルールを守らずCookieを送ってしまうケースがあるので注意するように、とも書かれています。

```http request
Set-Cookie: foo=bar; Domain=my.www.example.com;
```

### Path属性
RFC: https://triple-underscore.github.io/http-cookie-ja.html#sane-path

サーバーは、Cookieを送り返すパスを制限したい場合にこの属性を指定します。
ブラウザは、指定されたパス以下のURLにアクセスする場合のみCookieを送信します。

例えば、

```http request
Set-Cookie: foo=bar; Path=/foo/bar/
```

と指定した場合は、*/foo/bar/index.html* へアクセスする際にはCookieが送信されますが、 */foo/baz/index.html* へアクセスする際にはCookieは送信されません。

なお、Path属性を省略した場合は、現在アクセスしているパスが指定されたものとみなされます。

### Secure属性
RFC: https://triple-underscore.github.io/http-cookie-ja.html#sane-secure

サーバーは、この属性を使うことでセキュアなチャンネルで通信が行われる場合にのみCookieを送信するように求めることができます。

RFCにおいては「セキュアなチャンネル」が何かはブラウザが独自に定義してよいということになっておりますが、現代のブラウザはセキュアといえば*HTTPS*のことだと解釈します。

ちなみに、Secure属性には値は不要です（`Secure=true`などと書く必要はありません）。
```http request
Set-Cookie: foo=bar; Secure
```

### HttpOnly属性
RFC: https://triple-underscore.github.io/http-cookie-ja.html#sane-httponly

Javascriptからのリクエスト時にはCookieを送信させたくないときに指定します。

RFCには
「*非HttpAPI*（例えばwebブラウザAPIなど）を介してアクセスする際にはCookieを省略することを求める」
と書かれていますが、webブラウザAPI（JavascriptによるAjax通信など）もプロトコル自体はHTTPなので属性名はややこしいですが、歴史的経緯もありこうなっています。

また、HttpOnlyという名前だからといって、「HTTPSのときは送らない」という意味ではないことに注意してください。
HttpOnly属性とSecure属性は同時に機能することができます。
（Javascriptからのアクセスのときには送信せず、さらにHTTPS通信のときのみ送信する、という意味になる）

Secure属性と同様、値は不要です（`HttpOnly=true`などと書く必要はありません）。
```
Set-Cookie: foo=bar; HttpOnly
```

### Same-Site属性
RFC(draft): https://tools.ietf.org/html/draft-west-first-party-cookies-07

こちらの属性はまだドラフトでありRFCには正式採用されておりませんが、モダンブラウザはほぼ全て対応している属性でありセキュリティ上重要なものです。
この属性が重要視されている意味や、具体的な効果などは説明すると長くなりすぎるためここでは割愛しますが、概要だけを紹介しておきます。


これまで見てきた属性は、リクエストを送る先のページのpathやdomainだけを見てCookieの送信を制限していましたが、Same-Site属性は送り元のURLも制限の条件に加えます。

あるサイトA(*http://a.com*)をみていて、そのサイト内のリンクでサイトB(*http://b.com*)へリクエストを送信する（ページ遷移をしたり、フォームをPOSTしたりする）ことを考えます。

このとき、サイトAとサイトBのドメインが違う場合、Same-site属性によって

- **None**: 過去にサイトBから付与されたCookieは、無条件にサイトBへ送信されます
- **Lax**: 過去にサイトBから付与されたCookieは、（大雑把にいえば）GETリクエストのみ送信しますが、POSTやPUTなどのリクエストではCookieは送信しません。
- **Strict**: 過去にサイトBから付与されたCookieは、サイトBへは送信されません 

となります。
これは**CSRF**という脆弱性をある程度防ぐための機能です。

自分の作っているWebサイトで、外部サイトを経由すると何故かCookieがうまく使えない（よくあるのは、ログアウトされてしまうなど）という事象が発生したら、この属性をチェックしてみてください。

```
Set-Cookie: foo=bar; Same-site=Lax;
```

## ブラウザ要件 (=UA要件)
RFC: https://triple-underscore.github.io/http-cookie-ja.html#ua-requirements

さて、ここからはRFCによってブラウザ側に求められている仕様となります。
皆さんが「ブラウザそのもの」を開発するのでなければ、ほとんどのことは細かく知る必要はありません。

ただし、重要な項目が1点だけありますので、そちらだけ説明しておきます。

### Set-Cookieヘッダ
RFC: https://triple-underscore.github.io/http-cookie-ja.html#set-cookie

ブラウザがSet-Cookieヘッダを受け取った場合、どのように処理しなければならないかが書かれています。

>UA は、 HTTP 応答にて受信した Set-Cookie ヘッダを，**まるごと無視してもよい。** 例えば UA は、 “第三者主体” への要請に対する応答による，クッキーの設定に対し、阻止したいと望むかもしれない（ § 第三者主体クッキーを見よ）。
UA は Set-Cookie ヘッダをまるごと無視しない場合、以下で定義されるように， Set-Cookie ヘッダの値を set-cookie-string として構文解析しなければならない。

ここで重要なのは、ここまで見てきたようなサーバー側からのCookieの使用制限とは別に、そもそもブラウザは独自の判断で勝手にCookieを無視してよい、ということです。
「無視しないならこう解釈してね」というのが定められているにすぎないのです。

そのため、例えばブラウザを利用するユーザーがCookieを拒否するサイトを指定できるような設定が備わっていたり、あるいは手動でブラウザ内に保存されたCookieを削除できる機能が備わっていたりします。

Cookieそのものは悪用しなければユーザー体験を向上させる非常に便利な機能ですのでブラウザも危険のない範囲でできるだけ送り返す努力はしてくれますが、いつでも付与したCookieが送り返されてくるとは限らないということは常に心に留めておきましょう。


# 実際に動かしてみる

さて、ここまで長々と説明してきましたが、そろそろ私たちのWebアプリケーションを使って実際にCookieを送受信してみましょう。

おさらいをしておくと、「Cookieを送受信する」というのは、大雑把な流れとしては

1. サーバーから*Set-Cookie*ヘッダーを使ってデータを送信する
1. ブラウザは次回以降のリクエスト時に*Cookie*ヘッダーで付与したデータを送信してくる

という機能を利用していくことでした。

# STEP1: *Set-Cookie*ヘッダーを送信してみる
まず最初のステップとして、サーバーからクライアントへ送信されるのHTTPレスポンスに、Set-Cookieヘッダを付与してみましょう。

これまでのソースコードではHTTP*リクエスト*のヘッダーを処理してコード内で扱う仕組みはありましたが、HTTP*レスポンス*に自由なヘッダーを追加する機能はありませんでしたので、その機能も一緒に追加していきます。

ソースコードがこちらです。

## ソースコード

**`study/henango/http/response.py`**
https://github.com/bigen1925/introduction-to-web-application-with-python/blob/main/codes/chapter20/henango/http/response.py#L6

**`study/henango/server/worker.py`**
https://github.com/bigen1925/introduction-to-web-application-with-python/blob/main/codes/chapter20/henango/server/worker.py#L141-L142

**`study/views.py`**
https://github.com/bigen1925/introduction-to-web-application-with-python/blob/main/codes/chapter20/views.py#L56

**`study/urls.py`**
https://github.com/bigen1925/introduction-to-web-application-with-python/blob/main/codes/chapter20/urls.py#L10

## 解説

### `study/henango/server/worker.py`
#### 4-23行目

```python
class HTTPResponse:
    # ...
    headers: dict
    # ...

    def __init__(
        self,
        # ...
        headers: dict = None,
        # ...
    ):
        if headers is None:
            headers = {}

        # ...
        self.headers = headers
        # ...
```

`HTTPResponse`クラスに`headers`という属性をdict型で追加しました。
レスポンスヘッダーを追加する際は、この属性に `{<header-name>: <header-value>}`の組み合わせで値をセットします。

### `study/henango/server/worker.py`
#### 141-142行目
```python
        for header_name, header_value in response.headers.items():
            response_header += f"{header_name}: {header_value}\r\n"
```
レスポンスヘッダーを出力する際に、`response`オブジェクトの`headers`属性の中身も出力するようにしました。

### `study/views.py`
#### 56-57行目
```python
def set_cookie(request: HTTPRequest) -> HTTPResponse:
    return HTTPResponse(headers={"Set-Cookie": "username=TARO"})
```

Cookieを付与するためだけの非常にシンプルなviewを用意しました。
bodyは特に返さず、HTTPレスポンスとしては
```http request
HTTP/1.1 200 OK
...
Set-Cookie: username=TARO

```
のような内容を返すviewです。


### `study/urls.py`
#### 10行目
```python
url_patterns = [
    # ...
    URLPattern("/set_cookie", views.set_cookie)
]
```
viewを利用するため、URLパターンも追加しておきました

## 動かしてみる
本当にミニマムではありますが、サーバーから*Set-Cookie*ヘッダーを返却する用意ができました。
これでブラウザがどのような挙動をするか確かめてみましょう。

サーバーを再起動したあと、ブラウザを開きます。

Cookieが付与される前後の動きを確認したいので、まだ`/set_cookie`にはアクセスしないでください。
もしアクセスしてしまった人は、後述するCookieの削除をしてから再度動作確認してみてください。

今回の動作確認ではヘッダーの内容を細かく見ていきたいので、Chromeの任意の画面で `command` + `shift` + `J` を押して（または 右クリック → 検証）検証ツールを開きます。
検証ツールが開いたら、`Network`タブを開きます。

![](https://storage.googleapis.com/zenn-user-upload/4yipex88zndkrg8t0xv79fhc71iy)

検証ツールを開いたまま、URLバーに
`http://localhost:8080/set_cookie`
を入力してエンターを押してください。

そうすると、真っ白な画面が表示されたあと、検証ツールには次の図のように`set_cookie`へのアクセス記録が表示されるはずです。

![](https://storage.googleapis.com/zenn-user-upload/xh0amv9qpd5xnwv7h4erd5our329)

この`set_cookie`の行をクリックすると、詳細なアクセス記録を見ることができます。

![](https://storage.googleapis.com/zenn-user-upload/e9bfrgcsjkcmwitnjucroekk2vcp)

その記録の中の*Response Headers*の項目を見ると、確かに*Set-Cookie*ヘッダーが送られていることが確認できます。
（ちなみに以前もご紹介しましたが、*view source*をクリックすると生のレスポンスヘッダーも確認できます）

![](https://storage.googleapis.com/zenn-user-upload/7c5jl8j5uk1w0xqs9t9du684cbcb)

また、*Request Headers*の項目も見てみると、初めてのアクセスなのでこの時点では*Cookie*ヘッダーは送られていません。

![](https://storage.googleapis.com/zenn-user-upload/j9hk6pydicg5j3mkchpeyeefzz49)

図にすると、このような状態です。

![](https://storage.googleapis.com/zenn-user-upload/tsnxzif6wrz9bflk81141hq2iy1y)


それでは、この状態でページを更新してみましょう。

更新したあとまたネットワークの記録を見てみると、今度は*Request Headers*の項目に*Cookie*ヘッダーが付与されていることが確認できます。

![](https://storage.googleapis.com/zenn-user-upload/21ej1cv32x8bgeenh3n9ip94wljx)

図にすると、このような状態です。

![](https://storage.googleapis.com/zenn-user-upload/0893bjgyw8wtn5ndizxch2fbtoep)

つまり、2回目以降のアクセスで、サーバーの指定したデータをブラウザが*Cookie*ヘッダーを通じて送り返してくれたことが確認できました。

-------

ちなみに、せっかくなのでブラウザ側からCookieが削除される状況についても見ておきましょう。

Chromeでは、アクセス中のサイトで付与されているCookieを、URLバーのinformationアイコンから確認できます。

![](https://storage.googleapis.com/zenn-user-upload/udmhppmruiup8sy1n7s1na312hkw)

すでにCookieが付与されていれば、下図のように`username`というCookieがブラウザに保存されていることが確認できますので、試しに削除してみましょう。

![](https://storage.googleapis.com/zenn-user-upload/y1p4864sspwdpyqzjf92qfpupqt8)

この状態で、検証ツールを開いたままページを更新してみてください。
*Request Headers*を見ると、*Cookie*ヘッダーが表示されない、つまりCookieが送信されていないことが確認できると思います。

![](https://storage.googleapis.com/zenn-user-upload/j9hk6pydicg5j3mkchpeyeefzz49)

このように、ユーザーの操作によって簡単にCookieが削除できてしまうことを忘れないようにしましょう。

ちなみに、今回のCookieは有効期限を指定していないので、ブラウザを終了することでもCookieが削除されることを確認できます。
興味がある方はやってみましょう。

## STEP2: Cookieを使って超簡単なログイン機能を実装してみる

Cookieを使えるようになると、「以前どのような行動をしたユーザーであるか」というのをサーバー側でトラッキングできるようになります。

Cookieを使う代表的な機能といえば、ログイン（認証）機能です。

というわけで、超簡単なログイン機能を実装してみましょう。

ここで実装するログイン機能は本当に簡素で、パスワード認証もありません。
過去にログインページで名前を入力してフォームを送信したことがあればログイン済みとみなします。

まずはソースコードを見てみましょう。

### ソースコード
**`study/henango/server/worker.py`**
https://github.com/bigen1925/introduction-to-web-application-with-python/blob/main/codes/chapter20-2/henango/server/worker.py#L26

**`study/urls/py`**
https://github.com/bigen1925/introduction-to-web-application-with-python/blob/main/codes/chapter20-2/urls.py#L11-L12

**`study/templates/login.html`**
https://github.com/bigen1925/introduction-to-web-application-with-python/blob/main/codes/chapter20-2/templates/login.html

**`study/templates/welcome.html`**
https://github.com/bigen1925/introduction-to-web-application-with-python/blob/main/codes/chapter20-2/templates/welcome.html

**`study/views.py`**
https://github.com/bigen1925/introduction-to-web-application-with-python/blob/main/codes/chapter20-2/views.py#L60-L98

## 解説

### `study/henango/server/worker.py`
#### 26行目
```python
    STATUS_LINES = {
        # ...
        302: "302 Found",
        # ...
    }
```
今回の機能ではリダイレクト機能を使うため、ステータスコードを追加しました。

ステータスコード302は一時的なリダイレクトを意味し、ブラウザは`Location`ヘッダーで指定されたURLへ再度リクエストをし直してくれます。

### `study/urls.py`
#### 11-12行目
```python
url_patterns = [
    # ...
    URLPattern("/login", views.login),
    URLPattern("/welcome", views.welcome),
]
```
2つのエンドポイントを追加しました。

`/login`はその名の通りログインをするための画面で、名前を入力するフォームが表示されます。
フォームを送信すると、`/welcome`へリダイレクトされ、ウェルカムページでログインの時に送信した名前が表示されます。

ただし、ログインをしていない状態で直に`/welcome`ページへアクセスすると、ウェルカムページは表示されず`/login`へリダイレクトされます。

### `study/templates/login.html`
```html
<html>
<body>
  <h1>【ログイン】名前を入力してください</h1>

  <form method="POST">
    名前: <input name="username" type="text">

    <input type="submit" value="送信">
  </form>
</body>
</html>
```
名前を入力するフォームがあるだけの簡素なHTMLです。

formの`action`属性を指定していないので、フォームは`/login`へPOSTされます。

###`study/templates/welcome.html`
```html
<html>
<body>
  <h1>ようこそ！ {username} さん！</h1>
</body>
</html>
```
viewから受け取った名前を表示するだけの簡素なHTMLです。

### `study/views.py`
#### 60-70行目
```python
def login(request: HTTPRequest) -> HTTPResponse:
    if request.method == "GET":
        body = render("login.html", {})
        return HTTPResponse(body=body)

    elif request.method == "POST":
        post_params = urllib.parse.parse_qs(request.body.decode())
        username = post_params["username"][0]

        headers = {"Location": "/welcome", "Set-Cookie": f"username={username}"}
        return HTTPResponse(status_code=302, headers=headers)
```
さて、本題のviewです。

まず`login`から見ていきましょう。

*GET*リクエストのとき、つまりログインページを表示しようとしているときには単にテンプレートHTMLを表示しているだけです。

*POST*リクエストのときは、リクエストボディからPOSTパラメータを抽出し、usernameを取得しています。
その後、
```http request
HTTP/1.1 302 Found
...
Location: /welcome
Set-Cookie: username=<入力された名前>
```
とヘッダーが生成されるようにして、レスポンスを返却しています。

#### 73-98行目
```python
def welcome(request: HTTPRequest) -> HTTPResponse:
    cookie_header = request.headers.get("Cookie", None)

    # Cookieが送信されてきていなければ、ログインしていないとみなして/loginへリダイレクト
    if not cookie_header:
        return HTTPResponse(status_code=302, headers={"Location": "/login"})

    # str から list へ変換
    # ex) "name1=value1; name2=value2" => ["name1=value1", "name2=value2"]
    cookie_strings = cookie_header.split("; ")

    # list から dict へ変換
    # ex) ["name1=value1", "name2=value2"] => {"name1": "value1", "name2": "value2"}
    cookies = {}
    for cookie_string in cookie_strings:
        name, value = cookie_string.split("=", maxsplit=1)
        cookies[name] = value

    # Cookieにusernameが含まれていなければ、ログインしていないとみなして/loginへリダイレクト
    if "username" not in cookies:
        return HTTPResponse(status_code=302, headers={"Location": "/login"})

    # Welcome画面を表示
    body = render("welcome.html", context={"username": cookies["username"]})

    return HTTPResponse(body=body)
```

次に`welcome`です。

少しややこしいですが、やっていることはコメントを読んでいだければ分かると思います。

HTTPリクエストのヘッダーからCookieを取得し、`username`というCookieが送信されてきていればウェルカムページを表示し、送信されてきていなければログインページへリダイレクトしています。

注意点は、HTTPリクエストの`Cookie`ヘッダはCookieの数が1つとは限らず、`;`区切りで複数おくられてくることがある、ということです。
そのため、ヘッダーのパースに少し手間をかける必要が出てきています。

## 動作確認

では、動かしてみましょう。

今回もネットワークの記録を見ながら実験したいので、サーバーを再起動したら、Chromeを開いて **検証ツール → Network** を開いておいてください。
検証ツールを開いたら、
`http://localhost:8080/welcome`
へアクセスしてみましょう。

すると、ウェルカムページへアクセスしたはずなのに、ログインページへ飛ばされてしまうはずです。

![](https://storage.googleapis.com/zenn-user-upload/3pe5trmu913bjstp055eui3lt37x)

![](https://storage.googleapis.com/zenn-user-upload/py69h63kjtyqmhfa270qxpr8th15)

このとき、ブラウザが狙い通りの挙動をしてくれているか確認してみましょう。
検証ツールを見てみると、下図のようにリクエストの記録が2行になっているはずです。

これは、1回目は`/welcome`へリクエストを送ったらステータスコードが302のレスポンスを受け取ったので、`/login`へ2回目のリクエストを送信して今度はステータスコードが200だったので今のページが表示されていますよ、ということ意味しています。

![](https://storage.googleapis.com/zenn-user-upload/tuckp535cvp3s48yqe3fidryc222)

どうやら`/welcome`は想定通りの挙動をしてくれていそうです。

では、このまま`/login`ページで名前を入力してフォームを送信してみましょう。

![](https://storage.googleapis.com/zenn-user-upload/ojuowhoqp9ta74rvugo6xkha8jhx)

すると、`/welcome`へリダイレクトされ、ウェルカムページが表示されるはずです。

![](https://storage.googleapis.com/zenn-user-upload/2vxu642n5bw3ys7z6l9sryart5ow)

また、すでにログイン済みなので、この状態でもう一度`/welcome`へ直接アクセスしても、今度はページが表示されるはずです。

どうでしょう、とっても簡素ですが、Cookieを使ってログイン機能が実装できました。

余裕がある方は、Cookieを削除してもう一度`/welcome`へアクセスすると、今度はまた`/login`へリダイレクトされるようになることも確認してみましょう。


# STEP3: Webアプリケーション内でCookieを使いやすくする

これでもう皆さんはCookieを扱えるようになったわけですが、今のCookieの扱い方はいくつか問題があります。

まず、すでにみてもらったようにHTTPリクエストのCookieヘッダを解析するのは少し骨が折れます。
しかもCookieはよく使う機能ですので、viewにCookie解析のコードを繰り返し書くハメになるのはうんざりです。

次に、今のやり方では実は複数のCookieを扱えません。
RFCの定めによると、複数のCookieをセットしたい場合は
```
HTTP/1.1 200 OK
...
Set-Cookie: username=bigen
Set-Cookie: email=bigen@example.com
```
のように、*Set-Cookie*ヘッダーを**複数記述しなければなりません**。

しかし、今の`HTTPResponse`オブジェクトの`headers`は`dict`型になっており、同じキーの値を複数いれることはできません。

これらの問題を解決するために、Webアプリケーション内のCookieの扱い方に改良を加えていきます。

## ソースコード

**`study/henango/http/request.py`**
https://github.com/bigen1925/introduction-to-web-application-with-python/blob/main/codes/chapter20-3/henango/http/request.py

**`study/henango/http/response.py`**
https://github.com/bigen1925/introduction-to-web-application-with-python/blob/main/codes/chapter20-3/henango/http/response.py

**`study/henango/server/worker.py`**
https://github.com/bigen1925/introduction-to-web-application-with-python/blob/main/codes/chapter20-3/henango/server/worker.py

**`study/views.py`**
https://github.com/bigen1925/introduction-to-web-application-with-python/blob/main/codes/chapter20-3/views.py

**`study/templates/login.html`**
https://github.com/bigen1925/introduction-to-web-application-with-python/blob/main/codes/chapter20-3/templates/login.html#L7

**`study/templates/welcome.html`**
https://github.com/bigen1925/introduction-to-web-application-with-python/blob/main/codes/chapter20-3/templates/welcome.html#L4


## 解説

### **`study/henango/http/request.py`**
```python
class HTTPRequest:
    # ...
    headers: dict
    # ...

    def __init__(
        self,
        # ...
        cookies: dict = None,
        # ...
    ):
        if cookies is None:
            cookies = {}
        # ...

        # ...
        self.cookies = cookies
        # ...
```

`HTTPRequest`オブジェクトに、`cookies`という属性を追加しました。
後述の改良によって、複数のCookieの値がこの`cookies`に入るようにして、
```python
    username = request.cookies['username']
    email = request.cookies['email']
```
などのようにアクセスできるようにしていきます。

これならviewでCookieを扱うのも簡単ですよね

### **`study/henango/http/response.py`**
```python
class HTTPResponse:
    # ...
    cookies: dict
    # ...

    def __init__(
        self,
        # ...
        cookies: dict = None,
        # ...
    ):
        # ...
        if cookies is None:
            cookies = {}

        # ...
        self.cookies = cookies
        # ...
```
こちらもほぼ同様です。

`HTTPResponse`に`dict`型で`cookies`をセットできるようにして、複数のCookieであっても
```python
cookies = {
    'username': 'bigen',
    'email': 'bigen@example.com'
}
return HttpResponse(cookies=cookies)
```
のように扱えるようにしていきます。

### `study/henango/server/worker.py`
#### 109-116行目
```python
       cookies = {}
        if "Cookie" in headers:
            # str から list へ変換 (ex) "name1=value1; name2=value2" => ["name1=value1", "name2=value2"]
            cookie_strings = headers["Cookie"].split("; ")
            # list から dict へ変換 (ex) ["name1=value1", "name2=value2"] => {"name1": "value1", "name2": "value2"}
            for cookie_string in cookie_strings:
                name, value = cookie_string.split("=", maxsplit=1)
                cookies[name] = value
```
workerの*HTTPリクエスト*をパースする部分に、cookieのパースも追加しました。

この処理によって、`HTTPRequest`オブジェクトが生成される際にCookieのパースも済ませてしまうので、view側は難しいことは考えなくてよくなります。

#### 153-154行目
```python
        for cookie_name, cookie_value in response.cookies.items():
            response_header += f"Set-Cookie: {cookie_name}={cookie_value}\r\n"
```
今度は*HTTPレスポンス*を生成する部分に、cookieの扱いを追加しました。
cookie辞書の要素の数だけ、*Set-Cookie*ヘッダーを出力しています。

### `study/views.py`

#### 56-85行目
```python
def set_cookie(request: HTTPRequest) -> HTTPResponse:
    return HTTPResponse(cookies={"username": "TARO"})


def login(request: HTTPRequest) -> HTTPResponse:
    if request.method == "GET":
        body = render("login.html", {})
        return HTTPResponse(body=body)

    elif request.method == "POST":
        post_params = urllib.parse.parse_qs(request.body.decode())
        username = post_params["username"][0]
        email = post_params["email"][0]

        return HTTPResponse(
            status_code=302, headers={"Location": "/welcome"}, cookies={"username": username, "email": email}
        )


def welcome(request: HTTPRequest) -> HTTPResponse:
    # Cookieにusernameが含まれていなければ、ログインしていないとみなして/loginへリダイレクト
    if "username" not in request.cookies:
        return HTTPResponse(status_code=302, headers={"Location": "/login"})

    # Welcome画面を表示
    username = request.cookies["username"]
    email = request.cookies["email"]
    body = render("welcome.html", context={"username": username, "email": email})

    return HTTPResponse(body=body)
```

Cookieの扱いを改良したことによってviewがどのように変わったか見てみましょう。

以前に比べてCookieのセットも、Cookieの取得もとても簡単になっているのが分かると思います。

viewから見ると、たんに`cookies`に*name*と*value*の組み合わせを入れておけば、次回以降`cookies`から取り出せる、という非常に直感的な動きになっています。
複数のCookieの取り扱いも簡単です。

### `study/templates/login.html`
### `study/templates/welcome.html`

複数のCookieの取り扱い例を示すため、`/login`ではemailを入力するフォームを追加し、`welcome`ではメールアドレスを表示する文言を追加しました。
簡単ですので、解説は割愛します。

## 動作確認
機能としてはほとんど変わっていませんが、改良後も問題なく動くか動作確認はしておきましょう。

`/login`へアクセスし、名前とメールアドレスを入力した後、`/welcome`で正常に表示されるでしょうか。

![](https://storage.googleapis.com/zenn-user-upload/oxc41f730h6na7ga5cac6ungy1tv)

![](https://storage.googleapis.com/zenn-user-upload/fcpnjvgxyrta3u2si3a3zcvuc0ew)

# STEP4: 有効期限などの属性を付与できるようにする
さて、長かった本章もこれが最後です。

STEP3の改良でかなりイイ感じになってきたのですが、本章前半で説明したとおり、Cookieには*name*と*value*以外にも様々な属性が付与できます。
例えば`Expires`属性や`Secure`属性などです。

これらを扱うには、1つのCookieを表すのに*name*と*value*しか使えない`dict`型では不足してしまいます。

そこで、1つのCookieを表す`Cookie`クラスを作成し、様々な属性をセットできるようにしましょう。

また、`response.cookies`は`dict`型ではなく`Cookieインスタンスの配列`となるようにしましょう。

## ソースコード
ソースコードはこちらです。

**`study/henango/http/cookie.py`**
https://github.com/bigen1925/introduction-to-web-application-with-python/blob/main/codes/chapter20-4/henango/http/cookie.py

**`study/henango/http/response.py`**
https://github.com/bigen1925/introduction-to-web-application-with-python/blob/main/codes/chapter20-4/henango/http/response.py#L9

**`study/henango/server/worker.py`**
https://github.com/bigen1925/introduction-to-web-application-with-python/blob/main/codes/chapter20-4/henango/server/worker.py#L154-L170

**`study/views.py`**
https://github.com/bigen1925/introduction-to-web-application-with-python/blob/main/codes/chapter20-4/views.py#L71-L74

## 解説

### `study/henango/http/cookie.py`
```python
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
```
1つのCookieを表すクラスを新しく作成しました。

たんに属性を持っていて値を出し入れできるだけのいわゆるデータクラスですので、特に解説は不要ですね。


### `study/henango/http/response.py`
### 6-24行目
```python
class HTTPResponse:
    # ...
    cookies: List[Cookie]
    # ...

    def __init__(
        self,
        # ...
        cookies: List[Cookie] = None,
        # ...
    ):
        # ...
        if cookies is None:
            cookies = []

        # ...
```

`HTTPResponse`クラスの`cookies`属性を、`dict`から`List[Cookie]`に変更しました。
初期値が`{}`から`[]`に変更になっているのを忘れないようにしてください。

### `study/henango/server/worker.py`
#### 154-170行目
```python
        # Cookieヘッダーの生成
        for cookie in response.cookies:
            cookie_header = f"Set-Cookie: {cookie.name}={cookie.value}"
            if cookie.expires is not None:
                cookie_header += f"; Expires={cookie.expires.strftime('%a, %d %b %Y %H:%M:%S GMT')}"
            if cookie.max_age is not None:
                cookie_header += f"; Max-Age={cookie.max_age}"
            if cookie.domain:
                cookie_header += f"; Domain={cookie.domain}"
            if cookie.path:
                cookie_header += f"; Path={cookie.path}"
            if cookie.secure:
                cookie_header += "; Secure"
            if cookie.http_only:
                cookie_header += "; Http-Only"

            response_header += cookie_header + "\r\n"
```
HTTPレスポンスヘッダー生成処理の、Cookieヘッダーの生成部分です。

*name*と*value*だけでなく、他の属性も出力できるように変更しました。

### `study/views.py`
#### 71-74行目
```python
        cookies = [
            Cookie(name="username", value=username, max_age=30),
            Cookie(name="email", value=email, max_age=30),
        ]
```
view側では、このように`Cookie`インスタンスを生成してリストとして受け渡しています。

ここでは、Cookieの有効期限(*Max-Age*属性)を30sに設定しています。

:::details コラム: 実装の詳細を隠す
本書では簡単のためにこの程度の表現でとどめていますが、`Cookie`クラスが存在していることを機能を使うことができず、実装の詳細に立ち入りすぎと感じる方もいるかもしれません。
機能の利用者からすると、Cookieがdictで表現されているのか、オブジェクトなのか、それらは配列で格納されているのかなどといった実装の詳細には興味はありません。

その場合は、例えば`HTTPResponse`クラスにメソッドを追加して
```python
response.set_cookie("username", username, max_age=30)
```
などというインターフェースで扱えるようにすれば実装は隠され、よりDjangoっぽくなりますので挑戦してみてください。
:::

## 動作確認
では、動作を確認してみましょう。

今回もサーバーを再起動したら、まずは検証ツールを開きます。
検証ツールを開いたら、
`http://localhost:8080/login`
へアクセスし、フォームを入力して送信してみましょう。

すると`/welcome`ページへリダイレクトされると思いますので、**検証ツール → Network**から`/login`へアクセスしたときのレスポンスを確認してみましょう。
*Response Headers*を見てみると、*Set-Cookie*ヘッダに*Max-Age*属性が付与されていることが確認できると思います。

![](https://storage.googleapis.com/zenn-user-upload/sa8yf8whsmo4dxtztvf3ibtngwmi)

このCookieは30sが経過するとChromeによって削除され、サーバーへは送信されなくなります。

ログインしてすぐに`/welcome`をリロードした場合はウェルカムページが表示されるのに、30s待ってからリロードすると`/login`へリダイレクトされる、といった挙動が確認できればここでの動作確認は成功です。

余裕のある方は、pathやdomainに値をセットしてみたりして他の属性も動作確認してみても良いでしょう。


-------

# === フィードバックをお寄せください。 ===
本書の内容は、現在ここまでとなっております。
続編は鋭意執筆中ですので、乞うご期待。

本書の続編をご期待される方は、下記フォームよりフィードバックをお寄せください。
（1分程度で回答できます）
読者からのフィードバックが得られない場合、本書の執筆を中断することもありますので是非よろしくおねがいします。

https://docs.google.com/forms/d/1qTTNPbyPyAAMYALth5uDqgsDGmlCe-BXLYYDLk0QKfw/edit?usp=drive_web

また、本書の「いいね」や筆者フォロー、TwitterやFacebookでの拡散も大歓迎です。