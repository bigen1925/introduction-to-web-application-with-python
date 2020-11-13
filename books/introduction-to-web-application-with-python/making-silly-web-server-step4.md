---
title: "STEP4: 自作サーバーを進化させる"
---

# 自作サーバーを進化させる

前章までで、ChromeとApacheがどのようなデータをやりとりしているのかが分かりました。

本章では、STEP2で作成したTCPサーバーを改良して、Apacheが返していたのと全く同じレスポンスを返せるようにしてみます。

全く同じレスポンスを返せば、Chromeの画面には、Apacheの時と同じ`It works!`の画面が表示されるのでしょうか？

実験です！

![](https://storage.googleapis.com/zenn-user-upload/0wuw3i0kysdqo11er3s5u4mr22hy)

# ソースコード
ここまでくれば、もう難しい解説は不要でしょう。

いきなりソースコードの話にいってしまいます。

STEP2で作成した`TCPServer.py`を、以下のように修正します。

**`study/TCPServer.py`**
```python
import socket


class TCPServer:
    """
    TCP通信を行うサーバーを表すクラス
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

            # クライアントへ送信するレスポンスデータをファイルから取得する
            with open("server_send.txt", "rb") as f:
                response = f.read()

            # クライアントへレスポンスを送信する
            client_socket.send(response)

            # 通信を終了させる
            client_socket.close()

        finally:
            print("=== サーバーを停止します。 ===")


if __name__ == '__main__':
    server = TCPServer()
    server.serve()
```
https://github.com/bigen1925/introduction-to-web-application-with-python/blob/main/codes/chapter8/TCPServer.py

変わったのは36~41行目です。
::: messages
Zennではソースコードに行番号が表示されませんので、行数で場所が分からない方はgithubのソースコードも併せて参照してください。
:::

35行目までで以前と同じようにリクエストを`server_recv.txt`に書き出したあと、レスポンスを返すために`server_send.txt`からデータを読み込み、クライアントへ送信しています。

```python
            # クライアントへレスポンスを送信する
            client_socket.send(response)

            # 通信を終了させる
            client_socket.close()
```

ですので、このプログラムを動かすには、`study`ディレクトリに`server_send.txt`というファイルをあらかじめ作成しておく必要があります。
ファイルの内容は、レスポンスとしてクライアントへ送信するデータですので、STEP3で生成した`client_recv.txt`の中身（＝Apacheのレスポンス）をコピー＆ペーストしましょう。

**`study/server_send.txt`**
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

# プログラムを動かしてみる
それでは、改良したこのプログラムを動かしてみましょう。

## 自作TCPサーバーを起動する
STEP2と同様に、`study`ディレクトリまで移動し、コンソールでTCPサーバーを起動します。

```shell
$ python TCPServer.py
=== サーバーを起動します ===
=== クライアントからの接続を待ちます ===
```

## Chromeからリクエストを送る
ChromeのURLバーに`http://localhost:8080`と入力してみましょう。

**自作TCPサーバーは8080番ポートで起動していることに注意しましょう。**

![](https://storage.googleapis.com/zenn-user-upload/nzlgia81xhvzdagy9o6jj60xc72u)

無事`It works!`が表示されました！

## サーバーのログを確認する
前回同様、念の為サーバーのログを確認して正常に動作したか確認しておきましょう。

サーバーを起動したコンソールのタブを確認すると、下記のようにログが追加されているはずです。

```shell
$ python TCPServer.py
=== サーバーを起動します ===
=== クライアントからの接続を待ちます ===
=== クライアントとの接続が完了しました remote_address: ('127.0.0.1', 59550) ===
=== サーバーを停止します。 ===
```

# 自作Webサーバー、初めの一歩。
さて、ここまでくるのにも随分かかりましたが、なんとか曲りなりにもブラウザと通信できるサーバーを自作することができました！

今のところどんなpathにアクセスしても`It works!`と表示されてしまいますし、1度だけリクエストを受け付けたら終了してしまうとんでもない「へなちょこサーバー」ですが、これが皆さんの**自作Webサーバー ver0.1**ということになります。

勉強することは多かったかもしれませんが、まだ書いたプログラムは実質たったの十数行です。
「通信」とか「サーバー」とかいうと、とても難しい技術で手に負えないと思っていた方もいらっしゃると思いますが、一度知ってしまえば簡単なもんなのです。

次章以降では、このへなちょこWebサーバーを、もう少しまともなWebサーバーに改良していきます。
そして、そのために「まともなWebサーバーとはなにか」ということについて学んでいきます。

少しまたお勉強の時間になるかもしれませんが、頑張っていきましょう！

