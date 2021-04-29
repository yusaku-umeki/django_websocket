# プロジェクトテンプレート

DeMiA の Django プロジェクトで使うファイル群．

## 準備

すでに導入している場合は，このセクションは無視できる．

### Poetry のインストール

- Windows (非推奨)

  WSL の利用を推奨しているため，Linux の項目を参照．WSL ではなく Windows で利用したい場合は[公式ホームページ](https://python-poetry.org/docs/)を参照．

- macOS

  ```console
  $ brew install poetry
  ```

- Linux

  Ubuntu 20.04 の場合は `python` コマンドが Python3 になるように以下のコマンドを実行:

  ```console
  $ sudo apt update && sudo apt install python-is-python3
  ```

  次に，Poetry をインストール:

  ```console
  $ curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python3 -
  ```

  `.bashrc` に以下を追記:

  ```bash
  export PATH="$HOME/.poetry/bin:$PATH"
  ```

### Poetry の設定

```console
$ poetry config virtualenvs.in-project true
```

## 使用方法

### ファイル群の導入

GitHub から 本リポジトリをクローンし，`.git` ディレクトリを削除しておく．その後，プロジェクトの直下に全てのファイルを追加する．

- プロジェクトのディレクトリが存在しない場合:

  ```console
  $ cp -r project_template 'プロジェクトのパス'
  ```

- プロジェクトのディレクトリが存在する場合:

  ```console
  $ cp -r project_template/{*,.*} 'プロジェクトのパス'
  ```

**NOTE**: 隠しファイルが存在するため，コマンドラインから追加すること．また，`README.md` はプロジェクトのものに置き換える必要がある．

### プロジェクトの初期化

プロジェクトのディレクトリに移動後，以下のコマンドを実行する．

```console
$ poetry init -n --python '^3.8' --name 'プロジェクト名' --dependency django --dev-dependency pre-commit
$ poetry install
```
