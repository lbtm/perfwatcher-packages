#=================================================
# Specification file for perfwatcher frontend
#
# Installs perfwatcher frontend files
#
#=================================================

#=================================================
# Variables
#=================================================
%define	real_name		perfwatcher
%define	real_version		2.2	
%define	release_date		20140911	

%define	etc_dir			/etc	
%define	cron_dir		%{etc_dir}/cron.d	

## SLES
%if 0%{?sles_version}
%define apache                  wwwrun
%define apache_group            www
%define	html_dir		/srv/www/htdocs
%define	perfwatcher_logs_dir	%{html_dir}/%{real_name}/logs
%endif
## RHEL
%if 0%{?el6}
%define apache                  apache
%define apache_group            apache
%define	html_dir		/var/www/html
%define	perfwatcher_logs_dir	%{html_dir}/%{real_name}/logs
%endif

#=================================================
# Header
#=================================================
Name:		%{real_name}-frontend
Version:	%{real_version}
Release:	0%{dist}
Summary:	Performance Monitoring for Unix
Group:		Applications/System	
License:	GPLv2	
URL:		http://perfwatcher.org
Source:		http://perfwatcher.free.fr/download/perfwatcher/%{real_name}-%{version}-%{release_date}.tar.gz
BuildRoot:	%(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)
BuildArch:	noarch
%if 0%{?el6}
Requires:	httpd, php, php-cli, php-gd, php-pear, php5-curl 
Requires:	php-mysql, php-pear-MDB2-Driver-mysql, mysql-server, mysql
%endif
%if 0%{?sles_version}
Requires:	apache2, apache2-mod_php5, php5, php5-pear, php5-curl, php5-gd 
Requires:	mysql, mysql-client, php5-mysql, php5-pear-MDB2_Driver_mysql
%endif

%description 
Perfwatcher is a frontend for collectd witch show you graph 
and aggregate data over several host.

#=================================================
# Source preparation
#=================================================
%prep 
%setup -qn %{real_name}-%{version}-%{release_date}

#=================================================
# Building
#=================================================
%build 

#=================================================
# Installation
#=================================================
%install 
rm -rf %{buildroot}

mkdir -p %{buildroot}%{html_dir}/%{real_name}
mkdir -p %{buildroot}%{perfwatcher_logs_dir}
mkdir -p %{buildroot}%{html_dir}/%{real_name}/%{etc_dir}

install -m 755 etc/config.sample.php	%{buildroot}%{html_dir}/%{real_name}/%{etc_dir}/config.php

for _files in *; do
	%if 0%{?sles_version}
		cp -r $_files	%{buildroot}%{html_dir}/%{real_name}
	%endif
	%if 0%{?el6}
		cp -r $_files  %{buildroot}%{html_dir}/%{real_name}
	%endif
done

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
%{html_dir}/%{real_name}
%attr(755, %apache, %apache_group)	%{html_dir}/%{real_name}%{etc_dir}
%attr(755, %apache, %apache_group)	%{perfwatcher_logs_dir}

#=================================================
# Post Installation
#=================================================
%post 
## Cron configuration
echo "* * * * * %{html_dir}/%{real_name}/bin/peuplator
* * * * * %{html_dir}/%{real_name}/bin/aggregator
" > %{cron_dir}/perfwatcher

#Service httpd/mysql On
chkconfig --add httpd
chkconfig --add mysqld
chkconfig httpd on
chkconfig mysqld on
#run service httpd/mysql/crond
service httpd restart
service mysqld restart
service crond restart

#=================================================
# Post Uninstall
#=================================================
%postun
rm -f %{cron_dir}/perfwatcher

#=================================================
# Changelog
#=================================================
%changelog
* Tue Sep 16 2014 - LBTM <contact@lotautbrian.fr> 2.2-0
- Initial package
