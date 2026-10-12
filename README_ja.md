# fprintd-with-manager

[English](README.md) | 日本語

`fprintd-with-manager` は fprintd に指紋管理 GUI を追加した拡張パッケージです。
fprintd 本体の D-Bus サービス、コマンドラインツール、PAM モジュールを含み、
`fprintd` を提供するパッケージとして利用できます。

Lock screen トグルは Omarchy Quattro の専用 PAM サービスと従来の hyprlock に対応します。Quattro ではオフ時に指紋用設定を退避し、オン時に復元します。変更は次回ロック時に反映されます。

## manager の出典と謝辞

指紋管理 GUI `fprintd-manager` とデスクトップファイルは、Mahmud Farooque 氏の
[chipsailing-cs9711-fingerprint-linux](https://github.com/mmhfarooque/chipsailing-cs9711-fingerprint-linux)
に含まれる `cs9711-manager.py` と `cs9711-manager.desktop` を取り込み、改変したものです。

使いやすい指紋管理 GUI を開発し、オープンソースとして公開してくださった
Mahmud Farooque 氏と同プロジェクトの貢献者の皆様に感謝します。

本パッケージでは、CS9711 固有のインストーラーへの依存を整理し、fprintd 対応機種全般での
デバイス検出、選択した指の照合、Arch Linux パッケージへの統合に対応しています。
Omarchy-shell / Quickshell 向けの実装は [omarchy-plugin/README.md](omarchy-plugin/README.md) を参照してください。

## ライセンス

- fprintd 本体: GPL-2.0-or-later。fprintd のソースに含まれるライセンスに従います。
- 取り込んだ manager GUI とデスクトップファイル: MIT。
  原著作権表記は `Copyright (c) 2026 Mahmud Farooque` です。
  元のライセンス全文を [LICENSES/MIT.txt](LICENSES/MIT.txt) に保存しています。
  makepkg 用に同じ内容を `fprintd-manager.LICENSE` として同梱しています。
  パッケージにも `/usr/share/licenses/fprintd-with-manager/MIT.txt` として同梱します。
- 元の Arch Linux パッケージ設定: 0BSD。既存の [LICENSE](LICENSE) を参照してください。

Maintainer: Kazuhide Takahashi <kazuhide.t@linuxpowered.com>
