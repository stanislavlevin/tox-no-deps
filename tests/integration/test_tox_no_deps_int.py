import os
import sys
import subprocess

import pytest

NO_DEPS_SKIP_TEMPLATE = "no-deps plugin: deps: '{}' will be skipped for 'python'"
NO_EXTRAS_SKIP_TEMPLATE = "no-deps plugin: extras: '{}' will be skipped for 'python'"


def test_no_plugin_usage(tox_project, tox):
    """Plugin doesn't break regular tox"""
    project = tox_project()
    project.contents[
        "tox.ini"
    ] = """\
        [tox]
        skipsdist = True
        [testenv]
        commands=python -c "print('Hello, world!')"
        """
    project.make()
    result = tox("-vv", cwd=project.location)
    result.assert_success()


def test_no_plugin_usage_deps(tox_project, tox):
    project = tox_project()
    project.contents[
        "tox.ini"
    ] = """\
        [tox]
        skipsdist = True
        [testenv]
        deps =
            somenotexisted_package1 == 9.9.9
        commands=python -c "print('Hello, world!')"
        """
    project.make()
    result = tox("-vv", cwd=project.location)
    result.assert_fail()
    assert (
        "No matching distribution found for somenotexisted_package1==9.9.9\n"
    ) in result.stdout_text


def test_no_plugin_usage_extras(tox_project, tox):
    project = tox_project()
    project.contents[
        "tox.ini"
    ] = """\
        [tox]
        [testenv]
        extras =
            tests
        usedevelop=true
        commands=python -c "print('Hello, world!')"
        """
    project.contents[
        "setup.cfg"
    ] = """\
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
        """
    project.make()
    result = tox("-vv", cwd=project.location)
    result.assert_fail()
    assert (
        "No matching distribution found for somenotexisted_package1==9.9.9\n"
    ) in result.stdout_text


def test_deps_skipped(tox_project, tox):
    project = tox_project()
    project.contents[
        "tox.ini"
    ] = """\
        [tox]
        skipsdist = True
        [testenv]
        deps =
            somenotexisted_package1 == 9.9.9
            somenotexisted_package2
        commands=python -c "print('Hello, world!')"
        """
    project.make()
    result = tox("--no-deps", "-v", cwd=project.location)
    result.assert_success()

    assert (
        NO_DEPS_SKIP_TEMPLATE.format(
            "[somenotexisted_package1 == 9.9.9, somenotexisted_package2]"
        )
        in result.stdout_lines
    )


def test_extras_skipped(tox_project, tox):
    project = tox_project()
    project.contents[
        "tox.ini"
    ] = """\
        [tox]
        [testenv]
        extras =
            tests
        usedevelop=true
        commands=python -c "print('Hello, world!')"
        """
    project.contents[
        "setup.cfg"
    ] = """\
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
        """
    project.make()
    result = tox("--no-deps", "-v", cwd=project.location)
    result.assert_success()
    assert NO_EXTRAS_SKIP_TEMPLATE.format("['tests']") in result.stdout_lines


def test_deps_extras_skipped(tox_project, tox):
    project = tox_project()
    project.contents[
        "tox.ini"
    ] = """\
        [tox]
        [testenv]
        deps =
            somenotexisted_package1 == 9.9.9
            somenotexisted_package2
        extras =
            tests
        usedevelop=true
        commands=python -c "print('Hello, world!')"
        """
    project.contents[
        "setup.cfg"
    ] = """\
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
        """
    project.make()
    result = tox("--no-deps", "-v", cwd=project.location)
    result.assert_success()

    assert (
        NO_DEPS_SKIP_TEMPLATE.format(
            "[somenotexisted_package1 == 9.9.9, somenotexisted_package2]"
        )
        in result.stdout_lines
    )
    assert NO_EXTRAS_SKIP_TEMPLATE.format("['tests']") in result.stdout_lines


def test_deps_from_file_skipped(tox_project, tox):
    project = tox_project()
    project.contents[
        "tox.ini"
    ] = """\
        [tox]
        [testenv]
        deps =
            -rrequirements.txt
            somenotexisted_package2
        usedevelop=true
        commands=python -c "print('Hello, world!')"
        """
    project.contents[
        "requirements.txt"
    ] = """\
        somenotexisted_package1 == 9.9.9
        """
    project.make()
    result = tox("--no-deps", "-v", cwd=project.location)
    result.assert_success()

    assert (
        NO_DEPS_SKIP_TEMPLATE.format("[-rrequirements.txt, somenotexisted_package2]")
        in result.stdout_lines
    )


def test_deps_from_env_skipped(tox_project, tox):
    project = tox_project()
    project.contents[
        "tox.ini"
    ] = """\
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
        commands=python -c "print('Hello, world!')"
        """
    project.contents[
        "requirements.txt"
    ] = """\
        somenotexisted_package1 == 9.9.9
        """
    project.contents[
        "requirements1.txt"
    ] = """\
        somenotexisted_package2 == 9.9.9
        """
    project.make()
    result = tox("--no-deps", "-v", cwd=project.location)
    result.assert_success()

    assert (
        NO_DEPS_SKIP_TEMPLATE.format(
            "[-rrequirements.txt, somenotexisted_package3, -rrequirements1.txt,"
            " somenotexisted_package4]"
        )
        in result.stdout_lines
    )


def test_package_deps_required(tox_project, tox):
    """Plugin doesn't mangle package deps"""
    project = tox_project()
    project.contents[
        "tox.ini"
    ] = """\
        [tox]
        [testenv]
        usedevelop=true
        commands=python -c "print('Hello, world!')"
        """
    project.contents[
        "setup.cfg"
    ] = """\
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
        """
    project.make()
    result = tox("--no-deps", "-v", cwd=project.location)
    result.assert_fail()

    assert (
        "No matching distribution found for somenotexisted_package==9.9.9\n"
    ) in result.stdout_text
