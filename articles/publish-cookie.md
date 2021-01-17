---
title: "「伸び悩んでいる3年目Webエンジニアのための、Python Webアプリケーション自作入門」を更新しました"
emoji: "🚶"
type: "tech"
topics: [python, web, http]
published: true
---

# 本を更新しました

[チャプター「Cookieを扱う」](https://zenn.dev/bigen1925/books/introduction-to-web-application-with-python/viewer/cookie) 
を更新しました。

続きを読みたい方は、ぜひBookの「いいね」か「筆者フォロー」をお願いします ;-)

:::message alert
本章を更新するにあたって、既存のソースコードに不具合があったので変更を加えました。

`study/henango/server/worker.py`の`60-68行目`について、

誤）
```python
            # レスポンスヘッダーを生成
            response_header = self.build_response_header(response, request)

            # レスポンスラインを生成
            response_line = self.build_response_line(response)

            # レスポンスボディを変換
            if isinstance(response.body, str):
                response.body = response.body.encode()
```

正）
```python
            # レスポンスボディを変換
            if isinstance(response.body, str):
                response.body = response.body.encode()

            # レスポンスヘッダーを生成
            response_header = self.build_response_header(response, request)

            # レスポンスラインを生成
            response_line = self.build_response_line(response)
```

と変更しました。

bodyをbytesに変換してからヘッダーを生成しないと、Content-Lengthの計算に誤りが出てしまっていました。
:::

----

以下、書籍の内容の抜粋です。

------

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

------

# 続きはBookで！

[チャプター「Cookieを扱う」](https://zenn.dev/bigen1925/books/introduction-to-web-application-with-python/viewer/cookie) 
