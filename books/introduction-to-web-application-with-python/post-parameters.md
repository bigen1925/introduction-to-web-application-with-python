---
title: "POSTパラメータを扱えるようにする"
---

# リクエストボディを扱う

前章の最後に、Chromeで`/show_request`へアクセスした結果を見てみるとリクエストボディが空になっていたことが分かりました。

しかし、仮にボディが空でなかったとして、私達のWebアプリケーションはリクエストボディを変換したり解釈したりする処理はまだないのでした。
せっかくなので、ここいらでリクエストボディを扱えるようにしておきましょう。

リクエストボディはクライアントからサーバーへ付加的な情報（パラメータとも言う）を送るのに用いられ、一例として`POST`メソッドのリクエスト（以下、POSTリクエスト）などで使われます。

本章では、`POST`メソッドのパラメータに関する処理を実装することで、リクエストボディの取り扱いについて学びましょう。

# POSTリクエストを送信し、ボディを観察してみる。
アレコレと説明する前に、まずはリクエストボディが実際にどのように使われているのか観察するところから始めましょう。

## POSTリクエストを送信する
POSTリクエストをブラウザがどのようなときに送るかというと、代表的なのは`<form>`タグを用いて作られたフォームの`submit`ボタンが押された時です。

実際にフォームを含むHTMLを作成し、実験してみましょう。

下記のHTMLを`study/static`内に作成してください。

内容は初歩的なHTMLで、詳しく説明する必要はないでしょう。
1つの`<form>`タグの中に、テキストボックスやプルダウン、セレクトボックスなど、色々な種類の入力フォームが入っているだけです。

**`study/static/form.html`**
https://github.com/bigen1925/introduction-to-web-application-with-python/blob/main/codes/chapter15/static/form.html

また、今回からレスポンスヘッダーを少し変更します。
`Content-Type`ヘッダーには文字列のエンコーディングを指定することができ、ブラウザで日本語を表示させるためには日本語に対応したエンコーディングの指定が必要になります。

エンコーディングについては話が込み入ってしまいますので、ピンと来ない方はおなじないだと思って追記しておいてください。

**`study/workerthread.py`**
https://github.com/bigen1925/introduction-to-web-application-with-python/blob/main/codes/chapter15/workerthread.py#L169

このファイルは **`static`ディレクトリの中に入っており静的ファイル配信の対象となります** ので、サーバーを起動した状態でChromeから `http://localhsot:8080/form.html` へアクセスすると表示することができます。

![](https://storage.googleapis.com/zenn-user-upload/10tw1udmnxex3mayh325zn0az6cj)

------

ブラウザは、`type="submit"`の要素（以下、`submit`ボタンと呼びます）がクリックされると、`<form>`タグの`action`属性で指定されたURLへPOSTリクエストを送信します。

`action`属性で指定するURLについて、ホストやポートを省略すると、現在開いているページと同じホスト/ポートへ送信されます。
つまり、今回のように

- 現在開いているページが `http://localhost:8080/form.html` である
- `<form action="/show_request">`である

という場合では、POSTリクエストは`http://localhost:8080/show_request` へ送信されます。

-----

では、下図のようにフォームに値を入力して、送信ボタンを押してみましょう。

![](https://storage.googleapis.com/zenn-user-upload/pnd9bojbf6owzp3n0oug8jvl6l5p)

先程説明した通り、このフォームの入力内容は、POSTリクエスト`/show_request`へ送られます。
`/show_request`は前章でHTTPリクエストの内容が表示されるようにしておいたはずですので、これでPOSTリクエストの内容が見れるだろう、という算段です。

実際、送信ボタンを押すと、次の画面で下記のように表示されるはずです。

![](https://storage.googleapis.com/zenn-user-upload/z75ja4m8kbe0hnvn3m11mcdq55kn)

単にURLバーに`/show_request`と入力してページ遷移した場合と違って、リクエストボディに値が含まれていることが分かります。

また、
```http
Content-Type: application/x-www-form-urlencoded
```
というヘッダーも新たに追加されていることにも注目しておいてください。
後ほど、このヘッダーが大きな意味を持つことを説明します。

## POSTリクエストのボディを観察する

さて、POSTリクエストのボディの具体的な中身が見れたことですので、観察してお勉強していきましょう。
リクエストボディを見てみると、`テキストボックス`や`パスワード`などの個々の入力フォームの値が決まったフォーマットで連結されて渡されてきているのが分かります。

そのフォーマットとは、1つの入力フォームに対して
`[HTML要素のname属性の値]=[フォームに入力された値]`
というペアがあり、別々のフォームの値同士は`&`で連結されているようなフォーマットです。

また、`半角スペース`は`+`という記号に置き換えられ、`改行コード`や`日本語`は**`%`で始まる謎の文字列**に変換されていることが分かります。
（日本語の入力値は、hidden_valueの値を見てください）


また、`<select>`要素のように複数選択を許可する入力フォームでは、同じnameで複数の値が送られてきているようです。
例）`check_name=check2&check_name=check3`

また、アップロードしたファイルを見てみると*ファイル名だけ*しか送られておらず、ファイルの内容は送信されていません。

## POSTパラメータのフォーマットについて

POSTリクエストで送りたいデータ（以下、POSTパラメータ）をリクエストボディを使ってサーバーへ送る際、どのようなフォーマットで送るかは重要です。
ここでフォーマットと言っているのは、リクエストボディの中でパラメータの`name`と`value`を表すのになんの記号を使うのか、複数のデータを分けるのになんの記号を使うのか、マルチバイト文字をどのように表現するのか、画像ファイルのようなバイナリデータをどのように表現するのか、などです。

フォーマットは様々な種類が考えられますが、このフォーマット方式の認識がクライアント側とサーバー側で違うと、送ったパラメータをサーバ側で正しく認識できません。
（クライアント側は`=`という記号は「`name`と`value`を分ける記号」だと思って使っているのに、サーバー側ではこれを「改行コード」だと思って解釈してしまうと、訳の分からない事になってしまうわけです。）

そこで、POSTリクエストを送る時は、必ずリクエストボディのフォーマットを示す`Content-Type`というヘッダーをつけてフォーマットを明示してあげる必要があります。

今回でいうと、
```http
Content-Type: application/x-www-form-urlencoded
```
がそれに当たるというわけです。

以下では、よく使われるフォーマット(`Content-Type`)について3つ紹介しておきます。

### `application/x-www-form-urlencoded`
こちらは、ブラウザが`<form>`タグで`enctype`属性を指定しなかった場合に使われるデフォルトのフォーマットです。
別名「URLエンコーディング」や「パーセントエンコーディング」とも呼ばれ、URLとして利用可能な文字のみを使って様々なデータを表せるようにフォーマットが決められています。

既にさきほど見た通り、

1. 項目の`name`と`value`は`=`で連結する
1. 複数の項目を送る際は`&`で連結する
1. 半角スペースは`+`を使う
1. その他のURLに使えない文字は、`UTF-8`で符号化した上で、そのバイト列を`%XX`で表す
1. UTF-8で符号化できないバイナリデータは扱えない（ファイルアップロージ時、ファイルの中身は送信しない）

などが特徴です。

### `multipart/form-data`
こちらは、`<form enctype="multipart/form-data">`のように、`enctype`属性で明示的に指定することで利用できます。
説明する前に実際に中身を見てみましょう。

さきほど作成した`form.html`の`<form>`要素に、enctypeを指定して、フォームを送信してみてください。

:::message
**ファイルアップロードした時の表示を確認したい場合は、`Chrome`ではなく`Firefox`というブラウザを使い、小さいデータ（数KBの画像など）を送るようにしてください。**

ChromeやSafariは、ファイルデータを送る際にkeep-aliveを使って複数回に分けてリクエストを送信する挙動となっていますが、私たちのWebサーバーはkeep-aliveに対応しておらずデータを正常に受け取れないためです。

Firefoxは小さいデータであれば1リクエストで送ってきますので、正常にデータを受け取ることができます。

---
下記ではFirefoxで挙動確認した画面を掲載しますが、Firefoxをインストールするのが面倒な方は、Chromeでファイルは**アップロードせずに**動作確認してみてください。
テキストフォームなど、ファイル以外のフォームであればデータが受け取れるはずです。
:::
![](https://storage.googleapis.com/zenn-user-upload/jnbaf6b4w9y1qfs4obhgky9zyc2x)

![](https://storage.googleapis.com/zenn-user-upload/gs3wa6fl7hilf9fn65b55iuig83r)

まず最初に注目するのは、フォームデータの各項目が特殊なセパレータによって分割されている点です。
(今回でいうとセパレータは`---------------------------10847194838586372301567045317`)

このセパレータはリクエストを送る側が自由に決めて良いですが、フォームデータ本文の中に絶対に出てこない文字列にする必要があります。
今回のようにブラウザがPOSTリクエストを自動生成する場合は、ブラウザが毎回ランダムに生成してくれます。

また、セパレータはリクエストヘッダー`Content-Type`の中で
```http
Content-Type: multipart/form-data; boundary=---------------------------10847194838586372301567045317
```
のように指定します。

次に注目してほしいのは、フォームの項目ごとにデータの性質を示す`Content-Disposition`や`Content-Type`という補助情報があることです。

これにより、項目ごとに
「この項目はテキストデータとして解釈してね。この項目はPNGファイルとして解釈してね。この項目はPDFとして解釈してね。」
といった指示をサーバーへ伝えることができます。
そのため、`multipart/form-data`フォーマットでは、バイナリデータとテキストデータを混在して送信することができるようになっています。

なお、同じ項目名で複数のデータを送りたい場合は、`application/x-www-form-urlencoded`のときと同じく別々の項目として送信しています。

### `application/json`
次に近年よく使われるのが、`application/json`です。
HTMLとブラウザの組み合わせではこのフォーマットでデータを送ることはできませんが、JavascriptのAJAXという機能を使うことで利用できます。
ここ数年でJavascriptを使ったフロントエンドフレームワークはますます発展しており、参考までにご紹介しておきます。

なお、本書ではJavascriptは取り扱わないため、スルーしてもらっても構いません。

こちらのフォーマットでは、[JSONと呼ばれる文字列フォーマット](https://developer.mozilla.org/ja/docs/Web/JavaScript/Reference/Global_Objects/JSON) を用いて、様々なデータ構造を表現します。

一般的にはフォームデータをJSONオブジェクト（keyとvalueの組み合わせの集合）に変換して送信します。

POSTリクエスト例）
```http
POST /sample HTTP/1.1
...
Content-Type: application/json
...

{
  'text_name': 'text',
  'password_name': 'password',
  'check_name': ['check2', 'check3']
  ...
}
```

JSONでは`[]`を使って配列を表現できますので、複数の値を送信したい際には表現が容易になるでしょう。
また、文字列(`'0'`)と数値(`0`)も区別しますので、サーバーサイドでデータを扱いやすく、不具合を生じにくいというメリットもあります。

ただし、JSONフォーマット自体はテキストデータですので、バイナリデータの送信はできないことに注意しましょう。

# `multipart/form-data`に対応する

さて、メジャーどころの3つのフォーマットを紹介してきました。

Webアプリケーションを作っている我々としては、「POSTパラメータを扱う」ためにはこれらのフォーマットでリクエストボディが送られてきたときに、それを正しく解釈してパラメータを読み取らなければいけません。
しかし、ご覧のようにどのフォーマットもなかなかクセ（パーセントエンコードとか、セパレータとか）があって、パーサーを自力で書くのは大変そうです。

仕組みは分かっているのでやればできるのですが、本書では簡単のためにライブラリを使ってしまうことにします。
また、バイナリデータは当面扱いませんので、最初は最も一般的な`multipart/form-data`だけ対応することにしましょう。

**新しく`/parameters`というエンドポイント（特定のWebサービスを受けられるURLのこと）を作成し、このエンドポイントにPOSTリクエストを送るとパラメータが辞書の形で表示できるようにしていきます。**

## ソースコード
上記に対応したソースコードがこちらです。

https://github.com/bigen1925/introduction-to-web-application-with-python/blob/main/codes/chapter15-2/workerthread.py

https://github.com/bigen1925/introduction-to-web-application-with-python/blob/main/codes/chapter15-2/static/form.html

## 解説
### `study/workerthread.py`
#### 83-101行目
```python
            elif path == "/parameters":
                if method == "GET":
                    response_body = b"<html><body><h1>405 Method Not Allowed</h1></body></html>"
                    response_line = "HTTP/1.1 405 Method Not Allowed\r\n"

                elif method == "POST":
                    post_params = urllib.parse.parse_qs(request_body.decode())
                    html = f"""\
                        <html>
                        <body>
                            <h1>Parameters:</h1>
                            <pre>{pformat(post_params)}</pre>                        
                        </body>
                        </html>
                    """
                    response_body = textwrap.dedent(html).encode()

                    # レスポンスラインを生成
                    response_line = "HTTP/1.1 200 OK\r\n"
```
新しく `/parameters` エンドポイントを追加しました。

現時点ではこのエンドポイントではPOSTパラメータを解析するためのものですから、83-86行目でGETリクエストが来てしまった際には`405`というレスポンスステータスを返しています。
`405 Method Not Allowed`は、URLがリクエストのメソッドに対応していない（または許可していない）ことをクライアントへ伝えるためのステータスです。

88行目以降でPOSTリクエストの対応をしていますが、ライブラリを使用したおかげでそれほど難しいところはないでしょう。
`urllib.parse.parse_qs()`は、URLエンコードされた文字列を辞書へパースする関数です。

辞書のキーは項目名で`str`型ですが、同じ項目名で複数のデータが送られてくるのに対応するため辞書の値は常に（1個しかなくても）`list`型になっていることに注意してください。

### `study/static/form.html`
#### 3行目
```html
<form action="/parameters" method="post">
```

こちらは、`<form>`のPOSTリクエスト先を`/show_request`から`/parameters`へ変更しただけです。

## 動かしてみる

では、本章冒頭と同様に、Chromeで `http://localhost:8080/form.html` へアクセスし、フォームに値を入れて送信してみましょう。

![](https://storage.googleapis.com/zenn-user-upload/pnd9bojbf6owzp3n0oug8jvl6l5p)
![](https://storage.googleapis.com/zenn-user-upload/ra9oakmdx94e6zo7e37kdxkfj326)

POSTパラメータが表示されましたね。

この画面が正常に表示されたということは、POSTリクエストのボディとして送られてきたパラメータを解釈し、pythonの辞書に変換できているということです。


ソースコードとしては簡単なものでしたが、裏側で行われているやりとりは複雑で理解するのは意外と骨が折れたのではないでしょうか。

ちなみに、`multipart/form-data`形式で送られてきた内容をパースするには、pythonでは`cgi`モジュールの`FieldStorage`というクラスを利用します。
余裕のある人は、こちらにもチャレンジしてみても良いかもしれません。

-------

ついでにGETリクエストに対しては`405 Method Not Allowed`がレスポンスされるようにしていたのでした。
そちらも確認しておきましょう。

サーバーを起動したまま、今度は**単にChromeのURLバーに`http://localhost:8080/parameters` を入力してエンター**を押してください。

![](https://storage.googleapis.com/zenn-user-upload/38j3zvw4cbod7kc3udihscix2qfb)

ちゃんと表示されましたね。

ここまで説明を省略していましたが、**ブラウザはURLバーに直接URLを入力したり`<a>`タグのリンクをクリックして移動したりして（フォームの送信ではない）通常のページ遷移を行った場合はGETリクエストを送信**します。

今回のケースでは、URLバーに直接URLを入力することで、`/parameters`に対して（POSTではなく）GETリクエストを送信したため、`405 Method Not Allowd`の画面が表示されたわけです。

-------

# === フィードバックをお寄せください。 ===
本書の内容は、現在ここまでとなっております。
続編は鋭意執筆中ですので、乞うご期待。

本書の続編をご期待される方は、下記フォームよりフィードバックをお寄せください。
（30秒程度で回答できます）
読者からのフィードバックが得られない場合、本書の執筆を中断することもありますので是非よろしくおねがいします。

https://docs.google.com/forms/d/1qTTNPbyPyAAMYALth5uDqgsDGmlCe-BXLYYDLk0QKfw/edit?usp=drive_web

また、本書の「いいね」や筆者フォロー、TwitterやFacebookでの拡散も大歓迎です。