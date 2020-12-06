---
title: "共通機能パッケージを整理する"
---

# パッケージを整理する

前章で`henango`というパッケージを作成しました。

改めて説明しておくと、このパッケージは **「仮にこのWebアプリケーションを使って全く別のWebサービスを作ることになった場合でも必要になる（＝使い回せる）機能」** をまとめるパッケージです。

----

例えば「Webサービス」を作るといっても、「個人のブログ」や「キュレーションメディア」から、果ては「Gmail」や「Github」まで様々なものがあります。
しかし、どんなWebサービスを作るにしろ、

- HTTPリクエストを送受信できる
- HTTPリクエストをparseして、HTTPRequestクラスに変換する
- リクエストのpathを見て、エンドポイントごとに違う「レスポンス生成関数」を呼び出す
- cookieやsessionを管理する（後ほどでてきます）

などの機能は必ず必要になります。

これらの共通機能だけを1つのパッケージにまとめておくことで、色々なWebサービスを作ることになったときも使いまわしが効きます。

より具体的に言うと、ブログを作るにしろ、メディアを作るにしろ、共通機能パッケージをまるごとコピーして、`urls.py`と`views.py`だけ編集すればすぐに新しいWebサービスが構築できますよ、といった具合です。

これらの共通機能部分のことを総称して **Webフレームワーク** と呼び、様々な種類のものがライブラリ化され世の中に出回っています。
Pythonであれば`Django`や`Flask`、PHPであれば`Laravel`や`CakePHP`、Javaであれば`Spring`、Goであれば`echo`などが有名です。

----

本書で作るWebアプリケーションは、厳密に言うと共通機能と呼べるものは存在しません。
このWebアプリケーションを「共通で」使うことになる複数のWebサービスが存在しないからです。

[YAGNIの法則](https://ja.wikipedia.org/wiki/YAGNI) に従えば、実際にこのWebアプリケーションを使って複数のWebサービスを作ることになるまで共通機能部分の切り出しは行わないほうが良いでしょう。

しかし、皆さんが普段使っているであろう*Webフレームワーク*の挙動をより深く理解する、というのが本書の目的の一つですので、この共通機能（=フレームワーク）部分とサービス固有の部分とを区別して整理しておくことにします。

以後は
「仮にこのWebアプリケーションを使って全く別のWebサービスを作ることになった場合でも必要になる（＝使い回せる）機能」
を`henango`パッケージにまとめていきます。

この`henango`パッケージは、皆さんの使ったことがある「Webフレームワーク」に相当するパッケージですので、そのことを意識しながら
「`henango`でいう〇〇という機能は、`Laravel`でいう××という機能のことかなぁ」
などと照らし合わせながら読み進めていただけると効果的かと思います。

-------

パッケージの整理は細々とした変更をそれなりの量加えることになりますので、いくつかのステップに分けて説明していきます。

# STEP1: サーバーの起動スクリプトを`webserver.py`から分離する

現在、サーバーの起動スクリプトが`webserver.py`に含まれています。
この後`webserver.py`を`henango`モジュールへお引越しする予定なのですが、起動スクリプトはプロジェクトのトップディレクトリ（= `study`ディレクトリ）にないとimportが面倒なことになりますので、まずはこれを分離させます。

（`python`のご都合だと思っていただいて構いません。多くの言語で、セキュリティの観点から起動スクリプトより上位ディレクトリのソースコードは実行しにくくできています。）

`study`ディレクトリに起動スクリプト`start.py`を追加し、`webserver.py`からサーバーを起動する記述を削除します。

## ソースコード


**study/start.py**
https://github.com/bigen1925/introduction-to-web-application-with-python/blob/main/codes/chapter17/start.py

****
https://github.com/bigen1925/introduction-to-web-application-with-python/blob/main/codes/chapter17/webserver.py

## 解説
### `study/start.py`
```python
from webserver import WebServer

if __name__ == "__main__":
    WebServer().serve()

```
特に解説は不要でしょう。
`webserver.py`にかかれていた記述を切り出しただけです。

### `study/webserver.py`
#### 49行目以降

```python
# 削除
# if __name__ == "__main__":
#     WebServer().serve()
```
サーバーを起動する記述が書かれていたのを削除しました。

## 動かしてみる
起動スクリプトが変更になりましたので、起動コマンドも変更になります。

今回からは、コンソールで`study`ディレクトリまで移動した後、

```shell script
$ python start.py
```

としてサーバーを起動させてください。
(`webserver.py`から`start.py`へ変更になっています。)

挙動は変わっていませんので、いくつかのページ（`/index.html`や`/parameters`など）を表示させてみて、問題がないか確認してください。


# STEP2: `webserver.py`を`henango`パッケージへ移動する

では、改めて`webserver.py`と`workerthread.py`をお引越しさせます。
`henango`ディレクトリ下に、新しく`server`というディレクトリを作成し、その下に移動させます。

また、本書序盤では「Webサーバーとは何か」を説明したり「スレッドとはなにか」を説明するために敢えてファイル名にもそれらのワードを入れていましたが、今となっては少し冗長ですので

【ファイル名】
`webserver.py` => `server.py`
`workerthread.py` => `worker.py`

【クラス名】
`WebServer` => `Server`
`WorkerThread` => `Worker`

へとついでに変更してしまいます。

## ソースコード

**`study/henango/server/server.py`**
https://github.com/bigen1925/introduction-to-web-application-with-python/blob/main/codes/chapter17-2/henango/server/server.py

**`study/henango/server/worker.py`**
https://github.com/bigen1925/introduction-to-web-application-with-python/blob/main/codes/chapter17-2/henango/server/worker.py

**`study/start.py`**
https://github.com/bigen1925/introduction-to-web-application-with-python/blob/main/codes/chapter17-2/start.py

## 解説
### `study/henango/server/server.py`
```python
import socket

from henango.server.worker import Worker


class Server:
    """
    Webサーバーを表すクラス
    """

    # ...
```

ディレクトリ、ファイル名、クラス名を変更したのみですので、その他内容には変更はありません。
importするworkerのクラス名(`Worker`)が変更になっているのも忘れないようにしてください。

### `study/henango/server/worker.py`
```python
# ...

class Worker(Thread):
    # ...
```
こちらも同様です。

### `study/start.py`
```python
from henango.server.server import Server

if __name__ == '__main__':
    Server().serve()
```

こちらは、ファイル移動なども特になく、importするクラス名が変更になったのみです。


# STEP3: `STATIC_ROOT`の設定値を切り出す

上記を終えたあと、サーバーを起動して`/index.html`へアクセスしてみてください。
404になっていると思います。

![](https://storage.googleapis.com/zenn-user-upload/8t0cajr1jm5nyo39ar1ul6pg4fam)

これは、`worker.py`内で静的ファイルのディレクトリを示す変数`STATIC_ROOT`が相対パスの指定になっており、ディレクトリ構造が変わったことでファイルをみつけられなくなってしまったためです。

![](https://storage.googleapis.com/zenn-user-upload/kgoeakhi9g6ifk858iokfpwu7fhe)

フレームワークのディレクトリ構造が変わることは普通滅多にないこととはいえ、静的ファイルを配置するディレクトリはプロジェクトごとに変化することは十分考えられます。
現在はプロジェクトルート直下に`static`というディレクトリを用意していますが、プロジェクトによって`static`という名前を避けたいとか、`resouces/static`に配置したいとか、そういったことはよくあります。

そういった状況でもフレームワークには手を入れなくて良いように、`STATIC_ROOT`の設定値はフレームワーク外から上書きできたほうがよいでしょう。
フレームワークの設定値を上書きするためのモジュール`settings.py`をプロジェクトルートに作成しましょう。

## ソースコード
**`study/henango/server/worker.py`**
https://github.com/bigen1925/introduction-to-web-application-with-python/blob/main/codes/chapter17-3/henango/server/worker.py

**`study/settings.py`**
https://github.com/bigen1925/introduction-to-web-application-with-python/blob/main/codes/chapter17-3/settings.py

## 解説
### `study/henango/server/worker.py`
#### 122-132行目
```python
    def get_static_file_content(self, path: str) -> bytes:
        """
        リクエストpathから、staticファイルの内容を取得する
        """
        default_static_root = os.path.join(os.path.dirname(__file__), "../../static")
        static_root = getattr(settings, "STATIC_ROOT", default_static_root)

        # pathの先頭の/を削除し、相対パスにしておく
        relative_path = path.lstrip("/")
        # ファイルのpathを取得
        static_file_path = os.path.join(static_root, relative_path)
```

static_rootを取得する処理を変更しています。
`settings`モジュールに`STATIC_ROOT`という値が存在すればそれを取得し、なければデフォルトの値を使用しています。

### `study/settings.py`
```python
import os

# 実行ファイルのあるディレクトリ
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 静的配信するファイルを置くディレクトリ
STATIC_ROOT = os.path.join(BASE_DIR, "static")
```

`STATIC_ROOT`を上書き定義しています。
今のところ有意な値は`STATIC_ROOT`だけですが、今後色々と追加される予定です。

## 動かしてみる
それでは、`start.py`でサーバーを起動して、動作確認してみてください。
今度は`/index.html`も正常に表示されるはずです。

![](https://storage.googleapis.com/zenn-user-upload/3wkmy5m1enxrdi420drj5agy160g)

----

`Django`を使ったことがある人は、私達のWebアプリケーションがもうかなり`Django`っぽくなってきたことにお気づきでしょう。
`Django`を使ったことがない人も、それぞれのモジュールやパッケージが皆さんの使っているWebフレームワークにところどころ似ていることに気づくでしょう。

「アレをもうちょっと変えたら、もっと自分の知っているフレームワークに近づくんじゃないか？」
と疑問に思った人は、本書の筋から離れて改良してもらって全く構いません。

本書では、できるだけ自然に（= 必要になったときに）拡張を重ねていく方針ですので、あえて機能不足のまま進めている箇所があちこちにあります。

しかし、勉強はなにより自分が楽しいと思うまま、好奇心の赴くままにやるのが一番吸収が早いものです。

気が向いた方は、是非皆さん独自の「オレオレフレームワーク」を作り上げてみてください。
