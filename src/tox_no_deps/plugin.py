from tox import reporter
import pluggy


hookimpl = pluggy.HookimplMarker("tox")


@hookimpl
def tox_addoption(parser):
    parser.add_argument(
        "--no-deps",
        action="store_true",
        help="Skip the installation of deps and extras",
    )


@hookimpl
def tox_configure(config):
    if not config.option.no_deps:
        return

    for _, envconfig in config.envconfigs.items():
        reporter.verbosity1(
            f"no-deps plugin: deps: '{envconfig.deps}' will be skipped for "
            f"'{envconfig.envname}'"
        )
        envconfig.deps = []
        reporter.verbosity1(
            f"no-deps plugin: extras: '{envconfig.extras}' will be skipped for "
            f"'{envconfig.envname}'"
        )
        envconfig.extras = []
