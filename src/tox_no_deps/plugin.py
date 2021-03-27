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

    for envconfig in config.envconfigs.values():
        if not isinstance(envconfig.deps, list):
            raise TypeError("Not supported deps type", envconfig.deps)

        if envconfig.deps:
            reporter.verbosity1(
                f"no-deps plugin: deps: '{envconfig.deps}' will be skipped for"
                f" '{envconfig.envname}'"
            )
            envconfig.deps = []

        if not isinstance(envconfig.extras, list):
            raise TypeError("Not supported extras type", envconfig.extras)

        if envconfig.extras:
            reporter.verbosity1(
                f"no-deps plugin: extras: '{envconfig.extras}' will be skipped"
                f" for '{envconfig.envname}'"
            )
            envconfig.extras = []
