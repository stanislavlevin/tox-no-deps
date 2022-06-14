def test_flag_help(tox):
    result = tox("--help")
    assert result.returncode == 0
    assert b" --no-deps " in result.stdout
    assert result.stderr == b""
