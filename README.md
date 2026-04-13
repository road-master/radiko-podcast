# radiko Podcast

[![Test](https://github.com/road-master/radiko-podcast/workflows/Test/badge.svg)](https://github.com/road-master/radiko-podcast/actions?query=workflow%3ATest)
[![CodeQL](https://github.com/road-master/radiko-podcast/workflows/CodeQL/badge.svg)](https://github.com/road-master/radiko-podcast/actions?query=workflow%3ACodeQL)
[![Code Coverage](https://qlty.sh/gh/road-master/projects/radiko-podcast/coverage.svg)](https://qlty.sh/gh/road-master/projects/radiko-podcast)
[![Maintainability](https://qlty.sh/gh/road-master/projects/radiko-podcast/maintainability.svg)](https://qlty.sh/gh/road-master/projects/radiko-podcast)
[![Dependabot](https://flat.badgen.net/github/dependabot/road-master/radiko-podcast?icon=dependabot)](https://github.com/road-master/radiko-podcast/security/dependabot)
[![Python versions](https://img.shields.io/pypi/pyversions/radikopodcast.svg)](https://pypi.org/project/radikopodcast)
[![X URL](https://img.shields.io/twitter/url?style=social&url=https%3A%2F%2Fgithub.com%2Froad-master%2Fradiko-podcast)](https://x.com/intent/post?text=radiko%20Podcast&url=https%3A%2F%2Fpypi.org%2Fproject%2Fradikopodcast%2F&hashtags=python)

タイムフリー 1 週間では足りない人向けの radiko 番組自動アーカイブコマンドです

## 特徴

- 対象の番組をタイムフリーから検索し、自動的にアーカイブ
- 複数の番組を同時にアーカイブ

## 対象の番組をタイムフリーから検索し、自動的にアーカイブ

`config.yml` ファイルに設定を記述して `radiko-podcast` コマンドを実行すると、
自動的にタイムフリーを検索して、見つかった番組を
`output/` ディレクトリーにアーカイブし続けます

アーカイブした番組は m4a ファイルになるので、
iTunes で iPhone に入れることができ、
外出中でも sim の通信パケットを消費せずに番組を聴くことができます

コマンドを実行したままにしておけば、
radiko が夜間に新しく追加するタイムフリーの番組表も
自動的に検索してアーカイブを行い続けます
## 複数の番組を同時にアーカイブ

radiko の番組のアーカイブには時間がかかりますが、
この `radiko-podcast` コマンドは複数番組を同時にアーカイブできます

同時に実行するアーカイブのプロセス数は、設定ファイルで調整できます

## 動作環境の要件

- FFmpeg

## クイックスタート

### 1. インストール

```console
pip install radikopodcast
```

### 2. `config.yml` の作成

```yaml
# エリア ID (詳細は "ISO 3166-2:JP" で検索)
area_id: JP13
# 同時に実行するアーカイブのプロセス数
number_process: 3
# アーカイブするファイルが既に存在した場合、コマンドの実行を停止するかどうか
# true: 既に存在したファイルは上書きせず、他の番組のアーカイブを続けます
# false: コマンドの実行を停止します
stop_if_file_exists: false
# いずれかのキーワードで見つかった番組をアーカイブします
# 検索対象の情報は番組名のみです
keywords:
  - "SAISON CARD TOKIO HOT 100"
  - "K's Transmission"
  - "ROPPONGI PASSION PIT"
  - "カフェイン11"
# タイムフリー30 プランに加入したアカウントでログインした際の radiko_session を設定すると、
# 30 日まで遡ってアーカイブできます
# この値は開発者ツールの Network タブを開き、
# ログインした radiko で画面遷移した際のリクエストをクリック、
# Headers タブで Request Headers の Cookie を参照するなどして確認できます
radiko_session: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 3. `output/` ディレクトリーの作成

```console
mkdir output
```

この時点でディレクトリー構成は次のようになっています:

```text
your-workspace/
+----output/
+----config.yml
```

### 4. コマンドの実行

```console
radiko-podcast
```

すると、対象の番組をタイムフリーから検索し、
見つかった番組を `output/` ディレクトリーに自動的にアーカイブし続けます

### 5.終了する場合、ターミナルで Ctrl + C を入力します
