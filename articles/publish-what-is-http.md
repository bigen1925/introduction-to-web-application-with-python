---
title: "「伸び悩んでいる3年目Webエンジニアのための、Python Webアプリケーション自作入門」を更新しました"
emoji: "🚶"
type: "tech"
topics: [python, web, http]
published: true
---

# 本を更新しました

[チャプター「HTTPとは？」](https://zenn.dev/bigen1925/books/introduction-to-web-application-with-python/viewer/what-is-http) を更新しました。

続きを読みたい方は、ぜひBookの「いいね」か「筆者フォロー」をお願いします ;-)

----

以下、書籍の内容の抜粋です。

------

# HTTPについて学ぶ
さて、前章まででApacheとChromeの真似っ子をして、「エセWebサーバー」を作ってきました。
これをもう少し「最低限まともなWebサーバー」に進化させていきたいのですが、「最低限まともなWebサーバー」とは一体どういうものなんでしょうか？

ここから先へ進むにはどうしても**HTTP**の説明をしなければいけないので、また少しお付き合いください。

ここを抜ければ、「あとはじゃんじゃん書くだけ！」という感じになってきます。

# HTTPとは？

前章までで、皆さんは`TCP`については学びましたね。
（おさらいしておくと、TCPは「漏れなく順序よく」送るためのルールでした。）

「漏れなく順序よく」送れるということは、送ったメッセージはそっくりそのまま相手にちゃんと伝わることが保証されるわけですが、ではそのTCPを使って **「何を」（＝どんなメッセージを）伝えれば良いでしょうか？**


ここで、GoogleというWebサービスに対して、クライアントがサーバーへリクエストを伝えるときのことを考えてみましょう。
リクエストで伝えたい内容は、
`hogeというワードで検索したい。Cookieはhogeを使う。`
だとしましょう。(Cookieは本書後半で詳説します）

それぞれのクライアントが皆思い思いの形式でこれらの情報を伝えてくると、サーバーは困ったことになります。

例えば、

クライアント1) 日本語まじり...
`Cookieはfugaね、今回はwww.google.com/searchで検索ワードはhoge`

クライアント2) 区切り文字がコンマだったり数字だったりコロンだったりする...
`1.www 2.google 3.com 4.search, word:: hoge, cookie=fuga`

などのように毎回違う形式でリクエストを送られてくると、サーバーはリクエストのどの部分がどの情報を示しているのかわからなくなってしまうのです。

そこで、世界的に約束事（＝プロトコル）が制定されました。
**「Webサービスを利用する際は、TCPを使った上で、こういうフォーマットでメッセージを送りましょう」**
という約束事です。

先程のクライアントのリクエストの場合であれば、
```http
GET /search?q=hoge HTTP/1.1
Cookie: fuga

```
と送ることになっています。

世界中の全てのクライアントがこの形式で送ってくるとわかっていれば、お互いに見ず知らずの相手でも、Webサーバー側もメッセージを適切にパース（分解）して情報を取り出せるという寸法です。

この約束事を **HTTP(HyperText Transfer Protocol)** と呼びます。

::: details コラム: トランスポート層のプロトコルと、アプリケーション層のプロトコル
`「何を」伝えるか` に関するプロトコルは、提供したいサービスによって変わってきます。
なぜなら、何を相手に伝えなければいけないかは、サービスによって変わってくるからです。

例えば、**メールを送るサービス**であれば、

- 自分のメールアドレス
- 宛先メールアドレス
- タイトル
- 本文

などを相手に伝える必要があるでしょう。

同様に、**Webサービス**であれば、

- リクエストするWebページのURL
- リクエストの種類（Webページが見たいのか、入力したフォームのデータを送りたいのか、など）
- HTTPを使うのか、HTTPSを使うのか
- Cookieの値は何か（Cookieについては本書後半で詳説します）

などを相手に伝える必要があります。

当然、メールを送るサービスとWebサービスでは違うフォーマットで相手にメッセージを伝えることになりますし、それはプロトコルが変わってくるということを意味しています。
（ちなみにメールを送るときは`SMTP`、メールを受け取るときは`POP`というプロトコルが使われます）

-------

しかし、HTTPもSMTPもPOPも、全てメッセージのフォーマットに関する約束事であり、送る側も受け取る側も、メッセージは「漏れなく順序よく」届くことは大前提として作られています。
つまり、HTTPもSMTPもPOPも、**TCP通信を行うことを前提としたプロトコル**ということになります。

「どうやって送るか」のプロトコルがまずあって、その上に「何を送るか」のプロトコルがあるという構造になっているわけです。

このようなプロトコルの階層構造のモデルとして有名なものとして、[OSI参照モデル](https://ja.wikipedia.org/wiki/OSI%E5%8F%82%E7%85%A7%E3%83%A2%E3%83%87%E3%83%AB)があります。

OSI参照モデルでは、「どうやって送るか」に関するプロトコルを**トランスポート層**、「何を送るか」に関するプロトコルを**アプリケーション層**と呼んでいます。

なので、先輩エンジニアが
「それってトランスポート層の問題ってこと？」
などと言った場合には、
「レスポンスの中身とか順番の話は今していなくて、メッセージを漏れなく順序よく届ける仕組みのところの話をしていますよ」
という意味になります。

こういった一言の意味を即座に正確に理解できるかが、中級者と上級者を分ける一つの要素になるでしょう。

※　OSI参照モデルは今はもう古くなってしまっていると言われており、最近のインターネットで使われているプロトコルを全てOSI参照モデルのレイヤーに当てはめるのは困難ですが、プロトコルに階層構造があるという考え方だけは身につけておきましょう
:::

# HTTPのルールはどこに書いてある？
世界的に利用されているこのHTTPというルールですが、これは [IETF](https://ja.wikipedia.org/wiki/Internet_Engineering_Task_Force) という団体によって制定されています。

IETFという団体はHTTP以外にもたくさんのインターネット技術に関するプロトコルや仕様類に関する制定を行っており、詳細な仕様や説明は [RFC](https://ja.wikipedia.org/wiki/Request_for_Comments) というドキュメントとして発行されます。

RFCはネット上で簡単に検索することができ、誰でも読むことができます。

例えば、RFCの中でもHTTPの基本について書かれた `RFC2616` は、[こちら](https://tools.ietf.org/html/rfc2616) から読むことが出来ます。 

この`RFC2616`にHTTPの全容が書かれていますので、こちらを読んで勉強しましょう。

----

・・・といって、RFCのリンクを開いた方は早速心が折れたと思います。

RFCは、世界中のインターネット技術の拠り所、いわば法律のように機能するようなレベルのドキュメントのため、プロトコルが制定された背景から目的、細部の細部の仕様まで体系的にまとめられており、全て把握するのは困難です。

まず全部英語だしちょっときつい。

しかし、こういうリファレンスは概要を掴んだ上でかいつまんで読む分には意外と理解できたりするものです。

**エンジニアとしてレベルアップしていく上で、一次ソースを理解できるというのは非常に非常に大事なスキルです。**
RFCに限らず、フレームワークやライブラリの使い方を調べるのに、公式リファレンスをきちんと読めるかどうかは、上級者にステップアップするには必須のスキルといっていいでしょう。

ですので、以下ではまず私の言葉でHTTPの概要を説明しつつ、折に触れてRFCの該当の箇所もついでに読んでみる、というスタイルで解説を進めていきます。

また、RFCを参照する際は、簡単のために原文ではなく、下記の日本語訳サイトを利用します。
https://triple-underscore.github.io/rfc-others/RFC2616-ja.html

橋本英彦さん、ありがとうございます。

# HTTPにおける2種類のメッセージ

HTTPというプロトコルでは、リクエストとレスポンスでそれぞれ別のルール（フォーマット）が定められています。
この2種類のフォーマットについて、それぞれ順に見ていきましょう。

ちなみに単に「リクエスト」といった場合、一般には「(フォーマットや通信方法は問わず)クライアントからサーバーへのメッセージ」を指すことが多いですが、その中でもHTTPのルールに従って送られるメッセージのことを**HTTPリクエスト**と呼びます。
「レスポンス」についても同様に、HTTPのルールに従ったレスポンスを特に**HTTPレスポンス**と呼びます。

## 1. HTTPリクエスト
説明の前に、一例としてChromeがApacheに送っていたリクエストの中身を再掲しておくと、このようなものでした。

世の中の一般的なブラウザとWebサーバーはHTTPのルールに従っていますので、当然これもHTTPのルールにきちんと従った*HTTPリクエスト*になっています。

**Chrome => Apache**
```http
GET / HTTP/1.1
Host: localhost:8080
Connection: keep-alive
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
Sec-Fetch-Site: none
Sec-Fetch-Mode: navigate
Sec-Fetch-User: ?1
Sec-Fetch-Dest: document
Accept-Encoding: gzip, deflate, br
Accept-Language: ja-JP,ja;q=0.9,en-US;q=0.8,en;q=0.7


```

HTTPリクエストは、大きく3つの要素から構成されます。

1. 1行目: **リクエストライン**
2. 2行目~空行まで: **リクエストヘッダー**
3. 空行から後ろ〜: **リクエストボディ**

今回のリクエストでは、リクエストボディが空になっていますが、近々リクエストボディを含んだ例をお見せします。

### 1.1 リクエストライン

**リクエストライン**は、HTTPリクエストの1行目のことを指します。

*Chrome => Apache*のリクエストでいうと、

```http
GET / HTTP/1.1
```

の部分にあたります。

リクエストラインは、
```
<Method> <Request-URI> <HTTP-Version>
```
という3つの要素で構成されています。

#### 1.1.1 メソッド (Method)
リクエストメソッドは、リクエストラインの先頭の要素で、**リクエストの種類**を伝えます。

単に情報が欲しいだけ（GET）なのか、逆にフォームの入力情報などを渡したい（POST）のか、などによって変わってきます。

使えるメソッドの種類は、基本的には
- OPTIONS
- GET
- HEAD
- POST
- PUT
- DELETE
- TRACE
- CONNECT

のみです。

この中で今も昔も特によく使われるのは`GET`と`POST`、最近であれば`OPTIONS`や`DELETE`、`PUT`などもしばしば使われることがあります。

本書の中で使うのは`GET`と`POST`だけですので、この2つだけ覚えておいてもらえば大丈夫です。

#### 1.1.2 パス (Request-URI)

リクエストラインの2つめの要素はURIというよりはパス(path)とよく呼ばれ、**ドキュメントの場所**を示します。

最近のWebアプリケーションのように動的にレスポンスを生成するようなサービスにおいてはドキュメントの「*場所*を示す」と言ってもいまいちピンとは来ないかもしれませんが、HTTPが開発された当初はディスク内に置かれた特定のファイルを返すだけのような用途で使われることを想定されていたため、ファイルパスのような感覚で今もpathと呼ばれています。

Webアプリケーションにおいては、ファイルパスとして扱うというよりはどんな情報を求めているかを示す単なる文字列として扱うことが多いでしょう。

例）`/user/profile`という*パス*は、`user`ディレクトリの`profile`というファイルを意味するのではなく、「ユーザーのプロフィールが欲しい」ことを意味する文字列として扱う

#### 1.1.3 バージョン (Http-Version)
バージョンは、通信の際にクライアントがHTTPのルールのうちどのバージョンのルールに従って通信をしようとしているかを示します。

単にHTTPといっても、時間とともに改善が加えられ、使えるヘッダーが増えたり減ったり少しずつルールは変化しています。

サーバー側はこのバージョンを見ることで、
「ごめん、うちはHTTP/2のルールには対応してないから、HTTP1.1のルールで話してくれない？」
と返事を返すことができたりします。

本書では`HTTP/1.1`しか扱わないため、それほど神経質になる必要はありません。

::: details HTTPのバージョン
なお、HTTPのバージョンにはよく知られているものとして
- HTTP/0.9
- HTTP/1.0
- HTTP/1.1
- HTTP/2
- HTTP/3

があります。

本書は詳細には扱いませんが、いっぱしのWebエンジニアになるためにはバージョンの違いを抑えておく必要があるでしょう。
勉強熱心な読者の方には、[Real World HTTP 第2版](https://www.oreilly.co.jp/books/9784873119038/) という本をオススメします。
:::

#### 1.1.4 リクエストラインのまとめとRFC
以上をまとめると、*Chrome => Apache* のリクエストラインは、
**「`/`にあるドキュメントが欲しい（GET）。ルールはHTTP/1.1でリクエストするよ」**
という意味になります。


さて、1.1の最後として、RFCを見てみましょう。まずはこちらを見てみてください。
https://triple-underscore.github.io/rfc-others/RFC2616-ja.html#section-5

こちらは、RFCの「リクエストとは何か」を定める章です。
RFCによると、リクエストとは

```
Request       = Request-Line              ; Section 5.1
                 *(( general-header        ; Section 4.5
                  | request-header         ; Section 5.3
                  | entity-header ) CRLF)  ; Section 7.1
                 CRLF
                 [ message-body ]          ; Section 4.3
```

であるとされています。

始めはなんのこっちゃらと思うかもしれませんが、この記法は拡張BNF記法と呼ばれ、[同じドキュメント内の2.1](https://triple-underscore.github.io/rfc-others/RFC2616-ja.html#section-2.1)で詳しく説明されています。

このリクエストを読むのに必要なところだけ説明すると、
- **\*(X)** は、`X`の0回以上の繰り返し（= 全くなくてもよいし、いくらでもたくさんあって良い）がくること
- **X | Y** は、`X`または`Y`がくること
- **[X]** は、`X`が省略可能であること (= なくてもよい)

ことを示します。
つまり、上記の記述を日本語で解釈すると、
```
Request = Request-Line              ; Section 5.1
```
Requestは、始めにRequest-Lineが必ず1つあり、
```
         *(( general-header        ; Section 4.5
          | request-header         ; Section 5.3
          | entity-header ) CRLF)  ; Section 7.1
```
次に（`general-header`または`request-header`または`entity-header`のどれか1つ　＋　CRLFが1つ）の組み合わせ（つまり1行分のヘッダー）が0個以上あり
```
         CRLF
```
次にCRLFが1つあり
```
        [ message-body ]          ; Section 4.3
```
最後に省略可能な`message-body`がある、という意味になります。

ちなみに、CRLFは改行コードのことですが、[同じドキュメント内の2.2](https://triple-underscore.github.io/rfc-others/RFC2616-ja.html#section-2.2) でしっかりと定められています。

（CRLFの説明は割愛します。分からないかたは調べてみてください。）

--------

こうして読んでみると、RFCも部分的であれば意外と読めることがお分かりいただけると思います。
また、一口に「ヘッダー」と言っても厳密には`general-header` `request-header` `entity-header`の3種類に分かれていることや、改行コードも厳密には`LF`ではなく`CRLF`を使わないといけないことが分かります。

次に、[5.1 リクエストライン](https://triple-underscore.github.io/rfc-others/RFC2616-ja.html#section-5.1)の章も見てみましょう。

```
Request-Line   = Method SP  Request-URI SP HTTP-Version CRLF
```
こっちのほうが随分わかりやすいですね。
`SP`というのは、また[同じドキュメント内の2.2](https://triple-underscore.github.io/rfc-others/RFC2616-ja.html#section-2.2) を見てみると半角スペースのことであると定められています。
メソッド/パス/バージョンを区切るのは、厳密に半角スペースでならないことも、これで分かります。

ね？面白いでしょ？
 
### 1.2 リクエストヘッダー
**リクエストヘッダー**は、*HTTPリクエストの2行目〜空行*に書かれ、補助的な情報を伝える目的で使われます。
Cookieの値を送ったりレスポンスの言語を指定したりなど、様々な値を使うことができます。
1行につき1つの情報を伝えられ、複数行で構成することができます。

*Chrome => Apache*のリクエストでいうと、次の部分です

```http
Host: localhost:8080
Connection: keep-alive
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
Sec-Fetch-Site: none
Sec-Fetch-Mode: navigate
Sec-Fetch-User: ?1
Sec-Fetch-Dest: document
Accept-Encoding: gzip, deflate, br
Accept-Language: ja-JP,ja;q=0.9,en-US;q=0.8,en;q=0.7
```

先程RFCで見た通り厳密には3種類に分けられるのですが、本書ではそこまで細かく理解する必要はありません。

覚えておかなければいけないのは、どのヘッダーも
```
<field-name>: <field-value>
```
の形式をしていることぐらいです。

使えるヘッダーの種類も決められてはいますが、数が多いので必要になったときに必要なものだけ覚えるので構いません。

ちなみに、[RFC2616の4.2](https://triple-underscore.github.io/rfc-others/RFC2616-ja.html#section-4.2) によるとコロン(`:`)の後ろのスペースはいくらでも入れてよいが、**半角スペース1つだけにしておくのが好ましい**とされています。

 
### 1.3 リクエストボディ

**リクエストボディ**は、**HTTPリクエストの空行以降〜** に書かれ、リクエストの本文を表します。
*Chrome => Apache*のリクエストでは空となっています。

例えば、入力されたフォームの情報をサーバーへ送るために使われる`POST`メソッドでは、このリクエストボディが使われます。

一例として、*Chrome => Apache*のリクエストの代わりに、筆者がGithubでプルリクエストのbase_branchを変更した際のリクエストを記載しておきます。

```http
POST /bigen1925/test/pull/1/change_base HTTP/1.1
Host: github.com
Connection: keep-alive
Content-Length: 140
... 省略...
Accept-Encoding: gzip, deflate, br
Accept-Language: ja-JP,ja;q=0.9,en-US;q=0.8,en;q=0.7

authenticity_token=<this is secret>&new_base_binary=NC04
```

リクエストラインのメソッドをみると`POST`になっており、リクエスト本文には
```
authenticity_token=<this is secret>&new_base_binary=NC04
```
と書かれています。これは、`authenticity_token`は`<this is secret>`で、`new_base_binary`は`NC04`ですよ、とフォームの情報を送っています。

このように、サービスごとに独自のパラメータや情報をおくる際には、リクエストボディに情報を記載します。
本書でもPOSTを扱う章が後で出てきますので、詳細はそちらで説明します。

---
HTTPリクエストに関する概説は以上になります。

## 2. HTTPレスポンス
次は**HTTPレスポンス**ですが、こちらも先に前章までに取得した *Apache => Chrome*のレスポンスを例として見ておきましょう。

**Apache => Chrome**
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

HTTPレスポンスも、大きく3つの要素から構成されます。

1. **ステータスライン**
2. **レスポンスヘッダー**
3. **レスポンスボディ**

リクエストのときとほぼ同じですね。今度は説明が少なくて済みそうです。

### 2.1 ステータスライン
**ステータスライン** は、**HTTPレスポンスの1行目**のことを指します。
*Apache => Chrome*のレスポンスでいうと、以下の部分にあたります。

```
HTTP/1.1 200 OK
```

リクエストラインと同様3つの要素から構成されますが、リクエストラインとは少し内容が違います。

ステータスラインは、

```http
<Http-Version> <Status-Code> <Reason-Phrase>
```

によって構成されます。

#### 2.1.1 バージョン (Http-Version)
こちらは、リクエストラインのバージョンと同じようなものです。

Webサーバー側が、「今から返事するけど、このバージョンのHTTPのルールに従ってメッセージを送るよ」ということを意味します。

リクエストのときと同じく、本書はでは`HTTP/1.1`しか扱いません。

#### 2.1.2 ステータスコード (Status-Code)
**ステータスコード**とは、レスポンスの概要（＝HTTPリクエストがどのようにサーバーによって処理されたのか）を簡潔に示す3桁のコードです。

ステータスコードとして使える数字と意味は決められており、サーバー側が責任をもって適切なステータスコードを返却することが求められます。

例として、以下のようなものがあります

- **200**: 処理が正常に成功し、リクエストされたものを返却することを示す
- **301**: ドキュメントの場所が移動になったので、新しい場所へ再度リクエストしてほしいということを示す
- **404**: リクエストされたパスにドキュメントが見つからなかったことを示す
- **500**: リクエストを処理している最中に、Webサーバー内で予期せぬエラーが発生したことを示す

その他、完全なステータスコードの定義は[RFC2616](https://triple-underscore.github.io/rfc-others/RFC2616-ja.html#section-10) で定義されています。

本書では、必要になるステータスコードは都度説明しますので、*ステータスコードを暗記する必要はありません*。

#### 2.1.3 説明句 (Reason-Phrase)
説明句は、レスポンスの概要について、ステータスコードに追加で人間に理解しやすい完結な文として付け加えられるものです。

こちらはステータスコードと違い、文章がきっちりと定義されているわけではありません。
RFC内で推奨の文章というものはありますが、HTTPのルール内で自由に付与して良いです。

例として、以下のようなものがあります。

- (200のとき): `OK`
- (301のとき): `Moved Permanently`
- (404のとき): `Not Found`
- (500のとき): `Internal Server Error`

::: details コラム: Reason-Phraseはどこまで神経質になる必要がある？
ルール上自由に付与していいとはいえ、例えばブラウザによって何か利用されることがあるのであれば、Reason-Phraseはきちんとつけたくなるところです。
実際、どこまで神経質にReason-Phraseを考える必要があるのでしょう？

`RFC2616`を補足する別の[RFC7230](https://triple-underscore.github.io/RFC7230-ja.html#section-3.1.2) を見てみると、実はこのReason-Phraseは

`クライアントは、 reason-phrase の内容を無視するべきである。` 
（原文: `A client SHOULD ignore the reason-phrase content.`）

と書かれています。

更に続くReason-Phraseの文法を見てみると、
```
Reason-Phrase  = *<CR, LF を含まない TEXT>
```
ということになっています。

`*`は0回以上の繰り返しを示しますので、なんとReason-PhraseはHTTPのルール内で完全に省略しても良いということになってるのです。

これらを併せて考えると、結構適当でいいんだな、ということが分かります。

RFCを読んでおくと、「おっかなびっくり適当にやる」のではなく、「自信をもって適当にやる」ことができるので、少し安心ですね。

:::

### 2.2 レスポンスヘッダー
さて、お次はレスポンスヘッダーです。

**レスポンスヘッダー**は、**HTTPレスポンスの2行目〜空行まで**に書かれ、リクエストのときと同様付加的な情報を伝えるのに使われます。

*Apache => Chrome*のレスポンスでいうと下記の部分です

```http
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
```

リクエストヘッダーと同様、各行は
`<field-name>: <field-value>`
の形式で書かれます。

また、本当は3種類に分かれるとか、リクエストでしか使ってはいけないヘッダーとか色々あるんですが、今のところそこまで細かく覚える必要はありません。
本書でも必要になるヘッダーは都度説明しますので、必要なものだけ必要なときに覚えていきましょう。

### 2.3 レスポンスボディ

**レスポンスボディ**は、**HTTPレスポンスの空行以降**に書かれるもので、リクエストされたコンテンツの内容、またはエラー内容などが含まれます。

*Apache => Chrome*のレスポンスでいうと下記の部分です

```html
<html><body><h1>It works!</h1></body></html>
```

これは皆さんご存知の`HTML`の形式になっていますね。

リダイレクトを指示(ステータスコード`301`など)したりしていなければ、ブラウザの画面に表示されるのはこの部分となります。

レスポンスボディは様々なデータを返すことができ、今回はHTMLですが、JavascriptやCSS、画像のバイナリデータを返すこともできます。
（ただし、`Content-Type`というヘッダーでデータ形式を指定する必要があり、本書でも後ほど扱います。）

-------
HTTPについての解説は以上となります。

# まとめ

長くなってしまったので、ここまでの話の流れを振り返っておきます。

まず、世の中のWebサービスとブラウザは、お互いの言いたいことをきちんと理解するため、**HTTP**という決まったルールに従ってメッセージを送り合うのでした。

HTTPというルールの中では、ブラウザがWebサーバーへ**リクエスト**を送信する時には

- 1行目: **リクエストライン**
- 2行目〜空行: **リクエストヘッダー**
- 空行〜: **リクエストボディ**

の順に内容を書いてメッセージを送る決まりとなっていました。

また、Webサーバーがブラウザへ**レスポンス**を送信する時には、

- 1行目: **ステータスライン**
- 2行目〜空行: **レスポンスヘッダー**
- 空行〜: **レスポンスボディ**

の順に内容を書いてメッセージを送る決まりとなっていたことを学びました。

また、折に触れてChromeとApacheで送り合っていたメッセージを例に見つつ、RFCも参照してドキュメントの読み方についても理解を深めました。

---------

ここまでで、「Webサーバー」がやっている仕事の全容がほぼつかめてきたと言っても過言ではないでしょう。

次章では、冒頭でWebサーバーの仕事について改めて俯瞰した後、実際にソースコードを書いて皆さんの自作サーバーをどんどん「Webサーバーっぽく」していきます。