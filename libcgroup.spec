%define soversion 1.0.40
%define soversion_major 1

Name: libcgroup
Summary: Tools and libraries to control and monitor control groups
Group: Development/Libraries
Version: 0.40.rc1
Release: 26%{?dist}
License: LGPLv2+
URL: http://libcg.sourceforge.net/
Source0: http://downloads.sourceforge.net/libcg/%{name}-%{version}.tar.bz2
Source1: README.RedHat
Patch0: fedora-config.patch
Patch1: libcgroup-0.36.1-fix-initscripts.patch
Patch2: libcgroup-0.37-pam_cgroup.patch
Patch3: libcgroup-0.37-cgred-empty-config.patch
Patch4: libcgroup-0.37-chmod.patch
Patch5: libcgroup-0.40.rc1-coverity.patch
Patch6: libcgroup-0.40.rc1-restorecon.patch
Patch7: libcgroup-0.40.rc1-change-priority-of-init-scripts.patch
Patch8: libcgroup-0.40.rc1-cast-and-typo.patch
Patch9: libcgroup-0.40.rc1-config-table.patch
Patch10: libcgroup-0.40.rc1-fread.patch
Patch11: libcgroup-0.40.rc1-change-all-cgroups-cache.patch
Patch12: libcgroup-0.40.rc1-templates-fix.patch
Patch13: libcgroup-0.40.rc1-valgrind.patch
Patch14: libcgroup-0.40.rc1-wrapper.patch
Patch15: libcgroup-0.40.rc1-config-init-reload-template.patch
Patch16: libcgroup-0.40.rc1-pam-cache-turned-off.patch
# RFE #1058363
Patch17: libcgroup-0.40.rc1-reading-config-files-from-etc-cgconfig.d.patch
# retry to set control file  #1080281
Patch18: libcgroup-0.40.rc1-retry-to-set-control-file.patch
# support for multiline values #1036355
Patch19: libcgroup-0.40.rc1-support-for-multiline-values.patch

Patch20: libcgroup-0.41-extending-cgroup-names-with-default.patch
Patch21: libcgroup-0.41-infinite-loop.patch
Patch22: libcgroup-0.41-fix-order-of-memory-subsystem-parameters.patch
Patch23: libcgroup-0.41-change-cgroup-of-every-thread.patch
Patch24: libcgroup-0.41-api.c-fix-potential-buffer-overflow.patch
Patch25: libcgroup-0.41-increase-size-of-controller-values.patch

BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires: pam-devel
BuildRequires: byacc
BuildRequires: flex
BuildRequires: coreutils
BuildRequires: libtool
Requires(pre): shadow-utils
Requires(post): chkconfig, /sbin/service
Requires(preun): /sbin/chkconfig

# Dependency on this package is removed by libcgroup-0.36.1-fix-initscripts.patch
# Requires: redhat-lsb-core

%description
Control groups infrastructure. The tools and library help manipulate, control,
administrate and monitor control groups and the associated controllers.

%package pam
Summary: A Pluggable Authentication Module for libcgroup
Group: System Environment/Base
Requires: libcgroup = %{version}-%{release}

%description pam
Linux-PAM module, which allows administrators to classify the user's login
processes to configured control group(s).

%package devel
Summary: Development libraries to develop applications that utilize control groups
Group: Development/Libraries
Requires: libcgroup = %{version}-%{release}

%description devel
It provides API to create/delete and modify control group nodes. It will also in
the future allow creation of persistent configuration for control groups and
provide scripts to manage that configuration.

%prep
%setup -q
%patch0 -p1 -b .config
%patch1 -p1 -b .lsb
%patch2 -p1 -b .flags
%patch3 -p1 -b .empty-config
%patch4 -p1 -b .chmod
%patch5 -p1 -b .coverity
%patch6 -p1 -b .restorecon
%patch7 -p1 -b .change-priority-of-init-scripts
%patch8 -p1 -b .cast-and-typo
%patch9 -p1 -b .config-table
%patch10 -p1 -b .fread
%patch11 -p1 -b .change-all-cache
%patch12 -p1 -b .templates-fix
%patch13 -p1 -b .valgrind
%patch14 -p1 -b .wrapper
%patch15 -p1 -b .config-init-reload-template
%patch16 -p1
%patch17 -p1
%patch18 -p1
%patch19 -p1
%patch20 -p1
%patch21 -p1
%patch22 -p1
%patch23 -p1
%patch24 -p1
%patch25 -p1

%build
%configure --bindir=/bin --sbindir=/sbin --libdir=%{_libdir} --enable-initscript-install --enable-pam-module-dir=/%{_lib}/security
# remove rpath
sed -i 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|g' libtool
sed -i 's|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|g' libtool

make %{?_smp_mflags}


%install
rm -rf $RPM_BUILD_ROOT
make DESTDIR=$RPM_BUILD_ROOT install

# install config files
mkdir -p $RPM_BUILD_ROOT/%{_sysconfdir}/sysconfig
cp samples/cgred.conf $RPM_BUILD_ROOT/%{_sysconfdir}/sysconfig/cgred.conf
cp samples/cgconfig.sysconfig $RPM_BUILD_ROOT/%{_sysconfdir}/sysconfig/cgconfig
cp samples/cgconfig.conf $RPM_BUILD_ROOT/%{_sysconfdir}/cgconfig.conf
mkdir -p $RPM_BUILD_ROOT/%{_sysconfdir}/cgconfig.d
cp samples/cgrules.conf $RPM_BUILD_ROOT/%{_sysconfdir}/cgrules.conf
cp samples/cgsnapshot_blacklist.conf $RPM_BUILD_ROOT/%{_sysconfdir}/cgsnapshot_blacklist.conf

# sanitize pam module, we need only pam_cgroup.so
mv -f $RPM_BUILD_ROOT/%{_lib}/security/pam_cgroup.so.*.*.* $RPM_BUILD_ROOT/%{_lib}/security/pam_cgroup.so
rm -f $RPM_BUILD_ROOT/%{_lib}/security/pam_cgroup.la $RPM_BUILD_ROOT/%{_lib}/security/pam_cgroup.so.*

# move the libraries  to /
mkdir -p $RPM_BUILD_ROOT/%{_lib}
mv -f $RPM_BUILD_ROOT/%{_libdir}/libcgroup.so.%{soversion} $RPM_BUILD_ROOT/%{_lib}
rm -f $RPM_BUILD_ROOT/%{_libdir}/libcgroup.so.%{soversion_major}
ln -sf libcgroup.so.%{soversion} $RPM_BUILD_ROOT/%{_lib}/libcgroup.so.%{soversion_major}
ln -sf ../../%{_lib}/libcgroup.so.%{soversion} $RPM_BUILD_ROOT/%{_libdir}/libcgroup.so
rm -f $RPM_BUILD_ROOT/%{_libdir}/*.la

# pre-create /cgroup directory
mkdir $RPM_BUILD_ROOT/cgroup

# install README.RedHat
cp %SOURCE1 .

%clean
rm -rf $RPM_BUILD_ROOT

%pre
getent group cgred >/dev/null || groupadd -r cgred

%post 
/sbin/ldconfig
/sbin/chkconfig --add cgred
/sbin/chkconfig --add cgconfig

%preun
if [ $1 = 0 ]; then
    /sbin/service cgred stop > /dev/null 2>&1 || :
    /sbin/service cgconfig stop > /dev/null 2>&1 || :
    /sbin/chkconfig --del cgconfig
    /sbin/chkconfig --del cgred
fi

%postun -p /sbin/ldconfig

%files 
%defattr(-,root,root,-)
%config(noreplace) %{_sysconfdir}/sysconfig/cgred.conf
%config(noreplace) %{_sysconfdir}/sysconfig/cgconfig
%config(noreplace) %{_sysconfdir}/cgconfig.conf
%config(noreplace) %{_sysconfdir}/cgconfig.d
%config(noreplace) %{_sysconfdir}/cgrules.conf
%config(noreplace) %{_sysconfdir}/cgsnapshot_blacklist.conf
/%{_lib}/libcgroup.so.*
%attr(2755, root, cgred) /bin/cgexec
%attr(2755, root, cgred) /bin/cgclassify
/bin/cgcreate
/bin/cgget
/bin/cgset
/bin/cgdelete
/bin/lscgroup
/bin/lssubsys
/sbin/cgconfigparser
/sbin/cgrulesengd
/sbin/cgclear
/bin/cgsnapshot
%attr(0644, root, root) %{_mandir}/man1/*
%attr(0644, root, root) %{_mandir}/man5/*
%attr(0644, root, root) %{_mandir}/man8/*
%attr(0755,root,root) %{_initrddir}/cgconfig
%attr(0755,root,root) %{_initrddir}/cgred
%doc COPYING INSTALL README_daemon README.RedHat
%attr(0755,root,root) %dir /cgroup

%files pam
%defattr(-,root,root,-)
%attr(0755,root,root) /%{_lib}/security/pam_cgroup.so
%doc COPYING INSTALL

%files devel
%defattr(-,root,root,-)
%{_includedir}/libcgroup.h
%{_includedir}/libcgroup/*.h
%{_libdir}/libcgroup.*
%{_libdir}/pkgconfig/libcgroup.pc
%doc COPYING INSTALL 

%changelog
* Tue Nov 28 2017 Nikola Forró <nforro@redhat.com> - 0.40.rc1-26
- fix potentially unterminated string
  related: #1441163

* Thu May 11 2017 Nikola Forró <nforro@redhat.com> - 0.40.rc1-25
- increase maximal size of controller values
  resolves: #1441163

* Fri Feb 03 2017 Nikola Forró <nforro@redhat.com> - 0.40.rc1-24
- fix segfault in cgroup_pam.c
  resolves: #1419519

* Fri Oct 21 2016 Nikola Forró <nforro@redhat.com> - 0.40.rc1-23
- fix potential buffer overflow
  resolves: #1386742

* Thu Sep 01 2016 Nikola Forró <nforro@redhat.com> - 0.40.rc1-22
- fix memory leak detected by Covscan
  related: #1284495

* Thu Sep 01 2016 Nikola Forró <nforro@redhat.com> - 0.40.rc1-21
- change cgroup of every thread of a process
  resolves: #1284495

* Thu Sep 01 2016 Nikola Forró <nforro@redhat.com> - 0.40.rc1-20
- change priority of cgconfig and cgred init scripts
  resolves: #1233393

* Thu Aug 11 2016 Nikola Forró <nforro@redhat.com> - 0.40.rc1-19
- fix loading config files from /etc/cgconfig.d to make it work with libcgroup-pam
  resolves: #1345762

* Tue Jun 07 2016 Nikola Forró <nforro@redhat.com> - 0.40.rc1-18
- fix order of memory subsystem parameters generated by cgsnapshot
  resolves: #1315543

* Fri Mar 04 2016 Nikola Forró <nforro@redhat.com> - 0.40.rc1-17
- fix infinite loop
  resolves: #1280382

* Tue Jan 06 2015 jchaloup <jchaloup@redhat.com> - 0.40.rc1-16
- extending cgroup names with default
  resolves: #1139205
- fixing libcgroup-0.40.rc1-reading-config-files-from-etc-cgconfig.d.patch not to modify patch backup file
  resolves: #1162220

* Thu Oct 02 2014 jchaloup <jchaloup@redhat.com> - 0.40.rc1-15
- related: #1036355
  bumping the release, rhel-6.6 build was not Z-candidate

* Thu Oct 02 2014 jchaloup <jchaloup@redhat.com> - 0.40.rc1-14
- related: #1036355
  bumping the release so it can be built in z-stream for rhel-6.6

* Mon Sep 15 2014 jchaloup <jchaloup@redhat.com> - 0.40.rc1-13
- resolves: #1036355
  support for multiline values

* Thu Aug 07 2014 jchaloup <jchaloup@redhat.com> - 0.40.rc1-12
- related: #1080281

* Wed Aug 06 2014 jchaloup <jchaloup@redhat.com> - 0.40.rc1-11
- resolves: #1080281
  retry to set control file in cgroup_modify_cgroup

* Thu Jun 19 2014 jchaloup <jchaloup@redhat.com> - 0.40.rc1-10
- resolves: #1058363
  reading config files from /etc/cgconfig.d/

* Mon Jun 16 2014 jchaloup <jchaloup@redhat.com> - 0.40.rc1-9
- resolves: #1060227
  pam cache turned off

* Tue Mar 25 2014 jchaloup <jchaloup@redhat.com> - 0.40.rc1-8
- resolves: #1057676
  copy of cgroup template fixed, patch from upstream

* Mon Mar 17 2014 jchaloup <jchaloup@redhat.com> - 0.40.rc1-7
- resolves: #1022842
  multiple -r option of cgset corrected, patch from upstream

* Mon Dec  2 2013 Peter Schiffer <pschiffe@redhat.com> 0.40.rc1-6
- resolves: #1028773
  removed unnecessary dependency on redhat-lsb-core

* Fri Oct 25 2013 Peter Schiffer <pschiffe@redhat.com> 0.40.rc1-5
- related: #964219
  fixed memory leak occurring when reloading cache

* Mon Sep 30 2013 Peter Schiffer <pschiffe@redhat.com> 0.40.rc1-4
- related: #913286
  fixed performance regression when starting cgred service
- related: #589535
  fixed templates

* Mon Sep 16 2013 Peter Schiffer <pschiffe@redhat.com> 0.40.rc1-3
- related: #946953
  fixed typo and one incorrect cast
- related: #964219
  fixed two libcg crashes

* Wed Aug 28 2013 Peter Schiffer <pschiffe@redhat.com> 0.40.rc1-2
- fixed coverity findings
- resolves: #738620
  relabel cgred.pid file after service starts
- resolves: #961844
  increase start priority for cgred service

* Tue Aug 27 2013 Peter Schiffer <pschiffe@redhat.com> 0.40.rc1-1
- resolves: #589535
  rebase to 0.40.rc1
  added support for automated cgroup creation following a template

* Mon Aug 12 2013 Peter Schiffer <pschiffe@redhat.com> 0.37-10
- resolves: #921328
  cgred service can now start with an empty configuration file
- resolves: #863172
  cgconfig now sets group write permissions on files in the cgroup
- resolves: #916397
  fixed cgrulesengd segfault
- resolves: #924399
  fixed bug when the cgrulesengd had different logging level from the library
- resolves: #951724
  fixed cgget(1) man page
- resolves: #809550
  removed -s option from cgcreate(1) man page
- resolves: #913286
  fixed adding control subgroups after cgrulesengd has started
- resolves: #753334
  fixed bug when cgconfig fails to parse commas in the cgconfig.conf file

* Thu Jun 13 2013 Ivana Hutarova Varekova <varekova@redhat.com> 0.37-9
- resolves: #972893
  enable cache for pam_cgroup

* Wed Feb 20 2013 Peter Schiffer <pschiffe@redhat.com> 0.37-8
- resolves: #912425
  fixed problem when cgred service could segfault if entry in cgrules.conf file
  doesn't specify procname

* Thu Dec 20 2012 Peter Schiffer <pschiffe@redhat.com> 0.37-7
- related: #738737
  lowered default logging level from warning to error

* Mon Dec 17 2012 Peter Schiffer <pschiffe@redhat.com> 0.37-6
- related: #738737
  updated logging improvement
- resolves: #877042
  fixed coverity finding in libcgroup-0.37-add-inotify-fd.patch
- resolves: #869990
  fixed bug when cgconfig service was failing to start on read only file systems

* Thu Oct 11 2012 Peter Schiffer <pschiffe@redhat.com> 0.37-5
- resolves: #819137
  fixed bug when lscgroup was ltrimming path which wasn't prefixed with slash
- resolves: #773544
  made --sticky option effective when setuid(2) and setgid(2)
- resolves: #849757
  added inotify fd to scan running tasks and set control groups
- resolves: #738737
  logging improvement

* Wed Feb 22 2012 Peter Schiffer <pschiffe@redhat.com> 0.37-4
- Resolves: #758493
  fixes the admin/assign id bug in libcgroup

* Wed Jun 29 2011 Jan Safranek <jsafrane@redhat.com> 0.37-3.el6
- Fixed 'cgred' group not being created as system-group during installation
  of the package.
- Resolves: #715413

* Tue Mar  1 2011 Jan Safranek <jsafrane@redhat.com> 0.37-2.el6
- Fixed buffer overflow when parsing cgexec command line parameters.
- Added checking of source of netlink messages to cgrulesengd daemon.
- Resolves: CVE-2011-1006 CVE-2011-1022

* Tue Dec 14 2010 Jan Safranek <jsafrane@redhat.com> 0.37-1.el6
- Updated to 0.37
  - added new 'cgsnapshot' tool to generate cgconfig.conf (#649195)
  - fixed 'cgget' reading long variable values like devices.list (#626127)
  - fixed reading list of mounted controllers on library init (#635984)
  - fixed the library not to change current working directory when creating
    groups (#628895)
  - new user 'cgred' was added for better security - /bin/cgexec tool is no
    longer SUID to root but SGID to the new 'cgred' user, which has write
    access to /var/run/cgred.socket
  - may other fixes an enhancements
- Removed rpath from compiled binaries
- Fixed spelling and rpmlint errors in the .spec file (#634939)
- Fixed exit code of cgclassify tool (#667957)

* Wed Jul 14 2010 Ivana Hutarova Varekova <varekova@redhat.com> 0.36-6
- Resolves: #609816
  serivces of libcgroup not LSB-compliant

* Tue Jun 29 2010 Jan Safranek <jsafrane@redhat.com> 0.36-5
- Relax the dependency on redhat-lsb package (#607537)
- Fix installation of -devel libraries (#607538)

* Tue Jun 15 2010 Jan Safranek <jsafrane@redhat.com> 0.36-4
- Fix libcgroup.so link to the right soname (#599367)
- Fix segmentation fault in cgget tool (#601071)
- Fix lscgroup commandline parsing (#601095)

* Tue Jun  1 2010 Ivana Hutarova Varekova <varekova@redhat.com> 0.36-3
- Related: #594249
  add three man pages

* Wed May 26 2010 Ivana Hutarova Varekova <varekova@redhat.com> 0.36-2
- Resolves: #594249
  add three man pages

* Tue May 25 2010 Jan Safranek <jsafrane@redhat.com> 0.36-1
- Updated to 0.36.1 (#594703)

* Thu Apr 22 2010 Ivana Hutarova Varekova <varekova@redhat.com> 0.35-3
- Resolves: #584681
  fix man-pages problem

* Wed Apr 14 2010 Jan Safranek <jsafrane@redhat.com> 0.35-2
- Fix parsing of command line options on ppc (#581044)

* Tue Mar  9 2010 Jan Safranek <jsafrane@redhat.com> 0.35-1
- Update to 0.35.1
- Separate pam module to its own subpackage

* Mon Jan 18 2010 Jan Safranek <jsafrane@redhat.com> - 0.34-4
- Added README.RedHat to describe libcgroup integration into initscripts

* Mon Dec 21 2009 Jan Safranek <jsafrane@redhat.com> - 0.34-3
- Change the default configuration to mount everything to /cgroup

* Mon Nov 30 2009 Dennis Gregorovic <dgregor@redhat.com> - 0.34-2.1
- Rebuilt for RHEL 6

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
