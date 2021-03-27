import os
import sys
import subprocess

import pytest


def test_no_plugin_usage(initproj, cmd):
    """Plugin doesn't break regular tox"""
    initproj(
        "pkg123",
        filedefs={
            "tox.ini": """
                [tox]
                skipsdist = True
                [testenv]
                commands=python -c "print('test')"
            """,
        },
    )
    result = cmd()
    result.assert_success()


def test_no_plugin_usage_deps(initproj, cmd):
    initproj(
        "pkg123",
        filedefs={
            "tox.ini": """
                [tox]
                skipsdist = True
                [testenv]
                deps =
                    somenotexisted_package1 == 9.9.9
                commands=python -c "print('test')"
            """,
        },
    )
    result = cmd()
    result.assert_fail()
    assert (
        "No matching distribution found for somenotexisted_package1==9.9.9"
        in result.out
    )


def test_no_plugin_usage_extras(initproj, cmd):
    initproj(
        "pkg123",
        filedefs={
            "setup.cfg": """\
                [metadata]
                name = pkg123
                description = pkg123 project
                version = 0.0.1
                license = MIT
                platforms = unix

                [options]
                packages = find:

                [options.packages.find]
                where = .

                [options.extras_require]
                tests =
                    somenotexisted_package1 == 9.9.9
            """,
            "setup.py": """\
                from setuptools import setup
                if __name__ == "__main__":
                    setup()
            """,
            "tox.ini": """
                [tox]
                [testenv]
                extras =
                    tests
                usedevelop=true
                commands=python -c "print('test')"
            """,
        },
    )
    result = cmd()
    result.assert_fail()
    assert (
        "No matching distribution found for somenotexisted_package1==9.9.9"
        in result.out
    )


def test_deps_skipped(initproj, cmd):
    initproj(
        "pkg123",
        filedefs={
            "tox.ini": """
                [tox]
                skipsdist = True
                [testenv]
                deps =
                    somenotexisted_package1 == 9.9.9
                    somenotexisted_package2
                commands=python -c "print('test')"
            """
        },
    )

    result = cmd("--no-deps")
    result.assert_success()


def test_extras_skipped(initproj, cmd):
    initproj(
        "pkg123",
        filedefs={
            "setup.cfg": """\
                [metadata]
                name = pkg123
                description = pkg123 project
                version = 0.0.1
                license = MIT
                platforms = unix

                [options]
                packages = find:

                [options.packages.find]
                where = .

                [options.extras_require]
                tests =
                    somenotexisted_package1 == 9.9.9
                    somenotexisted_package2
            """,
            "setup.py": """\
                from setuptools import setup
                if __name__ == "__main__":
                    setup()
            """,
            "tox.ini": """
                [tox]
                [testenv]
                extras =
                    tests
                usedevelop=true
                commands=python -c "print('test')"
            """,
        },
    )

    result = cmd("--no-deps")
    result.assert_success()


def test_deps_extras_skipped(initproj, cmd):
    initproj(
        "pkg123",
        filedefs={
            "setup.cfg": """\
                [metadata]
                name = pkg123
                description = pkg123 project
                version = 0.0.1
                license = MIT
                platforms = unix

                [options]
                packages = find:

                [options.packages.find]
                where = .

                [options.extras_require]
                tests =
                    somenotexisted_package1 == 9.9.9
                    somenotexisted_package2
            """,
            "setup.py": """\
                from setuptools import setup
                if __name__ == "__main__":
                    setup()
            """,
            "tox.ini": """
                [tox]
                [testenv]
                deps =
                    somenotexisted_package1 == 9.9.9
                    somenotexisted_package2
                extras =
                    tests
                usedevelop=true
                commands=python -c "print('test')"
            """,
        },
    )

    result = cmd("--no-deps")
    result.assert_success()
