%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

%if 0%{?fedora} >= 23 || 0%{?rhel} >= 7
%global use_systemd 1
%else
%global use_systemd 0
%global install_opt TYPE=sysv
%endif

Name: koji
Version: 1.11.0
Release: 5%{?dist}.lr1
# koji.ssl libs (from plague) are GPLv2+
License: LGPLv2 and GPLv2+
Summary: Build system tools
Group: Applications/System
URL: https://pagure.io/koji/
Source0: https://releases.pagure.org/koji/koji-%{version}.tar.bz2
# https://pagure.io/koji/pull-request/246
Patch1: koji-pr246-kojigc-krb_rds-support.patch
# https://pagure.io/koji/pull-request/248
Patch2: koji-pr248-kojigc-keytab-support.patch
# https://pagure.io/koji/pull-request/243
Patch3: koji-pr243-CheckClientIP-and-TrustForwardedIP.patch
# https://pagure.io/koji/pull-request/239
Patch4: koji-pr239-principal-keytab-cli-config.patch
# Not upstreamable
Patch100: fedora-config.patch

Patch666: 0001-SSLConnection-ignore-errors-from-shutdown.patch

BuildArch: noarch
Requires: python-krbV >= 1.0.13
Requires: rpm-python
Requires: pyOpenSSL
Requires: python-requests
Requires: python-requests-kerberos
Requires: python-urlgrabber
Requires: python-dateutil
BuildRequires: python
BuildRequires: python-sphinx
%if %{use_systemd}
BuildRequires: systemd
BuildRequires: pkgconfig
%endif
%if 0%{?fedora} || 0%{?rhel} >= 7
Requires: python-libcomps
%endif

%description
Koji is a system for building and tracking RPMS.  The base package
contains shared libraries and the command-line interface.

%package hub
Summary: Koji XMLRPC interface
Group: Applications/Internet
License: LGPLv2 and GPLv2
# rpmdiff lib (from rpmlint) is GPLv2 (only)
Requires: httpd
Requires: mod_wsgi
Requires: postgresql-python
%if 0%{?rhel} == 5
Requires: python-simplejson
%endif
Requires: %{name} = %{version}-%{release}

%description hub
koji-hub is the XMLRPC interface to the koji database

%package hub-plugins
Summary: Koji hub plugins
Group: Applications/Internet
License: LGPLv2
Requires: %{name} = %{version}-%{release}
Requires: %{name}-hub = %{version}-%{release}
Requires: python-qpid >= 0.7
%if 0%{?rhel} >= 6
Requires: python-qpid-proton
%endif
%if 0%{?rhel} == 5
Requires: python-ssl
%endif
Requires: cpio

%description hub-plugins
Plugins to the koji XMLRPC interface

%package builder
Summary: Koji RPM builder daemon
Group: Applications/System
License: LGPLv2 and GPLv2+
#mergerepos (from createrepo) is GPLv2+
Requires: %{name} = %{version}-%{release}
Requires: mock >= 0.9.14
Requires(pre): /usr/sbin/useradd
Requires: squashfs-tools
%if %{use_systemd}
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd
%else
Requires(post): /sbin/chkconfig
Requires(post): /sbin/service
Requires(preun): /sbin/chkconfig
Requires(preun): /sbin/service
%endif
Requires: /usr/bin/cvs
Requires: /usr/bin/svn
Requires: /usr/bin/git
Requires: python-cheetah
%if 0%{?rhel} == 5
Requires: createrepo >= 0.4.11-2
Requires: python-hashlib
Requires: python-createrepo
%endif
%if 0%{?fedora} >= 9 || 0%{?rhel} > 5
Requires: createrepo >= 0.9.2
%endif

%description builder
koji-builder is the daemon that runs on build machines and executes
tasks that come through the Koji system.

%package vm
Summary: Koji virtual machine management daemon
Group: Applications/System
License: LGPLv2
Requires: %{name} = %{version}-%{release}
%if %{use_systemd}
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd
%else
Requires(post): /sbin/chkconfig
Requires(post): /sbin/service
Requires(preun): /sbin/chkconfig
Requires(preun): /sbin/service
%endif
Requires: libvirt-python
Requires: libxml2-python
Requires: /usr/bin/virt-clone
Requires: qemu-img

%description vm
koji-vm contains a supplemental build daemon that executes certain tasks in a
virtual machine. This package is not required for most installations.

%package utils
Summary: Koji Utilities
Group: Applications/Internet
License: LGPLv2
Requires: postgresql-python
Requires: %{name} = %{version}-%{release}
%if %{use_systemd}
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd
%endif

%description utils
Utilities for the Koji system

%package web
Summary: Koji Web UI
Group: Applications/Internet
License: LGPLv2
Requires: httpd
Requires: mod_wsgi
Requires: mod_auth_kerb
Requires: postgresql-python
Requires: python-cheetah
Requires: %{name} = %{version}-%{release}
Requires: python-krbV >= 1.0.13

%description web
koji-web is a web UI to the Koji system.

%prep
%setup -q
%patch1 -p1 -b .246
%patch2 -p1 -b .248
# This seems to break the koji hub currently, thefore do not apply it
#patch3 -p1 -b .243
%patch4 -p1 -b .239
%patch100 -p1 -b .fedoraconfig
%patch666 -p1

%build

%install
rm -rf $RPM_BUILD_ROOT
make DESTDIR=$RPM_BUILD_ROOT %{?install_opt} install

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
%{_bindir}/*
%{python_sitelib}/%{name}
%config(noreplace) %{_sysconfdir}/koji.conf
%dir %{_sysconfdir}/koji.conf.d
%doc docs Authors COPYING LGPL

%files hub
%defattr(-,root,root)
%{_datadir}/koji-hub
%dir %{_libexecdir}/koji-hub
%{_libexecdir}/koji-hub/rpmdiff
%config(noreplace) %{_sysconfdir}/httpd/conf.d/kojihub.conf
%dir %{_sysconfdir}/koji-hub
%config(noreplace) %{_sysconfdir}/koji-hub/hub.conf
%dir %{_sysconfdir}/koji-hub/hub.conf.d

%files hub-plugins
%defattr(-,root,root)
%dir %{_prefix}/lib/koji-hub-plugins
%{_prefix}/lib/koji-hub-plugins/*.py*
%dir %{_sysconfdir}/koji-hub/plugins
%{_sysconfdir}/koji-hub/plugins/*.conf

%files utils
%defattr(-,root,root)
%{_sbindir}/kojira
%if %{use_systemd}
%{_unitdir}/kojira.service
%else
%{_initrddir}/kojira
%config(noreplace) %{_sysconfdir}/sysconfig/kojira
%endif
%dir %{_sysconfdir}/kojira
%config(noreplace) %{_sysconfdir}/kojira/kojira.conf
%{_sbindir}/koji-gc
%dir %{_sysconfdir}/koji-gc
%config(noreplace) %{_sysconfdir}/koji-gc/koji-gc.conf
%{_sbindir}/koji-shadow
%dir %{_sysconfdir}/koji-shadow
%config(noreplace) %{_sysconfdir}/koji-shadow/koji-shadow.conf

%files web
%defattr(-,root,root)
%{_datadir}/koji-web
%dir %{_sysconfdir}/kojiweb
%config(noreplace) %{_sysconfdir}/kojiweb/web.conf
%config(noreplace) %{_sysconfdir}/httpd/conf.d/kojiweb.conf
%dir %{_sysconfdir}/kojiweb/web.conf.d

%files builder
%defattr(-,root,root)
%{_sbindir}/kojid
%dir %{_libexecdir}/kojid
%{_libexecdir}/kojid/mergerepos
%defattr(-,root,root)
%dir %{_prefix}/lib/koji-builder-plugins
%{_prefix}/lib/koji-builder-plugins/*.py*
%if %{use_systemd}
%{_unitdir}/kojid.service
%else
%{_initrddir}/kojid
%config(noreplace) %{_sysconfdir}/sysconfig/kojid
%endif
%dir %{_sysconfdir}/kojid
%dir %{_sysconfdir}/kojid/plugins
%config(noreplace) %{_sysconfdir}/kojid/kojid.conf
%config(noreplace) %{_sysconfdir}/kojid/plugins/runroot.conf
%attr(-,kojibuilder,kojibuilder) %{_sysconfdir}/mock/koji

%pre builder
/usr/sbin/useradd -r -s /bin/bash -G mock -d /builddir -M kojibuilder 2>/dev/null ||:

%if %{use_systemd}

%post builder
%systemd_post kojid.service

%preun builder
%systemd_preun kojid.service

%postun builder
%systemd_postun kojid.service

%else

%post builder
/sbin/chkconfig --add kojid

%preun builder
if [ $1 = 0 ]; then
  /sbin/service kojid stop &> /dev/null
  /sbin/chkconfig --del kojid
fi
%endif

%files vm
%defattr(-,root,root)
%{_sbindir}/kojivmd
#dir %{_datadir}/kojivmd
%{_datadir}/kojivmd/kojikamid
%if %{use_systemd}
%{_unitdir}/kojivmd.service
%else
%{_initrddir}/kojivmd
%config(noreplace) %{_sysconfdir}/sysconfig/kojivmd
%endif
%dir %{_sysconfdir}/kojivmd
%config(noreplace) %{_sysconfdir}/kojivmd/kojivmd.conf

%if %{use_systemd}

%post vm
%systemd_post kojivmd.service

%preun vm
%systemd_preun kojivmd.service

%postun vm
%systemd_postun kojivmd.service

%else

%post vm
/sbin/chkconfig --add kojivmd

%preun vm
if [ $1 = 0 ]; then
  /sbin/service kojivmd stop &> /dev/null
  /sbin/chkconfig --del kojivmd
fi
%endif

%if %{use_systemd}

%post utils
%systemd_post kojira.service

%preun utils
%systemd_preun kojira.service

%postun utils
%systemd_postun kojira.service

%else
%post utils
/sbin/chkconfig --add kojira
/sbin/service kojira condrestart &> /dev/null || :
%preun utils
if [ $1 = 0 ]; then
  /sbin/service kojira stop &> /dev/null || :
  /sbin/chkconfig --del kojira
fi
%endif

%changelog
* Sun Jan 08 2017 Till Maas <opensource@till.name> - 1.11.0-5
- Do not apply faulty CheckClientIP patch

* Sun Jan 08 2017 Till Maas <opensource@till.name> - 1.11.0-4
- Add patch for keytab kerberos client config
- Move non upstreamable Fedora patch to the end to ease rebasing to future
  upstream release
- Move license comment before license tag

* Sat Jan 07 2017 Till Maas <opensource@till.name> - 1.11.0-3
- Add patches for proxy IP forwarding

* Fri Jan 06 2017 Till Maas <opensource@till.name> - 1.11.0-2
- Update upstream URLs
- Add upstream koji-gc kerberos patches
- Use Source0

* Fri Dec 09 2016 Dennis Gilmore <dennis@ausil.us> - 1.11.0-1
- update to 1.11.0
- setup fedora config for kerberos and flag day

* Wed Sep 28 2016 Adam Miller <maxamillion@fedoraproject.org> - 1.10.1-13
- Patch new-chroot functionality into runroot plugin

* Tue Aug 23 2016 Dennis Gilmore <dennis@ausil.us> - 1.10.1-12
- add patch to disable bind mounting into image tasks chroots

* Tue Jul 19 2016 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.10.1-11
- https://fedoraproject.org/wiki/Changes/Automatic_Provides_for_Python_RPM_Packages

* Thu May 26 2016 Dennis Gilmore <dennis@ausil.us> - 1.10.1-10
- add patch to enable dns in runroot chroots

* Tue May 24 2016 Dennis Gilmore <dennis@ausil.us> - 1.10.1-9
- update to git master upstream, add lmc cosmetic fixes
- add patch to disable login in koji-web

* Fri Apr 08 2016 Dennis Gilmore <dennis@ausil.us> - 1.10.1-8
- do not remove the - for project on livemedia
- fix the sending of messages on image completion

* Thu Apr 07 2016 Dennis Gilmore <dennis@ausil.us> - 1.10.1-7
- --product had to be --project
- add missing Requires for koji-builder on python2-multilib

* Wed Apr 06 2016 Dennis Gilmore <dennis@ausil.us> - 1.10.1-6
- add --product to livemedia-creator calls rhbz#1315110

* Wed Apr 06 2016 Dennis Gilmore <dennis@ausil.us> - 1.10.1-5
- enable dns in runroots
- add koji signed repo support
- Run plugin callbacks when image builds finish

* Thu Mar 03 2016 Dennis Gilmore <dennis@ausil.us> - 1.10.1-4
- add a patch to install the runroot builder plugin in the correct place

* Tue Mar 01 2016 Dennis Gilmore <dennis@ausil.us> - 1.10.1-3
- update to git e8201aac8294e6125a73504886b0800041b58868
- https://pagure.io/fork/ausil/koji/branch/fedora-infra

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 1.10.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Tue Nov 17 2015 Dennis Gilmore <dennis@ausil.us> - 1.10.1-1
- update to 1.10.1
- Requires yum in the cli rhbz#1230888

* Thu Sep 24 2015 Kalev Lember <klember@redhat.com> - 1.10.0-2
- Backport two patches to fix ClientSession SSL errors

* Thu Jul 16 2015 Dennis Gilmore <dennis@ausil.us> - 1.10.0=1
- update to 1.10.0 release

* Mon Jul 06 2015 Dennis Gilmore <dennis@ausil.us> - 1.9.0-13.20150607gitf426fdb
- update the git snapshot to latest head
- enable systemd units for f23 up

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.9.0-12.20150423git52a0188
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Thu Apr 23 2015 Dennis Gilmore <dennis@ausil.us> - 1.9.0-11.20150423git52a0188
- update to latest git

* Tue Jan 27 2015 Dennis Gilmore <dennis@ausil.us> - 1.9.0-10.gitcd45e886
- update to git tarball

* Thu Dec 11 2014 Dennis Gilmore <dennis@ausil.us> - 1.9.0-9
- add upstream patch switching to TLS1 from sslv3

* Tue Sep 30 2014 Dennis Gilmore <dennis@ausil.us> - 1.9.0-8
- don't exclude koji-vm from ppc and ppc64

* Fri Sep 26 2014 Till Maas <opensource@till.name> - 1.9.0-7
- Use https for kojipkgs
- Update URL

* Mon Aug 04 2014 Dennis Gilmore <dennis@ausil.us> - 1.9.0-6
- add patch to fix kickstart parsing

* Mon Aug 04 2014 Dennis Gilmore <dennis@ausil.us> - 1.9.0-5
- add upstream patches for better docker support

* Tue Jul 29 2014 Dennis Gilmore <dennis@ausil.us> - 1.9.0-4
- add upstream patch to compress docker images

* Thu Jun 12 2014 Dennis Gilmore <dennis@ausil.us> - 1.9.0-3
- add patch to move builder workdir to /var/tmp
- add support for making raw.xz images

* Sun Jun 08 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.9.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Mon Mar 24 2014 Dennis Gilmore <dennis@ausil.us> - 1.9.0-1
- update to upstream 1.9.0

* Wed Jul 31 2013 Dennis Gilmore <dennis@ausil.us> - 1.8.0-2
- update from git snapshot

* Mon Apr 01 2013 Dennis Gilmore <dennis@ausil.us> - 1.8.0-1
- update to upstream 1.8.0

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.7.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Sun Jan 20 2013 Dennis Gilmore <dennis@ausil.us> - 1.7.1-2
- revert "avoid baseurl option in createrepo" patch
- fix integer overflow issue in checkUpload handler

* Wed Nov 21 2012 Dennis Gilmore <dennis@ausil.us> - 1.7.1-1
- update to upstream 1.7.1 release

* Sat Sep 01 2012 Dennis Gilmore <dennis@ausil.us> - 1.7.0-7
- add patch to mount all of /dev on appliances and lives

* Fri Aug 31 2012 Dennis Gilmore <dennis@ausil.us> - 1.7.0-4
- add patch to only make /dev/urandom if it doesnt exist
- add upstream patch for taginfo fixes with older servers

* Thu Jul 19 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.7.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Tue Jun 05 2012 Dennis Gilmore <dennis@ausil.us> - 1.7.0-2
- use topurl not pkgurl in the fedora config

* Fri Jun 01 2012 Dennis Gilmore <dennis@ausil.us> - 1.7.0-1
- update to 1.7.0 many bugfixes and improvements
- now uses mod_wsgi

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.6.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Mon Feb 07 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.6.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Fri Dec 17 2010 Dennis Gilmore <dennis@ausil.us> - 1.6.0-1
- update to 1.6.0

* Wed Dec 01 2010 Dennis Gilmore <dennis@ausil.us> - 1.5.0-1
- update to 1.5.0

* Tue Aug  3 2010 David Malcolm <dmalcolm@redhat.com> - 1.4.0-4
- fix python 2.7 incompatibilities (rhbz 619276)

* Wed Jul 21 2010 David Malcolm <dmalcolm@redhat.com> - 1.4.0-3
- Rebuilt for https://fedoraproject.org/wiki/Features/Python_2.7/MassRebuild

* Sat Jul 10 2010 Dennis Gilmore <dennis@ausil.us> - 1.4.0-2
- add missing Requires: python-cheetah from koji-builder

* Fri Jul 09 2010 Dennis Gilmore <dennis@ausil.us> - 1.4.0-1
- update to 1.4.0
- Merge mead branch: support for building jars with Maven *
- support for building appliance images *
- soft dependencies for LiveCD/Appliance features
- smarter prioritization of repo regenerations
- package list policy to determine if package list changes are allowed
- channel policy to determine which channel a task is placed in
- edit host data via webui
- description and comment fields for hosts *
- cleaner log entries for kojihub
- track user data in versioned tables *
- allow setting retry parameters for the cli
- track start time for tasks *
- allow packages built from the same srpm to span multiple external repos
- make the command used to fetch sources configuable per repo
- kojira: remove unexpected directories
- let kojid to decide if it can handle a noarch task
- avoid extraneous ssl handshakes
- schema changes to support starred items

* Fri Nov 20 2009 Dennis Gilmore <dennis@ausil.us> - 1.3.2-1
- update to 1.3.2

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.3.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.3.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Fri Feb 20 2009 Dennis Gilmore <dennis@ausil.us> - 1.3.1-1
- update to 1.3.1

* Wed Feb 18 2009 Dennis Gilmore <dennis@ausil.us> - 1.3.0-1
- update to 1.3.0

* Sat Nov 29 2008 Ignacio Vazquez-Abrams <ivazqueznet+rpm@gmail.com> - 1.2.6-2
- Rebuild for Python 2.6

* Mon Aug 25 2008 Dennis Gilmore <dennis@ausil.us> - 1.2.6-1
- update to 1.2.6
- make sure we have to correct version of createrepo on Fedora 8

* Tue Aug  5 2008 Tom "spot" Callaway <tcallawa@redhat.com> 1.2.5-2
- fix conditional (line 5)
- fix license tag

* Fri Jan 25 2008 jkeating <jkeating@redhat.com> 1.2.5-1
- Put createrepo arguments in correct order

* Thu Jan 24 2008 jkeating <jkeating@redhat.com> 1.2.4-1
- Use the --skip-stat flag in createrepo calls.
- canonicalize tag arches before using them (dgilmore)
- fix return value of delete_build
- Revert to getfile urls if the task is not successful in emails
- Pass --target instead of --arch to mock.
- ignore trashcan tag in prune-signed-copies command
- add the "allowed_scms" kojid parameter
- allow filtering builds by the person who built them

* Fri Dec 14 2007 jkeating <jkeating@redhat.com> 1.2.3-1
- New upstream release with lots of updates, bugfixes, and enhancements.

* Tue Jun  5 2007 Mike Bonnet <mikeb@redhat.com> - 1.2.2-1
- only allow admins to perform non-scratch builds from srpm
- bug fixes to the cmd-line and web UIs

* Thu May 31 2007 Mike Bonnet <mikeb@redhat.com> - 1.2.1-1
- don't allow ExclusiveArch to expand the archlist (bz#239359)
- add a summary line stating whether the task succeeded or failed to the end of the "watch-task" output
- add a search box to the header of every page in the web UI
- new koji download-build command (patch provided by Dan Berrange)

* Tue May 15 2007 Mike Bonnet <mikeb@redhat.com> - 1.2.0-1
- change version numbering to a 3-token scheme
- install the koji favicon

* Mon May 14 2007 Mike Bonnet <mikeb@redhat.com> - 1.1-5
- cleanup koji-utils Requires
- fix encoding and formatting in email notifications
- expand archlist based on ExclusiveArch/BuildArchs
- allow import of rpms without srpms
- commit before linking in prepRepo to release db locks
- remove exec bit from kojid logs and uploaded files (patch by Enrico Scholz)

* Tue May  1 2007 Mike Bonnet <mikeb@redhat.com> - 1.1-4
- remove spurious Requires: from the koji-utils package

* Tue May  1 2007 Mike Bonnet <mikeb@redhat.com> - 1.1-3
- fix typo in BuildNotificationTask (patch provided by Michael Schwendt)
- add the --changelog param to the buildinfo command
- always send email notifications to the package builder and package owner
- improvements to the web UI

* Tue Apr 17 2007 Mike Bonnet <mikeb@redhat.com> - 1.1-2
- re-enable use of the --update flag to createrepo

* Mon Apr 09 2007 Jesse Keating <jkeating@redhat.com> 1.1-1
- make the output listPackages() consistent regardless of with_dups
- prevent large batches of repo deletes from holding up regens
- allow sorting the host list by arches

* Mon Apr 02 2007 Jesse Keating <jkeating@redhat.com> 1.0-1
- Release 1.0!

* Wed Mar 28 2007 Mike Bonnet <mikeb@redhat.com> - 0.9.7-4
- set SSL connection timeout to 12 hours

* Wed Mar 28 2007 Mike Bonnet <mikeb@redhat.com> - 0.9.7-3
- avoid SSL renegotiation
- improve log file handling in kojid
- bug fixes in command-line and web UI

* Sun Mar 25 2007 Mike Bonnet <mikeb@redhat.com> - 0.9.7-2
- enable http access to packages in kojid
- add Requires: pyOpenSSL
- building srpms from CVS now works with the Extras CVS structure
- fixes to the chain-build command
- bug fixes in the XML-RPC and web interfaces

* Tue Mar 20 2007 Jesse Keating <jkeating@redhat.com> - 0.9.7-1
- Package up the needed ssl files

* Tue Mar 20 2007 Jesse Keating <jkeating@redhat.com> - 0.9.6-1
- 0.9.6 release, mostly ssl auth stuff
- use named directories for config stuff
- remove -3 requires on creatrepo, don't need that specific anymore

* Tue Feb 20 2007 Jesse Keating <jkeating@redhat.com> - 0.9.5-8
- Add Authors COPYING LGPL to the docs of the main package

* Tue Feb 20 2007 Jesse Keating <jkeating@redhat.com> - 0.9.5-7
- Move web files from /var/www to /usr/share
- Use -p in install calls
- Add rpm-python to requires for koji

* Mon Feb 19 2007 Jesse Keating <jkeating@redhat.com> - 0.9.5-6
- Clean up spec for package review

* Sun Feb 04 2007 Mike McLean <mikem@redhat.com> - 0.9.5-1
- project renamed to koji
