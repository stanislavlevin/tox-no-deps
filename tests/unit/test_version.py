def test_version():
    pkg = __import__("tox_no_deps", fromlist=["__version__"])
    assert pkg.__version__
