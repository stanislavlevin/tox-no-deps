# tox-no-deps plugin ![CI](https://github.com/stanislavlevin/tox-no-deps/workflows/CI/badge.svg)

This plugin skips the installation of all `deps` and `extras` of all the
Tox environments. The dependencies of tested package if any are not touched.

This is mostly used for testing purposes in ALTLinux during RPM build of Python
packages to run integration tests against the repository packages.

Usage
-----

Only the CLI option is supported, the configuration's one is considered
ambiguous.

```
tox --no-deps
```

License
-------

Distributed under the terms of the **MIT** license, `tox-no-deps` is
free and open source software.
