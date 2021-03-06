---
title: "本書にかける想い"
---

このチャプターでは、この本を書こうと思ったきっかけについて語ります。
長いですが、本章には関係のないお話なので、飛ばしてもらって構いません。
冗長なコラムですので、そのうち巻末に移動するかもしれません。


# Webエンジニアとしてぶち当たった壁
この本を書こうと思ったきっかけは、ある一冊の本との出会いから始まります。

当時、僕は新卒未経験で自社Webサービスを持つITベンチャーにエンジニアとして就職し、3年が経ったころでした。
その3年間は、サーバーサイドを中心に開発経験を積み、要件定義からアプリケーションの設計、実装も行っていました。

3年目ともなると、先人達の残したインフラ環境上でフレームワークのお作法に則りながら、数十人月にもなるような、ある程度大きな機能を実装・リリースできていました。
（もちろん一人ではなくチームで開発を行っていました）
ビジネスサイドと会話し、欲しい機能をきちんと言葉に落とし、プログラムをガリガリ書いてタスクをバッサバッサと倒していく感覚は、自分がいっぱしのエンジニアになれたかのような感覚があり、しばらくは楽しい時期でした。

ところが、そんなタスクスレイヤーも、1年も経てば気づいたのです。
この作業を5年続けても、目の前にいる先輩エンジニアのようにはなれない。

その会社の先輩エンジニアは、サーバー構成から言語実装の話、アルゴリズムの話、性能最適化（プロファイラやクエリオプティマイザなど）までなんでも知っていて困ったらいつでも魔法のように解決してくれるのです。

Webフレームワーク内（当時はLaravelを使っていました）にプログラムを書けば解決できる問題は、自分で解決できるようになっていました。
その瞬間は知っていなくても、フレームワークのリファレンスを読んで解決できることがほとんどです。
また、Web系ベンチャーの機能開発の業務時間の95%以上はその範疇に入っていました。

でも残り5%は、サーバーがなんちゃら、プロトコルがなんちゃら、ヘッダーがなんちゃらと言われて、良くわからないのです。
そういう問題にでくわすと、その先輩エンジニアがさっとやってきて、さっと解決していくのです。

ついでに僕の後学のためにと色々と教えようとしてくれるのですが、
「全部話すと長いから、こういうのは説明が難しいね（笑）」
といって、かいつまんで教えてくれるものの、深く理解はできず、次回また先輩に頼ることになるのです。

何か勉強しなくては追いつけない、と思いつつも自分と先輩との差は大きすぎて、何から勉強したらいいか分かりません。
手当たり次第にデザインパターンの本や、インフラの本を読もうと試みるのですが、実践の場がない知識はなかなか定着せず、いつまで経っても成長している感覚がありません。
業務の中で断片的にふれる課題から勉強しようにも、ベースになる知識がないのでなかなか身につきません。

そしてそんな焦りに追い打ちをかけるように、半年前には楽しんでいたタスクスレイヤーも、急にマンネリ感に襲われるようになります。
どんなゲームでもそうですが、長い間倒せなかった敵が倒せるようになってくると、そのことが嬉しくて何度もその敵に挑みに行くようになりますが、倒せることが当たり前になってくるとつまらなくなってしまうものです。

そういった感覚もあいまって、エンジニアリングが急につまらなくなってきていました。

# ブレイクスルー
そうして、4年目にさしかかったころ、ある本を読んで急に視界が開けたような感覚がありました。
その本が

[Webサーバを作りながら学ぶ　基礎からのWebアプリケーション開発入門 (前橋和弥 著](https://gihyo.jp/book/2016/978-4-7741-8188-2)

です。

この本では、Webサーバー、WebアプリケーションをJavaを使って自分で書き上げる本です。
「Webサーバー/Webアプリケーションとはなにか」の説明から始まり、実際に簡単なWebサーバー/Webアプリケーションを作り上げていく流れとなっています。

そして、本にそって実際に書いてみると、たった数十行のプログラムでブラウザにWebページが表示できるようになりました。
また、数百行もかけば、Cookieを使ったやりとりができ、ルーティングや、Cookieを使ったSession管理までできるWebフレームワークもどきができてしまうのです。

もちろん、細かいところでは世の中に出回っている高精度、高性能なWebサーバーやフレームワークには足元にも及びませんが、かなりWebフレームワークっぽく動きますし、ホームページも普通に表示できます。
しかも、実際に自分で手を動かして0から書いていくので、少なくとも自分が作り上げたアプリケーションについては、具体的な処理がすべて把握できている状態です。

僕はこの本を終えたあと、
「じゃあ、LaravelでいうMiddlewareはこうやって実装されているってことか？」
「Laravelのルーティングは裏側では実際こういうことをやっているってことか？」
など、業務では詳細に知る必要のないところも、調べる前から仕組みが想像できるようになっていました。

（Middlewareなどは前橋先生の本には書かれていませんでしたが、読了後楽しくなって実際に自分で書いてみたら、実装することができました）

この本を読み終えたころ、お世話になった1社目を辞め、2社目へ転職していました。

会社が変わったので、新しいプロダクトに触れるわけですが、1社目とは言語も変わってPython-DjangoのWebサービスでした。

PHPしか書いたことのない自分にとっては覚えることも多かったのですが、WebフレームワークであるDjangoの仕組みは簡単なイントロダクションを読めばスラスラと頭に入ってくるのです。
それどころか、イントロダクションに出てこない知らない機能も、実際の業務を進める時には
「きっとこの辺りにこういう機能があって、設定値で変えられるようになってるはずだよね？」
というあたりがついて、調べてみると実際に存在していました。

デキるエンジニアとそうじゃないエンジニアを分ける特質の1つに、「あたりをつけられる」能力があると思います。
エラーが発生したとき、エラーメッセージをひと目見て「ああここがおかしいんだな」と分かる力。
新しい機能を作るとき、「ああ、ここを変えれば終わりだな」とすぐに分かる力。

その一部が身についた感覚がありました。
視界が急に広くなり、見える景色が変わりました。


# できるだけ多くの人が、エンジニアリングを楽しめるように
そして僕が一番重要だと思っているのは、それ以降、またエンジニアリングが楽しくなったのです。

知識というのは不思議なもので、知れば知るほど、知らないことが増えていきます。

WebサーバーやWebアプリケーションについて理解すると、次はTCP通信について知りたくなり、あるいはDjangoとLaravelの違いについて知りたくなり、あるいはWebアプリケーションとデータベースアプリケーションの違いを知りたくなってきました。
あるいは、フレームワークを理解するために、たんにそもそもPythonをもっと深く勉強したいと思うようになりました。
（[Fluent Python](https://www.oreilly.co.jp/books/9784873118178/)がオススメです）

フレームワークの違いを勉強する中で、言語的な制約や文化がフレームワークに大きく影響を与えることに気づくと、今度は言語実装について学びたくなります。
（[低レイヤを知りたい人のためのCコンパイラ作成入門](https://www.sigbus.info/compilerbook)がオススメです）

しかし、やはり業務から離れすぎることを学ぶ際には、モチベーションが下がることも分かってきました。
僕にとっては、フロントアプリケーションを深く使う機会が少ないため、[Javascript 第6版](https://www.oreilly.co.jp/books/9784873115733/)を読むのはかなり大変でした。

それでも、学ぶことも、書くことも、この1年は毎日楽しいです。



そしてふと周りを見渡してみると、僕と同じように2~3年目で伸び悩むエンジニアがたくさんいるように見えました。
そして伸び悩んだまま5年目、7年目になってしまっているエンジニアの方も見受けられました。

ここで言いたいのは、伸び悩んでいるから悪いとか、壁を超えたから優秀だ、という話ではなく、そういうった方々は共通してエンジニアリングに飽きているように見えるということです。

そんな人でも、僕は「やっぱりエンジニアリングを楽しい」と思ってもらいたいと思うようになりました。
かつて僕がそうであったように、ふと手にとった一冊の本がまた「エンジニアリングは楽しい」ということを思い出させてくれることがあるかもしれません。
そして、そんな本が世の中にないのであれば、僕が書いてみるのも悪くない、そう思い立ってこの本を書き始めることにしました。

「人生を楽しめ」とか「仕事を楽しめ」とか、そんな押し付けがましいことを言う気はさらさらありません。
僕が求めているのは、自分が好きなゲームを一緒に目をキラキラさせてやってくれる友達なのです。
この本はあなたの為に書く本ではなく、僕がエンジニアリングというゲームをより楽しむために、僕のために書く本です。

# 内容について
本の内容としては、前半は [Webサーバを作りながら学ぶ　基礎からのWebアプリケーション開発入門 (前橋和弥 著](https://gihyo.jp/book/2016/978-4-7741-8188-2) をトレースしながら、JavaではなくPythonでWebアプリケーションを作る内容になる予定です。
後半は、Djangoを題材に、モダンなフレームワークに搭載されている様々な機能について、模倣していく流れとなります。

前半は、単に前橋先生の本を紹介するだけでもよかったんですが、Python使いが多い社内でジュニアエンジニア向けに勉強会したところ、
* そもそもJavaであることが障壁になってしまうメンバーがいた
* ジュニアエンジニアが混乱してしまうような説明の流れの箇所があり、より良い内容にできそうだった
* Zennというプラットフォームで公開することで、より広くのエンジニアに届けられる可能性がある
といった理由から、僕の言葉で新たに執筆することにしました。

後半については、前橋先生の本では「いっぱしのWebエンジニアとして知っておかなければならないこと」を主眼にかかれていて、SSLやセキュリティなど、様々な周辺知識まで紹介しています。
しかし、今回の僕の本では、たんに自分のおもちゃを分解していじくりまわして自己満足するための本ですので、少し内容を改変してお伝えしようかなと思う次第です。

エンジニアとしてお金を稼いで行く気のある人は、前橋先生の本にかかれている内容は必修事項ですので、興味がある方は是非そちらも読んでみてください。

~~なお、前橋先生の許諾は現在確認中であり、許諾が得られない場合は直ちに本書の執筆は終了します。~~
**前橋先生より快諾をいただきました。ありがとうございます。**

また、どのような本がブレイクスルーのきっかけになるかは、人によって違うと思います。
途中で触れたように、勉強していて楽しいと思える本は、自分の普段書くコードにとても近くて、でもギリギリしらない事（僕はよく"自分という領域の一歩外側"と言います）というのが適切です。

そういう意味で、この本がすべての人のブレイクスルーになるとは思っていません。
ですが、Webサービス全盛のこの時代、単純な技術でいいから、ちょろっと書けるようになっただけのエンジニアでいいから、とにかくサービスをばりばり増殖させてほしい会社がたくさんあります。
また、プログラミングスクールも隆盛を極め、簡単なWebフレームワークの使い方だけを学んで実戦投入されるジュニアエンジニアも山程います。
自分もその一人です。

そういった人たちはだいたい自分と同じようなところでつまずくのではないかと思い、自分のような人に向けて、そして「あと1年早くこんな本に出会っていれば」という思いを込めて、あえて **「伸び悩んでいる3年目Webエンジニアのための、Python Webアプリケーション自作入門」** と名付けました。

この本が、どこかの僕じゃない僕を楽しませてくれることを願います。


# 謝辞(加筆予定)

まずなによりきっかけを与えてくださった前橋様、及び先行書籍の販売に携わった技術評論社様には何よりも感謝しています。

その他、謝辞を述べたい方はたくさんいらっしゃいますが、本書籍執筆完了後にまとめさせてください。
