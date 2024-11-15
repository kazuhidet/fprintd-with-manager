# Maintainer: Jan Alexander Steffens (heftig) <heftig@archlinux.org>
# Contributor: Nikolay Rysev <mad.f3ka@gmail.com>

pkgname=fprintd
pkgver=1.94.4
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
b2sums=('99fc9ed566fb3aecf6a2b737ee2d5ce4c7e655f606bb8af18faaa5fe662eda67ea4b547daa61bf8899174c3c0e1c0312d89e1e80467faf54c51934a1e31042f7'
        '119ee0ebc02a3bf62bb6704aa0229a5bb383bc3fcb8b86501cf94551274532cf5578fca2aba2dc17b45f98683f1445f25b4fe3cb756be5fddb46d61f7b95f198')
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
