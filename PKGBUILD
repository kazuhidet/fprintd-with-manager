# Maintainer: Kazuhide Takahashi <kazuhide.t@linuxpowered.com>
# Contributor: Jan Alexander Steffens (heftig) <heftig@archlinux.org>
# Contributor: Nikolay Rysev <mad.f3ka@gmail.com>
# Extends fprintd with a fingerprint manager GUI and includes all fprintd functionality.
# Manager adapted from https://github.com/mmhfarooque/chipsailing-cs9711-fingerprint-linux
# Thanks to Mahmud Farooque and the upstream contributors (manager: MIT).

pkgname=fprintd-with-manager
pkgver=1.94.5
pkgrel=3
pkgdesc="fprintd extended with a fingerprint manager GUI, including all fprintd functionality"
url="https://fprint.freedesktop.org/"
arch=(x86_64 aarch64)
license=(GPL-2.0-or-later MIT)
depends=(
  dbus
  glib2
  glibc
  libgcc
  libfprint
  pam
  polkit
  systemd
  systemd-libs
)
makedepends=(
  git
  glib2-devel
  gtk-doc
  meson
  pam_wrapper
  python-cairo
  python-dbus
  python-dbusmock
  python-packaging
)
optdepends=(
  'python-gobject: fprintd manager GUI'
  'gtk4: fprintd manager GUI'
  'libadwaita: fprintd manager GUI'
)
groups=(fprint)
provides=("fprintd=$pkgver")
conflicts=(fprintd)
source=(
  "git+https://gitlab.freedesktop.org/libfprint/fprintd.git?signed#tag=v$pkgver"
  fprintd-manager
  fprintd-manager.desktop
  fprintd-manager.LICENSE
  README.md
  README_ja.md
)
b2sums=('e9fec866da871cdae2f3312b8428209237f94312c6baa622cb1d71960d2de422c7aab339b75c05607cb915da28ad0135c9cf3538fbde9df1700a36d5f9547ba8'
  '35d5c18c31b8c601ef47a939a7fad82b268bfa9e50ee24b28d085936353aa7bb2cf1753da391902dcb2ccf688d51ed0b1ad7b24bbde71a04172fae18bde3899d'
  'ace225b3d44034f987c1de794feca633795fe6c49db67ab9543f4fb5d0dc8e819ca357dddb0209767d1b17721007227dc665ca2fd62496c69030306717690ec0'
  'dd7262b522112d8371ca0eb51a66bb8391ef666a877700e44139dedbdb62868616ebcc721b9d79e1c2a4c8cbd85d61966f73d892d85d55623d08d4290557ca45'
  '3d95edaf74b9a1fc3324f2ae091717adcdd2735fd9850d29d1e7ffa2cfd7ecf7e759ebd1b987758f87e08983f06a59587f941f2671fa6ceafdf4a4f41013521c'
  'a3dc7f5f7c32e00b75387771d9ba1556ab0038f66836600e9035b09b77dbcedf3ee59fca48c89c4cd448b3656a4abdd9d276e146fe9ce2ee2206e9e21e75991a')
validpgpkeys=(
  D4C501DA48EB797A081750939449C2F50996635F # Marco Trevisan (Treviño) <mail@3v1n0.net>
)

prepare() {
  cd fprintd

  # Fix tests
  git cherry-pick -n ec2a995c36f0757e1f5c695a80d89f41d2fa03bb
}

build() {
  local meson_options=(
    -D gtk_doc=true
    -D pam_modules_dir=/usr/lib/security
  )

  arch-meson fprintd build "${meson_options[@]}"
  meson compile -C build
}

check() {
  meson test -C build --print-errorlogs
}

package() {
  depends+=(libfprint-2.so)

  meson install -C build --destdir "$pkgdir"
  install -Dm644 "$startdir/fprintd-manager.LICENSE" "$pkgdir/usr/share/licenses/$pkgname/MIT.txt"
  install -Dm644 "$startdir/README.md" "$pkgdir/usr/share/doc/$pkgname/README.md"
  install -Dm644 "$startdir/README_ja.md" "$pkgdir/usr/share/doc/$pkgname/README_ja.md"
  install -Dm755 "$srcdir/fprintd-manager" "$pkgdir/usr/bin/fprintd-manager"
  install -Dm644 "$srcdir/fprintd-manager.desktop" "$pkgdir/usr/share/applications/fprintd-manager.desktop"
}

# vim:set sw=2 sts=-1 et:
