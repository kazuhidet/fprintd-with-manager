# Maintainer: Kazuhide Takahashi <kazuhide.t@linuxpowered.com>
# Contributor: Jan Alexander Steffens (heftig) <heftig@archlinux.org>
# Contributor: Nikolay Rysev <mad.f3ka@gmail.com>
# Extends fprintd with a fingerprint manager GUI and includes all fprintd functionality.
# Manager adapted from https://github.com/mmhfarooque/chipsailing-cs9711-fingerprint-linux
# Thanks to Mahmud Farooque and the upstream contributors (manager: MIT).

pkgname=fprintd-with-manager
pkgver=1.94.5
pkgrel=4
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
  'e426be2ba27b2c49af09d57e26ece10d124d4e5d1b73844f596a29b893205bd63c28e7103e99267c108b9d8a1de3ec369bece93a5205f4025f1a6b9df3a5c3c7'
  'ace225b3d44034f987c1de794feca633795fe6c49db67ab9543f4fb5d0dc8e819ca357dddb0209767d1b17721007227dc665ca2fd62496c69030306717690ec0'
  'dd7262b522112d8371ca0eb51a66bb8391ef666a877700e44139dedbdb62868616ebcc721b9d79e1c2a4c8cbd85d61966f73d892d85d55623d08d4290557ca45'
  'de15fdd101959e6b6ac926d115ce96008a6a5a6707cc13062393416ef4e606a7a6d0c32a25cf4ca189099620fe0da268e6cf92df66dac614239483c282a531bb'
  '7f51f297c23157963769988a929d6721f4b8c32ac94cd976bc87c053144483e36d41f2ba53b08d8628173a658d89553c88efd0aed9a34b101c58f2e990e59526')
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
