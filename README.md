# tox-no-deps plugin ![CI](https://github.com/stanislavlevin/tox-no-deps/workflows/CI/badge.svg)

In network-isolated environments it's impossible to install anything from
Python package index and only globally installed packages can be used within tox
test environments.

This plugin skips an installation of dependencies of tox test environments:

- [deps](https://tox.wiki/en/latest/config.html#deps)
- [extras](https://tox.wiki/en/latest/config.html#extras)
- [dependency_groups](https://tox.wiki/en/latest/config.html#dependency_groups)

This is mostly used for testing purposes in ALTLinux during RPM build of Python
packages to run integration tests against the repository packages.

Usage
-----

```
tox --no-deps
```

License
-------

Distributed under the terms of the **MIT** license, `tox-no-deps` is
free and open source software.
