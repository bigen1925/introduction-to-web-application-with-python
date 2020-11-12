---
title: "HTMLファイルを配信できるようにする"
---

# リクエストを解釈し、指定されたHTMLファイルを返せるようにする

前章までで、まずはHTTPのフォーマットでレスポンスを返せるサーバーを作ることができました。

しかし、ブラウザから送られてきたリクエストを解釈するような処理は一切実装していないため、どんなリクエストが来てもボディはいつも `It works!` を返しています。

これではあんまりなので、あらかじめプログラムのソースコードとは別にHTMLファイルを用意しておき、リクエストのpathで指定されたファイルをレスポンスボディとして返せるようにしていきましょう。

所謂、*静的ファイル配信*と呼ばれる機能です。

サーバーのソースコードなどはサーバを通じて公開する必要はありませんので、**サーバーを通じて公開したいファイルは`study/static/`というディレクトリに入れる**ことにして、

例）リクエストのpathが`/index.html`
=> `study/static/index.html` の内容がレスポンスボディとして返される

といった具合です。

# ソースコード
他にくだくだと説明することもありませんので、いきなりソースコードにいってみましょう。

あらかじめ用意したHTMLファイルをレスポンスボディとして返せるように改良したものがこちらです。

:::message
ソースコードも長くなってきましたので、今回から内容が多いソースコードについては全体は転載しないことにします。

Githubにソースコード全体がアップロードされていますので、そちらをご参照ください。
:::

**`study/WebServer.py`**
https://github.com/bigen1925/introduction-to-web-application-with-python/blob/main/codes/chapter11/WebServer.py

また、プログラムが正常に動いているか確認するにはHTMLファイルを別途用意する必要があるので、そちらも作成しておきます。
`study`ディレクトリ直下に`static`ディレクトリを新しく作成し、その中に`index.html`を作成します。

せっかくなので、Apacheのパクりではない内容に変えておきました。皆さんの好きな内容にしていただいて構いません。
ただし、ファイル名を変えてしまうと本書の説明通りでは動かなくなってしまうので、ファイル名は`index.html`のままにしておいてください。

**`study/static/index.html`**
https://github.com/bigen1925/introduction-to-web-application-with-python/blob/main/codes/chapter11/static/index.html

# 解説

## 10-13行目: HTMLファイルを置くディレクトリの定義
で、HTMLファイルを置くディレクトリ（`DOCUMENT_ROOT`と呼ぶことにしています）を定義しています。

```python
    # 実行ファイルのあるディレクトリ
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    # 静的配信するファイルを置くディレクトリ
    DOCUMENT_ROOT = os.path.join(BASE_DIR, "static")
```

pythonでファイルパスを扱いなれてない方は読みづらいかもしれませんが、
- `BASE_DIR`: `study`ディレクトリの絶対パス
- `DOCUMENT_ROOT`: `study/static`ディレクトリの絶対パス

が格納されています。

## 43-61行目: ファイルからレスポンスボディを生成する
こちらがメインです。

HTTPリクエストをパース（分解）して、pathの情報を抜き出しています。

その後、pathをもとにファイルを読み込み、レスポンスボディを生成しています。

```python
            # リクエスト全体を
            # 1. リクエストライン(1行目)
            # 2. リクエストボディ(2行目〜空行)
            # 3. リクエストボディ(空行〜)
            # にパースする
            request_line, remain = request.split(b"\r\n", maxsplit=1)
            request_headers, request_body = remain.split(b"\r\n\r\n", maxsplit=1)

            # リクエストラインをパースする
            method, path, http_version = request_line.decode().split(" ")

            # pathの先頭の/を削除し、相対パスにしておく
            relative_path = path.lstrip("/")
            # ファイルのpathを取得
            static_file_path = os.path.join(self.DOCUMENT_ROOT, relative_path)

            # ファイルからレスポンスボディを生成
            with open(static_file_path, "rb") as f:
                response_body = f.read()
```

:::message
pathを取得したあと`DOCUMENT_ROOT`と結合して`static_file_path`を取得するのですが、その前に先頭の`/`を削除していることに注意してください。

これは、pythonの`os.path.join(base, path)`の仕様として、第2引数`path`に`/`で始まる絶対パスを与えると第一引数`base`を無視してしまうためです。
:::

# 動かしてみる
やりたいことがわかっていれば、ソースコードは難しいものではないと思いますので、早速動かしてみましょう。

もし不明点があれば、[こちらから](https://github.com/bigen1925/introduction-to-web-application-with-python) お気軽にご質問ください。

まずはこれまで同様、コンソールで`study`ディレクトリまで移動し、サーバーを起動します。
```bash
$ python WebServer.py
=== サーバーを起動します ===
=== クライアントからの接続を待ちます ===
```

次に、ブラウザからアクセスしてみます。
前回まではルートパス `http://localhost:8080` にアクセスしていましたが、**今回は取得したいファイル名をpathで指定する必要があるため`http://localhost:8080/index.html`へアクセスしてください。**

用意したHTMLファイルの内容が表示されれば成功です！

![](https://storage.googleapis.com/zenn-user-upload/ue235fvd63biv11e151ww2abmbp5)

意外と簡単ですね〜

興味のある方は、`DOCUMENT_ROOT`に他のhtmlファイルも用意してみて、それぞれファイル名をpathに指定するとブラウザに内容が表示されることも確認してみましょう。

# `404 Not Found`を実装する
ところで、サーバーを起動したあと、ブラウザでファイルが存在しないパス（`/hoge.html`など）にアクセスしてみましょう。

次のように、エラー画面が表示されると思います。

![](https://storage.googleapis.com/zenn-user-upload/zhoh0n0g9xcp511lts1xa4ema3f2)

これは困りました。

原因を探るため、サーバーを起動していたコンソールを見てみましょう。

以下のような`FileNotFoundError`のエラーログが出ていると思います。

```bash
$ python WebServer.py
=== サーバーを起動します ===
=== クライアントからの接続を待ちます ===
=== クライアントとの接続が完了しました remote_address: ('127.0.0.1', 60130) ===
=== サーバーを停止します。 ===
Traceback (most recent call last):
  File "/~~~~/WebServer.py", line 88, in <module>
    server.serve()
  File "/~~~~/WebServer.py", line 60, in serve
    with open(static_file_path, "rb") as f:
FileNotFoundError: [Errno 2] No such file or directory: '/~~~~/static/hoge.html'
```

これは、対象のファイルが存在しなかったことによる`open()`関数のエラーです。

レスポンスを生成しようとしている途中でプログラムが異常終了してしまうため、ブラウザはレスポンスを受け取ることができないままコネクションが切断されてしまい、エラー画面が表示されてしまっているという訳です。

-----

存在しないファイルをリクエストされても困るのは確かなんですが、かといってプログラムが途中で異常終了してしまうのは行儀がよろしくありません。

クライアントからすると、リクエストは正しいのにサーバーの不具合でエラーになったのか、リクエストが間違っててリソースが存在しなかったのかを区別できないからです。

そこでHTTPのルールでは、クライアントに「リソースが存在しなかった」ことを明示的に伝えたい場合はステータスコード`404`のHTTPレスポンスを返却することになっています。

こちらの機能を実装して、クライアントに（ひいてはユーザーに）ファイルが存在しないことを伝えるようにしてみましょう。

## ソースコード
`404 Not Found`を実装したソースコードがこちらになります。

**`study/WebServer.py`**
https://github.com/bigen1925/introduction-to-web-application-with-python/blob/main/codes/chapter11/WebServer2.py

## 解説
### 59-70行目
変更を加えたのはこちらです。
```python
            # ファイルからレスポンスボディを生成
            try:
                with open(static_file_path, "rb") as f:
                    response_body = f.read()

                # レスポンスラインを生成
                response_line = "HTTP/1.1 200 OK\r\n"

            except OSError:
                # ファイルが見つからなかった場合は404を返す
                response_body = b"<html><body><h1>404 Not Found</h1></body></html>"
                response_line = "HTTP/1.1 404 Not Found\r\n"
```
`open()`関数は、ファイルが開けない場合には`OSError`例外を送出します。

この例外をキャッチした場合には、専用のレスポンスボディとレスポンスラインを生成します。

この時、HTTPレスポンスは具体的には下記のようになります。

```http
HTTP/1.1 404 Not Found
Date: Tue, 10 Nov 2020 07:43:54 GMT
Host: HenaServer/0.1
Content-Length: 48
Connection: Close
Content-Type: text/html

<html><body><h1>404 Not Found</h1></body></html>
```

:::details コラム: open関数の例外
実は`open()`関数は、ファイルが見つからなかった場合は`FileNotFoundError`、対象がファイルじゃなくてディレクトリだった場合は`IsADirectoryError`、など原因別にもう少しエラーを区別できるのですが、今回は細かいことは気にしないことにしましょう。

いずれにせよ、ファイル内容を正常に取得できなかった場合は`OSError`を継承したエラーが送出されます。
:::

## 動かしてみる
それでは、動作確認をしてみましょう。

先程と同様、サーバーを起動してからブラウザでファイルが存在しないパスにアクセスしてみてください。

今度はこのような画面が表示されていれば、成功です。

![](https://storage.googleapis.com/zenn-user-upload/5vlupgqzyy9scjpmxdi0or7d7ojt)

これで、HTMLファイルを配信することができるようになった上に、存在しないファイル名を指定されても異常終了しないWebサーバーとなりました。

どんどんWebサーバーっぽい雰囲気が出てきましたね！


# == 現在、本書はここまでとなります ==
現在、本書はここまでとなります。続編は鋭意執筆中ですので、少々お待ちください。

また、本書の執筆は、読者の皆様のフィードバックにより加速したり減速したりします。
フィードバックはあればあるほど、良い評価であれ悪い評価であれ、執筆は加速します。

また、説明量を調節したりなど、内容にも反映させていただきますので、
**是非下記アンケートフォームよりフィードバックをお寄せください。**

https://forms.gle/qaeEBS6ts7KAGb1W8

また、本の「いいね」や、筆者のフォローもよろしくお願いします。