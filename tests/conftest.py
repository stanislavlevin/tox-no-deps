from pathlib import Path
import shutil
import subprocess
import sys
import textwrap

import pytest


@pytest.fixture
def tmp_dir(tmp_path):
    yield tmp_path
    shutil.rmtree(tmp_path)


class ToxProject:
    def __init__(self, location, name="my_tox_project", contents=None):
        self.name = name
        self.location = location
        self.location.mkdir()

        if contents is None:
            self.contents = {
                Path(name)
                / "__init__.py": """\
                    def main():
                        print("Hello, World! I'm a test tox project")
                    """,
                "setup.cfg": f"""\
                    [metadata]
                    name = {name}
                    description = {name} project
                    version = 1.0
                    license = MIT

                    [options]
                    packages = find:

                    [options.packages.find]
                    where = .
                    """,
                "setup.py": """\
                    from setuptools import setup
                    if __name__ == "__main__":
                        setup()
                    """,
            }
        else:
            self.contents = dict(contents)

    def make(self):
        for file, content in self.contents.items():
            if Path(file).is_absolute():
                raise RuntimeError(
                    f"Files paths in contents should be relative, given: {file}"
                )
            target = self.location / file
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(textwrap.dedent(content), encoding="utf-8")


@pytest.fixture
def tox_project(tmp_dir, monkeypatch):
    def _make_tox_project(name="my_tox_project", contents=None):
        location = tmp_dir / name
        project = ToxProject(
            location,
            name=name,
            contents=contents,
        )
        monkeypatch.chdir(project.location)
        return project

    return _make_tox_project


class ToxResult:
    def __init__(self, result):
        self.result = result
        self.returncode = result.returncode

        self.stdout = self.result.stdout
        self.stdout_text = self.stdout.decode("utf-8")
        self.stdout_lines = self.stdout_text.splitlines()

        self.stderr = self.result.stderr
        self.stderr_text = self.stderr.decode("utf-8")
        self.stderr_lines = self.stderr_text.splitlines()

    def assert_success(self, command_out="Hello, world!"):
        assert self.returncode == 0
        assert self.stderr == b""
        assert command_out in self.stdout_lines

    def assert_fail(self, command_out="Hello, world!"):
        assert self.returncode != 0
        assert self.stderr == b""
        assert command_out not in self.stdout_lines


@pytest.fixture
def tox():
    def _run_tox(*args, cwd=None):
        tox_args = [sys.executable, "-m", "tox"]
        tox_args.extend(args)
        result = subprocess.run(tox_args, capture_output=True, cwd=cwd)
        return ToxResult(result)

    return _run_tox
