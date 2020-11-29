---
title: "「伸び悩んでいる3年目Webエンジニアのための、Python Webアプリケーション自作入門」を更新しました"
emoji: "🚶"
type: "tech"
topics: [python, web, http]
published: true
---

# 本を更新しました

[チャプター「共通機能パッケージを整理する」](https://zenn.dev/bigen1925/books/introduction-to-web-application-with-python/viewer/modulize) を更新しました。

続きを読みたい方は、ぜひBookの「いいね」か「筆者フォロー」をお願いします ;-)

:::message alert
前回更新した際から、chapter16に変更が加わっています。

- urls.pyを切り出す処理を追加
- 不要な`__init__.py`を削除

すでにchapter16を実装済みの方は、再度内容を確認してください。
:::

----

以下、書籍の内容の抜粋です。

------
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

------

# 続きはBookで！

[チャプター「共通機能パッケージを整理する」](https://zenn.dev/bigen1925/books/introduction-to-web-application-with-python/viewer/modulize)  
