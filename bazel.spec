%global debug_package %{nil}
%global __debug_install_post %{nil}
%global __os_install_post %{nil}

Name: bazel  
Version: 4.0.0  
Release: 1%{?dist}  
Summary: Bazel build system  
License: Apache 2.0  
URL: https://bazel.build  
Source0: 4.0.0.tar.gz 

Patch1:         bazel-1.0.0-log-warning.patch
Patch2:         bazel-gcc.patch

# BuildRequires: gcc-c++, unzip, zip, java-11-openjdk-devel, python3  
Requires: java-11-openjdk-headless  

%description  
Fast, scalable, multi-language build system from Google.  

%prep  
%setup -n bazel-4.0.0 
%patch1 -p0
%patch2 -p0

%build
find . -type f -regextype posix-extended -iregex '.*(sh|txt|py|_stub|stub_.*|bazel|get_workspace_status|protobuf_support|_so)' -exec %{__sed} -i -e '1s|^#!/usr/bin/env python$|#!/usr/bin/env python3|' "{}" \;
export EXTRA_BAZEL_ARGS="${EXTRA_BAZEL_ARGS} --python_path=/usr/bin/python3"

# horrible of horribles, just to have `python` in the PATH
%{__mkdir_p} ./bin-hack
%{__ln_s} /usr/bin/python3 ./bin-hack/python
export PATH=$(pwd)/bin-hack:$PATH

%ifarch aarch64
export EXTRA_BAZEL_ARGS="${EXTRA_BAZEL_ARGS} --nokeep_state_after_build --notrack_incremental_state --nokeep_state_after_build"
%else
%endif

%ifarch s390x
# increase heap size to addess s390x build failures
export BAZEL_JAVAC_OPTS="-J-Xmx4g -J-Xms512m"
%else
%endif

# loose epoch from their release date
export SOURCE_DATE_EPOCH="$(date -d $(head -1 CHANGELOG.md | %{__grep} -Eo '\b[[:digit:]]{4}-[[:digit:]]{2}-[[:digit:]]{2}\b' ) +%s)"
export EMBED_LABEL="%{version}"

# for debugging's sake
which g++
g++ --version

export TMPDIR=%{_tmppath}
export CC=gcc
export CXX=g++
export EXTRA_BAZEL_ARGS="${EXTRA_BAZEL_ARGS} --sandbox_debug --host_javabase=@local_jdk//:jdk --verbose_failures --subcommands --explain=build.log --show_result=2147483647"
env ./compile.sh
env ./scripts/generate_bash_completion.sh --bazel=output/bazel --output=output/bazel-complete.bash

%install
%{__mkdir_p} %{buildroot}/%{_bindir}
%{__mkdir_p} %{buildroot}/%{bashcompdir}
%{__cp} output/bazel %{buildroot}/%{_bindir}/

%clean
%{__rm} -rf %{buildroot}

%files
%defattr(-,root,root)
%attr(0755,root,root) %{_bindir}/bazel
