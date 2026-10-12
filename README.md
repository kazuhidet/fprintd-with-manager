# fprintd-with-manager

English | [Japanese](README_ja.md)

`fprintd-with-manager` extends fprintd with a graphical fingerprint manager.
It includes fprintd's D-Bus service, command-line tools, and PAM module,
and provides the `fprintd` package for dependency compatibility.

The Lock screen toggle supports Omarchy Quattro’s dedicated PAM service and hyprlock. On Quattro, disabling fingerprint moves its PAM file aside; enabling restores it. Changes take effect the next time you lock the screen.

## Manager origin and acknowledgments

The `fprintd-manager` GUI and its desktop entry are adapted from
`cs9711-manager.py` and `cs9711-manager.desktop` in Mahmud Farooque's
[chipsailing-cs9711-fingerprint-linux](https://github.com/mmhfarooque/chipsailing-cs9711-fingerprint-linux)
project.

Thank you to Mahmud Farooque and the project's contributors for developing
an accessible fingerprint manager and making it available as open source.

This package removes dependencies on the CS9711-specific installer, supports
device detection across readers supported by fprintd, verifies the selected
finger, and integrates the manager into an Arch Linux package.
For the Omarchy-shell / Quickshell implementation, see
[omarchy-plugin/README.md](omarchy-plugin/README.md) (in Japanese).

## Licenses

- fprintd: GPL-2.0-or-later, as specified in the upstream fprintd sources.
- The adapted manager GUI and desktop entry: MIT.
  The original copyright notice is `Copyright (c) 2026 Mahmud Farooque`.
  The complete original license is preserved in [LICENSES/MIT.txt](LICENSES/MIT.txt)
  and included as `fprintd-manager.LICENSE` for makepkg. It is installed at
  `/usr/share/licenses/fprintd-with-manager/MIT.txt`.
- The original Arch Linux packaging files: 0BSD. See [LICENSE](LICENSE).

Maintainer: Kazuhide Takahashi <kazuhide.t@linuxpowered.com>
