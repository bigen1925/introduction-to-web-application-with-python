---
title: "テンプレートエンジンを実装する"
---

# テンプレートエンジン？

さて、この章ではいわゆる「テンプレートエンジン」なるものを実装していくのですが、「テンプレートエンジンとはなにか」をくだくだと説明することはしません。

私達は難しい言葉について理解したいのではなく、単に便利に使えるWebアプリケーションを作りたいだけなのです。

ですので、この章でもやることは単純で、ここまで作ってきたWebアプリケーションを見渡してみて「ここ使いにくいな〜」「ここ見にくいな〜」と思うところをただ改善していくだけです。

それが終わって気がついてみれば、結果的に世の中ではテンプレートエンジンと呼ばれているものを作ることになっていた、と、そういう仕立てになっています。

-----

# STEP1: レスポンスのテンプレートをHTMLファイルに切り出す

では、具体的に「ここ使いにくいな〜」ポイントについて見ていきます。

この章で扱うのは **Pythonのソースコード(`views.py`)の中でHTMLを作っている** 部分です。

以下は、現在の`views.py`からの一部抜粋です。

```python
def now(request: HTTPRequest) -> HTTPResponse:
    """
    現在時刻を表示するHTMLを生成する
    """
    html = f"""\
        <html>
        <body>
            <h1>Now: {datetime.now()}</h1>
        </body>
        </html>
    """
    body = textwrap.dedent(html).encode()
    content_type = "text/html; charset=UTF-8"

    return HTTPResponse(body=body, content_type=content_type, status_code=200)
```

レスポンスとして返すHTMLを、pythonのf-string（変数展開のできる文字列）を使って構築しています。

これはこれでお手軽にHTMLを作れて良いのですが、ちょっと大きめのWebページを作ったことのある人はわかると思いますが、普通のWebページはたった1ページのHTMLだけで何百行〜何千行もあるものです。
それをこの`views.py`に全部書いていては見通しは悪くなるのは自明です。

また、htmlを記述している部分はエディタからするとただのpython文字列に見えるでしょうから、エディタの強力なHTML作成補助機能の恩恵を受けづらいという側面もあります。
（シンタックスエラーなどを表示してくれなかったりなど。）

そこで、htmlを構築する部分を外部ファイルに切り出し、これらの問題を解決していきましょう。

まずはこの`now`関数だけ、HTMLを外部に切り出してみたのが以下になります。

## ソースコード


**`study/vies.py`**
https://github.com/bigen1925/introduction-to-web-application-with-python/blob/main/codes/chapter19/views.py

**`study/templates/now.html`**
https://github.com/bigen1925/introduction-to-web-application-with-python/blob/main/codes/chapter19/templates/now.html

レスポンスの雛形となるhtmlファイルは、新たに`templates`というディレクトリを作り、そこの中にまとめることにしました。

## 解説
### `study/vies.py`
#### 14-16行目
```python
    with open("./template/now.html") as f:
        template = f.read()
        html = template.format(now=datetime.now())
```

やっていることは難しくないでしょう。

pythonの文字列として作っていたHTMLを外部ファイルから読み込むことにして、`.format()`メソッドによって変数の置き換えを行っているだけです。

ここでは、`now`という変数をHTMLファイルの中に記載しておき、それを後から`.format()`によって現在時刻に置き換えています。

### `study/templates/now.html`
```html
<html>
<body>
    <h1>Now: {now}</h1>
</body>
</html>
```

こちらも特に説明はありません。
pythonの文字列として定義していたものを、HTMLファイルに切り出しただけです。

ただし、注目すべき点として、htmlファイルになったことでエディタの支援が受けられるようになっているということです。
恐らく皆さんが使っているようなモダンなエディタであれば、シンタックスハイライト（色付け）がされるようになったでしょうし、恐らくEmmet記法なども使えると思います。

エディタの機能を豊富に使えるかどうかというのは開発速度に大きく影響する部分なので、これだけでもかなりありがたいですね。

::: details コラム: Emmetとは
`Emmet`とは複雑なHTMLを短い記法で表現する記法（あるいはマークアップ言語）のことで、ご存知でない方は、htmlファイルで何もないところに`!`とだけ入力して、`Tab`キーを押してみてください。または、`h1*3`とだけ入力して`Tab`キーを入力してみてください。
`PyCharm`や`Visual Studio Code`、`Sublime Text`などといった最近のエディタであれば、HTMLタグが展開されると思います。

他にも色々な短縮記法が使えるので、是非調べてみてください。
:::

::: message
f-string記法から`.format()`メソッドへ切り替えていくにあたって、f-string記法とは違って文字列の中で関数呼び出しができないことに注意してください。

例えば今回でいうと、
```python
'<h1>Now: {datetime.now()}</h1>'.format(datetime=datetime)
```
のような使い方はできないということです。
（`now()`メソッドの呼び出しができず、エラーになります。）

関数呼び出しを伴う値で変数を置き換えたい場合は、python側で関数呼び出しを行い、その返り値で置き換えるようにしてください。

なぜこのような仕様になっているのか私も調べてみたのですが、理由はよく分かりませんでした。
:::

## 動作確認

まだ改良したいポイントはたくさんありますが、まずはこまめに動作確認をしておきましょう。
サーバーを再起動したらブラウザで `http://localhost:8080/now` へアクセスしてみましょう。

以前までと変わらず、現在時刻が表示されていれば問題ありません。

# STEP2: お決まりの処理をフレームワーク内に隠蔽する
さて、HTMLファイルを切り出せただけでも結構な偉業ですが、view関数の中に

- ファイルを開く (`open()`)
- ファイルを読み込む (`read()`)
- 変数を置き換えるためのメソッドを呼び出す (`format()`)

などの処理が残ってしまっています。

しかも、これらの処理はHTMLを外部から読み込む場合には今後も毎回必ず必要になります。

たった2行ほどのことではありますが、エンジニアは繰り返しを嫌うものですから、これらもフレームワークの中に隠蔽してしまいましょう。

## ソースコード

それがこちらです。

**`study/vies.py``**
https://github.com/bigen1925/introduction-to-web-application-with-python/blob/main/codes/chapter19-2/views.py

**`study/henango/templates/renderer.py`**