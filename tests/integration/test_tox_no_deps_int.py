import os
import sys
import subprocess

import pytest

NO_DEPS_SKIP_TEMPLATE = "no-deps plugin: deps: '{}' will be skipped for 'python'"
NO_EXTRAS_SKIP_TEMPLATE = "no-deps plugin: extras: '{}' will be skipped for 'python'"


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

    result = cmd("--no-deps", "-v")
    result.assert_success()
    assert (
        NO_DEPS_SKIP_TEMPLATE.format(
            "[somenotexisted_package1 == 9.9.9, somenotexisted_package2]"
        )
        in result.outlines
    )


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

    result = cmd("--no-deps", "-v")
    result.assert_success()
    assert NO_EXTRAS_SKIP_TEMPLATE.format("['tests']") in result.outlines


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

    result = cmd("--no-deps", "-v")
    result.assert_success()
    assert (
        NO_DEPS_SKIP_TEMPLATE.format(
            "[somenotexisted_package1 == 9.9.9, somenotexisted_package2]"
        )
        in result.outlines
    )
    assert NO_EXTRAS_SKIP_TEMPLATE.format("['tests']") in result.outlines


def test_deps_from_file_skipped(initproj, cmd):
    initproj(
        "pkg123",
        filedefs={
            "requirements.txt": """\
                somenotexisted_package1 == 9.9.9
            """,
            "tox.ini": """
                [tox]
                [testenv]
                deps =
                    -rrequirements.txt
                    somenotexisted_package2
                usedevelop=true
                commands=python -c "print('test')"
            """,
        },
    )

    result = cmd("--no-deps", "-v")
    result.assert_success()
    assert (
        NO_DEPS_SKIP_TEMPLATE.format("[-rrequirements.txt, somenotexisted_package2]")
        in result.outlines
    )


def test_deps_from_env_skipped(initproj, cmd):
    initproj(
        "pkg123",
        filedefs={
            "requirements.txt": """\
                somenotexisted_package1 == 9.9.9
            """,
            "requirements1.txt": """\
                somenotexisted_package2 == 9.9.9
            """,
            "tox.ini": """
                [tox]
                [base]
                deps =
                    -rrequirements.txt
                    somenotexisted_package3
                [testenv]
                deps =
                    {[base]deps}
                    -rrequirements1.txt
                    somenotexisted_package4
                usedevelop=true
                commands=python -c "print('test')"
            """,
        },
    )

    result = cmd("--no-deps", "-v")
    result.assert_success()
    assert (
        NO_DEPS_SKIP_TEMPLATE.format(
            "[-rrequirements.txt, somenotexisted_package3, -rrequirements1.txt,"
            " somenotexisted_package4]"
        )
        in result.outlines
    )


def test_package_deps_required(initproj, cmd):
    """Plugin doesn't mangle package deps"""
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
                install_requires =
                    somenotexisted_package == 9.9.9

                [options.packages.find]
                where = .
            """,
            "setup.py": """\
                from setuptools import setup
                if __name__ == "__main__":
                    setup()
            """,
            "tox.ini": """
                [tox]
                [testenv]
                usedevelop=true
                commands=python -c "print('test')"
            """,
        },
    )

    result = cmd("--no-deps")
    result.assert_fail()
    assert (
        "No matching distribution found for somenotexisted_package==9.9.9" in result.out
    )
