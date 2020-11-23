---
title: "Request / Response / View クラスを作って見通しを良くする"
---
# リファクタリングする

動的レスポンスを生成するエンドポイントも3つになってきて、`workerthread.py`も200行近くになってきました。

現時点でも、1ファイルで多種多様なことをやっているため、200行でもかなり見通しが悪くごちゃごちゃしたモジュールになってきてしまいました。

しかも、皆さんがこのWebアプリケーションを進化させていくとエンドポイントはますます増えていきます。
そのたびに`workerthread.py`に追記していたのではメンテナンスできなくなるのは目に見えています。
責務の切り分けとファイル分割を行って`workerthread.py`の見通しを良くしていく必要がでてきたといえるしょう。

つまり、そろそろ**リファクタリングの季節がやってきた**というわけです。

本章では、「エンドポイントごとに動的にレスポンスボディを生成している処理」を外部モジュールへ切り出して行きます。

# 単に関数として切り出してみる

まずは、エンドポイントごとのHTML生成処理を、単純にまるっと別のモジュールへ切り出してみましょう。

切り出す先のモジュールの名前は、`views`とします。
コネクションがどうとか、ヘッダーのパースがこうとか、そういったHTTPの事情は関知せず、見た目(view)の部分（= リクエストボディ）を生成することだけを責務として持つモジュールだからです。

## ソースコード

**`study/workerthread.py`**
https://github.com/bigen1925/introduction-to-web-application-with-python/blob/main/codes/chapter16/workerthread.py#L50-L59

**`study/views.py`**
https://github.com/bigen1925/introduction-to-web-application-with-python/blob/main/codes/chapter16/views.py

