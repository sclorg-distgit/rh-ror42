%global scl_name_prefix rh-
%global scl_name_base ror
%global scl_name_version 42

%global scl %{scl_name_prefix}%{scl_name_base}%{scl_name_version}

# Fallback to rh-ruby23. rh-ruby23-scldevel is probably not available in
# the buildroot.
%{!?scl_ruby:%global scl_ruby rh-ruby23}
%{!?scl_prefix_ruby:%global scl_prefix_ruby %{scl_ruby}-}

# Fallback to rh-nodejs4 rh-nodejs4-scldevel is probably not available in
# the buildroot.
%{!?scl_nodejs:%global scl_nodejs rh-nodejs4}
%{!?scl_prefix_nodejs:%global scl_prefix_nodejs %{scl_nodejs}-}

# Do not produce empty debuginfo package.
%global debug_package %{nil}

# Support SCL over NFS.
%global nfsmountable 1

%{!?install_scl: %global install_scl 1}

%scl_package %scl

Summary: Package that installs %scl
Name: %scl_name
Version: 2.2
Release: 7%{?dist}
License: GPLv2+
Source0: README
Source1: LICENSE

%if 0%{?install_scl}
Requires: %{scl_prefix}rubygem-sqlite3
Requires: %{scl_prefix}rubygem-rails
Requires: %{scl_prefix}rubygem-sass-rails
Requires: %{scl_prefix}rubygem-coffee-rails
Requires: %{scl_prefix}rubygem-jquery-rails
Requires: %{scl_prefix}rubygem-sdoc
Requires: %{scl_prefix}rubygem-turbolinks
Requires: %{scl_prefix}rubygem-bcrypt
Requires: %{scl_prefix}rubygem-uglifier
Requires: %{scl_prefix}rubygem-jbuilder
Requires: %{scl_prefix}rubygem-spring
Requires: %{scl_prefix}rubygem-byebug
Requires: %{scl_prefix}rubygem-web-console
Requires: %{scl_prefix_nodejs}nodejs
%endif
BuildRequires: help2man
BuildRequires: scl-utils-build
BuildRequires: %{scl_prefix_ruby}scldevel
BuildRequires: %{scl_prefix_ruby}rubygems-devel

%description
This is the main package for %scl Software Collection.

%package runtime
Summary: Package that handles %scl Software Collection.
Requires: scl-utils
# enable scriptlet depends on ruby executable.
Requires: %{scl_prefix_ruby}ruby

%description runtime
Package shipping essential scripts to work with %scl Software Collection.

%package build
Summary: Package shipping basic build configuration
Requires: scl-utils-build
Requires: %{scl_runtime}
Requires: %{scl_prefix_ruby}scldevel
Requires: %{scl_prefix_nodejs}scldevel

%description build
Package shipping essential configuration macros to build %scl Software Collection.

%package scldevel
Summary: Package shipping development files for %scl
Provides: scldevel(%{scl_name_base})

%description scldevel
Package shipping development files, especially usefull for development of
packages depending on %scl Software Collection.

%prep
%setup -T -c

# Expand macros used in README file.
cat > README << EOF
%{expand:%(cat %{SOURCE0})}
EOF

cp %{SOURCE1} .

%build
# Generate a helper script that will be used by help2man.
cat > h2m_help << 'EOF'
#!/bin/bash
[ "$1" == "--version" ] && echo "%{scl_name} %{version} Software Collection" || cat README
EOF
chmod a+x h2m_help

# Generate the man page from include.h2m and ./h2m_help --help output.
help2man -N --section 7 ./h2m_help -o %{scl_name}.7

%install
%scl_install

cat >> %{buildroot}%{_scl_scripts}/enable << EOF
export PATH=%{_bindir}\${PATH:+:\${PATH}}
export LD_LIBRARY_PATH=%{_libdir}\${LD_LIBRARY_PATH:+:\${LD_LIBRARY_PATH}}
export MANPATH=%{_mandir}:\${MANPATH}
export PKG_CONFIG_PATH=%{_libdir}/pkgconfig\${PKG_CONFIG_PATH:+:\${PKG_CONFIG_PATH}}
export GEM_PATH=\${GEM_PATH:=%{gem_dir}:\`scl enable %{scl_ruby} -- ruby -e "print Gem.path.join(':')"\`}

. scl_source enable %{scl_ruby}
EOF

cat >> %{buildroot}%{_root_sysconfdir}/rpm/macros.%{scl_name_base}-scldevel << EOF
%%scl_%{scl_name_base} %{scl}
%%scl_prefix_%{scl_name_base} %{scl_prefix}
EOF

# Install generated man page.
mkdir -p %{buildroot}%{_mandir}/man7/
install -p -m 644 %{scl_name}.7 %{buildroot}%{_mandir}/man7/

scl enable %{scl_ruby} - << \EOF
set -e

# Fake rh-ror42 SCL environment.
# TODO: Is there a way how to leverage the enable scriptlet created above?
GEM_PATH=%{gem_dir}:`ruby -e "print Gem.path.join(':')"` \
X_SCLS=%{scl} \
ruby -rfileutils > rubygems_filesystem.list << \EOR
  # Create RubyGems filesystem.
  Gem.ensure_gem_subdirectories '%{buildroot}%{gem_dir}'
  FileUtils.mkdir_p File.join '%{buildroot}', Gem.default_ext_dir_for('%{gem_dir}')

  # Output the relevant directories.
  puts Gem.default_dirs['%{scl}_system'.to_sym].values
EOR
EOF

%files

%files runtime -f rubygems_filesystem.list
%doc README LICENSE
%scl_files
# Own the manual directories (rhbz#1080036, rhbz#1072319).
%dir %{_mandir}/man1
%dir %{_mandir}/man5
%dir %{_mandir}/man7
%{_mandir}/man7/%{scl_name}.*

%files build
%{_root_sysconfdir}/rpm/macros.%{scl}-config

%files scldevel
%{_root_sysconfdir}/rpm/macros.%{scl_name_base}-scldevel

%changelog
* Wed Apr 06 2016 Pavel Valena <pvalena@redhat.com> - 2.2-7
- Add rubygem-web-console do Requires
  - Resolves: rhbz#1317080

* Thu Mar 03 2016 Pavel Valena <pvalena@redhat.com> - 2.2-6
- Add rubygem-byebug to Requires

* Thu Mar 03 2016 Pavel Valena <pvalena@redhat.com> - 2.2-5
- Add nodejs to Requires

* Thu Mar 03 2016 Pavel Valena <pvalena@redhat.com> - 2.2-4
- Enable install_scl

* Thu Feb 25 2016 Pavel Valena <pvalena@redhat.com> - 2.2-3
- Add rh-nodejs4-scldevel to the Requires of build subpackage

* Sat Feb 20 2016 Pavel Valena <pvalena@redhat.com> - 2.2-2
- Fix path generation in Fake SCL environment

* Thu Dec 17 2015 Pavel Valena <pvalena@redhat.com> - 2.2-1
- Initial metapackage.
