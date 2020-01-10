%global soversion_major 1
%global soversion 1.0.41
%global _hardened_build 1

Summary: Library to control and monitor control groups
Name: libcgroup
Version: 0.41
Release: 15%{?dist}
License: LGPLv2+
Group: Development/Libraries
URL: http://libcg.sourceforge.net/
Source0: http://downloads.sourceforge.net/libcg/%{name}-%{version}.tar.bz2
Source1: cgconfig.service
Source2: cgred.service
Source3: cgred.sysconfig

Patch0: fedora-config.patch
Patch1: libcgroup-0.37-chmod.patch
Patch2: libcgroup-0.40.rc1-coverity.patch
Patch3: libcgroup-0.40.rc1-fread.patch
Patch4: libcgroup-0.40.rc1-templates-fix.patch
Patch5: libcgroup-0.41-runlibcgrouptest-systemd-fix.patch 
Patch6: libcgroup-0.40.rc1-retry-to-set-control-file.patch
Patch7: libcgroup-0.41-config.c-xfs-file-system-sets-item-d_type-to-zero-st.patch
Patch8: libcgroup-0.41-loading-configuration-files-from-etc-cgconfig.d-dire.patch
Patch9: libcgroup-0.41-use-character-as-a-meta-character-for-all-mounted-co.patch
Patch10: libcgroup-0.41-add-examples-to-man-pages.patch
Patch11: libcgroup-0.41-extending-cgroup-names-with-default.patch
Patch12: libcgroup-0.41-api.c-support-for-setting-multiline-values-in-contro.patch

# resolves #1348864
Patch13: libcgroup-0.41-api.c-fix-order-of-memory-subsystem-parameters.patch
# resolves #1347765
Patch14: libcgroup-0.41-api.c-fix-potential-buffer-overflow.patch
# resolves #1406927
Patch15: libcgroup-0.41-api.c-fix-log-level.patch
# resolves #1384390
Patch16: libcgroup-0.41-api.c-preserve-dirty-flag.patch
# resolves #1505443
Patch17: libcgroup-0.41-infinite-loop.patch

BuildRequires: byacc, coreutils, flex, pam-devel, systemd
Requires(pre): shadow-utils
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd

%description
Control groups infrastructure. The library helps manipulate, control,
administrate and monitor control groups and the associated controllers.

%package tools
Summary: Command-line utility programs, services and daemons for libcgroup
Group: System Environment/Base
Requires: %{name}%{?_isa} = %{version}-%{release}
# needed for Delegate property in cgconfig.service
Requires: systemd >= 217-0.2

%description tools
This package contains command-line programs, services and a daemon for
manipulating control groups using the libcgroup library.

%package pam
Summary: A Pluggable Authentication Module for libcgroup
Group: System Environment/Base
Requires: %{name}%{?_isa} = %{version}-%{release}

%description pam
Linux-PAM module, which allows administrators to classify the user's login
processes to pre-configured control group.

%package devel
Summary: Development libraries to develop applications that utilize control groups
Group: Development/Libraries
Requires: %{name}%{?_isa} = %{version}-%{release}

%description devel
It provides API to create/delete and modify cgroup nodes. It will also in the
future allow creation of persistent configuration for control groups and
provide scripts to manage that configuration.

%prep
%setup  -q  -n %{name}-%{version}
%patch0 -p1 -b .config-patch
%patch1 -p1 -b .chmod
%patch2 -p1 -b .coverity
%patch3 -p1 -b .fread
%patch4 -p1 -b .templates-fix
%patch5 -p1 -b .runlibcgrouptest-systemd-fix
%patch6 -p1
%patch7 -p1
%patch8 -p1
%patch9 -p1
%patch10 -p1
%patch11 -p1
%patch12 -p1
%patch13 -p1
%patch14 -p1
%patch15 -p1
%patch16 -p1
%patch17 -p1

%build
%configure --enable-pam-module-dir=%{_libdir}/security \
           --enable-opaque-hierarchy="name=systemd"
#           --disable-daemon
make %{?_smp_mflags}

%install
make DESTDIR=$RPM_BUILD_ROOT install

# install config files
install -d ${RPM_BUILD_ROOT}%{_sysconfdir}
install -m 644 samples/cgconfig.conf $RPM_BUILD_ROOT/%{_sysconfdir}/cgconfig.conf
install -d $RPM_BUILD_ROOT/%{_sysconfdir}/cgconfig.d
install -m 644 samples/cgrules.conf $RPM_BUILD_ROOT/%{_sysconfdir}/cgrules.conf
install -m 644 samples/cgsnapshot_blacklist.conf $RPM_BUILD_ROOT/%{_sysconfdir}/cgsnapshot_blacklist.conf

# sanitize pam module, we need only pam_cgroup.so
mv -f $RPM_BUILD_ROOT%{_libdir}/security/pam_cgroup.so.*.*.* $RPM_BUILD_ROOT%{_libdir}/security/pam_cgroup.so
rm -f $RPM_BUILD_ROOT%{_libdir}/security/pam_cgroup.la $RPM_BUILD_ROOT/%{_libdir}/security/pam_cgroup.so.*

rm -f $RPM_BUILD_ROOT/%{_libdir}/*.la

# install unit and sysconfig files
install -d ${RPM_BUILD_ROOT}%{_unitdir}
install -m 644 %SOURCE1 ${RPM_BUILD_ROOT}%{_unitdir}/
install -m 644 %SOURCE2 ${RPM_BUILD_ROOT}%{_unitdir}/
install -d ${RPM_BUILD_ROOT}%{_sysconfdir}/sysconfig
install -m 644 %SOURCE3 ${RPM_BUILD_ROOT}%{_sysconfdir}/sysconfig/cgred

%pre
getent group cgred >/dev/null || groupadd -r cgred

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%pre tools
getent group cgred >/dev/null || groupadd -r cgred

%post tools
if [ $1 -eq 1 ] ; then 
    # Initial installation 
    /bin/systemctl daemon-reload >/dev/null 2>&1 || :
fi
%systemd_post cgconfig.service cgred.service

%preun tools
if [ $1 -eq 0 ] ; then
    # Package removal, not upgrade
    /bin/systemctl --no-reload disable cgconfig.service > /dev/null 2>&1 || :
    /bin/systemctl stop cgconfig.service > /dev/null 2>&1 || :
    /bin/systemctl --no-reload disable cgred.service > /dev/null 2>&1 || :
    /bin/systemctl stop cgred.service > /dev/null 2>&1 || :
fi
%systemd_preun cgconfig.service cgred.service

%postun tools
/bin/systemctl daemon-reload >/dev/null 2>&1 || :
if [ $1 -ge 1 ] ; then
    # Package upgrade, not uninstall
    /bin/systemctl try-restart cgconfig.service >/dev/null 2>&1 || :
    /bin/systemctl try-restart cgred.service >/dev/null 2>&1 || :
fi
%systemd_postun_with_restart cgconfig.service cgred.service

%triggerun -- libcgroup < 0.38
# Save the current service runlevel info
# User must manually run systemd-sysv-convert --apply cgconfig/cgred
# to migrate them to systemd targets
/usr/bin/systemd-sysv-convert --save cgconfig >/dev/null 2>&1 ||:
/usr/bin/systemd-sysv-convert --save cgred >/dev/null 2>&1 ||:

# Run these because the SysV package being removed won't do them
/sbin/chkconfig --del cgconfig >/dev/null 2>&1 || :
/bin/systemctl try-restart cgconfig.service >/dev/null 2>&1 || :
/sbin/chkconfig --del cgred >/dev/null 2>&1 || :
/bin/systemctl try-restart cgred.service >/dev/null 2>&1 || :

%files
%doc COPYING README
%{_libdir}/libcgroup.so.*

%files tools
%doc COPYING README README_systemd
%config(noreplace) %verify(not md5 size mtime) %{_sysconfdir}/cgconfig.conf
%config(noreplace) %verify(not md5 size mtime) %{_sysconfdir}/cgconfig.d
%config(noreplace) %verify(not md5 size mtime) %{_sysconfdir}/cgrules.conf
%config(noreplace) %verify(not md5 size mtime) %{_sysconfdir}/cgsnapshot_blacklist.conf
%config(noreplace) %verify(not md5 size mtime) %{_sysconfdir}/sysconfig/cgred
/usr/bin/cgcreate
/usr/bin/cgget
/usr/bin/cgset
/usr/bin/cgdelete
/usr/bin/lscgroup
/usr/bin/lssubsys
/usr/sbin/cgconfigparser
/usr/sbin/cgrulesengd
/usr/sbin/cgclear
/usr/bin/cgsnapshot
%attr(2755, root, cgred) /usr/bin/cgexec
%attr(2755, root, cgred) /usr/bin/cgclassify
%attr(0644, root, root) %{_mandir}/man1/*
%attr(0644, root, root) %{_mandir}/man5/*
%attr(0644, root, root) %{_mandir}/man8/*
%{_unitdir}/cgconfig.service
%{_unitdir}/cgred.service

%files pam
%doc COPYING README
%attr(0755,root,root) %{_libdir}/security/pam_cgroup.so

%files devel
%doc COPYING README
%{_includedir}/libcgroup.h
%{_includedir}/libcgroup/*.h
%{_libdir}/libcgroup.so
%{_libdir}/pkgconfig/libcgroup.pc

%changelog
* Tue Oct 24 2017 Nikola Forró <nforro@redhat.com> - 0.41-15
- resolves: #1464015
  do not verify size, mtime and checksum of config files

* Tue Oct 24 2017 Nikola Forró <nforro@redhat.com> - 0.41-14
- resolves: #1505443
  fix infinite loop

* Thu Mar 16 2017 Nikola Forró <nforro@redhat.com> - 0.41-13
- resolves: #1384390
  preserve dirty flag when copying controller values

* Tue Jan 24 2017 Nikola Forró <nforro@redhat.com> - 0.41-12
- resolves: #1406927
  start cgred service after nss-user-lookup target
  show warnings about unsuccessful user/group lookups

* Thu Jun 23 2016 Nikola Forró <nforro@redhat.com> - 0.41-11
- resolves: #1347765
  fix potential buffer overflow

* Thu Jun 23 2016 Nikola Forró <nforro@redhat.com> - 0.41-10
- resolves: #1348864
  fix order of memory subsystem parameters generated by cgsnapshot

* Wed Apr 06 2016 Nikola Forró <nforro@redhat.com> - 0.41-9
- resolves: #1322571
  set Delegate property for cgconfig service

* Sat Sep 20 2014 jchaloup <jchaloup@redhat.com> - 0.41-8
- resolves: #885174
  loading configuration files from /etc/cgconfig.d/ directory
- resolves: #885166
  use * character as a meta character for all mounted
- resolves: #886920
  add examples to man pages
- resolves: #1143851
  extending cgroup names with default
- resolves: #1142807
  api.c: support for setting multiline values in control files
  config.c: xfs file system sets item->d_type to zero, stat() and S_ISREG() test added (#885174)

* Thu Sep 11 2014 jchaloup <jchaloup@redhat.com> - 0.41-7
- resolves: #963515
  retry to set control file in cgroup_modify_cgroup

* Tue Mar 04 2014 jchaloup <jchaloup@redhat.com> - 0.41-6
- related: #1016810
  specfile corrected, make was not fired

* Tue Feb 25 2014 jchaloup <jchaloup@redhat.com> - 0.41-5
- related: #1016810
  missing man pages for cgrulesengd, cgred.conf, cgrule.conf added

* Mon Feb 24 2014 jchaloup <jchaloup@redhat.com> - 0.41-4
- related: #1016810
  cgrulesengd returned

* Fri Feb 14 2014 jchaloup <jchaloup@redhat.com> - 0.41-3
- related: #1052471
  runlibcgrouptest fix, ignore systemd mount

* Fri Jan 24 2014 Daniel Mach <dmach@redhat.com> - 0.41-2
- Mass rebuild 2014-01-24

* Tue Jan 14 2014 Peter Schiffer <pschiffe@redhat.com> 0.41-1
- resolves: #1052471
  updated to 0.41

* Fri Dec 27 2013 Daniel Mach <dmach@redhat.com> - 0.40-1.rc1.3
- Mass rebuild 2013-12-27

* Mon Nov  4 2013 Peter Schiffer <pschiffe@redhat.com> 0.40-0.rc1.3
- related: #819568
  fixed some coverity findings

* Fri Nov  1 2013 Peter Schiffer <pschiffe@redhat.com> 0.40-0.rc1.2
- related: #1016810
  returned creation of cgred group, which was removed in previous commit by mistage

* Fri Nov  1 2013 Peter Schiffer <pschiffe@redhat.com> 0.40-0.rc1.1
- resolves: #819568, #740113
  rebased to 0.40.rc1
- resolves: #983264
  rebuilt with full relro and PIE
- resolves: #1016810
  removed cgrulesengd daemon

* Fri Nov 23 2012 Peter Schiffer <pschiffe@redhat.com> - 0.38-3
- resolves: #850183
  scriptlets replaced with new systemd macros (thanks to vpavlin)
- cleaned .spec file

* Thu Jul 19 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.38-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Mon Feb 20 2012 Jan Safranek <jsafrane@redhat.com> 0.38-1
- updated to 0.38

* Fri Feb  3 2012 Jan Safranek <jsafrane@redhat.com> 0.38-0.rc1
- updated to 0.38.rc1

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.37.1-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Mon May 30 2011 Jan Safranek <jsafrane@redhat.com> 0.37.1-4
- fixed cgconfig service not to unmount stuff it did not mount
- added better sample cgconfig.conf file to reflect systemd
  mounting all controllers during boot (#702111)

* Wed May 25 2011 Ivana Hutarova Varekova <varekova@redhat.com> 0.37.1-3
- split tools part from libcgroup package

* Fri Apr  8 2011 Jan Safranek <jsafrane@redhat.com> 0.37.1-2
- Remove /cgroup directory, groups are created in /sys/fs/cgroup
  (#694687)

* Thu Mar  3 2011 Jan Safranek <jsafrane@redhat.com> 0.37.1-1
- Update to 0.37.1

* Mon Feb 07 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.37-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Mon Jan 17 2011 Jan Safranek <jsafrane@redhat.com> 0.37-2
- Create the 'cgred' group as system group, not as user
- Fix cgclassify exit code

* Mon Dec 13 2010 Jan Safranek <jsafrane@redhat.com> 0.37-1
- Update to 0.37
- use /sys/fs/cgroup as default directory to mount control groups (and rely on
  systemd mounting tmpfs there)

* Fri Nov 12 2010 Jan Safranek <jsafrane@redhat.com> 0.36.2-3
- Ignore systemd hierarchy - it's now invisible to libcgroup (#627378)

* Mon Aug  2 2010 Jan Safranek <jsafrane@redhat.com> 0.36.2-2
- Fix initscripts to report stopped cgconfig service as not running
  (#619091)

* Tue Jun 22 2010 Jan Safranek <jsafrane@redhat.com> 0.36.2-1
- Update to 0.36.2, fixing packaging the libraries (#605434)
- Remove the dependency on redhat-lsb (#603578)

* Fri May 21 2010 Jan Safranek <jsafrane@redhat.com> 0.36-1
- Update to 0.36.1

* Tue Mar  9 2010 Jan Safranek <jsafrane@redhat.com> 0.35-1
- Update to 0.35.1
- Separate pam module to its own subpackage

* Mon Jan 18 2010 Jan Safranek <jsafrane@redhat.com> 0.34-4
- Added README.Fedora to describe initscript integration

* Mon Oct 19 2009 Jan Safranek <jsafrane@redhat.com> 0.34-3
- Change the default configuration to mount everything to /cgroup

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.34-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Tue Jul  7 2009 Jan Safranek <jsafrane@redhat.com> 0.34-1
- Update to 0.34
* Mon Mar 09 2009 Dhaval Giani <dhaval@linux.vnet.ibm.com> 0.33-3
- Add a workaround for rt cgroup controller.
* Mon Mar 09 2009 Dhaval Giani <dhaval@linux.vnet.ibm.com> 0.33-2
- Change the cgconfig script to start earlier
- Move the binaries to /bin and /sbin
* Mon Mar 02 2009 Dhaval Giani <dhaval@linux.vnet.ibm.com> 0.33-1
- Update to latest upstream
* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> 0.32.2-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Mon Jan 05 2009 Dhaval Giani <dhaval@linux.vnet.ibm.com> 0.32.2-3
- Fix redhat-lsb dependency
* Mon Dec 29 2008 Dhaval Giani <dhaval@linux.vnet.ibm.com> 0.32.2-2
- Fix build dependencies
* Mon Dec 29 2008 Dhaval Giani <dhaval@linux.vnet.ibm.com> 0.32.2-1
- Update to latest upstream
* Thu Oct 23 2008 Dhaval Giani <dhaval@linux.vnet.ibm.com> 0.32.1-1
* Tue Feb 24 2009 Balbir Singh <balbir@linux.vnet.ibm.com> 0.33-1
- Update to 0.33, spec file changes to add Makefiles and pam_cgroup module
* Fri Oct 10 2008 Dhaval Giani <dhaval@linux.vnet.ibm.com> 0.32-1
- Update to latest upstream
* Thu Sep 11 2008 Dhaval Giani <dhaval@linux-vnet.ibm.com> 0.31-1
- Update to latest upstream
* Sat Aug 2 2008 Dhaval Giani <dhaval@linux.vnet.ibm.com> 0.1c-3
- Change release to fix broken upgrade path
* Wed Jun 11 2008 Dhaval Giani <dhaval@linux.vnet.ibm.com> 0.1c-1
- Update to latest upstream version
* Tue Jun 3 2008 Balbir Singh <balbir@linux.vnet.ibm.com> 0.1b-3
- Add post and postun. Also fix Requires for devel to depend on base n-v-r
* Sat May 31 2008 Balbir Singh <balbir@linux.vnet.ibm.com> 0.1b-2
- Fix makeinstall, Source0 and URL (review comments from Tom)
* Mon May 26 2008 Balbir Singh <balbir@linux.vnet.ibm.com> 0.1b-1
- Add a generatable spec file
* Tue May 20 2008 Balbir Singh <balbir@linux.vnet.ibm.com> 0.1-1
- Get the spec file to work
* Tue May 20 2008 Dhaval Giani <dhaval@linux.vnet.ibm.com> 0.01-1
- The first version of libcg
