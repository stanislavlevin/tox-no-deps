from tox_no_deps import __version__


def test_help(tox_project):
    """
    - run tox --help
    - check if return code is 0
    - check if output contains --no-deps option
    """
    result = tox_project().run(["--help"])
    assert not result.returncode
    assert " --no-deps " in result.stdout
    assert not result.stderr


def test_version(tox_project):
    """
    - run tox --version
    - check if return code is 0
    - check if output contains plugin name and its version
    """
    result = tox_project().run(["--version"])
    assert not result.returncode
    expected_version = "tox-no-deps-" + __version__
    assert expected_version in result.stdout
    assert not result.stderr


def test_plugin_usage_deps(tox_project):
    """
    - set test env deps according to:
      https://tox.wiki/en/latest/config.html#deps
    - run tox with --no-deps
    - check if no deps are installed
    - check if output contains the only related record
    """
    project = tox_project()
    env_name = "py"
    project.contents[
        "tox.ini"
    ] = f"""\
        [tox]
        env_list = {env_name}
        [testenv]
        deps =
          foo_foo
          bar_bar
        commands = python --version
        """
    project.create()
    result = project.run(["-v", "--no-deps"])
    assert not result.returncode
    assert not result.stderr

    # must only be skipped for run environments
    assert result.stdout.count("relaxing dependencies for test env:") == 1
    # check an exact logging record
    assert (
        result.stdout.count(f"relaxing dependencies for test env: {env_name}")
        == 1
    )


def test_plugin_usage_extras(tox_project):
    """
    - set test env extras according to:
      https://tox.wiki/en/latest/config.html#extras
    - run tox with --no-deps
    - check if no deps are installed
    - check if output contains the only related record
    """
    project = tox_project()
    env_name = "py"
    project.contents[
        "pyproject.toml"
    ]: f"""\
        [project]
        name = "{project.name}"
        version = "1.0"

        [project.optional-dependencies]
        extra_foo = [
          "bar1_bar1",
          "bar2_bar2",
        ]
        """
    project.contents[
        "tox.ini"
    ] = f"""\
        [tox]
        env_list = {env_name}
        [testenv]
        extras = extra_foo
        commands = python --version
        """
    project.create()
    result = project.run(["-v", "--no-deps"])
    assert not result.returncode
    assert not result.stderr

    # must only be skipped for run environments
    assert result.stdout.count("relaxing dependencies for test env:") == 1
    # check an exact logging record
    assert (
        result.stdout.count(f"relaxing dependencies for test env: {env_name}")
        == 1
    )


def test_plugin_usage_dependency_groups(tox_project):
    """
    - set test env dependency_groups according to:
      https://tox.wiki/en/latest/config.html#dependency_groups
    - run tox with --no-deps
    - check if no deps are installed
    - check if output contains the only related record
    """
    project = tox_project()
    env_name = "py"
    project.contents[
        "pyproject.toml"
    ]: f"""\
        [project]
        name = "{project.name}"
        version = "1.0"

        [dependency-groups]
        group_foo = [
           "bar1_bar1",
           "bar2_bar2",
        ]
        """
    project.contents[
        "tox.ini"
    ] = f"""\
        [tox]
        env_list = {env_name}
        [testenv]
        dependency_groups = group_foo
        commands = python --version
        """
    project.create()
    result = project.run(["-v", "--no-deps"])
    assert not result.returncode
    assert not result.stderr

    # must only be skipped for run environments
    assert result.stdout.count("relaxing dependencies for test env:") == 1
    # check an exact logging record
    assert (
        result.stdout.count(f"relaxing dependencies for test env: {env_name}")
        == 1
    )


def test_plugin_usage_no_deps(tox_project):
    """
    - configure no env deps
    - run tox with --no-deps
    - check if output contains the only related record
    """
    project = tox_project()
    env_name = "py"
    project.contents[
        "tox.ini"
    ] = f"""\
        [tox]
        env_list = {env_name}
        [testenv]
        commands=python -c "print('Hello, hello')"
        """
    project.create()
    result = project.run(["-v", "--no-deps"])
    assert not result.returncode
    assert not result.stderr

    # must only be skipped for run environments
    assert result.stdout.count("relaxing dependencies for test env:") == 1
    # check an exact logging record
    assert (
        result.stdout.count(f"relaxing dependencies for test env: {env_name}")
        == 1
    )


def test_no_plugin_usage(tox_project):
    """
    - configure no env deps for network-isolated tox
    - run tox without --no-deps
    - check if output doesn't contain any related record
    """
    project = tox_project()
    env_name = "py"
    project.contents[
        "tox.ini"
    ] = f"""\
        [tox]
        env_list = {env_name}
        [testenv]
        commands=python -c "print('Hello, hello')"
        """
    project.create()
    result = project.run(["-v"])
    assert not result.returncode
    assert not result.stderr
    assert not result.stdout.count("relaxing dependencies for test env:")
