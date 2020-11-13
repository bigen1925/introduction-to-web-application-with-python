---
title: "複数回のHTTPリクエストに繰り返し応答できるようにする"
---

# Webサーバーがリクエストを1回だけしか処理できない問題
そろそろこの問題に対処しましょう。

皆さんにこれまで作ってもらったWebサーバーは、一回のHTTPリクエストを処理するとすぐに終了してしまいます。

そのため、繰り返しリクエストに応答しようと思うと毎回サーバーを起動しなおさなければいけません。

開発中に動作確認のたびにサーバーを起動するのがめんどくさいというのもありますが、一般的なWebページを正常に表示する上でも問題があります。

## HTMLから外部ファイルの参照ができない
例えば、前章で作ってもらった`index.html`を下記のように変更してみてください。

**`study/static/index.html`**
```html
<!doctype html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <title>HenaServer</title>
  <link rel="stylesheet" href="index.css">
</head>
<body>
  <img alt="logo" src="logo.png">
  <h1>Welcome to HenaServer!</h1>
</body>
</html>
```
https://github.com/bigen1925/introduction-to-web-application-with-python/blob/main/codes/chapter12/static/index.html

6行目: `<link rel="stylesheet" href="index.css">`
10行目: `<img alt="logo" src="logo.png">`

を追加しました。

よくある外部CSSファイルの読み込みと、画像ファイルの読み込みです。

次に、読み込もうとしているファイルを、同じディレクトリ内に新しく用意します。

CSSファイルの内容は下記のようにしています。

**`study/static/index.css`**
```css
h1 {
    color: red;
}
```
https://github.com/bigen1925/introduction-to-web-application-with-python/blob/main/codes/chapter12/static/index.css

画像ファイルはこちらです。

**`study/static/logo.png`**
https://github.com/bigen1925/introduction-to-web-application-with-python/blob/main/codes/chapter12/static/logo.png

画像ファイルは何でも良いのですが、本書では「いらすとや」^[https://www.irasutoya.com/] から拝借しています。お好きな画像を使っていただいて構いません。

-------

見ていただければ分かるように、通常のWebページであればChromeにはロゴ画像が表示され、文字にはCSSが適用されて赤色に表示されるはずです。

では、サーバーを起動してChromeで`http://localhost:8080/index.html`へアクセスしてみましょう。

![](https://storage.googleapis.com/zenn-user-upload/4rnyq1kslehdyf2b4yxwgl6gmt62)

これはよくないですね。
画像もCSSも読み込まれていません。

------

ブラウザはWebサーバーからレスポンスを受け取った際、レスポンスボディのHTML内に外部ファイル参照（`<img src="">`、`<script src="">`、`<link href="">`など）が記載されていると、再度リクエストを送信しなおしてファイル内容を取得しようとします。

しかし、私たちのWebサーバーは最初のリクエストを処理したあと、すぐにプログラムを終了させてしまうため、追加のリクエスト（今回でいうとCSSと画像のリクエスト）を処理できていないのです。

![](https://storage.googleapis.com/zenn-user-upload/jkhgc3a7aqutbdl5y9nctxtlwtn5)

その様子を、もう少し具体的に見てみましょう。

ChromeにはHTTPリクエストの通信結果を詳細に見れる「開発者ツール」という機能が備わっています。
そちらを使って、実際に行われたリクエストの様子を確認していきます。

さきほどChromeで`http://localhost:8080/index.html` にアクセスした画面で、`ctrl` + `shift` + `j`を押してみましょう。
（または、画面を右クリックして`検証`を選択し、`Console`タブを開きます）

![](https://storage.googleapis.com/zenn-user-upload/fgcpx7l5sos1qb60073q316ng38i)

図のように、既に `index.css` と `logo.png` を取得する際に、**Webサーバーとのコネクションに失敗したことを示すエラーログが表示されています。**

（Chromeは他にも、特に指示がなくても勝手にファビコンの画像を取得しにくような仕様になっており、そちらのエラーも表示されていますが、本書では特に気にする必要はありません。）

次に、開発者ツールの`Network`タブを開き、*サーバーを起動してから*リロードしてみましょう。
（ネットワークタブは、開発者ツールを開いて以降の通信のみ情報を表示するため、リロードする必要があります）

![](https://storage.googleapis.com/zenn-user-upload/l6ja92bnbrw2rcji95h47hsdf50l)

Chromeはこのページを表示するために、全部で4件の通信を行っていることが分かります。
（バージョンや環境によって内容は異なるかもしれません、）

内訳を見てみると、`index.html`を取得する通信は成功（`status`が`200`）しており、`index.css`と`logo.png`は通信に失敗(`status`が`failed`)していることが分かります。

# 繰り返しリクエストを処理できるようにする
このままでは「ただ面倒くさい」だけではなく、CSSや画像、JSなどを使った普通のWebページ1つすら表示できないということが分かりました。

では、Webサーバーを改良して、これらの問題を解決していきましょう。

## ソースコード
まずは、コネクションを確立してレスポンスを返す処理を無限ループに中に入れることで、繰り返しリクエストに対応できるようにします。

ソースコードがこちらです。

**`study/WebServer.py`**
https://github.com/bigen1925/introduction-to-web-application-with-python/blob/main/codes/chapter12/WebServer.py

## 解説

### 30行目
```python
            while True:
```
まず一番大きな変更点として、「クライアントからのコネクションを待つ」〜「コネクションを終了する」までの処理（31行目-97行目）をまるごと無限ループの中にいれたところです。
（無限ループの記法が分からない方は、「python while true」で調べてみてください。）

たった1行ですが、これにより、1つのリクエストの処理が完了し、コネクションを終了させた後、ループの先頭にもどり再度リクエストを待機することになります。
次のリクエストの処理が完了すると、またループの先頭に戻り、次のリクエストを待ちます。

つまり、プログラムを起動した人が明示的にプログラムを中断させるまで、無限にリクエストをさばき続けるプログラムになります。

### 89-97行目
```python
                except Exception:
                    # リクエストの処理中に例外が発生した場合はコンソールにエラーログを出力し、
                    # 処理を続行する
                    print("=== リクエストの処理中にエラーが発生しました ===")
                    traceback.print_exc()

                finally:
                    # 例外が発生した場合も、発生しなかった場合も、TCP通信のcloseは行う
                    client_socket.close()
```

ついでに、例外処理を追加しておきました。

例外処理をしておかないとループの途中で例外が発生した場合にプログラム全体が停止してしまいますが、上記のようにハンドリングすることでその時扱っているリクエストの処理だけ中断させますが、プログラム全体は停止せずに次のループへ進むことになります。

また、`client_socket`の`close()`はtry句の末尾でやるのではなく、finally句で行います。
try句の末尾でやってしまうと、途中で例外が発生した場合にコネクションの切断がスキップされてしまうためです。

# 動かしてみる
では実際に動かしてみましょう。

いつもどおりコンソールからサーバーを起動します。

```bash
$ python WebServer.py
=== サーバーを起動します ===
=== クライアントからの接続を待ちます ===
```

次に、Chromeから`http://localhost:8080/index.html` へアクセスしてみます。

![](https://storage.googleapis.com/zenn-user-upload/y7utr2351advls0l2kzq1125srbe)

やりましたね！画像が表示されました。

それに、このページをリロードしてみてください。
何回読み込み直しても毎回ページが表示されるはずです。

サーバーのログも確認してみましょう。
サーバーを起動したコンソールのタブを見てください。

繰り返しコネクションを確立させ、リクエストを処理している様子が分かるはずです。

```bash
$ python WebServer.py
=== サーバーを起動します ===
=== クライアントからの接続を待ちます ===
=== クライアントとの接続が完了しました remote_address: ('127.0.0.1', 50404) ===
=== クライアントからの接続を待ちます ===
=== クライアントとの接続が完了しました remote_address: ('127.0.0.1', 50405) ===
=== クライアントからの接続を待ちます ===
=== クライアントとの接続が完了しました remote_address: ('127.0.0.1', 50407) ===
=== クライアントからの接続を待ちます ===
=== クライアントとの接続が完了しました remote_address: ('127.0.0.1', 50418) ===
=== クライアントからの接続を待ちます ===
=== クライアントとの接続が完了しました remote_address: ('127.0.0.1', 50419) ===
=== クライアントからの接続を待ちます ===
=== クライアントとの接続が完了しました remote_address: ('127.0.0.1', 50421) ===
=== クライアントからの接続を待ちます ===
```

--------

・・・しかし、Chromeの画面をよく見ると**CSSはまだ適用されていなさそう**ですね？

様子がおかしいので、開発者ツールの`Network`タブで見てみましょう。

![](https://storage.googleapis.com/zenn-user-upload/rp19emm4gubwk92q01yt6dd6o52j)

今度は先程と違い、cssも画像も`status`が`200`になっていますので、通信には成功していそうです。

詳しく調べるために、cssファイルの行をクリックして、レスポンスの詳細を確認します。
詳細画面の`Response`タブをクリックすると、レスポンスボディが確認できます。

![](https://storage.googleapis.com/zenn-user-upload/5fejvi407sftksfx1jn7wskykemu)

どうやら、ちゃんと意図どおりのCSSがレスポンスボディとして取得できているようです。

何が起きているのでしょうか？

------

このケースのように、データとしては正しいものが渡せているのに思った挙動をしてくれないという場合によくあるのが、読み込みフォーマット問題です。
例えばjpegファイルをpngファイルだと思って読み込んでも画像は表示できませんし、エクセルファイルをPDFだと思って読み込んでも当然正常に読み込めません。

今回でいうと、実は[レスポンスのヘッダーを作るとき](https://zenn.dev/bigen1925/books/introduction-to-web-application-with-python/viewer/improve-to-minimal-web-server#content-type) に手抜きをして固定で`Content-Type: text/html`を返すようにしてしまったことが原因となっています。
このヘッダーのせいで、Chromeは `h1 { color: red; }` という文字列をCSSだと理解できずにいるのです^[この理屈でいくと画像ファイルも読み込めないはずなのですが、Chromeさんはとても賢いので、テキストファイルと画像ファイルぐらい全然違うものだと自動でファイル形式を認識してくれるようです。] 。

検証ツールを使って実際にこの様子を確認しておきましょう。
先程と同様に、cssファイルのレスポンスの詳細画面の、`Header`タブを開いてみましょう。

![](https://storage.googleapis.com/zenn-user-upload/vyywi90rqx05owfm58wvqyvvr74x)

実際にレスポンスボディで送っているのはCSS形式の文字列なのに、サーバーは「htmlだと思って読んでね」と指示してしまっている状態です。

# 適切な`Content-Type`を返せるようにする
Webサーバーを更に改良して、ファイル形式に沿った`Content-Type`を返せるようにしていきましょう。

## ソースコード
改良したものがこちらです。

**`study/WebServer.py`**
https://github.com/bigen1925/introduction-to-web-application-with-python/blob/main/codes/chapter12/WebServer2.py

## 解説

### 16-27行目
```python
    # 拡張子とMIME Typeの対応
    MIME_TYPES = {
        "html": "text/html",
        "css": "text/css",
        "png": "image/png",
        "jpg": "image/jpg",
        "gif": "image/gif",
    }
```
拡張子と、それに対応するMIME Typeの対応を辞書で保持しています。

本当はもっとたくさんの種類のMIME Typeがありますが、まずは最低限のものだけで先に進めましょう。

ここにない拡張子のファイルを使ってみたい方は、[こちら](https://developer.mozilla.org/ja/docs/Web/HTTP/Basics_of_HTTP/MIME_types/Common_types) を参考に自分で追加してみてください。

### 88-96行目
```python
                    # ヘッダー生成のためにContent-Typeを取得しておく
                    # pathから拡張子を取得
                    if "." in path:
                        ext = path.rsplit(".", maxsplit=1)[-1]
                    else:
                        ext = ""
                    # 拡張子からMIME Typeを取得
                    # 知らない対応していない拡張子の場合はoctet-streamとする
                    content_type = self.MIME_TYPES.get(ext, "application/octet-stream")
```
pathから拡張子(=`ext`)を取得し、拡張子と先ほど定義した辞書を使って対応するMIME Typeを取得しています。

拡張子が存在しない（pathが`.`で区切られていない）場合は、拡張子は空文字としています。

ちなみに、
`path.rsplit(".", maxsplit=1)[-1]`
は、pathを`.`で右から1回だけ分割し、得られたリストの-1番目(= 最後尾)を取得しています。
`.`が含まれない（=要素数が1になってしまう）パターンは事前に除外しては除外していますので、今回に限っては
`path.rsplit(".", maxsplit=1)[1]`
と同じ意味になります。

### 104行目
```python
                    response_header += f"Content-Type: {mime_type}\r\n"
```

忘れずに`Content-Type`ヘッダーを変数を使って生成するよう変更しておきましょう。

# 動かしてみる
それでは動作確認をしてみましょう。

まずは、サーバーを再起動させます。

サーバーが実行中のコンソールのタブを開き、`ctrl + C`を入力します。
するとサーバーが停止しますので、あらためてサーバーを起動させます。

次に、またChromeから`http://localhost:8080/index.html`へアクセスします。


:::details コラム: 「サーバーの再起動」
本章から私達のWebサーバーは1回起動すると実行しっぱなしになっているわけですが、ソースコードはプログラムを実行したタイミングで一度だけ読み込まれ、その時点のソースコードをもとに動作します。
そのため、ソースコードの変更をプログラムの挙動に反映させるためにはサーバーを再起動する必要があることに気をつけてください。
ただし、サーバーのソースコード自体ではなく、リクエストを受けたときに毎回読み込み直すファイル（例えば、`static`配下のhtmlファイルやcssファイル）の変更を反映させたい場合は、サーバーを再起動する必要はありません。

**サーバーのソースコードはプログラム実行時に一度だけ読み込まれ、`static`のファイルはリクエストが来た時に毎回読み込まれる**という違いを理解しておくことは重要です。

このあたりの挙動が分かってくるようになると、サーバーの設定を触り始めた中級者がハマりがちな
「ファイルを変更したんだけど、サーバーの再起動が必要なタイミングがよく分からない」
「何かファイルを変えたら不安だからとりあえず毎回サーバーを再起動している」
といった壁を超えることができるでしょう。
:::

![](https://storage.googleapis.com/zenn-user-upload/y7naret579pcvn8gocccoheuyg1e)

完璧です！

CSSも適用されて、画像も表示されました。

ここまでくれば、もう「阿部寛のホームページ」^[シンプルで軽量なホームページとして巷で有名。 http://abehiroshi.la.coocan.jp/] ぐらいのものは世間に提供できるシロモノになってきましたね。

最後に、検証ツールを使って本当に私達の目論見通りのレスポンスになっているのか確認しておきましょう。

検証ツールの`Network`タブを開いて、ページをリロードします。
（サーバーを再起動しなくていいのは良いですね〜）

![](https://storage.googleapis.com/zenn-user-upload/00a4t04c2ztgc95otuo9wxwgvjvo)

`index.css`の`Header`タブを確認してみると、たしかに`Content-Type: text/css`になっていますね。

めでたしめでたし。


# == 現在、本書はここまでとなります ==
現在、本書はここまでとなります。続編は鋭意執筆中ですので、少々お待ちください。

また、本書の執筆は、読者の皆様のフィードバックにより加速したり減速したりします。
フィードバックはあればあるほど、良い評価であれ悪い評価であれ、執筆は加速します。

また、説明量を調節したりなど、内容にも反映させていただきますので、
**是非下記アンケートフォームよりフィードバックをお寄せください。**

https://forms.gle/qaeEBS6ts7KAGb1W8

また、本の「いいね」や、筆者のフォローもよろしくお願いします。
