---
title: "本を更新しました: 「HTMLファイルを配信できるようにする」"
emoji: "🚶"
type: "tech"
topics: [python, web, http]
published: true
---

# 本を更新しました

[チャプター「HTMLファイルを配信できるようにする」](https://zenn.dev/bigen1925/books/introduction-to-web-application-with-python/viewer/delivery-static-html) を更新しました。

続きを読みたい方は、ぜひBookの「いいね」か「筆者フォロー」をお願いします ;-)

----

以下、書籍の内容の抜粋です。

------

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
ソースコードも長くなってきましたので、今回からソースコード全体は転載しないことにします。

各章、Githubにソースコード全体がアップロードされていますので、そちらをご参照ください。
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
            request_header, request_body = remain.split(b"\r\n\r\n", maxsplit=1)

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

------

# 続きはBookで！

[チャプター「HTMLファイルを配信できるようにする」](https://zenn.dev/bigen1925/books/introduction-to-web-application-with-python/viewer/delivery-static-html)
