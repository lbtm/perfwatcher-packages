#=================================================
# Specification file for perfwatcher server
#
# Installs perfwatcher server files
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
Name:		%{real_name}-server
Version:	%{real_version}
Release:	0%{?dist}
Summary:	Collectd patched for PerfWatcher server
Group:		System Environment/Daemons
License:	GPLv2	
URL:		http://perfwatcher.org
Source0:        http://perfwatcher.free.fr/download/collectd/collectd-%{collectd_version}.%{collectd_date_release}.tar.gz
BuildRoot:	%(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)
Packager:	LBTM <contact@lotautbrian.fr>
## SLES
%if 0%{?sles_version}
BuildRequires:	gcc, libart_lgpl-devel, zlib-devel, rrdtool-devel >= 1.4.0, zlib, json-c-devel, libmicrohttpd-devel, libnotify-devel
%endif
## RHEL
%if 0%{?el6}
BuildRequires:	gcc, zlib-devel, rrdtool-devel >= 1.4.0, json-c-devel, libmicrohttpd-devel, libnotify-devel
%endif
Requires:	rrdtool >= 1.4.0, json-c >= 0.10, libmicrohttpd >= 0.9.22, perl-Regexp-Common
%ifarch %ix86
BuildArch:	i?86
%endif
%ifarch x86_64
BuildArch:	x86_64
%endif

%description 
Collectd patched for PerfWatcher.
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
%configure --enable-top --enable-cpu --enable-rrdtool \
--enable-jsonrpc --enable-notify_file --enable-basic_aggregator \
--enable-write_top \
--prefix=/usr 
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
TypesDB     \"/etc/types-perfwatcher.db\"
Interval     60

LoadPlugin cpu
LoadPlugin df
LoadPlugin disk
LoadPlugin interface
LoadPlugin load
LoadPlugin memory
LoadPlugin processes
LoadPlugin swap
LoadPlugin top
LoadPlugin uptime

LoadPlugin network
<Plugin network>
	Listen \"0.0.0.0\" \"25826\"
	MaxPacketSize 65535
</Plugin>

LoadPlugin rrdtool
<Plugin rrdtool>
	DataDir \"/var/lib/collectd\"
</Plugin>

LoadPlugin jsonrpc
<Plugin jsonrpc>
	Port \"8080\"
	MaxClients 64
# Note : write_top and jsonrpc work together.
# This is why we need to define this path twice.
	DataDir \"/var/lib/collectd\"
# If you prefer to use rrdcached, uncomment and update the next line
#	RRDCachedDaemonAddress \"/var/run/rrdcached/rrdcached.sock\"
	RRDToolPath \"/usr/bin/rrdtool\"
	TopPsDataDir \"/var/lib/collectd/top\"
</Plugin>

LoadPlugin notify_file
<Plugin notify_file>
	DataDir \"/var/lib/collectd/_notification\"
# This is an include list. If you prefere an exclude list,
# you should exclude \"top\".
	Plugin \"sysconfig\"
	InvertPluginList false
	LinkLast \"sysconfig\"
</Plugin>

LoadPlugin write_top
<Plugin write_top>
	DataDir \"/var/lib/collectd/top\"
	FlushWhenOlderThanMin 30
	FlushWhenBiggerThanK 500
</Plugin>

LoadPlugin basic_aggregator
<Plugin basic_aggregator>
	Aggregators_config_file \"/<path to perfwatcher>/etc/aggregator.conf\"
</Plugin>
" > %{collectdconffile} 

## Aggregators_config_file
## SLES
%if 0%{?sles_version}
sed -i 's/Aggregators_config_file "\/<path to perfwatcher>\/etc\/aggregator.conf"/Aggregators_config_file "\/srv\/www\/htdocs\/perfwatcher\/etc\/aggregator.conf"/' %{collectdconffile}
%endif
## RHEL
%if 0%{?el6}
sed -i 's/Aggregators_config_file "\/<path to perfwatcher>\/etc\/aggregator.conf"/Aggregators_config_file "\/var\/www\/html\/perfwatcher\/etc\/aggregator.conf"/' %{collectdconffile}
%endif

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
