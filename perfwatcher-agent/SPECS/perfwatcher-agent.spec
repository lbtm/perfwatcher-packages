#=================================================
# Specification file for perfwatcher agent
#
# Installs perfwatcher agent files
#
#=================================================

#=================================================
# Variables
#=================================================
%define		real_name		perfwatcher
%define		real_version		2.2	
%define		collectd_version	5.4.0
%define		collectd_date_release	20140805

%define		etc_dir			/etc	
%define		usr_dir			/usr
%define         perfwatcher_db          %{etc_dir}/types-perfwatcher.db
%define		collectdinitscript	%{etc_dir}/init.d/collectd
%define		collectdconffile	%{etc_dir}/collectd.conf
%define 	bin_dir			%{usr_dir}/bin
%define 	include_dir		%{usr_dir}/include
%define 	lib64_dir		%{usr_dir}/lib64
%define 	sbin_dir		%{usr_dir}/sbin
%define 	share_dir		%{usr_dir}/share

#=================================================
# Header
#=================================================
Name:		%{real_name}-agent
Version:	%{real_version}
Release:	0%{?dist}
Summary:	Collectd patched for PerfWatcher agent
Group:		System Environment/Daemons
License:	GPLv2	
URL:		http://perfwatcher.org
Source:		http://perfwatcher.free.fr/download/collectd/collectd-%{collectd_version}.%{collectd_date_release}.tar.gz	
BuildRoot:	%(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)
Packager:       LBTM <contact@lotautbrian.fr>
Requires:	perl-Regexp-Common
## SLES
%if 0%{?sles_version}
BuildRequires:	gcc, libart_lgpl-devel
%endif
## RHEL
%if 0%{?el6}
BuildRequires:	gcc
%endif
## Arch
%ifarch %ix86
BuildArch:      i?86
%endif
%ifarch x86_64
BuildArch:      x86_64
%endif

%description 
Collectd patched for PerfWatcher agent.
Perfwatcher is a frontend for collectd witch show you graph 
and aggregate data over several host.

#=================================================
# Source preparation
#=================================================
%prep
%setup -qn collectd-%{collectd_version}.%{collectd_date_release}

#=================================================
# Building
#=================================================
%build 
%configure --enable-top --enable-sysconfig --enable-cpu --prefix=/usr
make %{?_smp_mflags}

#=================================================
# Installation
#=================================================
%install 
rm -rf %{buildroot}
make install DESTDIR=%{buildroot}

mkdir -p %{buildroot}%{etc_dir}/init.d

install -m 644 src/types-perfwatcher.db		%{buildroot}%{perfwatcher_db}

%if 0%{?sles_version}
install -m 755 contrib/sles10.1/init.d-collectd	%{buildroot}%{collectdinitscript}
%endif
%if 0%{?el6}
install -m 755 contrib/redhat/init.d-collectd	%{buildroot}%{collectdinitscript}
%endif

#=================================================
# Cleaning
#=================================================
%clean
rm -rf %{buildroot}

#=================================================
# Files
#=================================================
%files 
%defattr(-,root,root,-)
%{bin_dir}
%{lib64_dir}
%{sbin_dir}
%{share_dir}
%{include_dir}/collectd
%attr(0755, root, root) %{collectdinitscript}
%attr(0644, root, root) %{collectdconffile}
%attr(0644, root, root) %{perfwatcher_db}

#=================================================
# Post Installation
#=================================================
%post 
echo "TypesDB     \"/usr/share/collectd/types.db\"
Interval     60

LoadPlugin cpu
LoadPlugin df
LoadPlugin disk
LoadPlugin interface
LoadPlugin load
LoadPlugin memory
LoadPlugin processes
LoadPlugin swap
LoadPlugin sysconfig
LoadPlugin top
LoadPlugin uptime

LoadPlugin network
<Plugin network>
	# IP to be replaced by Collectd server's IP
	Server \"192.168.10.120\" \"25826\"
	MaxPacketSize 65535
</Plugin>
" > /etc/collectd.conf 

#Service collectd On
chkconfig --add collectd
chkconfig collectd on
#run service collectd
service collectd restart

#=================================================
# Changelog
#=================================================
%changelog
* Tue Sep 16 2014 - LBTM <contact@lotautbrian.fr> 2.2-0
- Initial package
