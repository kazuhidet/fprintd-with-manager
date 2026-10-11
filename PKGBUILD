# Maintainer: Jan Alexander Steffens (heftig) <heftig@archlinux.org>
# Contributor: Nikolay Rysev <mad.f3ka@gmail.com>

pkgname=fprintd
pkgver=1.94.5
pkgrel=3
pkgdesc="D-Bus service to access fingerprint readers"
url="https://fprint.freedesktop.org/"
arch=(x86_64 aarch64)
license=(GPL-2.0-or-later)
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
source=(
  "git+https://gitlab.freedesktop.org/libfprint/fprintd.git?signed#tag=v$pkgver"
  fprintd-manager
  fprintd-manager.desktop
)
b2sums=('e9fec866da871cdae2f3312b8428209237f94312c6baa622cb1d71960d2de422c7aab339b75c05607cb915da28ad0135c9cf3538fbde9df1700a36d5f9547ba8'
        '78c077e07f911970487631ccc8e37fd9c888bfc2fabc1dc2cb743ccca2c46baa627417efc44f89459feae8b808ac22e3f827488987f24b271fb831a8d5b0217e'
        '0251f46cb59b09c7de5968ead7933e59ea5bd736b38e58b6a33d13a7662c2083350c875911565cb2e5b7921123cc9e46741354b73f3efcb830b8acac8117a3c7')
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
  install -Dm755 "$srcdir/fprintd-manager" "$pkgdir/usr/bin/fprintd-manager"
  install -Dm644 "$srcdir/fprintd-manager.desktop" "$pkgdir/usr/share/applications/fprintd-manager.desktop"
}

# vim:set sw=2 sts=-1 et:
