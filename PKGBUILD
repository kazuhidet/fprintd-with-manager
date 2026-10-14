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
  '75f646fcc236d19887241a5906ed67f7de1ce1b0bc8addb025ae2a2a36f3ec3108661e8f23549ac496fff84deab093eefa15d766a9a678c48ba301b76e7d942d'
  'ace225b3d44034f987c1de794feca633795fe6c49db67ab9543f4fb5d0dc8e819ca357dddb0209767d1b17721007227dc665ca2fd62496c69030306717690ec0'
  'dd7262b522112d8371ca0eb51a66bb8391ef666a877700e44139dedbdb62868616ebcc721b9d79e1c2a4c8cbd85d61966f73d892d85d55623d08d4290557ca45'
  '2e22c77b43a819c3453ffbdfbc252db78d085f88dd7acbf46445a24020d1920871d10e8ee44eefc1618e2a900c81724901463fd184ba1d387d54cffbf165dfc9'
  '9c8465c3a052ea03dea71237841da51dc82519638b8beb957a3ea0620521462f16f3e26349145baadf6a0b396646dad3ed573be2407b063b0e9e12c4b869cc9e')
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
  sed -i "s/@PKG_VERSION@/$pkgver-$pkgrel/" "$pkgdir/usr/bin/fprintd-manager"
  install -Dm644 "$srcdir/fprintd-manager.desktop" "$pkgdir/usr/share/applications/fprintd-manager.desktop"
}

# vim:set sw=2 sts=-1 et:
