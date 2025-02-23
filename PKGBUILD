# Maintainer: Jan Alexander Steffens (heftig) <heftig@archlinux.org>
# Contributor: Nikolay Rysev <mad.f3ka@gmail.com>

pkgname=fprintd
pkgver=1.94.5
pkgrel=1
pkgdesc="D-Bus service to access fingerprint readers"
url="https://fprint.freedesktop.org/"
arch=(x86_64)
license=(GPL-2.0-or-later)
depends=(
  dbus
  gcc-libs
  glib2
  glibc
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
groups=(fprint)
source=(
  "git+https://gitlab.freedesktop.org/libfprint/fprintd.git?signed#tag=v$pkgver"
  tests.diff
)
b2sums=('e9fec866da871cdae2f3312b8428209237f94312c6baa622cb1d71960d2de422c7aab339b75c05607cb915da28ad0135c9cf3538fbde9df1700a36d5f9547ba8'
        '46c3287cb9430e607af53b4000144cd7b4c95cdd8f388b342136838ffcce400c36691bb8571a4413aca0d9b698c7f3eec766654ee9c30da7298d806127972cec')
validpgpkeys=(
  D4C501DA48EB797A081750939449C2F50996635F # Marco Trevisan (Treviño) <mail@3v1n0.net>
)

prepare() {
  cd fprintd

  # PAM tests succeed but time out?
  git apply -3 ../tests.diff
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
}

# vim:set sw=2 sts=-1 et:
