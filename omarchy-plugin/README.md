# fprintd.manager — Omarchy-shell plugin

Quickshell の管理パネルで指紋を登録・照合・削除します。GTK は起動しません。
パネルはフォーカス中のモニター中央にポップアップし、Escape または外側のクリックで閉じます。

## インストール

必要なパッケージ: `fprintd`、対応ドライバーを含む `libfprint`、`python-gobject`、Omarchy-shell / Quickshell。

リポジトリのルートから実行します。

```sh
python3 omarchy-plugin/install.py
omarchy-shell shell rescanPlugins
omarchy-shell shell summon fprintd.manager '{}'
```

`~/.config/omarchy/plugins/fprintd.manager/` にファイルを配置し、`shell.json` の
`plugins` に登録します。既存の設定は保持し、変更前の `shell.json` はバックアップします。
パネルは `omarchy-shell shell toggle fprintd.manager '{}'` でも呼び出せます。

## 機能

- fprintd が公開するデバイスを選択。CS9711 以外も対応。
- 10 本の指の登録、登録段階の進捗表示、照合。
- 選択した指または選択したデバイスの全指紋を、確認後に削除。
- 登録・照合のキャンセル。終了時には Stop / Release を呼び、120 秒でタイムアウト。
- ログイン、ロック画面、sudo、polkit の PAM 設定の検出。
- このプラグインが追加した PAM 行の有効化・無効化、試行回数・タイムアウト設定。
- パネル内の操作ログ。永続保存はしません。

登録と削除の権限は fprintd の polkit ポリシーに従います。PAM の変更時は
`pkexec` で管理者認証し、パスワードをプラグイン内に保存しません。
PAM ファイルは最初の変更時に `.fprintd-manager.bak` として保存します。

既存の PAM 設定で有効になっている指紋認証は「既存の PAM 設定で管理されています」と
表示し、変更しません。Omarchy 固有の `omarchy-lock-fingerprint` と `hyprlock` も検出します。
PAM スタック内の必須チェックとパスワード認証を保持します。
共通認証設定が間接的に指紋認証を有効にしている場合、その場所の切り替えは管理者設定に委ねます。

## 検証

```sh
/usr/bin/python3 -m unittest discover -s tests -p 'test_fprintd_plugin.py' -v
```

実機の登録・削除・PAM 変更は確認ダイアログからユーザーが実行してください。

## アンインストール

プラグインから追加した認証設定を無効化した後、`shell.json` の `plugins` から
`fprintd.manager` を除き、ユーザーのプラグインディレクトリを削除します。
登録済み指紋と既存 PAM 設定はプラグイン削除だけでは変更されません。
