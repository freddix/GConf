Summary:	GNOME configuration database system
Name:		GConf
Version:	3.2.5
Release:	5
License:	LGPL
Group:		X11/Applications
Source0:	http://ftp.gnome.org/pub/gnome/sources/GConf/3.2/GConf-%{version}.tar.xz
# Source0-md5:	1b803eb4f8576c572d072692cf40c9d8
Patch0:		%{name}-NO_MAJOR_VERSION.patch
Patch1:		%{name}-reload.patch
Patch2:		%{name}-xml-gettext-domain.patch
URL:		http://www.gnome.org/
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	dbus-glib-devel
BuildRequires:	gettext-devel
BuildRequires:	gtk+3-devel
BuildRequires:	gtk-doc
BuildRequires:	intltool
BuildRequires:	libtool
BuildRequires:	libxml2-devel
BuildRequires:	perl-base
BuildRequires:	pkg-config
BuildRequires:	polkit-devel
Requires(post):	GConf
Requires:	%{name}-utils = %{version}-%{release}
Requires:	polkit
Requires:	sgml-common
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_libexecdir	%{_libdir}/%{name}2

%description
GConf is a configuration database system, functionally similar to the
Windows registry but lots better. :-) It's being written for the
GNOME desktop but does not require GNOME; configure should notice if
GNOME is not installed and compile the basic GConf2 library anyway.

%package libs
Summary:	GConf library
Group:		Libraries

%description libs
GConf library.

%package devel
Summary:	GConf includes, etc
Group:		X11/Development/Libraries
Requires:	%{name}-utils = %{version}-%{release}

%description devel
GConf includes etc.

%package utils
Summary:	GConf utilities
Group:		Applications
Requires:	%{name}-libs = %{version}-%{release}

%description utils
GConf utilities.

%package backend-gsettings
Summary:	GConf GSettings backend
Group:		Applications
Requires:	%{name}-libs = %{version}-%{release}
Requires:	glib-gio-gsettings

%description backend-gsettings
GConf GSettings backend.

%package apidocs
Summary:	GConf API documentation
Group:		Documentation
Requires:	gtk-doc-common

%description apidocs
GConf API documentation.

%prep
%setup -q
%patch0 -p1
%patch1 -p1
%patch2 -p1

%build
%{__gtkdocize}
%{__glib_gettextize}
%{__intltoolize}
%{__libtoolize}
%{__aclocal}
%{__autoheader}
%{__autoconf}
%{__automake}
%configure \
	--disable-orbit			\
	--disable-static		\
	--enable-defaults-service	\
	--enable-gtk			\
	--with-html-dir=%{_gtkdocdir}
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sysconfdir}/gconf/{schemas,gconf.xml.system},%{_datadir}/GConf/gsettings}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

rm -rf $RPM_BUILD_ROOT%{_datadir}/locale/{ca@valencia,en@shaw}

%find_lang %{name}2

rm -f $RPM_BUILD_ROOT%{_libdir}/GConf2/lib*.la

%clean
rm -rf $RPM_BUILD_ROOT

%post
umask 022
for GCONF_DIR in %{_sysconfdir}/gconf/gconf.xml.mandatory %{_sysconfdir}/gconf/gconf.xml.defaults ;
    do
    GCONF_TREE=$GCONF_DIR/%gconf-tree.xml
    if [ ! -f "$GCONF_TREE" ]; then
	gconf-merge-tree "$GCONF_DIR"
        chmod 644 "$GCONF_TREE"
        find "$GCONF_DIR" -mindepth 1 -maxdepth 1 -type d -exec rm -rf \{\} \;
        rm -f "$GCONF_DIR/%gconf.xml"
    fi
done

%post	libs -p /sbin/ldconfig
%postun	libs -p /sbin/ldconfig

%post backend-gsettings
%{_bindir}/gio-querymodules %{_libdir}/gio/modules

%postun backend-gsettings
umask 022
%{_bindir}/gio-querymodules %{_libdir}/gio/modules
exit 0

%files -f %{name}2.lang
%defattr(644,root,root,755)
%doc ChangeLog TODO AUTHORS NEWS README

%dir %{_sysconfdir}/gconf
%dir %{_sysconfdir}/gconf/schemas

%attr(755,root,root) %{_libexecdir}/gconfd-2
%attr(755,root,root) %{_libexecdir}/gconf-defaults-mechanism
%{_datadir}/dbus-1/services/org.gnome.GConf.service
%{_datadir}/dbus-1/system-services/org.gnome.GConf.Defaults.service
%{_datadir}/polkit-1/actions/org.gnome.gconf.defaults.policy
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/gconf/path
%{_sysconfdir}/dbus-1/system.d/org.gnome.GConf.Defaults.conf
%{_sysconfdir}/gconf/gconf.xml.*

%attr(755,root,root) %{_libdir}/GConf2/libgconfbackend-oldxml.so
%attr(755,root,root) %{_libdir}/GConf2/libgconfbackend-xml.so

%{_datadir}/sgml/gconf
%{_mandir}/man1/*

%files libs
%defattr(644,root,root,755)
%dir %{_datadir}/GConf
%dir %{_datadir}/GConf/gsettings
%attr(755,root,root) %ghost %{_libdir}/lib*.so.?
%attr(755,root,root) %{_libdir}/lib*.so.*.*.*
%{_libdir}/girepository-1.0/*.typelib

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/gsettings-schema-convert
%attr(755,root,root) %{_libdir}/lib*.so
%{_includedir}/gconf2
%{_aclocaldir}/*.m4
%{_datadir}/gir-1.0/GConf-2.0.gir
%{_pkgconfigdir}/*.pc

%files backend-gsettings
%defattr(644,root,root,755)
%{_sysconfdir}/xdg/autostart/gsettings-data-convert.desktop
%attr(755,root,root) %{_bindir}/gsettings-data-convert
%attr(755,root,root) %{_libdir}/gio/modules/libgsettingsgconfbackend.so

%files utils
%defattr(644,root,root,755)
%dir %{_libexecdir}
%attr(755,root,root) %{_bindir}/gconf*
%attr(755,root,root) %{_libexecdir}/gconf-sanity-check-2

%files apidocs
%defattr(644,root,root,755)
%{_gtkdocdir}/gconf

