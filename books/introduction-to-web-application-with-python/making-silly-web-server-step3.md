---
title: "STEP3: 自作クライアントとApacheで通信してみる"
---

# 自作クライアントと Apache で通信してみる

本章では、世間一般の Web サーバーがブラウザに対してどのようなレスポンスを返しているのかを調べるために、Chrome の代わりとなるような自作クライアントを作っていきます。
この自作クライアントから Apache にリクエストを送り、そのレスポンスの中身を観察すれば、Web サーバーのレスポンスがどんなものか分かるはずです。

というわけで、本章では下図の状態を目指します。

![](https://storage.googleapis.com/zenn-user-upload/agm34wy2s5sd162qhdl2eeh4q8i3)

# TCP クライアントを作る

さて Chrome の代わりになるようなプログラムを作っていくのですが、Chrome をはじめとするブラウザのように、サーバーに対して TCP のルールに従ってリクエストを送り、TCP のルールに従ってレスポンスを受け取るようなプログラムを`TCPクライアント`と呼びます。

ブラウザはこの TCP クライアントの機能の上に、更に URL バーになにか入力すると小難しいリクエストを自動生成したり、ボタンをクリックしたら次のページへ移動できたり、履歴を管理できたり、様々な機能を備えたプログラムです。
しかし、私たちがこれから作るプログラムは Chrome の代わりを努めてもらうとはいえ「ブラウザ」と呼べるほど立派な機能がついているわけではなく、TCP 通信がたった 1 回だけできる簡単なプログラムなので、単に`TCPクライアント`と呼ぶことにします。

# いきなりソースコード

さて、前章と同じく、そんな TCP クライアントのソースコードをいきなり書いてみましょう。

前章同様、`study`ディレクトリの中に次の`tcpclient.py`を用意してください。

**`study/tcpclient.py`**

```python
import socket


class TCPClient:
    """
    TCP通信を行うクライアントを表すクラス
    """
    def request(self):
        """
        サーバーへリクエストを送信する
        """

        print("=== クライアントを起動します ===")

        try:
            # socketを生成
            client_socket = socket.socket()
            client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            # サーバーと接続する
            print("=== サーバーと接続します ===")
            client_socket.connect(("127.0.0.1", 80))
            print("=== サーバーとの接続が完了しました ===")

            # サーバーに送信するリクエストを、ファイルから取得する
            with open("client_send.txt", "rb") as f:
                request = f.read()

            # サーバーへリクエストを送信する
            client_socket.send(request)

            # サーバーからレスポンスが送られてくるのを待ち、取得する
            response = client_socket.recv(4096)

            # レスポンスの内容を、ファイルに書き出す
            with open("client_recv.txt", "wb") as f:
                f.write(response)

            # 通信を終了させる
            client_socket.close()

        finally:
            print("=== クライアントを停止します。 ===")


if __name__ == '__main__':
    client = TCPClient()
    client.request()
```

https://github.com/bigen1925/introduction-to-web-application-with-python/blob/main/codes/chapter7/tcpclient.py

また、`server_recv.txt`ファイルを同じディレクトリに`client_send.txt`という名前でコピーしてください。

:::message alert
ファイルを新規作成してから内容だけをコピーするのではなく、ファイルごとコピーするようにしてください。
本書で使うプログラム群では「改行コード」が重要なのですが、内容だけを貼り付けした場合、改行コードがエディタによって自動的に変換されてしまう可能性があるためです。
:::

**`study/client_send.txt`**
（一例）

```http
GET / HTTP/1.1
Host: localhost:8080
Connection: keep-alive
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
Sec-Fetch-Site: none
Sec-Fetch-Mode: navigate
Sec-Fetch-User: ?1
Sec-Fetch-Dest: document
Accept-Encoding: gzip, deflate, br
Accept-Language: ja-JP,ja;q=0.9,en-US;q=0.8,en;q=0.7


```

# Apache を起動して、TCP クライアントを起動してみる

先に TCP クライアントの挙動を補足しておくと、上記の TCP クライアントのプログラムは起動すると`client_send.txt`というファイルの内容を取得し、そのまま Apache(`localhost:80`）に送信します。

また、Apache からの応答は`client_recv.txt`へ書き込みます。

`client_send.txt`には、STEP2 で Chrome が送ってきたリクエスト内容がそのまま入っているわけですから、Chrome になりすまして Apache へリクエストを送っていることになるわけです。

![](https://storage.googleapis.com/zenn-user-upload/nrewexbi23p51z3kyb4q12ihaycs)

::: message
今回の実験では、TCP クライアントはポート **80 番** へリクエストを送ることに注意してください。
前章の実験では、私たちの自作サーバー（8080 番を見張っている）にリクエストを送信していたのに対し、今回の実験では Apache(80 番を見張っている)にリクエストしたいからです。
![](https://storage.googleapis.com/zenn-user-upload/4qk43opw6ws6x2fatddfvk12si3e)
:::

## Apache を起動する

それでは、まずは Apache を起動します。

STEP1 のときと同様に、`apachectl`を使って Apache を起動させます。

```shell
$ sudo apachectl start
$
```

前回は`ps`コマンドをつかって Apache の起動確認をしましたが、今回からはブラウザを使って確認しておきましょう。
Chrome で`http://localhost`へアクセスし、`It works!`の画面が表示されれば起動完了です。

![](https://storage.googleapis.com/zenn-user-upload/5ck8hf5ow3ewo8yn3x4amvx641xt)

この時点での状態はこうです。
![](https://storage.googleapis.com/zenn-user-upload/jakitt95dxbfovd2fuctls3pvmir)

## TCP クライアントを起動する

次に、TCP クライアントを起動してみましょう。

コンソールで study ディレクトリまで移動し、`tcpclient.py`を実行します。

```shell
$ python tcpclient.py
=== クライアントを起動します ===
=== サーバーと接続します ===
=== サーバーとの接続が完了しました ===
=== クライアントを停止します。 ===
```

このようにログがでれば、正常に Apache との通信が終了しています。

## レスポンスの内容を確認する

最後に、Apache からのレスポンスの内容を確認してみましょう。
`study/client_recv.txt`が作成されているはずですので、エディタで開いてみてください。

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

無事にレスポンスの中身が取得できました！　パンパカパーン！

ブラウザで`It works!`と表示されていた画面の本体（画面のもと？）は、このような文字列だったということになります。

なんだかリクエストと少しフォーマットは似ていますが、やっぱりわけのわからない文字列たちでした。

ですが、最後の行には見覚えがあると思います。
皆さんお馴染みの`HTML`ですね。

# ソースコードの解説

では、ソースコードの解説です。

## エントリーポイントと、socket インスタンスの生成

socket インスタンスを生成するところまでは前章とほぼ同じなので、解説は不要でしょう。

おさらいしておくと、`socket`*モジュール*は TCP 通信を行うためのライブラリで、`socket`*インスタンス*は各通信ごとの受け口にあたるオブジェクトです。

```python
import socket


class TCPClient:
    """
    TCP通信を行うクライアントを表すクラス
    """
    def request(self):
        """
        サーバーへリクエストを送信する
        """

        print("=== クライアントを起動します ===")

        try:
            # socketを生成
            client_socket = socket.socket()
            client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            # ...中略

        finally:
            print("=== クライアントを停止します。 ===")


if __name__ == '__main__':
    client = TCPClient()
    client.request()

```

## サーバーとの接続

前章、TCP サーバーと違うのはここからです。
サーバーを作るときは、外部からのリクエストを受け付ける（or 待ち受ける）ために、socket インスタンスに対して`.bind()`や`.listen()`を呼びだしていました。

しかし、クライアント側はポートをじっと待ち受ける必要はありませんので、bind や listen は不要です。

代わりに、socket インスタンスに対して`.connect()`メソッドを呼び出してあげることで、TCP サーバーへ接続を試みます。

```python
            # サーバーと接続する
            print("=== サーバーと接続します ===")
            client_socket.connect(("localhost", 80))
            print("=== サーバーとの接続が完了しました ===")
```

ここでは、`localhost`の`ポート80`、つまり Apache が起動しているはずのポートへ向けて接続を試みています。

接続先が見つからない（宛先ホストが存在しない IP アドレスになっていたり、宛先ポートで TCP サーバーが起動していなかったり）場合は、例外が送出されます。
無事接続先が見つかった場合は、このメソッドによってコネクションが確立されます。

ちなみに、TCP は双方向に通信を行うことを前提としたプロトコルですので、クライアント側のプログラムにもポート番号を割り当てる必要があります。
（でないと、サーバーは正確にクライアントプログラムに宛ててデータを送ることができません。）

ここでは、`.connect()`によってコネクションが確立される際に、ライブラリが自動的に空いているポートを適当に見つけてきて、割り当ててくれています。
このポート番号は(well known port じゃない範囲から)毎回ランダムに選ばれますので、注意してください。

## リクエストデータを取得し、サーバーへリクエストを送る

次に、ファイル(`client_send.txt`)からサーバーへ送るためのデータを取得し、サーバーへ送信する部分です。

```python
            # サーバーに送信するリクエストを、ファイルから取得する
            with open("client_send.txt", "rb") as f:
                request = f.read()

            # サーバーへリクエストを送信する
            client_socket.send(request)
```

データを送信するには、接続済みの socket インスタンスに対して`.send()`メソッドを呼び出します。

引数は送信したいデータですが、bytes 型でないといけないことに気をつけてください。
（よく文字列のまま send に渡してしまってエラーを発生させている筆者より）

## レスポンスを受け取る

Web サーバーがリクエストを受け取ると、それほど間もなくレスポンスを返してくれるはずです。
なので、`.send()`を実行したあとは、そのまますぐにレスポンスを待つ処理を実行しましょう。

```python
            # サーバーからレスポンスが送られてくるのを待ち、取得する
            response = client_socket.recv(4096)

            # レスポンスの内容を、ファイルに書き出す
            with open("client_recv.txt", "wb") as f:
                f.write(response)
```

ここでレスポンス待ちを実行しているのは、TCP サーバーのときにも使った`.recv()`メソッドです。

サーバーはすぐにレスポンスを返すとはいえ、ほんの少しはタイムラグがあります。
`.send()`をした直後はまだサーバーがレスポンスを返していませんので、`.recv()`メソッドが実行された時点ではまだネットワークバッファには受け取りデータが溜まっていない状態です。

ですので、プログラムはここで一瞬止まり、レスポンスを待つことになります。

（おさらいですが、`.recv()`メソッドは呼び出した時点ですでにネットワークバッファにデータが溜まっていれば値を返しますが、データが空っぽのときは新しいデータが届くまでプログラムを停止させます。）

そして無事レスポンスが届き次第、値は`response`変数に代入され、すぐに`client_recv.txt`ファイルへ書き出されます。

## TCP 接続の切断

```python
            # 通信を終了させる
            client_socket.close()
```

前章で説明した通りです。

通信を終了させるときには、`.close()`メソッドを呼び出して接続を切断させるのを忘れないようにしましょう。

::: details コラム: コンテキストマネージャーによる socket
本書では、TCP 通信初心者の方に`close()`は忘れてはいけないものだということを意識してもらうために、実はあえて close を書かなければいけない記法を採用していました。

しかし、python にはコンテキストマネージャー（with 句）というものが用意されており、file の close や、socket の close のような忘れてはいけない処理を自動的にやってくれる仕組みがあります。
socket ライブラリもそれに対応しており、以下の記法を使うと with 句を抜ける際に自動的に close を実行してくれます。

```python
with socket.socket() as socket:
  # do something to socket
  # ex) socket.bind()
  # ex) socket.connect()
```

:::

# 終わり

本章までで、自作サーバーと自作クライアントを使って、Chrome と Apache がどのようなデータを送り合っているのかを特定することができました。

![](https://storage.googleapis.com/zenn-user-upload/ma6c4rph0ximuzi2xk8urpachg6b)

![](https://storage.googleapis.com/zenn-user-upload/u13spvyfk65k0wjgnqav7hfqh7zg)

次章では仕上げとして、本章で生成した Apache のレスポンスデータを、自作サーバーからブラウザへ返せるように改良して、どのように動くのかを観察してみようと思います。
