---
title: "「伸び悩んでいる3年目Webエンジニアのための、Python Webアプリケーション自作入門」を更新しました"
emoji: "🚶"
type: "tech"
topics: [python, web, http]
published: true
---

# 本を更新しました

[チャプター「複数回のHTTPリクエストに繰り返し応答できるようにする」](https://zenn.dev/bigen1925/books/introduction-to-web-application-with-python/viewer/daemonize) を更新しました。

続きを読みたい方は、ぜひBookの「いいね」か「筆者フォロー」をお願いします ;-)

----

以下、書籍の内容の抜粋です。

------

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

**`study/webserver.py`**
https://github.com/bigen1925/introduction-to-web-application-with-python/blob/main/codes/chapter12/webserver.py

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

--------

# 続きはBookで！

[チャプター「複数回のHTTPリクエストに繰り返し応答できるようにする」](https://zenn.dev/bigen1925/books/introduction-to-web-application-with-python/viewer/daemonize) 
