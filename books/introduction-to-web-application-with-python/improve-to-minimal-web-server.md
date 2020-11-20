---
title: "「まともなWebサーバー」へ進化する"
---

# まともなWebサーバーになるためには？

本章では、[既に皆さんに作っていただいた](https://zenn.dev/bigen1925/books/introduction-to-web-application-with-python/viewer/making-silly-web-server) 「へなちょこWebサーバー」を、「まともなWebサーバー」へ進化させていきます。

そこで、皆さんに作っていただいたWebサーバーが具体的何がへなちょこだったのか整理しておきましょう。

そもそもWebサーバーとは、**HTTPのルールにしたがって通信を行うサーバー**のことでした。
逆に言うと、いっぱしのWebサーバーになるためには、**HTTPのルールに従ってレスポンスを返せるサーバー**でなくてはありません。

しかし、皆さんのへなちょこWebサーバーは、HTTPのルールにしっかりと従っているとは言えません。

具体的に皆さんのサーバーが返しているレスポンス(= `server_send.txt`)を再度見てみましょう。

------
`server_send.txt`
```http
HTTP/1.1 200 OK
Date: Wed, 28 Oct 2020 07:57:45 GMT
Server: Apache/2.4.41 (Unix)
Content-Location: index.html.en
Vary: negotiate
TCN: choice
Last-Modified: Thu, 29 Aug 2019 05:05:59 GMT
ETag: "2d-5913a76187bc0"
Accept-Ranges: bytes
Content-Length: 45
Keep-Alive: timeout=5, max=100
Connection: Keep-Alive
Content-Type: text/html

<html><body><h1>It works!</h1></body></html>

```

-----

みなさんのWebサーバーは、**いつどんなpathにリクエストが来ても、固定でこの内容をレスポンスとして返しています。**

改めて見て見ると、そもそもHTTPのフォーマットを守れているかと言うと、しっかりと守れていそうです。
1行目にレスポンスラインがあり、2行目からいくつかのヘッダーがあり、空行の後にボディがあります。
もともとApacheのレスポンスを拝借したので、これは当たり前ですね

どんなpathへのリクエストであってもボディが「It works!」なのは、イケてはいませんがルール違反というほどではありません。
「うちはそういうサービスなのだ」と言い張ることにしましょう。

**問題は、ヘッダーにあります。**

例えば[RFC7231 7.1.1.2](https://triple-underscore.github.io/RFC7231-ja.html#section-7.1.1.2) によると、`Date`ヘッダーはWebサーバーがレスポンスを発信した日時を記載しなければならないことになっています。
しかし、現在はレスポンス生成日時に関係なく固定になってしまっています。
（上記例だと`Date`は`2020/10/28 7:57:45`固定）

また、`Server`ヘッダー([RFC7231 7.4.2](https://triple-underscore.github.io/RFC7231-ja.html#section-7.4.2) )は、レスポンスを生成したプログラムに関する情報を記載することになっており、一般的にWebサーバーの名前などが記載されます。
しかし、私達が作ったのは`Apache`という名前のWebサーバーではないのに、`Server: Apache/2.4.41 (Unix)`で固定になってしまっています。

（Webサーバー名はサーバーの開発者が自由につけていいことになっているので、厳密にはルール違反ではありませんが、他人のプログラム名を騙るのは「まともな」Webサーバーとは言えないでしょう。）

----

というわけで、「まともなWebサーバー」に進化するために、これらのヘッダーを整えてHTTPのルールにきちんと従ったレスポンスを自力で生成できるようにプログラムを改良していきましょう。

**最初のステップとして、Apacheが返しているヘッダーを1つずつ見ていって、手直しが必要かどうか確認していきます。**

ちなみに、HTTPヘッダーのうち必須とされているものは、リクエストにおける`Host`ヘッダーのみであり、レスポンスには必須ヘッダーは存在しません。
そのため、実装や学習に手間のかかるものはこのステップで取り除いてしまいます。

**次のステップとして、プログラムを実際に修正し、適切なヘッダーをレスポンスに含めることができるように改良していきます。**


# Apacheのレスポンスのヘッダーを確認する

それではApacheのレスポンスに含まれるヘッダーを順に見ていき、必要なものを取捨選択し、手直しの内容を確認していきましょう。
少し内容が多くなるので、あまり細かいことに興味がない方は飛ばし読みでも構いません。

## Date
```http
Date: Wed, 28 Oct 2020 07:57:45 GMT
```
RFC: https://triple-underscore.github.io/RFC7231-ja.html#header.date

先程すでに見たところですが、まずは`Date`ヘッダーについて見てみます。
`Date`はレスポンスを生成した日時を表します。

今は固定の日時が返却されてしまっていますが、Pythonであれば`datetime`モジュールを使えば日時の取得は簡単ですので、きちんと**レスポンスを生成した日時**を返すようにしましょう。

## Server
```http
Server: Apache/2.4.41 (Unix)
```
RFC: https://triple-underscore.github.io/RFC7231-ja.html#header.server

こちらも先程すでに見ましたが、`Server`ヘッダーはレスポンスを生成したプログラムに関する情報を返します。
記載内容は特に指定はされていませんが、あんまり細かすぎる情報は書くべきではないとされていて、サーバー名やOS名ぐらいに留めておくことが一般的です。

今は`Apache/2.4.41 (Unix)`で固定になっていますが、自分でつけたオリジナルの名前にしてしまいましょう。

本書では、へなちょこWebサーバーのver.0.1、略して**HenaServer/0.1**を返すことにします。

皆さんはご自分でお好きな名前をつけてあげてください。


## Content-Location
```http
Content-Location: index.html.en
```
RFC: https://triple-underscore.github.io/RFC7231-ja.html#header.content-location

`Content-Location`は、返却されたレスポンスを取得するための、代わりのURLを示します。

こちらは理解が少し難しいかもしれません。

今回のケースでいうと、Chromeは`/`というリソースを要求する際に、ついでにコンテントネゴシエーションというプロセスを行っています。

具体的には、ChromeはHTTPリクエスト内で
```http
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
Accept-Encoding: gzip, deflate, br
Accept-Language: ja-JP,ja;q=0.9,en-US;q=0.8,en;q=0.7
```
などのヘッダーを通じて
「私が理解できるコンテンツの形式はこれで、対応している圧縮形式はこれで、言語は日本語が一番欲しいけど、でも英語でもいいよ」
といったことを伝えています。

サーバー側は、その内容に応じて適切なレスポンスを生成しています。

この協調作業をコンテントネゴシエーションと言いますが、これはリクエストの仕方によって内容がコロコロ変わりうる、ということになります。

そのため、
「今回返却されたレスポンスと同じ内容が欲しい場合は、`/`じゃなくて代わりに`/index.html.en`にアクセスしてね」
ということをApacheが伝えているのです。

本書で作るサーバーはそこまで複雑なことはしませんので、このヘッダーは**返却しない**ことにします。


## Vary
```http
Vary: negotiate
```
RFC: https://triple-underscore.github.io/RFC7231-ja.html#header.vary

`Vary`ヘッダーは、ブラウザや中間サーバーがキャッシュを使用するかどうかを制御するためのヘッダーです。
このヘッダーに記載されたヘッダーが変化しない限りは、キャッシュを使って良いということを意味します。

今回でいうと、先程説明したコンテントネゴシエーションを行うヘッダーに変化がない限り、キャッシュされた内容を使いまわして良いですよ、とサーバーが伝えていることになります。

本書ではキャッシュ制御は行いませんので、このヘッダーは**返却しない**ことにします。

## TCN
```http
TCN: choice
```
RFC: https://tools.ietf.org/html/rfc2295#section-8.5

こちらは少しマイナーなヘッダーで、Transparent Content Negotiationについて書かれた別のRFC 2295に記載されています。

どのようにコンテントネゴシエーションが行われたかを伝えるヘッダーですが、煩雑になってしまうためここでは説明は割愛します。

コンテントネゴシエーションは本書では行いませんので、このヘッダーは**返却しない**ことにします。

## Last-Modified
```http
Last-Modified: Thu, 29 Aug 2019 05:05:59 GMT
```
RFC: https://triple-underscore.github.io/RFC7232-ja.html#header.last-modified

`Last-Modified`ヘッダーは、コンテンツの内容が最後に変更された日時を返します。
一貫した最終変更日時を返却できるならば、このヘッダーは返すべきであるとされています。

なお、「一貫した最終変更日時を返却できない」状況というのは、リクエストごとに毎回内容がことなるURLなどではLast-Modifiedが同じなのに内容が違ったり、Last-Modifiedが違うのに内容が同じだったりしてしまい、意味のあるLast-Modifiedの値が存在しない場合などを指します。

本書ではURLごとに最終変更日時が意味を持ったり持たなかったりしますので、簡単のためこのヘッダーは**返却しない**ことにします。

## ETag
```http
ETag: "2d-5913a76187bc0"
```
RFC: https://triple-underscore.github.io/RFC7232-ja.html#header.etag

`ETag`ヘッダーは、レスポンスを生成するリソースの特定のバージョンを示す識別子です。
すなわち、リソースが何かしら更新されれば、ETagも違う値になることが期待されます。
多くの場合、ファイルやコンテンツのハッシュ値などが使われます。

こちらもブラウザや中間サーバーのキャッシュ制御に用いられるものですが、本書ではキャッシュ制御は扱わないためこのヘッダーは**返却しない**ことにします。

## Accept-Ranges
```http
Accept-Ranges: bytes
```
RFC: https://triple-underscore.github.io/RFC7233-ja.html#header.accept-ranges

`Accept-Ranges`ヘッダーは、`Range Requests`という「リソースの部分的なリクエスト」に対応していることを示すヘッダーです。

`Range Requests`は、大きなサイズのファイルをダウンロードする際に分割ダウンロードなどができるようにするための機能です。

本書では`Range Requests`には対応しませんので、このヘッダーは**返却しない**ことにします。

## Content-Length
```http
Content-Length: 45
```
RFC: https://triple-underscore.github.io/RFC7230-ja.html#header.content-length

`Content-Length`ヘッダーは、レスポンスボディのバイト数を10進数で示す値を返します。

こちらはサーバーは一部の例外を除き、返却すべきということになっています。

pythonでバイト数を取得するのは難しくありませんので、きちんと**ボディのバイト数を返却する**ことにします。

## Keep-Alive
```http
Keep-Alive: timeout=5, max=100
```
RFC: https://tools.ietf.org/id/draft-thomson-hybi-http-timeout-01.html#keep-alive

`Keep-Alive`ヘッダーは、次に説明するコネクションの再利用に関して、いつまでコネクションを再利用して良いかの情報を返します。

このヘッダーはドラフトのRFC（試験的な仕様）として提出されており、モダンブラウザはほぼ全て対応していますが、まだ正式なRFCの標準仕様としては取り込まれていません。

本書ではコネクションの再利用を実装しないため、このヘッダーは**返却しない**ことにします。

## Connection
```http
Connection: Keep-Alive
```

`Connection`ヘッダーは、一度確立したTCPコネクションを次のリクエストで再利用して良いかどうかを返します。

TCPコネクションは確立するのにそれなりに時間がかかり、表示速度を最適化する際にはTCPコネクションの再利用が効果的であることが知られています。

コネクションの再利用の機能は本書の範囲外となるため、実装しません。

ただし、`HTTP/1.1`では通信はデフォルトでコネクションの再利用をすることになっており、**コネクションの再利用に対応していないサーバーは`Connection: Close`を返却しなければならないことになっているので、本書ではこれを返すようにします。**

## Content-Type
```http
Content-Type: text/html
```
RFC: https://triple-underscore.github.io/RFC7231-ja.html#header.content-type

`Content-Type`ヘッダーは、レスポンスボディの形式を返します。
使える値は、`MIME-Type`と呼ばれている値で、

- text/html
- text/css
- image/jpeg
- application/javascript
- application/json

などがあります。

一覧を調べたい方は、[こちらのサイト](https://developer.mozilla.org/ja/docs/Web/HTTP/Basics_of_HTTP/MIME_types/Common_types) が参考になるでしょう。

このヘッダーは省略してしまうと「正体不明のファイル」として扱われてしまいブラウザの画面で表示されないことがありますので、きちんと内容にあったものを返しましょう。

本書では、次のステップではボディとして`HTML`しか返却しませんので、**まずは`text/html`を固定で返すことにします。**
また後ほど`HTML`以外のボディを返却することになった際に、色々な値を返せるように改良しましょう。


# きちんとしたヘッダーを返す「まともなWebサーバー」へ改良する

それでは、上記の方針できちんとしたヘッダーを返すサーバーへ改良していきましょう。

改良ポイントを改めてまとめておくと、

- `Date`で`レスポンス生成日時`を返すようにする
- `Host`で`HenaServer/0.1`を返すようにする
- `Content-Length`で`ボディのバイト数`を返すようにする
- `Connection`で`Close`を返すようにする
- `Content-Type`で`text/html`を返すようにする

です。

また、ヘッダーを色々書き換える必要があるので、レスポンスをファイルから取得するのはやめて、ボディ（`It Works!`）もpythonで生成するようにしてしまいましょう。

## ソースコード

では、まずは改良を加えたソースコードを見ていきましょう。

**`study/webserver.py`** (旧: `study/tcpserver.py`)
```python
import socket
from datetime import datetime


class WebServer:
    """
    Webサーバーを表すクラス
    """
    def serve(self):
        """
        サーバーを起動する
        """

        print("=== サーバーを起動します ===")

        try:
            # socketを生成
            server_socket = socket.socket()
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            # socketをlocalhostのポート8080番に割り当てる
            server_socket.bind(("localhost", 8080))
            server_socket.listen(10)

            # 外部からの接続を待ち、接続があったらコネクションを確立する
            print("=== クライアントからの接続を待ちます ===")
            (client_socket, address) = server_socket.accept()
            print(f"=== クライアントとの接続が完了しました remote_address: {address} ===")

            # クライアントから送られてきたデータを取得する
            request = client_socket.recv(4096)

            # クライアントから送られてきたデータをファイルに書き出す
            with open("server_recv.txt", "wb") as f:
                f.write(request)

            # レスポンスボディを生成
            response_body = "<html><body><h1>It works!</h1></body></html>"

            # レスポンスラインを生成
            response_line = "HTTP/1.1 200 OK\r\n"
            # レスポンスヘッダーを生成
            response_header = ""
            response_header += f"Date: {datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')}\r\n"
            response_header += "Host: HenaServer/0.1\r\n"
            response_header += f"Content-Length: {len(response_body.encode())}\r\n"
            response_header += "Connection: Close\r\n"
            response_header += "Content-Type: text/html\r\n"

            # ヘッダーとボディを空行でくっつけた上でbytesに変換し、レスポンス全体を生成する
            response = (response_line + response_header + "\r\n" + response_body).encode()

            # クライアントへレスポンスを送信する
            client_socket.send(response)

            # 通信を終了させる
            client_socket.close()

        finally:
            print("=== サーバーを停止します。 ===")


if __name__ == '__main__':
    server = WebServer()
    server.serve()

```
https://github.com/bigen1925/introduction-to-web-application-with-python/blob/main/codes/chapter10/webserver.py

## 解説
### ファイル名とクラス名を変更
`tcpserver.py` => `webserver.py`
```python
class WebServer:
    """
    Webサーバーを表すクラス
    """
```
```python
if __name__ == '__main__':
    server = WebServer()
    server.serve()
```
まずは今回の修正で、TCP通信を行う「エセWebサーバー」から「まともなWebサーバー」に成長しましたので、クラス名とファイル名も変更しておきました。

### レスポンスを動的に生成
変更があったのは、37行目-46行目で、以前はファイルからレスポンスを取得していた箇所をPythonで生成するようにしました。

```python
            # レスポンスボディを生成
            response_body = "<html><body><h1>It works!</h1></body></html>"

            # レスポンスラインを生成
            response_line = "200 OK\r\n"
            # レスポンスヘッダーを生成
            response_header = ""
            response_header += f"Date: {datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')}\r\n"
            response_header += "Host: HenaServer/0.1\r\n"
            response_header += f"Content-Length: {len(response_body.encode())}\r\n"
            response_header += "Connection: Close\r\n"
            response_header += "Content-Type: text/html\r\n"
```

本書の読者には特に説明は不要でしょう。

単純に必要な文字列をPythonで生成し、`bytes`へ変換しているだけです。

難しいくて分からないという方より、どちらかというと、
「こんなベタ書きでいいのか？」
「繰り返しでてくる改行コードは定数にしなくていいのか？」
「文字列結合にjoinとか使わなくていいのか？」
などとツッコミたくなる方のほうが多いでしょう。

いいんです。

まだ人様に見せるソースコードではありませんし、ヘッダーの数もそれほど多いわけじゃありません。
むしろ並べて書いておいたほうが見やすいぐらいです。

ヘッダーの数が増えてソースコードの見通しが悪くなったり、コピペするのが疲れるぐらい改行コードが出てくるようになってから初めてリファクタリングすれば良いのです。

本書は自分の勉強のためにするものですから、自分が理解できて動けばそれで良いのです。

## 動かしてみる
それでは、実際にプログラムを動かしてみましょう。

動かし方は前回までと同じで、コンソールで`study`ディレクトリまで移動した後、`python webserver.py`を実行します。

```shell
$ python webserver.py
=== サーバーを起動します ===
=== クライアントからの接続を待ちます ===
```

このタブを開いたまま、ブラウザで`http://localhost:8080`へアクセスしてみましょう。

今まで通り、`It works!`が表示されていれば成功です！

![](https://storage.googleapis.com/zenn-user-upload/nzlgia81xhvzdagy9o6jj60xc72u)

# 「Webサーバー」になった
今回の修正によって、皆さんの自作サーバーはかなり「Webサーバー」と呼べるものになってきました。

もちろんまだ`It works!`しか表示できませんし、コネクション管理やキャッシュ制御もできません。

それでも最低限とはいえHTTPのルールをそれなりに守ってますし、もうChromeやApacheからパクってきた箇所は1行もありません。

みなさんが全て自力で作り上げた、立派なWebサーバーなのです。

また、たったの20行程度ですが、この20行にWebサーバーの基本が全て詰まっているといっても過言ではありません。

「Webサーバー」なるものの正体は、ただの「HTTPを喋るデーモンプログラム^[バッグクラウンドでずっと動き続けているプログラムのこと]」だったのです。
